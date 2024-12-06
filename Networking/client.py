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
    def __init__(self, server_ip, server_port):
        self.server_ip = server_ip
        self.server_port = server_port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.running = True  # Flag to control the listener thread
        self.buffer = b""    # Buffer to handle partial message reads

    def connect_to_server(self):
        try:
            self.sock.connect((self.server_ip, self.server_port))
            log.info(f"Connected to server at {self.server_ip}:{self.server_port}")
            self.send_join_request()

            # Start a listener thread for updates from the server
            threading.Thread(target=self.listen_for_updates, daemon=True).start()
        except Exception as e:
            log.error(f"Error connecting to server: {e}")
            sys.exit(1)

    def send_join_request(self):
        message = {"action": "join"}
        self.sock.sendall(Protocol.encode_message(message))

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
                data = self.sock.recv(4096)  # Receive data from the server
                if data:
                    self.buffer += data  # Append to the buffer
                    log.debug(f"Received data: {data[:50]}...")  # Debugging partial data

                    while Protocol.message_complete(self.buffer):
                        # Process complete message
                        jsonheader, header_len = Protocol.decode_header(self.buffer)
                        content = Protocol.decode_message(self.buffer[header_len:], jsonheader)

                        # Calculate the length of the entire message (header + content)
                        message_len = header_len + jsonheader["content-length"]

                        # Process the complete message and reset the buffer
                        self.handle_server_message(content)

                        # Update the buffer to keep only unprocessed data
                        self.buffer = self.buffer[message_len:]

                else:
                    log.info("Server disconnected")
                    self.running = False
                    self.sock.close()

            except Exception as e:
                log.error(f"Error receiving message: {e}")
                self.running = False
                self.sock.close()

    def handle_server_message(self, content):
        action = content.get("action")
        if action == "update":
            self.display_game_state(content["game_state"])
        else:
            log.warning(f"Unknown action received: {action}")

    def display_game_state(self, game_state):
        grid_size = 10
        grid = [["." for _ in range(grid_size)] for _ in range(grid_size)]

        for player, info in game_state["players"].items():
            x, y = info["position"]
            grid[y][x] = "P"

        tx, ty = game_state["treasure"]
        grid[ty][tx] = "T"

        print("\nCurrent Game State:")
        for row in grid:
            print(" ".join(row))
        print("\nPlayers:")
        for player, info in game_state["players"].items():
            print(f"{player}: Position {info['position']}, Health {info['health']}")
        print(f"Treasure: Position {game_state['treasure']}")

        if game_state["game_over"]:
            print(f"\nGame Over! {game_state['winner']} wins the game!")
            self.prompt_for_replay()

    def prompt_for_replay(self):
        replay = input("Do you want to play again? (yes/no): ").strip()
        if replay == "no":
            self.running = False
            self.sock.close()
            sys.exit(0)
        else:
            self.send_action("replay")

    def run(self):
        """ Main loop for user interaction """
        try:
            while self.running:
                action = input("Enter action (move/attack/quit): ").strip()
                if action == "quit":
                    self.send_action("quit")
                    self.running = False
                    self.sock.close()
                elif action == "move":
                    direction = input("Enter direction (N/S/E/W/NE/NW/SE/SW): ").strip()
                    self.send_action("move", direction)
                elif action == "attack":
                    target = input("Enter player to attack: ").strip()
                    self.send_action("attack", target)
        except KeyboardInterrupt:
            log.info("Client shutting down")
            self.running = False
            self.sock.close()

def main():
    parser = argparse.ArgumentParser(description="Connect to the game server.")
    parser.add_argument("-i", "--ip", type=str, required=True, help="IP address of the server")
    parser.add_argument("-p", "--port", type=int, required=True, help="Port of the server")
    args = parser.parse_args()

    client = Client(args.ip, args.port)
    client.connect_to_server()
    client.run()

if __name__ == "__main__":
    main()
