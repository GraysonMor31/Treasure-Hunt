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
        self.send_game_state(conn)  # Send initial game state to the new client
        self.send_game_state_to_all()

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
        except Exception as e:
            log.error(f"Error sending game state to client: {e}")
            self.disconnect_client(conn)

    def send_game_state_to_all(self):
        game_state = self.game.get_game_state()
        message = {"action": "update", "game_state": game_state}
        self.send_to_all(message)

    def disconnect_client(self, conn):
        log.info("Client disconnected")
        self.sel.unregister(conn)
        conn.close()
        if conn in self.player_connections:
            del self.player_connections[conn]

    def send_to_all(self, message):
        encoded_message = Protocol.encode_message(message)
        for key in self.sel.get_map().values():
            if isinstance(key.fileobj, socket.socket) and key.fileobj != self.server_socket:
                try:
                    key.fileobj.sendall(encoded_message)
                except Exception as e:
                    log.error(f"Error sending message to client: {e}")
                    self.sel.unregister(key.fileobj)
                    key.fileobj.close()

    def event_loop(self):
        while True:
            events = self.sel.select(timeout=1)
            for key, mask in events:
                callback = key.data
                try:
                    callback(key.fileobj, mask)
                except Exception as e:
                    log.error(f"Error in event loop: {e}")
                    self.sel.unregister(key.fileobj)
                    key.fileobj.close()

    def start(self):
        try:
            self.event_loop()
        except KeyboardInterrupt:
            log.info("Server shutdown")
            self.server_socket.close()
            self.sel.close()

def main():
    parser = argparse.ArgumentParser(description="Start the game server.")
    parser.add_argument("-p", "--port", type=int, required=True, help="Port for the server to listen on")
    args = parser.parse_args()

    server = Server("0.0.0.0", args.port)
    server.start()

if __name__ == "__main__":
    main()