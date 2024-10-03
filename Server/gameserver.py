# Import the necessary libraries
import selectors
import struct
import json
import io 
import sys
import logging

# Set up logging for debug, info, error, and critical messages
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
log = logging.getLogger(__name__)

class Message:
    def __init__(self, selector, sock, addr, game_logic):
        self.selector = selector
        self.sock = sock
        self.addr = addr
        self.game_logic = game_logic
        self._recv_buffer = b""
        self._send_buffer = b""
        self._jsonheader_len = None
        self.jsonheader = None
        self.request = None
        self.response_created = False
        
    def set_selector_events_mask(self, mode):
        """
        Set selector to listen for events: mode is 'r', 'w', or 'rw'.
        
        Args:
            mode (str): The mode to set the selector to listen for events
            self (Message): The Message object
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
        Read data from the client socket
        
        Args:
            self (Message): The Message object
        """
        try:
            # Should be ready to read
            data = self.sock.recv(12288)
        except BlockingIOError:
            # Resource temporarily unavailable (errno EWOULDBLOCK)
            pass
        else:
            if data:
                self._recv_buffer += data
            else:
                raise RuntimeError("Peer closed.")
            
    def write(self):
        """
        Write data to the client socket
        
        Args:
            self (Message): The Message object
            
        Returns:
            bytes: The data to write to the client socket
        """
        if self._send_buffer:
            log.debug(f"sending {repr(self._send_buffer)} to {self.addr}")
            try:
                # Should be ready to write
                sent = self.sock.send(self._send_buffer)
            except BlockingIOError:
                # Resource temporarily unavailable (errno EWOULDBLOCK)
                pass
            else:
                self._send_buffer = self._send_buffer[sent:]
                # Close when the buffer is drained. The response has been sent.
                if sent and not self._send_buffer:
                    self.close()
                    
    def json_encode(self, obj, encoding):
        """
        Encode a JSON object to bytes
        
        Args:
            obj (dict): The JSON object to encode
            encoding (str): The encoding to use for the JSON object
        
        Returns:
            bytes: The encoded JSON object
        """
        return json.dumps(obj, ensure_ascii=False).encode(encoding)
    
    def json_decode(self, json_bytes, encoding):
        """
        Decode a JSON object from bytes
        
        Args:
            json_bytes (bytes): The JSON object to decode
            encoding (str): The encoding to use for the JSON object
        
        Returns:
            dict: The decoded JSON object
        """
        text_wrapper = io.TextIOWrapper(io.BytesIO(json_bytes), encoding=encoding, newline="")
        obj = json.load(text_wrapper)
        text_wrapper.close()
        return obj
    
    def create_message(self, content_bytes, content_type, content_encoding):
        """
        Create a message to send to the client
        
        Args:
            content_bytes (bytes): The content to send to the client
            content_type (str): The type of content to send to the client
            content_encoding (str): The encoding of the content to send to the client
        
        Returns:
            bytes: The message to send to the client
        """
        jsonheader = {
            "byteorder": sys.byteorder,
            "content-type": content_type,
            "content-encoding": content_encoding,
            "content-length": len(content_bytes),
        }
        jsonheader_bytes = self.json_encode(jsonheader, "utf-8")
        message_hdr = struct.pack(">H", len(jsonheader_bytes))
        message = message_hdr + jsonheader_bytes + content_bytes
        return message
    
    def create_response_json_content(self):
        """
        Create a JSON response to send to the client
        
        Args:
            self (Message): The Message object
        
        Returns:
            dict: The JSON response to send to the client
        """
        action = self.request.get("action")
        if action == "update_state":
            new_state = self.request.get("state")
            self.game_logic.game_state.update(new_state)
            content = {"result": "State updated."}
        elif action == "get_state":
            content = {"result": self.game_logic.game_state.get_state()}
        else:
            content = {"result": f'Error: invalid action "{action}".'}
        content_encoding = "utf-8"
        response = {
            "content_bytes": self.json_encode(content, content_encoding),
            "content_type": "text/json",
            "content_encoding": content_encoding,
        }
        return response
    
    def process_events(self, mask):
        """
        Process events for the given mask
        
        Args:
            mask (str): The mask to process events for
            self (Message): The Message object
        """
        if mask & selectors.EVENT_READ:
            self.read()
        if mask & selectors.EVENT_WRITE:
            self.write()
    
    def process_protoheader(self):
        """
        Process the protocol header to determine the length of the JSON header
        
        Args:
            self (Message): The Message object
        
        Returns:
            int: The length of the JSON header
        """
        hdrlen = 2
        if len(self._recv_buffer) >= hdrlen:
            self._jsonheader_len = struct.unpack(">H", self._recv_buffer[:hdrlen])[0]
            self._recv_buffer = self._recv_buffer[hdrlen:]
    
    def process_jsonheader(self):
        """
        Process the JSON header to determine the content length and type
        
        Args:
            self (Message): The Message objecgt
        """
        hdrlen = self._jsonheader_len
        if len(self._recv_buffer) >= hdrlen:
            self.jsonheader = self.json_decode(self._recv_buffer[:hdrlen], "utf-8")
            self._recv_buffer = self._recv_buffer[hdrlen:]
            for reqhdr in ("byteorder", "content-length", "content-type", "content-encoding"):
                if reqhdr not in self.jsonheader:
                    raise ValueError(f'Missing required header "{reqhdr}".')
    
    def process_request(self):
        """
        Process the request from the client, determine the content length and type
        
        Args:
            self (Message): The Message
        
        Returns:
            bytes: The data from the client
        """
        content_len = self.jsonheader["content-length"]
        if not len(self._recv_buffer) >= content_len:
            return
        data = self._recv_buffer[:content_len]
        self._recv_buffer = self._recv_buffer[content_len:]
        if self.jsonheader["content-type"] == "text/json":
            encoding = self.jsonheader["content-encoding"]
            self.request = self.json_decode(data, encoding)
            log.debug(f"received request {repr(self.request)} from {self.addr}")
        else:
            # Ignore unknown content type
            self.request = None
            log.error(f"unsupported content type: {self.jsonheader['content-type']}")
            
    def create_response(self):
        """
        Create a response to send to the client, based on the request and game state
        
        Args:
            self (Message): The Message object
        
        Returns:
            bytes: The response to send to the client
        """
        if self.request:
            response = self.create_response_json_content()
            message = self.create_message(**response)
            self.response_created = True
            self._send_buffer += message
            self._set_selector_events_mask("w")
        else:
            log.error("no request")
            
    def close(self):
        """
        Handles closing the connection to the client, unregistering the socket, and closing the socket
        
        Args:
            self (Message): The Message
        """
        log.debug(f"closing connection to {self.addr}")
        try:
            self.selector.unregister(self.sock)
        except Exception as e:
            log.error(f"error: selector.unregister() exception for {self.addr}: {repr(e)}")
        finally:
            self.sock.close()
            # Delete reference to socket object for garbage collection
            self.sock = None
            
class GameState:
    def __init__(self):
        self.state = {"players": []}
       
    def update(self, new_state):
        self.state.update(new_state)
        
    def add_player(self, player):
        self.state["players"].append(player)
        
    def remove_player(self, player):
        self.state["players"].remove(player)
        
    def get_state(self):
        return self.state
    
class GameLogic:
    def __init__(self):
        self.game_state = GameState()
        
    def handle_game_action(self, action, data):
        if action == "add_player":
            self.game_state.add_player(data)
            return {"result": "Player added."}
        elif action == "remove_player":
            self.game_state.remove_player(data)
            return {"result": "Player removed."}
        elif action == "update_state":
            self.game_state.update(data)
            return {"result": "State updated."}
        elif action == "get_state":
            return {"result": self.game_state.get_state()}
        else:
            return {"result": f'Error: invalid action "{action}".'} 