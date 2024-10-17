# Import python libraries
import selectors
import struct
import json
import io
import sys
import logging

from protocol import Protocol
from game_state import GameState

# Set up logging for debug, info, error, and critical messages
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
log = logging.getLogger(__name__)

class Message:
    def __init__(self, selector, sock, addr, game_state):
        self.selector = selector
        self.sock = sock
        self.addr = addr
        self.game_state = game_state
        self.recv_buffer = b""
        self.send_buffer = b""
        self.jsonheader = None
        self.request = None
        self.response_created = False

    def set_selector_events_mask(self, mode):
        if mode == "r":
            events = selectors.EVENT_READ
        elif mode == "w":
            events = selectors.EVENT_WRITE
        elif mode == "rw":
            events = selectors.EVENT_READ | selectors.EVENT_WRITE
        else:
            raise ValueError(f"Invalid events mask mode {repr(mode)}.")
        self.selector.modify(self.sock, events, data=self)

    def read(self):
        try:
            data = self.sock.recv(12288)
        except BlockingIOError:
            pass
        else:
            if data:
                self.recv_buffer += data
            else:
                raise RuntimeError("Peer closed.")

    def write(self):
        if self.send_buffer:
            log.info(f"sending {repr(self.send_buffer)} to {self.addr}")
            try:
                sent = self.sock.send(self.send_buffer)
            except BlockingIOError:
                pass
            else:
                self.send_buffer = self.send_buffer[sent:]
                if sent and not self.send_buffer:
                    self.close()

    def process_events(self, mask):
        if mask & selectors.EVENT_READ:
            self.read()
            self.process_protoheader()
            self.process_jsonheader()
            self.process_request()
            if self.request and not self.response_created:
                self.create_response()
        if mask & selectors.EVENT_WRITE:
            self.write()

    def process_protoheader(self):
        if len(self.recv_buffer) >= Protocol.HEADER_LENGTH:
            self.jsonheader, header_len = Protocol.decode_header(self.recv_buffer)
            self.recv_buffer = self.recv_buffer[header_len:]

    def process_jsonheader(self):
        if self.jsonheader:
            content_len = self.jsonheader["content-length"]
            if len(self.recv_buffer) >= content_len:
                self.request = Protocol.decode_message(self.recv_buffer, self.jsonheader)
                self.recv_buffer = self.recv_buffer[content_len:]
                log.info(f"received request {repr(self.request)} from {self.addr}")

    def process_request(self):
        if self.jsonheader is None:
            return
        content_len = self.jsonheader["content-length"]
        if len(self.recv_buffer) >= content_len:
            data = self.recv_buffer[:content_len]
            self.recv_buffer = self.recv_buffer[content_len:]
            if self.jsonheader["content-type"] == "text/json":
                encoding = self.jsonheader["content-encoding"]
                self.request = json.loads(data.decode(encoding))
                log.info(f"received request {repr(self.request)} from {self.addr}")
            else:
                self.request = data
                log.info(f"received {self.jsonheader['content-type']} request from {self.addr}")

    def create_response(self):
    `   # Once a player joins the game, send the player list to all players
        if self.request["action"] == "join_game":
            player_name = self.request["player_name"]
            self.game_state.join_game(player_name)
            self.send_player_list()
        elif self.request["action"] == "leave_game":
            player_name = self.request["player_name"]
            self.game_state.leave_game(player_name)
            self.send_player_list()
        elif self.request["action"] == "send_chat":
            chat_message = self.request["chat_message"]
            self.game_state.send_chat(chat_message)
    
    def send_player_list(self):
        current_players = self.game_state.get_players()
        current_players_json = json.dumps({
        "type": "text/json",
        "encoding": "utf-8",
        "content": current_players,  # player list goes here
        "content-length": len(json.dumps(current_players)),  # length of serialized content
        "action": "send_player_list"
        })
        
        response = Protocol.encode_message(current_players_json)
        self.send_buffer += response
        
    def close(self):
        log.info(f"closing connection to {self.addr}")
        try:
            self.selector.unregister(self.sock)
        except Exception as e:
            log.error(f"error: selector.unregister() exception for {self.addr}: {repr(e)}")
        finally:
            self.sock.close()
            self.sock = None