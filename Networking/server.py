# Import the necessary libraries
import socket
import selectors
import socketserver
import traceback
import logging
import http.server
import threading
import os
import sys

# Add the parent directory to the path to get other modules
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'Game'))
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'Protocol'))
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'Web'))

# Import custom modules
from game_server import Message
from game_state import GameState
from web_server import MyRequestHandler
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
    host = input("Enter the host to listen on, defualt is localhost @ 127.0.0.1: ")
    if not host:
        log.error("Invalid hostname or IP address, assigning default the defualt host")
        host = "127.0.0.1"
    return host

def get_port():
    port_input = input("Enter the port to listen on, default is 12345: ")
    try:
        port = int(port_input)
    except ValueError:
        log.error("Invalid port number, assigning the defualt port")
        port = 12345
    return port

def create_web_server():
    web_port = 3001
    handler = MyRequestHandler

    with socketserver.TCPServer(("", web_port), handler) as httpd:
        log.info(f"Serving on port {web_port}")
        httpd.serve_forever()

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

    # Main event loop to listen for incoming connections continuously, only exit on keyboard interrupt
    try:
        while True:
            events = selector.select(timeout=None)
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
        log.info("Closing the server and cleaning up")
        for key in selector.get_map().values():
            key.data.close()
        selector.close()
            
if __name__ == "__main__":
    main()