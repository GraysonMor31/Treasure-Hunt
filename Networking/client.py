# Import the necessary libraries
import argparse
import sys
import traceback
import requests
import selectors
import logging
import webbrowser
import os
import socket
import json

# Import custom libraries
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'Game'))
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'Protocol'))

from protocol import Protocol

# Set up logging for debug, info, error, and critical messages
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
log = logging.getLogger(__name__)

sel = selectors.DefaultSelector()

# List to maintain connected clients and game data
connected_clients = []

# Create a request dictionary based on the action 
def create_request(action, value):
    if action == "join_game":
        log.info(f"Adding player with name {value}")
        return {"action": action, "player_name": value}
    elif action == "leave_game":
        log.info(f"Player leaving: {value}")
        return {"action": "leave_game", "player_name": value}
    elif action == "get_state":
        log.info("Getting game state")
        return {"action": action, "value": value}
    elif action == "move":
        log.info(f"Player {value['player_name']} moving to {value['position']}")
        return {"action": action, "player_name": value["player_name"], "position": value["position"]}
    elif action == "chat":
        log.info(f"Player {value['player_name']} sending message: {value['message']}")
        return {"action": action, "player_name": value["player_name"], "message": value["message"]}
    else:
        raise ValueError(f"Unknown action: {action}")

# Update the handle_update function

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
    
    elif action == 'state_update':
        log.info(f"Game state updated: {data.get('state')}")
    
    elif action == 'chat':
        log.info(f"Chat message from {data.get('player_name')}: {data.get('message')}")

def send_tcp_request(sock, action, value):
    request = create_request(action, value)
    message = Protocol.encode_message(request)
    sock.sendall(message)

def send_http_request(action, value, web_server_ip):
    url = f"http://{web_server_ip}:3003"
    if action == "join_game":
        response = requests.post(f"{url}/join_game", json={"player_name": value})
    elif action == "leave_game":
        response = requests.post(f"{url}/leave_game", json={"player_name": value})
    elif action == "get_state":
        response = requests.get(f"{url}/get_state")
    else:
        raise ValueError(f"Unknown action: {action}")
    
    if response.status_code == 200:
        data = response.json()
        handle_update(data)
    else:
        log.error(f"Request failed with status code {response.status_code}")
'''
def main():
    if len(sys.argv) != 6:
        log.error("Usage: python client.py <tcp_host> <tcp_port> <web_server_ip> <action> <value>")
        sys.exit(1)
    
    tcp_host, tcp_port, web_server_ip = sys.argv[1], int(sys.argv[2]), sys.argv[3]
    action, value = sys.argv[4], sys.argv[5]
    
    # Open the web browser to the Flask server
    webbrowser.open_new_tab(f"http://{web_server_ip}:3003")

    try:
        # Create a socket object for TCP communication
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((tcp_host, tcp_port))
        sock.setblocking(False)
        sel.register(sock, selectors.EVENT_READ | selectors.EVENT_WRITE, data=None)

        send_tcp_request(sock, action, value)

        buffer = b""
        while True:
            events = sel.select(timeout=1)
            if not events:
                log.debug("No events detected, continuing...")
                continue  # Continue looping if no events
            for key, mask in events:
                if mask & selectors.EVENT_READ:
                    response = sock.recv(4096)
                    if response:
                        buffer += response
                        while True:
                            if len(buffer) < Protocol.HEADER_LENGTH:
                                break
                            jsonheader, header_length = Protocol.decode_header(buffer)
                            if jsonheader is None:
                                break
                            if len(buffer) < header_length + jsonheader["content-length"]:
                                break
                            message = Protocol.decode_message(buffer[header_length:], jsonheader)
                            buffer = buffer[header_length + jsonheader["content-length"]:]
                            handle_update(message)
                    else:
                        log.info("Connection closed by server")
                        sel.unregister(sock)
                        sock.close()
                        return  # Exit the loop and function
                if mask & selectors.EVENT_WRITE:
                    # Handle write events if needed
                    pass
    except KeyboardInterrupt:
        log.info("Caught keyboard interrupt, exiting")
        send_tcp_request(sock, "leave_game", value)
        sel.unregister(sock)
        sock.close()
    except Exception as e:
        log.error(f"main: error: {e}\n{traceback.format_exc()}")
        sel.unregister(sock)
        sock.close()
        '''
def main():
    parser = argparse.ArgumentParser(description="Client for connecting to the game server.")
    parser.add_argument('-i', '--ip', required=True, help="Server IP address or DNS.")
    parser.add_argument('-p', '--port', type=int, required=True, help="Server TCP port.")
    parser.add_argument('action', choices=['join_game', 'leave_game', 'get_state'], help="Action to perform.")
    parser.add_argument('value', help="Value for the action, like player name.")
    
    args = parser.parse_args()
    tcp_host = args.ip
    tcp_port = args.port
    action = args.action
    value = args.value
    
    # Open the web browser to the Flask server
    webbrowser.open_new_tab(f"http://{tcp_host}:3003")

    try:
        # Create a socket object for TCP communication
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((tcp_host, tcp_port))
        sock.setblocking(False)
        sel.register(sock, selectors.EVENT_READ | selectors.EVENT_WRITE, data=None)

        send_tcp_request(sock, action, value)

        buffer = b""
        while True:
            events = sel.select(timeout=1)
            if not events:
                log.debug("No events detected, continuing...")
                continue
            for key, mask in events:
                if mask & selectors.EVENT_READ:
                    response = sock.recv(4096)
                    if response:
                        buffer += response
                        while True:
                            if len(buffer) < Protocol.HEADER_LENGTH:
                                break
                            jsonheader, header_length = Protocol.decode_header(buffer)
                            if jsonheader is None:
                                break
                            if len(buffer) < header_length + jsonheader["content-length"]:
                                break
                            message = Protocol.decode_message(buffer[header_length:], jsonheader)
                            buffer = buffer[header_length + jsonheader["content-length"]:]
                            handle_update(message)
                    else:
                        log.info("Connection closed by server")
                        sel.unregister(sock)
                        sock.close()
                        return
                if mask & selectors.EVENT_WRITE:
                    pass
    except KeyboardInterrupt:
        log.info("Caught keyboard interrupt, exiting")
        send_tcp_request(sock, "leave_game", value)
        sel.unregister(sock)
        sock.close()
    except Exception as e:
        log.error(f"main: error: {e}\n{traceback.format_exc()}")
        sel.unregister(sock)
        sock.close()


if __name__ == "__main__":
    main()