import argparse
import socket
import logging
import sys
from protocol import Protocol

# Set up logging for debug, info, error, and critical messages
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
log = logging.getLogger(__name__)

class Client:
    def __init__(self, server_ip, server_port):
        self.server_ip = server_ip
        self.server_port = server_port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def connect_to_server(self):
        try:
            self.sock.connect((self.server_ip, self.server_port))
            log.info(f"Connected to server at {self.server_ip}:{self.server_port}")
            self.send_join_request()
            self.receive_message()  # Receive and display the initial game state
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
        self.sock.sendall(Protocol.encode_message(message))

    def receive_message(self):
        try:
            data = self.sock.recv(4096)
            if data:
                jsonheader, header_len = Protocol.decode_header(data)
                content = Protocol.decode_message(data[header_len:], jsonheader)
                if content["action"] == "update":
                    self.display_game_state(content["game_state"])
            else:
                log.info("Server disconnected")
                self.sock.close()
                sys.exit(0)
        except Exception as e:
            log.error(f"Error receiving message: {e}")
            self.sock.close()
            sys.exit(1)

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
            
            replay = input("Do you want to play again? (yes/no): ").strip()
            if replay == "no":
                self.sock.close()
                sys.exit(0)
            else:
                self.send_action("replay")
                self.receive_message()

    def run(self):
        while True:
            action = input("Enter action (move/attack/quit): ").strip()
            if action == "quit":
                self.sock.close()
                break
            elif action == "move":
                direction = input("Enter direction (N/S/E/W/NE/NW/SE/SW): ").strip()
                self.send_action("move", direction)
            elif action == "attack":
                target = input("Enter player to attack: ").strip()
                self.send_action("attack", target)
            self.receive_message()

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