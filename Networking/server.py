import argparse
import selectors
import socket
import logging
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'Game'))
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'Protocol'))

from game import GameState
from protocol import Protocol

# Set up logging for debug, info, error, and critical messages
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
log = logging.getLogger(__name__)

class Server:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.sel = selectors.DefaultSelector()
        self.game = GameState()
        self.server_socket = self._create_server_socket()
        self.player_count = 0
        self.player_connections = {}

    def _create_server_socket(self):
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.bind((self.host, self.port))
        server_socket.listen()
        server_socket.setblocking(False)
        self.sel.register(server_socket, selectors.EVENT_READ, self.accept_connection)
        log.info(f"Server started on {self.host}:{self.port}")
        return server_socket

    def accept_connection(self, server_socket, mask):
        conn, addr = server_socket.accept()  # Accept the client connection
        log.info(f"Accepted connection from {addr}")
        conn.setblocking(False)
        self.sel.register(conn, selectors.EVENT_READ, self.handle_client)
        self.player_count += 1
        player_name = f"Player {self.player_count}"
        self.game.add_player(player_name)
        self.player_connections[conn] = player_name
        log.info(f"{player_name} has joined the game")
        
        # Send initial game state to the new player
        self.send_game_state(conn)

    def reset_game(self):
        self.game = GameState()
        self.player_count = 0
        self.player_connections = {}
        log.info("Game has been reset")

    def handle_client(self, conn, mask):
        try:
            data = conn.recv(4096)
            if data:
                jsonheader, header_len = Protocol.decode_header(data)
                content = Protocol.decode_message(data[header_len:], jsonheader)
                if not content:
                    raise ValueError("Invalid message format")

                action = content.get("action")
                if action == "join":
                    pass  # Join action is handled in accept_connection
                elif action == "move":
                    self.handle_move(conn, content)
                elif action == "attack":
                    self.handle_attack(conn, content)
                elif action == "replay":
                    self.reset_game()
                    self.send_game_state_to_all()
                else:
                    raise ValueError("Unknown action")
            else:
                self.disconnect_client(conn)
        except Exception as e:
            log.error(f"Error handling client: {e}")
            self.disconnect_client(conn)

    def handle_move(self, conn, content):
        player_name = self.player_connections[conn]
        direction = content.get("target")
        result = self.game.move_player(player_name, direction)
        if isinstance(result, str):  # Check if the result is a win message
            log.info(result)
        else:
            if result:
                log.info(f"{player_name} moved {direction}")
            else:
                log.warning(f"{player_name} failed to move {direction}")
        self.send_game_state_to_all()

    def handle_attack(self, conn, content):
        player_name = self.player_connections[conn]
        target = content.get("target")
        result = self.game.attack_player(player_name, target)
        log.info(result)
        self.send_game_state_to_all()

    def send_game_state(self, conn):
        game_state = self.game.get_game_state()
        message = {"action": "update", "game_state": game_state}
        encoded_message = Protocol.encode_message(message)
        try:
            conn.sendall(encoded_message)
            log.debug(f"Sent game state to {self.player_connections[conn]}")
        except Exception as e:
            log.error(f"Error sending game state to {self.player_connections[conn]}: {e}")
            self.disconnect_client(conn)

    def send_game_state_to_all(self):
        game_state = self.game.get_game_state()
        message = {"action": "update", "game_state": game_state}
        self.send_to_all(message)

    def send_to_all(self, message):
        for conn in self.player_connections:
            try:
                encoded_message = Protocol.encode_message(message)
                conn.sendall(encoded_message)
                log.debug(f"Sent message to {self.player_connections[conn]}")
            except Exception as e:
                log.error(f"Error sending message to {self.player_connections[conn]}: {e}")
                self.disconnect_client(conn)

    def disconnect_client(self, conn):
        player_name = self.player_connections.pop(conn, None)
        if player_name:
            log.info(f"{player_name} disconnected.")
        self.sel.unregister(conn)
        conn.close()

    def run(self):
        try:
            while True:
                events = self.sel.select()
                for key, mask in events:
                    callback = key.data
                    callback(key.fileobj, mask)
        except KeyboardInterrupt:
            log.info("Server shutting down.")
        finally:
            self.server_socket.close()

def main():
    parser = argparse.ArgumentParser(description="Start the game server.")
    parser.add_argument("-i", "--ip", type=str, default="0.0.0.0", help="IP address to bind the server")
    parser.add_argument("-p", "--port", type=int, required=True, help="Port to bind the server")
    args = parser.parse_args()

    server = Server(args.ip, args.port)
    server.run()

if __name__ == "__main__":
    main()
