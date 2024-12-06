# Protocol Module Documentation

## Overview
This module provides functionality to encode and decode messages with a JSON header. It includes methods to encode messages, decode headers, decode messages, and check if a message is complete.

## Classes

### `Protocol`
Handles the encoding and decoding of messages.

#### Attributes
- `HEADER_LENGTH` (int): The length of the header length field (2 bytes).

#### Methods

- `encode_message(content, content_type="text/json", encoding="utf-8")`: Encodes a message with a JSON header and the given content.
  - **Parameters**: 
    - `content` (dict): The content to encode.
    - `content_type` (str): Content type (default is "text/json").
    - `encoding` (str): Encoding type (default is "utf-8").
  - **Returns**: 
    - `bytes`: Encoded message as bytes, or `None` if an error occurs.
- `decode_header(data)`: Decodes the JSON header from the received data.
  - **Parameters**: 
    - `data` (bytes): The received data.
  - **Returns**: 
    - `tuple`: A tuple containing the JSON header (dict) and the total header length (int), or `(None, 0)` if an error occurs.
- `decode_message(data, jsonheader)`: Decodes the message content based on the JSON header.
  - **Parameters**: 
    - `data` (bytes): The received data.
    - `jsonheader` (dict): The JSON header.
  - **Returns**: 
    - `dict`: The decoded content, or `None` if an error occurs.
- `message_complete(buffer)`: Checks if the entire message (header + content) is present in the buffer.
  - **Parameters**: 
    - `buffer` (bytes): The buffer containing the message.
  - **Returns**: 
    - `bool`: `True` if the message is complete, `False` otherwise.