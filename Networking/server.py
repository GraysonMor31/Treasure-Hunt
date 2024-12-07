import argparse
import selectors
import socket
import logging
import sys
import os

# append paths for the "game" and "protocol" modules
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'Game'))
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'Protocol'))

from game import GameState
from protocol import Protocol

# Set up logging for debug, info, error, and critical messages
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
log = logging.getLogger(__name__)

class Server:
    # Initialize the server with the host and port and other necessary variables
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.sel = selectors.DefaultSelector()
        self.game = GameState()
        self.server_socket = self.create_server_socket()
        self.player_count = 0
        self.player_connections = {}

    # Creating and set up the server socket
    def create_server_socket(self):
        try:
            # Create a TCP/IP socket, host will always listen on all interfaces, user will set the port when they start the game
            server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            server_socket.bind((self.host, self.port))
            server_socket.listen()
            server_socket.setblocking(False)
            self.sel.register(server_socket, selectors.EVENT_READ, self.accept_connection)
            log.info(f"Server started on {self.host}:{self.port}")
            return server_socket 
        # Handle socket errors
        except socket.error as e:
            log.error(f"Failed to create server socket: {e}")
            sys.exit(1) # Exit the program if there is a failure

    # Handle new inciming client connections 
    def accept_connection(self, server_socket, mask):
        try:
            conn, addr = server_socket.accept()  # Accept the client 
            log.info(f"Accepted connection from {addr}")
            conn.setblocking(False) # Set to be a non-blocking socket this way we can have multiple connections
            self.sel.register(conn, selectors.EVENT_READ, self.handle_client)
            
            # Attempt to add the player to the game, if it fails disconnect the client
            try:
                self.player_count += 1
                player_name = f"Player {self.player_count}"
                self.game.add_player(player_name)
                self.player_connections[conn] = player_name
                log.info(f"{player_name} has joined the game")
            # Handle errors adding the player this, not occured in testing but ya never know
            except ValueError as e:
                log.error(f"Error adding player: {e}")
                self.disconnect_client(conn)
            self.send_game_state(conn)
        # This is caused by the socket being closed unexpectedly
        except socket.error as e:
            log.error(f"Error accepting connection: {e}, closing server.")

    # reset the game state and add players back 
    def reset_game(self):
        self.game = GameState()
        log.info("Game has been reset")
        for player in self.player_connections.values():
            self.game.add_player(player)

    # handle client messages, including moves, attacks, and other actions 
    def handle_client(self, conn, mask):
        try:
            data = conn.recv(8192) # Receive data from the client in 8192 byte chunks
            if data:
                jsonheader, header_len = Protocol.decode_header(data)
                content = Protocol.decode_message(data[header_len:], jsonheader)
                if not content:
                    raise ValueError("Invalid message format should be in JSON")

                action = content.get("action")
                if action == "join":
                    pass  # Join action is handled in accept_connection (default)
                # These seem self-explanatory
                elif action == "move":
                    self.handle_move(conn, content)
                elif action == "attack":
                    self.handle_attack(conn, content)
                elif action == "replay":
                    self.reset_game()
                    self.send_game_state_to_all()
                else:
                    raise ValueError("Unknown action, should be 'join', 'move', 'attack', or 'replay'")
            else:
                self.disconnect_client(conn)
        # Handle socket errors and invalid messages
        except (socket.error, ValueError) as e:
            log.error(f"Error handling client: {e}")
            self.disconnect_client(conn)

    # handle player movment 
    def handle_move(self, conn, content):
        try:
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
        # Wrong directions
        except KeyError as e:
            log.error(f"Error handling move: {e}, should be 'N', 'S', 'E', 'W', 'NE', 'NW', 'SE', or 'SW'")

    # handle player attacks
    def handle_attack(self, conn, content):
        try:
            player_name = self.player_connections[conn]
            target = content.get("target")
            result = self.game.attack_player(player_name, target)
            log.info(result)
            self.send_game_state_to_all() # Send the game state to all players
        # Deal with wrong names
        except KeyError as e:
            log.error(f"Error handling attack: {e}, should be a valid player name, i.e. 'Player 1'")

    # current game state to a specific player 
    def send_game_state(self, conn):
        try:
            game_state = self.game.get_game_state()
            message = {"action": "update", "game_state": game_state}
            encoded_message = Protocol.encode_message(message)
            conn.sendall(encoded_message) # Send the game state to the client
            log.debug(f"Sent game state to {self.player_connections[conn]}")
        # GameState may not store right or whatever reason
        # Look into this more
        except (socket.error, KeyError) as e:
            log.error(f"Error sending game state to {self.player_connections.get(conn, 'unknown')}: {e}")
            self.disconnect_client(conn)

    # sent the current game state to all players
    def send_game_state_to_all(self):
        game_state = self.game.get_game_state()
        message = {"action": "update", "game_state": game_state}
        self.send_to_all(message)

    # send a message to all player 
    def send_to_all(self, message):
        for conn in list(self.player_connections):
            try:
                # Send the message to all players
                encoded_message = Protocol.encode_message(message)
                conn.sendall(encoded_message)
                log.debug(f"Sent message to {self.player_connections[conn]}")
            # More socket errors (shocker)
            except (socket.error, KeyError) as e:
                log.error(f"Error sending message to {self.player_connections.get(conn, 'unknown')}: {e}")
                self.disconnect_client(conn)

    # disconnect a cluent and clean up 
    def disconnect_client(self, conn):
        player_name = self.player_connections.pop(conn, None)
        if player_name:
            log.info(f"{player_name} disconnected.") # Log the disconnection on the server
        try:
            self.sel.unregister(conn)
            conn.close()
        # More socket errors, I feel like this is getting out of hand
        except socket.error as e:
            log.error(f"Error disconnecting client: {e}")

    # run the server and handle incoming connection 
    def run(self):
        try:
            while True:
                events = self.sel.select()
                for key, mask in events:
                    callback = key.data
                    callback(key.fileobj, mask)
        except KeyboardInterrupt:
            log.info("Server shutting down.") # Close the server if ^C
        except Exception as e:
            log.error(f"Unexpected error: {e}") # Log any other errors
        finally:
            self.server_socket.close() # Close the server socket

# main funcion to start the server
def main():
    parser = argparse.ArgumentParser(description="Start the game server.")
    parser.add_argument("-i", "--ip", type=str, default="0.0.0.0", help="IP address to bind the server")
    parser.add_argument("-p", "--port", type=int, required=True, help="Port to bind the server")
    args = parser.parse_args()

    server = Server(args.ip, args.port)
    server.run()

if __name__ == "__main__":
    main()