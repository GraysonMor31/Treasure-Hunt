import unittest
import socket
import struct
import selectors
import logging
import sys
from unittest.mock import patch, MagicMock

# Import custom libraries
import server
import gameserver

class TestServer(unittest.TestCase):
    @patch('builtins.input', return_value='0.0.0.0')
    def test_get_host_valid(self, mock_input):
        self.assertEqual(server.get_host(), '0.0.0.0')
    
    @patch('builtins.input', return_value='8080')
    def test_get_port_valid(self, mock_input):
        self.assertEqual(server.get_port(), 8080)
    
    @patch('builtins.input', side_effect=['', 'localhost'])
    def test_get_host_invalid(self, mock_input):
        with self.assertLogs(server.log, level="ERROR") as log:
            self.assertEqual(server.get_host(), 'localhost')
    
    @patch('builtins.input', side_effect=['', '12345'])
    def test_get_port_invalid(self, mock_input):
        with self.assertLogs(server.log, level="ERROR") as log:
            self.assertEqual(server.get_port(), 12345)
            
class TestMessage(unittest.TestCase):

    def setUp(self):
        self.selector = selectors.DefaultSelector()
        self.sock = MagicMock()
        self.addr = ('localhost', 8080)
        self.game_state = gameserver.GameState()
        self.game_logic = gameserver.GameLogic()
        self.message = gameserver.Message(self.selector, self.sock, self.addr, self.game_logic)

    def test_create_message(self):
        self.content = {"result": "test"}
        content_bytes = self.message.json_encode(self.content, "utf-8")
        message = self.message.create_message(content_bytes, "text/json", "utf-8")
        
        jsonheader = {
            "byteorder": sys.byteorder,
            "content-type": "text/json",
            "content-encoding": "utf-8",
            "content-length": len(content_bytes),
        }
        jsonheader_bytes = self.message.json_encode(jsonheader, "utf-8")
        message_hdr = struct.pack(">H", len(jsonheader_bytes))
        expected_message = message_hdr + jsonheader_bytes + content_bytes
        
        self.assertEqual(message, expected_message)

    def test_process_protoheader(self):
        self.message._recv_buffer = struct.pack(">H", 10) + b"1234567890"
        self.message.process_protoheader()
        self.assertEqual(self.message._jsonheader_len, 10)

    def test_process_jsonheader(self):
        jsonheader = {
            "byteorder": sys.byteorder,
            "content-type": "text/json",
            "content-encoding": "utf-8",
            "content-length": 10,
        }
        jsonheader_bytes = self.message.json_encode(jsonheader, "utf-8")
        self.message._recv_buffer = struct.pack(">H", len(jsonheader_bytes)) + jsonheader_bytes
        self.message.process_protoheader()
        self.message.process_jsonheader()
        self.assertEqual(self.message.jsonheader["content-length"], 10)

    def test_create_response_json_content(self):
        self.message.request = {"action": "get_state"}
        response = self.message.create_response_json_content()
        self.assertIn("content_bytes", response)
        self.assertIn("content_type", response)
        self.assertIn("content_encoding", response)

if __name__ == '__main__':
    unittest.main()