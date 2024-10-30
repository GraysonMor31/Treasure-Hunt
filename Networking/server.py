# Import the necessary libraries
import socket
import selectors
import traceback
import logging
import threading
import os
import sys
import time
import flask

# Add the parent directory to the path to get other modules
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'Game'))
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'Protocol'))
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'Web'))

# Import custom modules
from game_server import Message
from game_state import GameState
from website import Website
from protocol import Protocol

# Set up logging for debug, info, and error messages
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
log = logging.getLogger(__name__)

# Create a selector object
selector = selectors.DefaultSelector()
game_state = GameState()

# Define a function to wrap the accept() method of the socket object
def accept_wrapper(sock):
    try:
        connection, address = sock.accept()
        log.info(f"Accepted connection from {address}")
        connection.setblocking(False)
        message = Message(selector, connection, address, game_state)
        selector.register(connection, selectors.EVENT_READ, data=message)
    except Exception as e:
        log.error(f"Error accepting connection: {e}")
        log.error(traceback.format_exc())

def get_host():
    host = input("Enter the host to listen on, default is localhost @ 0.0.0.0: ")
    if not host:
        log.error("Invalid hostname or IP address, assigning default the default host")
        host = "0.0.0.0"
    return host

def get_port():
    port_input = input("Enter the port to listen on, default is 12345: ")
    try:
        port = int(port_input)
    except ValueError:
        log.error("Invalid port number, assigning the default port")
        port = 12345
    return port

def create_web_server():
    Website.run()

def broadcast_game_state(game_state, selector):
    timestamp = time.time()  # Server timestamp
    current_state = game_state.get_state()
    update_message = {"action": "state_update", "timestamp": timestamp, "state": current_state}
    message = Protocol.encode_message(update_message)
    
    clients = list(selector.get_map().values())
    
    for client in clients:
        if isinstance(client.data, Message):
            client.data.send_buffer += message
            client.data.set_selector_events_mask("w")

def main():
    # Get the host and port from user input
    host = get_host()
    port = get_port()
    
    # Start a thread for the web server
    web_server_thread = threading.Thread(target=create_web_server, daemon=True)
    web_server_thread.start()

    # Create a socket object and bind it to the host and port
    listen_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    listen_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    listen_socket.bind((host, port))
    
    # Don't block on the socket, to listen for multiple incoming connections
    log.info(f"Listening on {host}: {port}")
    listen_socket.listen()
    listen_socket.setblocking(False)
    selector.register(listen_socket, selectors.EVENT_READ, data=None)

    # Set up timing for periodic game state broadcasts
    BROADCAST_INTERVAL = 0.1  # in seconds
    last_broadcast = time.time()

    # Main event loop to listen for incoming connections continuously, only exit on keyboard interrupt
    try:
        while True:
            # Check the time for broadcasting the game state
            current_time = time.time()
            if current_time - last_broadcast >= BROADCAST_INTERVAL:
                broadcast_game_state(game_state, selector)
                last_broadcast = current_time

            events = selector.select(timeout=0.05)
            for key, mask in events:
                if key.data is None:
                    accept_wrapper(key.fileobj)
                else:
                    message = key.data
                    try:
                        message.process_events(mask)
                    except Exception as e:
                        log.error(f"Error processing events: {e}")
                        log.error(traceback.format_exc())
                        message.close()
    except KeyboardInterrupt:
        log.info("Caught keyboard interrupt, exiting")
    finally:
        selector.close()
        
if __name__ == "__main__":
    main()