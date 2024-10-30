# Import the necessary libraries
import sys
import traceback
import requests
import logging
import webbrowser
import os
import selectors

# Import custom libraries
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'Game'))
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'Web'))

# Set up logging for debug, info, error, and critical messages
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
log = logging.getLogger(__name__)

# List to maintain connected clients and game data
connected_clients = []

sel = selectors.DefaultSelector()
# create a request dictionary based on the action 
def create_request(action, value):
    if action == "join_game":
        log.info(f"Adding player with name {value}")
        return dict(action=action, player_name=value)
    elif action == "leave_game":
        log.info(f"Player leaving: {value}")
        return dict(action="leave_game", player_name=value)
    elif action == "get_state":
        log.info("Getting game state")
        return dict(action=action, value=value)
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

def send_request(action, value):
    url = "http://localhost:3003"
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

def main():
    if len(sys.argv) != 5:
        log.error("Usage: python client.py <host> <port> <action> <value>")
        sys.exit(1)
    
    host, port = sys.argv[1], int(sys.argv[2])
    action, value = sys.argv[3], sys.argv[4]
    request = create_request(action, value)
    
    webbrowser.open_new_tab("http://localhost:3003")

    try:
        send_request(action, value)

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
        send_request("leave_game", value)

if __name__ == "__main__":
    main()