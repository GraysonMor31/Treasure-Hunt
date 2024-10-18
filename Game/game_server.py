# Import necessary libraries
import selectors
import traceback
import logging

# Set up logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
log = logging.getLogger(__name__)

class Message:
    
    def __init__(self, selector, connection, address, game_state):
        self.selector = selector
        self.connection = connection
        self.address = address
        self.game_state = game_state
        self.data = b''
        self.outb = b''
        self.jsonheader = None
        self.response = None
        
    def process_events(self, mask):
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
            data = self.connection.recv(6144)
        except BlockingIOError:
            pass
        else:
            if data:
                self.data += data
            else:
                log.info(f"Closing connection to {self.address}")
                self.selector.unregister(self.connection)
                self.connection.close()
                
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
                self.response = self.game_state.(self.request)
            elif action == "leave":
                self.response = self.game_state.(self.request) 
        
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