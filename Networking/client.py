import argparse
import socket
import logging
import sys
import os
import threading

sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'Protocol'))

from protocol import Protocol

# Set up logging for debug, info, error, and critical messages
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
log = logging.getLogger(__name__)

class Client:
    # Initialize the client with the server IP and port and other necessary variables
    def __init__(self, server_ip, server_port):
        self.server_ip = server_ip
        self.server_port = server_port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.running = True  # Flag to control the listener thread
        self.buffer = b""    
        self.game_state = None 

    def connect_to_server(self):
        # Attempt to connect to the server given the IP and port, send a join action (default on the server)
        try:
            self.sock.connect((self.server_ip, self.server_port))
            log.info(f"Connected to server at {self.server_ip}:{self.server_port}")
            self.send_join_request()

            # Start a separate thread that will listen for updates
            threading.Thread(target=self.listen_for_updates, daemon=True).start()
        # Handle connection errors and exit the program if necessary
        except Exception as e:
            log.error(f"Error connecting to server: {e}")
            sys.exit(1)

    def send_join_request(self):
        message = {"action": "join"}
        try:
            self.sock.sendall(Protocol.encode_message(message))
        # Joining the server went no bueno
        except Exception as e:
            log.error(f"Error sending join request to server: {e}")
            self.running = False
            self.sock.close()

    def send_action(self, action, target=None):
        message = {"action": action}
        if target:
            message["target"] = target
        try:
            self.sock.sendall(Protocol.encode_message(message))
        except Exception as e:
            log.error(f"Error sending action to server: {e}")
            self.running = False
            self.sock.close()

    def listen_for_updates(self):
        while self.running:
            try:
                data = self.sock.recv(8192) 
                try:
                    if data:
                        self.buffer += data  
                        while Protocol.message_complete(self.buffer):
                            # Process complete message
                            jsonheader, header_len = Protocol.decode_header(self.buffer)
                            content = Protocol.decode_message(self.buffer[header_len:], jsonheader)

                            # Calculate the length of the entire message (header + content)
                            message_len = header_len + jsonheader["content-length"]
                            self.handle_server_message(content)
                            self.buffer = self.buffer[message_len:]  # Remove the processed message
                    else:
                        log.info("Server disconnected")
                        self.running = False
                        self.sock.close()
                # Deal with the message not being in JSON format or not being able to be read
                except Exception as e:
                    log.error(f"Error processing message: {e}")
                    self.running = False
                    self.sock.close()
            # This is handle the socket being closed unexpectedly, or other things in which the server doesn't send data back
            except Exception as e:
                log.error(f"Error receiving message: {e}")
                self.running = False
                self.sock.close()

    def handle_server_message(self, content):
        action = content.get("action")
        if action == "update":
            self.game_state = content["game_state"]  # Update the game state
            self.display_game_state()
        else:
            log.warning(f"Unknown action received: {action}")

    def display_game_state(self):
        if not self.game_state:
            return
        # Display the game state in a grid format (10x10)
        grid_size = 10
        grid = [["." for _ in range(grid_size)] for _ in range(grid_size)]
        # Add players to the grid in the corners
        for player, info in self.game_state["players"].items():
            x, y = info["position"]
            grid[y][x] = "P"
        # Add the treasure to the grid 
        tx, ty = self.game_state["treasure"]
        grid[ty][tx] = "T"
        # Display the grid
        print("\nCurrent Game State:")
        for row in grid:
            print(" ".join(row))
        print("\nPlayers:")
        
        # Display player information
        for player, info in self.game_state["players"].items():
            print(f"{player}: Position {info['position']}, Health {info['health']}")
        print(f"Treasure: Position {self.game_state['treasure']}")
        # Check if the game is over and display the winner, then ask to replay (doesn't work yet)
        if self.game_state["game_over"]:
            print(f"\nGame Over! {self.game_state['winner']} wins the game!")
            self.prompt_for_replay()
        else:
            self.prompt_for_action()

    def prompt_for_action(self):
        print("Enter action (move/attack/quit): ", end="", flush=True)

    def prompt_for_replay(self):
        # Ask the user if they want to play again
        try:
            replay = input("Do you want to play again? (yes/no): ").strip().lower()
            if replay == "no":
                self.running = False
                self.sock.close()
                sys.exit(0)
            elif replay == "yes":
                self.send_action("replay")
            else:
                print("Invalid input. Please enter 'yes' or 'no'.")
                self.prompt_for_replay()
        # Player may just quit 
        except KeyboardInterrupt:
            log.info("Client shutting down")
            self.running = False
            self.sock.close()

    def run(self):
        # Main loop for the clients
        try:
            while self.running:
                action = input().strip()  # Block until the user enters an action
                if action == "quit":
                    self.send_action("quit")
                    self.running = False
                    self.sock.close()
                    log.info("Client shutting down")
                # Cardinal directions (game rule)
                elif action == "move":
                    direction = input("Enter direction (N/S/E/W/NE/NW/SE/SW): ").strip()
                    self.send_action("move", direction)
                    log.info(f"Player moved {direction}")
                # Attack another player (need to test more)
                elif action == "attack":
                    target = input("Enter player to attack: ").strip()
                    self.send_action("attack", target)
                    log.info(f"Player attacked {target}")
        except KeyboardInterrupt:
            log.info("Client shutting down")
            self.running = False
            self.sock.close()

def main():
    # Parse the IP and port arguments and create a client object (requirement)
    parser = argparse.ArgumentParser(description="Connect to the game server.")
    parser.add_argument("-i", "--ip", type=str, required=True, help="IP address of the server")
    parser.add_argument("-p", "--port", type=int, required=True, help="Port of the server")
    args = parser.parse_args()

    client = Client(args.ip, args.port)
    client.connect_to_server()
    client.run()

if __name__ == "__main__":
    main()