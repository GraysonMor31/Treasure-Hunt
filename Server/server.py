# Import the necessary libraries
import socket
import selectors
import traceback
import logging
import sys

# Import custom libraries
from gameserver import Message, GameState

# Set up logging for debug, info, and error messages
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
log = logging.getLogger(__name__)

# Create a selector object
selector = selectors.DefaultSelector()

# Define a function to wrap the accept() method of the socket object
def accept_wrapper(sock):
    """
    Accept a connection and set it to non-blocking mode, register the connection with the selector object
    
    Args:
        sock (socket.socket): A socket object that is listening for incoming connections
    """
    try:
        connection, address = sock.accept()
        log.info(f"Accepted connection from {address}")
        connection.setblocking(False)
        message = gameserver.Message(selector, conn, addr, game_state)
        selector.register(connection, selectors.EVENT_READ, data=message)
    except Exception as e:
        log.error(f"Error accepting connection: {e}")
        log.error(traceback.format_exc())

def get_host():
    host = input("Enter the host to listen on: ")
    if not host:
        log.error("Invalid hostname or IP address, assigning default host 'localhost'")
        host = "localhost"
    return host

def get_port():
    port_input = input("Enter the port to listen on: ")
    try:
        port = int(port_input)
    except ValueError:
        log.error("Invalid port number, assigning default port 12345")
        port = 12345
    return port

def main():
    # Get the host and port from user input
    host = get_host()
    port = get_port()

    listen_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    listen_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    listen_socket.bind((host, port))
    log.info(f"Listening on {host}:{port}")
    listen_socket.listen()
    listen_socket.setblocking(False)
    selector.register(listen_socket, selectors.EVENT_READ, data=None)

    # Main event loop
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
        selector.close()

if __name__ == "__main__":
    main()