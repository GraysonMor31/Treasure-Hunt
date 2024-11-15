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

    @staticmethod
    def encode_message(content, content_type="text/json", encoding="utf-8"):
        try:
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
        except Exception as e:
            log.error(f"Error encoding message: {e}")
            return None

    @staticmethod
    def decode_header(data):
        try:
            jsonheader_len = struct.unpack(">H", data[:Protocol.HEADER_LENGTH])[0]
            jsonheader = json.loads(data[Protocol.HEADER_LENGTH:Protocol.HEADER_LENGTH + jsonheader_len].decode("utf-8"))
            return jsonheader, Protocol.HEADER_LENGTH + jsonheader_len
        except Exception as e:
            log.error(f"Error decoding header: {e}")
            return None, 0

    @staticmethod
    def decode_message(data, jsonheader):
        try:
            content_len = jsonheader["content-length"]
            content = json.loads(data[:content_len].decode(jsonheader["content-encoding"]))
            return content
        except Exception as e:
            log.error(f"Error decoding message: {e}")
            return None