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
    def __init__(self, selector, sock, addr, game_state):
        self.game_state = game_state
        self.selector = selector
        self.sock = sock
        self.addr = addr
        self.recv_buffer = b""
        self.send_buffer = b""
        self.jsonheader_len = None
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
                log.debug(f"Received {len(data)} bytes from {self.addr}")
            else:
                raise RuntimeError("Peer closed.")
            
    def write(self):
        if self.send_buffer:
            log.debug(f"sending {repr(self.send_buffer)} to {self.addr}")
            try:
                sent = self.sock.send(self.send_buffer)
            except BlockingIOError:
                pass
            else:
                self.send_buffer = self.send_buffer[sent:]
                if sent and not self.send_buffer:
                    self.close()
                    
    def json_encode(self, obj, encoding):
        return json.dumps(obj, ensure_ascii=False).encode(encoding)
    
    def json_decode(self, json_bytes, encoding):
        text_wrapper = io.TextIOWrapper(io.BytesIO(json_bytes), encoding=encoding, newline="")
        obj = json.load(text_wrapper)
        text_wrapper.close()
        return obj
    
    def create_message(self, *, content_bytes, content_type, content_encoding):
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
        action = self.request.get("action")
        value = self.request.get("value")
        if action == "add_player":
            self.game_state.add_player(value)
            response = {"result": "player added"}
        elif action == "get_state":
            response = {"result": self.game_state.get_state()}
        return response
    
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
        hdrlen = 2
        if len(self.recv_buffer) >= hdrlen:
            self.jsonheader_len = struct.unpack(">H", self.recv_buffer[:hdrlen])[0]
            self.recv_buffer = self.recv_buffer[hdrlen:]
            log.debug(f"Processed protoheader, jsonheader_len: {self.jsonheader_len}")
    
    def process_jsonheader(self):
        hdrlen = self.jsonheader_len
        if len(self.recv_buffer) >= hdrlen:
            self.jsonheader = self.json_decode(self.recv_buffer[:hdrlen], "utf-8")
            self.recv_buffer = self.recv_buffer[hdrlen:]
            for reqhdr in ("byteorder", "content-length", "content-type", "content-encoding"):
                if reqhdr not in self.jsonheader:
                    raise ValueError(f'Missing required header "{reqhdr}".')
            log.debug(f"Processed jsonheader: {self.jsonheader}")
    
    def process_request(self):
        if self.jsonheader is None:
            return
        content_len = self.jsonheader["content-length"]
        if len(self.recv_buffer) >= content_len:
            data = self.recv_buffer[:content_len]
            self.recv_buffer = self.recv_buffer[content_len:]
            if self.jsonheader["content-type"] == "text/json":
                encoding = self.jsonheader["content-encoding"]
                self.request = self.json_decode(data, encoding)
                log.info(f"received request {repr(self.request)} from {self.addr}")
            else:
                self.request = data
                log.info(f"received {self.jsonheader['content-type']} request from {self.addr}")
    
    def create_response(self):
        if self.request:
            response = self.create_response_json_content()
            message = self.create_message(
                content_bytes=self.json_encode(response, "utf-8"),
                content_type="text/json",
                content_encoding="utf-8",
            )
            self.response_created = True
            self.send_buffer += message
            log.debug(f"Response created and added to send_buffer: {response}")
            self.set_selector_events_mask("w")
        else:
            log.error("no request")
            
    def close(self):
        log.debug(f"closing connection to {self.addr}")
        try:
            self.selector.unregister(self.sock)
        except Exception as e:
            log.error(f"error: selector.unregister() exception for {self.addr}: {repr(e)}")
        finally:
            self.sock.close()
            self.sock = None
            
class GameState:
    def __init__(self):
        self.state = {"players": []}
        
    def add_player(self, player_name):
        self.state["players"].append(player_name)
        log.info(f"Added player {player_name}, new game state: {self.state}")
        
    def get_state(self):
        return self.state