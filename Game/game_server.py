# Import python libraries
import selectors
import struct
import json
import io
import sys
import logging
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'Protocol'))
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
        """
        Set the selector events mask for the socket 

        Args:
            mode (str): The mode to set the events mask to
        """
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
        """
        Read data from the socket into a 12KB buffer
        
        Args:
            Message object
        """
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
        """
        Write data to a buffer and send it to the socket
        
        Args:
            Message object
        """
        if self.send_buffer:
            log.info(f"sending {repr(self.send_buffer)} to {self.addr}")
            try:
                sent = self.sock.send(self.send_buffer)
            except BlockingIOError:
                pass
            else:
                self.send_buffer = self.send_buffer[sent:]
                if sent and not self.send_buffer:
                    self.set_selector_events_mask("r")
                    
    def process_events(self, mask):
        """
        Process events for the socket wether it is read or write

        Args:
            Message object
            mask: The mask of events to process
        """
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
        """
        Process the protocol header for the message
        
        Args:
            Message object
        """
        if len(self.recv_buffer) >= Protocol.HEADER_LENGTH:
            self.jsonheader, header_len = Protocol.decode_header(self.recv_buffer)
            self.recv_buffer = self.recv_buffer[header_len:]

    def process_jsonheader(self):
        """
        Process the JSON header for the message (only if it is a JSON message ie content-type is text/json)
        
        Args:
            Message object
        """
        if self.jsonheader:
            content_len = self.jsonheader["content-length"]
            if len(self.recv_buffer) >= content_len:
                self.request = Protocol.decode_message(self.recv_buffer, self.jsonheader)
                self.recv_buffer = self.recv_buffer[content_len:]
                log.info(f"received request {repr(self.request)} from {self.addr}")

    def process_request(self):
        """
        Process the request from the client, and decode it if it is a JSON message
        
        Args:
            Message object
        """
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
        if self.request:
            action = self.request.get("action")
            if action == "join_game":
                player_name = self.request.get("player_name")
                self.game_state.add_player(player_name, self.addr)
                self.send_player_list()
            elif action == "leave_game":
                player_name = self.request.get("player_name")
                self.game_state.remove_player(player_name)
                self.send_player_list()
            elif action == "get_state":
                response = {
                    "result": self.game_state.get_state(),
                    "current_turn": self.game_state.get_curr_turn()
                }
                message = Protocol.encode_message(response)
                self.send_buffer += message
                self.set_selector_events_mask("w")
            elif action == "move":
                player_name = self.request.get("player_name")
                new_position = self.request.get("position")
                self.game_state.update_player_position(player_name, new_position)
                self.broadcast_game_state()
            elif action == "chat":
                player_name = self.request.get("player_name")
                message = self.request.get("message")
                self.broadcast_chat_message(player_name, message)
            else:
                log.error("Unknown action received")
                response = {"error": "Unknown action"}
                message = Protocol.encode_message(response)
                self.send_buffer += message
                self.set_selector_events_mask("w")
            self.response_created = True
        else:
            log.error("No request")
    
    def broadcaset_turn_update(self): 
        curr_trun = self.game_state.get_curr_turn()
        update_message = {"action": "update_turn", "current_player": curr_trun}
        message = Protocol.encode_message(update_message)
        
        for client in self.selector.get_map().values():
            if isinstance(client.data, Message):
                client.data.send_buffer += message
                client.data.set_selector_events_mask("w")
                
    def broadcast_game_state(self):
        current_state = self.game_state.get_state()
        update_message = {"action": "state_update", "state": current_state}
        message = Protocol.encode_message(update_message)
        for client in self.selector.get_map().values():
            if isinstance(client.data, Message):
                client.data.send_buffer += message
                client.data.set_selector_events_mask("w")

    def broadcast_chat_message(self, player_name, message):
        chat_message = {"action": "chat", "player_name": player_name, "message": message}
        message = Protocol.encode_message(chat_message)
        for client in self.selector.get_map().values():
            if isinstance(client.data, Message):
                client.data.send_buffer += message
                client.data.set_selector_events_mask("w")            
    
    def send_player_list(self, delta_only=True):
        clients = self.game_state.get_recent_changes() if delta_only else self.game_state.get_players()

        if not clients:  # If no recent changes, send the full list
            clients = self.game_state.get_players()
        
        update_message = {"action": "update_clients", "clients": clients}
        log.info(f"Broadcasting updated client list: {clients}")
        message = Protocol.encode_message(update_message)

        # Make a copy of the values to avoid dictionary changes during iteration
        clients_list = list(self.selector.get_map().values())
        for client in clients_list:
            if isinstance(client.data, Message):
                client.data.send_buffer += message
                client.data.set_selector_events_mask("w")

    
    def close(self):
        """
        Close the connection to the socket and deregister it from the selector
        
        Args:
            Message object
        
        log.info(f"closing connection to {self.addr}")
        try:
            self.selector.unregister(self.sock)
        except Exception as e:
            log.error(f"error: selector.unregister() exception for {self.addr}: {repr(e)}")
        finally:
            self.sock.close()
            self.sock = None
            """
    def close(self):
        log.info(f"closing connection to {self.addr}")
        player_name = self.game_state.get_player_name(self.addr)  # Retrieve player's name before removal
        self.game_state.remove_player(player_name)
        disconnect_message = {"action": "player_disconnect", "player": player_name}
        message = Protocol.encode_message(disconnect_message)

        # Broadcast the disconnect message to all clients
        for client in self.selector.get_map().values():
            if isinstance(client.data, Message) and client.data != self:
                client.data.send_buffer += message
                client.data.set_selector_events_mask("w")
        try:
            self.selector.unregister(self.sock)
        except Exception as e:
            log.error(f"error: selector.unregister() exception for {self.addr}: {repr(e)}")
        finally:
            self.sock.close()
            self.sock = None