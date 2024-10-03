import unittest
import socket
import selectors
import logging
import sys
from unittest.mock import patch, MagicMock

# Import custom libraries
import libserver
import server

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
        
if __name__ == '__main__':
    unittest.main()                  