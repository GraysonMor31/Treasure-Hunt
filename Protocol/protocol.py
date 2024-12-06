import struct
import json
import sys
import logging

# Set up logging for debug, info, error, and critical messages
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
log = logging.getLogger(__name__)

class Protocol:
    HEADER_LENGTH = 2  # Length of the header length field

    @staticmethod
    def encode_message(content, content_type="text/json", encoding="utf-8"):
        """
        Encodes a message with a JSON header and the given content.

        :param content: The content to encode (dictionary)
        :param content_type: Content type (default is "text/json")
        :param encoding: Encoding type (default is "utf-8")
        :return: Encoded message as bytes
        """
        try:
            content_bytes = json.dumps(content, ensure_ascii=False).encode(encoding)
            jsonheader = {
                "byteorder": sys.byteorder,
                "content-type": content_type,
                "content-encoding": encoding,
                "content-length": len(content_bytes),
            }
            jsonheader_bytes = json.dumps(jsonheader, ensure_ascii=False).encode(encoding)
            message_hdr = struct.pack(">H", len(jsonheader_bytes))  # Length of header
            message = message_hdr + jsonheader_bytes + content_bytes
            return message
        except Exception as e:
            log.error(f"Error encoding message: {e}")
            return None

    @staticmethod
    def decode_header(data):
        """ Decodes the JSON header from the received data """
        try:
            jsonheader_len = struct.unpack(">H", data[:Protocol.HEADER_LENGTH])[0]
            jsonheader_bytes = data[Protocol.HEADER_LENGTH:Protocol.HEADER_LENGTH + jsonheader_len]
            jsonheader = json.loads(jsonheader_bytes.decode("utf-8"))
            if "content-length" not in jsonheader:
                raise ValueError("Missing 'content-length' in header")
            return jsonheader, Protocol.HEADER_LENGTH + jsonheader_len
        except Exception as e:
            log.error(f"Error decoding header: {e}")
            return None, 0

    @staticmethod
    def decode_message(data, jsonheader):
        """ Decodes the message content based on the JSON header """
        try:
            if "content-length" not in jsonheader:
                raise ValueError("Missing 'content-length' in header")
            content_len = jsonheader["content-length"]
            content = json.loads(data[:content_len].decode(jsonheader["content-encoding"]))
            return content
        except Exception as e:
            log.error(f"Error decoding message: {e}")
            return None

    @staticmethod
    def message_complete(buffer):
        try:
        # Ensure buffer is large enough for header length
            if len(buffer) < Protocol.HEADER_LENGTH:
                #log.debug("Buffer too small for header length field")
                return False

        # Decode the header length
            jsonheader_len = struct.unpack(">H", buffer[:Protocol.HEADER_LENGTH])[0]
            total_header_length = Protocol.HEADER_LENGTH + jsonheader_len

        # Ensure the header is fully present
            if len(buffer) < total_header_length:
                #log.debug("Incomplete header in buffer")
                return False

        # Parse the JSON header
            jsonheader_bytes = buffer[Protocol.HEADER_LENGTH:total_header_length]
            jsonheader = json.loads(jsonheader_bytes.decode("utf-8"))
            #log.debug(f"Parsed header: {jsonheader}")

        # Ensure 'content-length' exists
            content_length = jsonheader.get("content-length")
            if content_length is None:
                raise ValueError("Header missing 'content-length'")

        # Ensure that the entire message (header + content) is present
            complete = len(buffer) >= total_header_length + content_length
            #log.debug(f"Message complete: {complete}")
            return complete
        except Exception as e:
            #log.error(f"Error in message_complete: {e}")
            return False