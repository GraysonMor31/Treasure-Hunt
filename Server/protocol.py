# Necessary imports
import json
import struct
import sys

# Define the Protocol class
class Protocol:
    HEADER_LENGTH = 2

    @staticmethod
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

    @staticmethod
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

    @staticmethod
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