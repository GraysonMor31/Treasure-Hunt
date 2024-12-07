import unittest
from unittest.mock import patch, MagicMock
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'Networking'))
from client import Client

class TestClient(unittest.TestCase):
    @patch('client.socket.socket')
    def setUp(self, MockSocket):
        self.mock_socket = MockSocket.return_value
        self.client = Client('localhost', 12345)

    def test_connect_to_server(self):
        self.client.connect_to_server()
        self.mock_socket.connect.assert_called_with(('localhost', 12345))

    @patch('client.Protocol.encode_message', return_value=b'encoded_message')
    def test_send_join_request(self, mock_encode_message):
        self.client.send_join_request()
        self.mock_socket.sendall.assert_called_with(b'encoded_message')

    @patch('client.Protocol.encode_message', return_value=b'encoded_message')
    def test_send_action(self, mock_encode_message):
        self.client.send_action("move", "N")
        self.mock_socket.sendall.assert_called_with(b'encoded_message')

    def test_handle_server_message(self):
        content = {"action": "update", "game_state": {"players": {}, "treasure": (0, 0), "game_over": False}}
        self.client.handle_server_message(content)
        self.assertIsNotNone(self.client.game_state)

    def test_display_game_state(self):
        self.client.game_state = {"players": {"Player 1": {"position": (0, 0), "health": 100}}, "treasure": (1, 1), "game_over": False}
        self.client.display_game_state()
        

    @patch('builtins.input', side_effect=['yes'])
    def test_prompt_for_replay_yes(self, mock_input):
        with patch.object(self.client, 'send_action') as mock_send_action:
            self.client.prompt_for_replay()
            mock_send_action.assert_called_with("replay")

if __name__ == '__main__':
    unittest.main()