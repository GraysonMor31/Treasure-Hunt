# Socket programming/messaging libraries
import sys
import os
import socket
import selectors
import traceback
import logging
import struct
import json

# Browser/HTTP server libraries
import webbrowser
import threading
import http.server
from http.server import HTTPServer, BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse, parse_qs

# Add the path to the custom libraries to the system path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'Server'))
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'WebPages'))

# Import custom libraries
from game_state import GameState
from game_client import Message

# Set up logging for debug, info, error, and critical messages
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
log = logging.getLogger(__name__)

# Create an object to manage socket connections
sel = selectors.DefaultSelector()

# List to maintain connected clients and game data
connected_clients = []

game_state = GameState()

class GameHTTPRequestHandler(http.server.BaseHTTPRequestHandler):
    # Handle GET requests (Starting a HTTP server on the clients machine)
    def do_GET(self):
        parsed_path = urlparse(self.path)
        query = parse_qs(parsed_path.query)
        action = query.get('action', [None])[0]
        value = query.get('value', [None])[0]

        # Check if the path is the root or index.html
        if self.path == "/" or self.path == "/index.html":
            self.serve_index()
        elif action == "get_players":
            response = self.get_players()
        else:
            response = {"error": "Unknown action"}

        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(response).encode('utf-8'))

    def serve_index(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        with open(os.path.join(os.path.dirname(__file__), '..', 'WebPages', 'index.html'), 'rb') as file:
            self.wfile.write(file.read())

    def get_players(self):
        return {"players" :game_state.get_players()}


def create_request(action, value):
    if action == "join_game":
        return dict(
            type="text/json",
            encoding="utf-8",
            content=dict(action=action, value=value),
        )
    else:
        # error if the action is unknown 
        raise ValueError(f"Unknown action: {action}")
    
def start_http_server():
    log.info("Starting HTTP server")
    server_address = ('', 8080)
    httpd = ThreadingHTTPServer(server_address, GameHTTPRequestHandler)
    httpd.serve_forever()

def start_connection(host, port, request):
    addr = (host, port)
    log.info(f"Starting connection to {addr}")
    
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # create a TCP socket
    sock.setblocking(False)
    sock.connect_ex(addr)
    
    events = selectors.EVENT_READ | selectors.EVENT_WRITE
    message = Message(sel, sock, addr, request)
    sel.register(sock, events, data=message)


def main():
    # Check if the correct number of command-line arguments is provided 
    if len(sys.argv) != 4:
        log.error("Usage: python client.py <host> <port> <username>")
        sys.exit(1) # Exit if the usage is incorrect 

    # Extract command-line arguments 
    host, port, username = sys.argv[1], int(sys.argv[2]), sys.argv[3]
    log.info(f"Joining game {host}: {port} as {username}")
    
    # Start the HTTP server in a separate thread
    http_server_thread = threading.Thread(target=start_http_server)
    http_server_thread.daemon = True
    http_server_thread.start()
    
    # Open the web page in the default web browser
    webbrowser.open('http://localhost:8080')
    
    # Start a persistent connection to the server to do the set actions
    start_connection(host, port, None)
    
    # Get the message object from the selector
    message = None
    for key in sel.get_map().values():
        if isinstance(key.data, Message):
            message = key.data
            break
    
    # Ask user for inputs to perform actions
    try:
        while True:
            action = input("Enter an action: ")
            value = input("Enter a value: ")
            
            # If a player leaves break the loop and ternimate the connection otherwise create a request
            if action != "leave_game":
                request = create_request(action, value)
                message.request = request
            elif action == "leave_game":
                request = create_request(action, value)
                message.request = request
                break
            else:
                log.error("Unknown action")
            
            # Wait for events to occur timeout is set to 5 seconds (this may need to be adjusted)
            events = sel.select(timeout=5)
            for key, mask in events:
                message = key.data
                try:
                    message.process_events(mask)
                except Exception as e:
                    log.error(f"Error processing events: {e}")
                    log.error(traceback.format_exc())
                    
            # Close the connection if player leaves the game                    
            if not sel.get_map():
                break
    
    # Handle keyboard interrupt and close the selector
    except KeyboardInterrupt:
        log.info("Caught keyboard interrupt, exiting")
    finally:
        sel.close()

if __name__ == "__main__":
    main()