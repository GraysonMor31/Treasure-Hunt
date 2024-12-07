import unittest
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'Game'))
from game import GameState

class TestGameState(unittest.TestCase):
    def setUp(self):
        self.game = GameState()

    def test_add_player(self):
        self.assertTrue(self.game.add_player("Player 1"))
        self.assertIn("Player 1", self.game.players)

    def test_move_player(self):
        self.game.add_player("Player 1")
        result = self.game.move_player("Player 1", "N")
        self.assertTrue(result)
        self.assertEqual(self.game.players["Player 1"]["position"], (0, 9))

    def test_attack_player(self):
        self.game.add_player("Player 1")
        self.game.add_player("Player 2")
        result = self.game.attack_player("Player 1", "Player 2")
        self.assertIn("attacked", result)
        self.assertEqual(self.game.players["Player 2"]["health"], 1)

    def test_get_game_state(self):
        self.game.add_player("Player 1")
        state = self.game.get_game_state()
        self.assertIn("players", state)
        self.assertIn("treasure", state)
        self.assertIn("game_over", state)
        self.assertIn("winner", state)

if __name__ == '__main__':
    unittest.main()