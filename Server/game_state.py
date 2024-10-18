import logging
import json

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
log = logging.getLogger(__name__)

class GameState:
   
    def __init__(self):
       self.players = []
       
    def join_game(self, player_name):
        self.players.append(player_name)
        log.info(f"Player {player_name} joined the game")
        
    def leave_game(self, player_name):
        self.players.remove(player_name)
        log.info(f"Player {player_name} left the game")
        
    def get_players(self):
        return self.players 