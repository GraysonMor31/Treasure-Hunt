

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