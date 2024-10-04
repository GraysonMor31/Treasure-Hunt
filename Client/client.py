# Import the necessary libraries
import sys
import socket
import selectors
import traceback
import logging
import struct

# Import custom libraries
from gameclient import Message

# Set up logging for debug, info, error, and critical messages
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
log = logging.getLogger(__name__)

sel = selectors.DefaultSelector()


def create_request(action, value):
    if action == "add_player":
        log.info(f"Adding player with name {value}")
        return dict(
            type="text/json",
            encoding="utf-8",
            content=dict(action=action, value=value),
    )
    elif action == "get_state":
        log.info("Getting game state")
        return dict(
            type="text/json",
            encoding="utf-8",
            content=dict(action=action, value=value),
        )
 
    else:
       raise ValueError(f"Unknown action: {action}")
   


def start_connection(host, port, request):
    addr = (host, port)
    log.info(f"Starting connection to {addr}")
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setblocking(False)
    sock.connect_ex(addr)
    events = selectors.EVENT_READ | selectors.EVENT_WRITE
    message = Message(sel, sock, addr, request)
    sel.register(sock, events, data=message)


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
        for key, mask in events:
            message = key.data
            try:
                message.process_events(mask)
            except Exception:
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
finally:
    sel.close()