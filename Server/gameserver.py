# Import python libraries
import selectors
import struct
import json
import io
import sys
import logging

# Set up logging for debug, info, error, and critical messages
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
log = logging.getLogger(__name__)

# Define the Protocol class
class Protocol:
    HEADER_LENGTH = 2

    def encode_message(content, content_type="text/json", encoding="utf-8"):
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
        jsonheader_len = struct.unpack(">H", data[:Protocol.HEADER_LENGTH])[0]
        jsonheader = json.loads(data[Protocol.HEADER_LENGTH:Protocol.HEADER_LENGTH + jsonheader_len].decode("utf-8"))
        return jsonheader, Protocol.HEADER_LENGTH + jsonheader_len

    def decode_message(data, jsonheader):
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
            data = self.sock.recv(4096)
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
        if self.request:
            action = self.request.get("action")
            value = self.request.get("value")
            if action == "add_player":
                self.game_state.add_player(value)
                response = {"result": "player added"}
            elif action == "get_state":
                response = {"result": self.game_state.get_state()}
            message = Protocol.encode_message(response)
            self.response_created = True
            self.send_buffer += message
            self.set_selector_events_mask("w")
        else:
            log.error("no request")

    def close(self):
        log.info(f"closing connection to {self.addr}")
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