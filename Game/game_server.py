# Import necessary libraries
'''
import json
import selectors
import traceback
import logging

from protocol import Protocol

# Set up logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
log = logging.getLogger(__name__)

class Message:
    
    def __init__(self, selector, connection, address, game_state):
        self.selector = selector
        self.connection = connection
        self.address = address
        self.game_state = game_state
        self.recv_buffer = b'' 
        self.send_buffer = b''  
        self.jsonheader = None
        self.response = None
        
    def process_events(self, mask):
        if mask == "r":
            events = selectors.EVENT_READ
        elif mask == "w":
            events = selectors.EVENT_WRITE
        elif mask == "rw":
            events = selectors.EVENT_READ | selectors.EVENT_WRITE
        else:
            raise ValueError(f"Invalid events mask mode {repr(mask)}.")
        self.selector.modify(self.sock, events, data=self)
        
    def read(self):
        try:
            data = self.connection.recv(6144)
            if data:
                self.recv_buffer += data
                self.process_header()  # Process headers after receiving data
            else:
                log.info(f"Closing connection to {self.address}")
                self.close()
        except BlockingIOError:
            pass
                
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
            
    def process_header(self): 
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
        if self.request:
            action = self.request.get("action")
            
            if action == "join":
                self.response = self.game_state.add_player(self.request)
            elif action == "leave":
                self.response = self.game_state.remove_player(self.request)
            else:
                raise ValueError(f"Invalid action {action}") 
        
    def close(self):
        log.info("Closing connection to {self.address}")
        try:
            self.selector.unregister(self.connection)
        except Exception as e:
            log.error(f"error: selector.unregister() exception for {self.address}: {e}")
        try:
            self.connection.close()
        except Exception as e:
            log.error(f"error: self.connection.close() exception for {self.address}: {e}")
        finally:
            self.connection = None
'''
# Import python libraries
import selectors
import struct
import json
import io
import sys
import logging
from game_state import GameState

# Set up logging for debug, info, error, and critical messages
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
log = logging.getLogger(__name__)

# Define the Protocol class
class Protocol:
    HEADER_LENGTH = 2

    def encode_message(content, content_type="text/json", encoding="utf-8"):
        """
        A method to encode a message to be sent over a socket

        Args:
            content (dict): The content to encode
            content_type (str): The type of content to encode
            encoding (str): The encoding to use for the content

        Returns:
            A bytes object containing the encoded message
        """
        content_bytes = json.dumps(content, ensure_ascii=False).encode(encoding)
        jsonheader = {
            "byteorder": sys.byteorder,
            "content-type": content_type,
            "content-encoding": encoding,
            "content-length": len(content_bytes),
        }
        jsonheader_bytes = json.dumps(jsonheader, ensure_ascii=False).encode(encoding)
        message_hdr = struct.pack(">H", len(jsonheader_bytes))
        message = message_hdr + jsonheader_bytes + content_bytes
        return message

    def decode_header(data):
        """
        A method to decode the header of a message

        Args:
            data (bytes): The data to decode
        
        Returns:
            A tuple containing the decoded header and the length of the header
        """
        jsonheader_len = struct.unpack(">H", data[:Protocol.HEADER_LENGTH])[0]
        jsonheader = json.loads(data[Protocol.HEADER_LENGTH:Protocol.HEADER_LENGTH + jsonheader_len].decode("utf-8"))
        return jsonheader, Protocol.HEADER_LENGTH + jsonheader_len

    def decode_message(data, jsonheader):
        """
        A method to decode a message

        Args:
            data (bytes): The data to decode
            jsonheader (dict): The header of the message

        Returns:
            The decoded message
        """
        content_len = jsonheader["content-length"]
        content = json.loads(data[:content_len].decode(jsonheader["content-encoding"]))
        return content

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
                    self.close()

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
        """
        Create a response to the request based on the action and value in the request
        
        Args:
            Message object
        """
        if self.request:
            action = self.request.get("action")
            if action == "join_game":
                player_name = self.request.get("value")
                self.game_state.add_player(player_name)
                self.send_player_list()
            elif action == "leave_game":
                player_name = self.request.get("player_name")
                self.game_state.remove_player(player_name)
                self.send_player_list()
            elif action == "get_state":
                response = {"result": self.game_state.get_state()}
                message = Protocol.encode_message(response)
                self.send_buffer += message
                self.set_selector_events_mask("w")
            else:
                log.error("Unknown action received")
                response = {"error": "Unknown action"}
                message = Protocol.encode_message(response)
                self.send_buffer += message
                self.set_selector_events_mask("w")
            self.response_created = True
        else:
            log.error("No request")
    
    def send_player_list(self):
        clients = self.game_state.get_players()  # Use the new get_players method
        update_message = {"action": "update_clients", "clients": clients}
        message = Protocol.encode_message(update_message)
        self.send_buffer += message
        self.set_selector_events_mask("w")

    def close(self):
        """
        Close the connection to the socket and deregister it from the selector
        
        Args:
            Message object
        """
        log.info(f"closing connection to {self.addr}")
        try:
            self.selector.unregister(self.sock)
        except Exception as e:
            log.error(f"error: selector.unregister() exception for {self.addr}: {repr(e)}")
        finally:
            self.sock.close()
            self.sock = None
