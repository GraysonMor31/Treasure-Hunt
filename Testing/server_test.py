import unittest
from unittest.mock import patch, MagicMock
import selectors
import sys
import os 

sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'Networking'))
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'Game'))
from server import Server
from game import GameState

class TestServer(unittest.TestCase):
    @patch('server.socket.socket')
    @patch('server.selectors.DefaultSelector')
    def setUp(self, MockSelector, MockSocket):
        self.mock_selector = MockSelector.return_value
        self.mock_socket = MockSocket.return_value
        self.server = Server('localhost', 12345)

    def test_create_server_socket(self):
        self.mock_socket.bind.assert_called_with(('localhost', 12345))
        self.mock_socket.listen.assert_called_once()
        self.mock_selector.register.assert_called_with(self.mock_socket, selectors.EVENT_READ, self.server.accept_connection)

    def test_accept_connection(self):
        mock_conn = MagicMock()
        self.mock_socket.accept.return_value = (mock_conn, ('127.0.0.1', 54321))
        self.server.accept_connection(self.mock_socket, None)
        self.mock_selector.register.assert_called_with(mock_conn, selectors.EVENT_READ, self.server.handle_client)

    def test_handle_client(self):
        mock_conn = MagicMock()
        mock_conn.recv.return_value = b'{"action": "move", "target": "N"}'
        self.server.player_connections[mock_conn] = "Player 1"
        with patch('server.Protocol.decode_header', return_value=({}, 0)), \
             patch('server.Protocol.decode_message', return_value={"action": "move", "target": "N"}):
            self.server.handle_client(mock_conn, None)
        self.assertIn(mock_conn, self.server.player_connections)

    def test_disconnect_client(self):
        mock_conn = MagicMock()
        self.server.player_connections[mock_conn] = "Player 1"
        self.server.disconnect_client(mock_conn)
        self.assertNotIn(mock_conn, self.server.player_connections)
        self.mock_selector.unregister.assert_called_with(mock_conn)
        mock_conn.close.assert_called_once()

if __name__ == '__main__':
    unittest.main()