# Import the necessary libraries
import sys
import socket
import selectors
import traceback
import logging
import struct
import json
import os

# Import custom libraries
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'Game'))
from game_client import Message

# Set up logging for debug, info, error, and critical messages
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
log = logging.getLogger(__name__)

# crate an objet to manage socket connections
sel = selectors.DefaultSelector()

# List to maintain connected clients and game data
connected_clients = []

# create a request dictionary based on the action 
def create_request(action, value):
    if action == "join_game":
        log.info(f"Adding player with name {value}")
        return dict(
            type="text/json", # specify the request type
            encoding="utf-8", # specify the encoding 
            content=dict(action=action, value=value),
    )
    elif action == "leave_game":
        log.info(f"Player leaving: {value}")
        return dict(
            type="text/json",
            encoding="utf-8",
            content=dict(action="leave_game", player_name=value),
    )
    elif action == "get_state":
        log.info("Getting game state")
        return dict(
            type="text/json",
            encoding="utf-8",
            content=dict(action=action, value=value), # content with action and value
        )
    else:
        # error if the action is unknown 
       raise ValueError(f"Unknown action: {action}")
    
# Handle server response to update the list of clients
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
   
# establish a non-blocking connection to the server 
def start_connection(host, port, request):
    addr = (host, port)
    log.info(f"Starting connection to {addr}")
    
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # create a TCP socket
    sock.setblocking(False)
    sock.connect_ex(addr)
    
    events = selectors.EVENT_READ | selectors.EVENT_WRITE
    message = Message(sel, sock, addr, request)
    sel.register(sock, events, data=message)

'''
# wait for events for up to seoncd 
# iterate throught triggered evetns
def main():
# check if the correct number of command-line arguments is provided 
    if len(sys.argv) != 5:
        log.error("Usage: python client.py <host> <port> <action> <value>")
        sys.exit(1) # exit if the usage is incorrect 

# extract command-line arguments 
    host, port = sys.argv[1], int(sys.argv[2])
    action, value = sys.argv[3], sys.argv[4]
    request = create_request(action, value)
    start_connection(host, port, request)
 
    try:
        while True:
            events = sel.select(timeout=1)
            for key, mask in events:
                message = key.data
                try:
                    message.process_events(mask)
                except Exception:
                # log any exceptions that occur during event processing
                    log.error(
                    "main: error: exception for",
                    f"{message.addr}:\n{traceback.format_exc()}",
                    )
                message.close()
            # Check for a socket being monitored to continue.
            if not sel.get_map():
                break
    except KeyboardInterrupt:
        log.info("Caught keyboard interrupt, exiting")
        leave_request = create_request("leave_game", value)
        start_connection(host, port, leave_request)
    finally:
        sel.close() # close the selector to release resources 

if __name__ == "__main__":
    main()
'''
def start_connection(host, port, request):
    addr = (host, port)
    log.info(f"Starting connection to {addr}")
    
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setblocking(False)
    sock.connect_ex(addr)
    
    events = selectors.EVENT_READ | selectors.EVENT_WRITE
    message = Message(sel, sock, addr, request)
    sel.register(sock, events, data=message)

def main():
    if len(sys.argv) != 5:
        log.error("Usage: python client.py <host> <port> <action> <value>")
        sys.exit(1)
    
    host, port = sys.argv[1], int(sys.argv[2])
    action, value = sys.argv[3], sys.argv[4]
    request = create_request(action, value)
    start_connection(host, port, request)

    try:
        while True:
            events = sel.select(timeout=1)
            if not events:
                log.debug("No events detected, continuing...")
                continue  # Continue looping if no events

            for key, mask in events:
                message = key.data
                try:
                    message.process_events(mask)
                except Exception as e:
                    log.error(f"main: error: exception for {message.addr}: {e}\n{traceback.format_exc()}")
                    message.close()  # Ensure the message/socket is closed on error

            # Check if no more sockets are being monitored and break the loop
            if not sel.get_map():
                log.info("No more active connections, exiting.")
                break

    except KeyboardInterrupt:
        log.info("Caught keyboard interrupt, exiting")
        leave_request = create_request("leave_game", value)
        start_connection(host, port, leave_request)
    finally:
        sel.close()  # Close the selector to release resources


if __name__ == "__main__":
    main()