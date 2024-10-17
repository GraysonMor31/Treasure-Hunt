import sys
import socket
import selectors
import traceback
import logging
import struct
import json
import threading
import webbrowser
import http.server
from http.server import HTTPServer, BaseHTTPRequestHandler, SimpleHTTPRequestHandler, ThreadingHTTPServer, CGIHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

import os
server = sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'Server'))
html = sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'WebPages', 'index.html'))

# Import custom libraries
from game_client import Message
from game_server import GameState

# Set up logging for debug, info, error, and critical messages
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
log = logging.getLogger(__name__)

# Create an object to manage socket connections
sel = selectors.DefaultSelector()

# List to maintain connected clients and game data
connected_clients = []

game_state = GameState()

class GameHTTPRequestHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        parsed_path = urlparse(self.path)
        query = parse_qs(parsed_path.query)
        action = query.get('action', [None])[0]
        value = query.get('value', [None])[0]

        if self.path == "/":
            self.serve_index()
        elif action == "join_game":
            response = self.add_player(value)
        elif action == "send_chat":
            response = self.send_chat(value)
        elif action == "leave_game":
            response = self.leave_game(value)
        elif action == "up":
            response = self.up()
        elif action == "down":
            response = self.down()
        elif action == "left":
            response = self.left()
        elif action == "right":
            response = self.right()
        elif action == "diag_up_left":
            response = self.diag_up_left()
        elif action == "diag_up_right":
            response = self.diag_up_right()
        elif action == "diag_down_left":
            response = self.diag_down_left()
        elif action == "diag_down_right":
            response = self.diag_down_right()
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
        with open(html, 'rb') as file:
            self.wfile.write(file.read())

    def join(self, player_name):
        if player_name:
            game_state.add_player(player_name)
            return {"status": "Player added", "player_name": player_name}
        return {"error": "Player name is required"}

    def send_chat(self, message):
        if message:
            game_state.send_chat(message)
            return {"status": "Chat message sent", "message": message}
        return {"error": "Message is required"}

    def leave_game(self, player_name):
        if player_name:
            game_state.remove_player(player_name)
            return {"status": "Player left", "player_name": player_name}
        return {"error": "Player name is required"}

    def up(self):
        game_state.move_player("up")
        return {"status": "Player moved up"}
        
    def down(self):
        game_state.move_player("down")
        return {"status": "Player moved down"}
    
    def left(self):
        game_state.move_player("left")
        return {"status": "Player moved left"}
    
    def right(self):
        game_state.move_player("right")
        return {"status": "Player moved right"}
    
    def diag_up_left(self):
        game_state.move_player("diag_up_left")
        return {"status": "Player moved diagonally up and left"}
    
    def diag_up_right(self):
        game_state.move_player("diag_up_right")
        return {"status": "Player moved diagonally up and right"}
    
    def diag_down_left(self):
        game_state.move_player("diag_down_left")
        return {"status": "Player moved diagonally down and left"}
    
    def diag_down_right(self):
        game_state.move_player("diag_down_right")
        return {"status": "Player moved diagonally down and right"}

def create_request(action, value):
    if action == "leave_game":
        log.info(f"Player leaving: {value}")
        return dict(
            type="text/json",
            encoding="utf-8",
            content=dict(action="leave_game", player_name=value),
    )
    elif action == "send_chat":
        log.info(f"Sending chat message: {value}")
        return dict(
            type="text/json",
            encoding="utf-8",
            content=dict(action=action, value=value),
    )
    elif action == "up":
        log.info(f"Moving player up")
        return dict(
            type="text/json",
            encoding="utf-8",
            content=dict(action=action),
    )
    elif action == "down":
        log.info(f"Moving player down")
        return dict(
            type="text/json",
            encoding="utf-8",
            content=dict(action=action),
    )
    elif action == "left":
        log.info(f"Moving player left")
        return dict(
            type="text/json",
            encoding="utf-8",
            content=dict(action=action),
    )
    elif action == "right":
        log.info(f"Moving player right")
        return dict(
            type="text/json",
            encoding="utf-8",
            content=dict(action=action),
    )
    elif action == "diag_up_left":
        log.info(f"Moving player diagonally up and left")
        return dict(
            type="text/json",
            encoding="utf-8",
            content=dict(action=action),
    )
    elif action == "diag_up_right":
        log.info(f"Moving player diagonally up and right")
        return dict(
            type="text/json",
            encoding="utf-8",
            content=dict(action=action),
    )
    elif action == "diag_down_left":
        log.info(f"Moving player diagonally down and left")
        return dict(
            type="text/json",
            encoding="utf-8",
            content=dict(action=action),
    )
    elif action == "diag_down_right":
        log.info(f"Moving player diagonally down and right")
        return dict(
            type="text/json",
            encoding="utf-8",
            content=dict(action=action),
    )
    elif action == "get_players":
        log.info(f"Getting players")
        return dict(
            type="text/json",
            encoding="utf-8",
            content=dict(action=action),
    )
    else:
        # error if the action is unknown 
       raise ValueError(f"Unknown action: {action}")

def handle_update(data):
    global connected_clients
    action = data.get('action')
    
    if action == 'update_clients':
        connected_clients = data.get('clients', [])
        log.info(f"Updated client list: {connected_clients}")
    
    elif action == 'player_joined':
        log.info(f"Player joined: {data.get('player_name')}")
    
    elif action == 'player_left':
        log.info(f"Player left: {data.get('player_name')}")

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
    if len(sys.argv) != 3:
        log.error("Usage: python client.py <host> <port>")
        sys.exit(1) # Exit if the usage is incorrect 

    # Extract command-line arguments 
    host, port = sys.argv[1], int(sys.argv[2])
    log.info(f"Connecting to {host}: {port}")
    
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
            username = input("Enter your username: ")
            
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