class GameState: 
    def __init__(self):
        self.curr_players = []
        self.player_count = 0
        self.player_dict = {}
        self.game_over = False
        self.winner = None
    
    def add_player(self, player):
        self.curr_players.append(player)
        self.player_count += 1
        
    def remove_player(self, player):
        self.curr_players.remove(player)
        self.player_count -= 1

    def get_players(self):
        # Returns a list of player data (names and addresses)
        return [{"name": player} for player in self.curr_players]
    
    # TODO: Implement the following methods at a later time  
    # def send_chat(self, message):


    # def player_turn(self, player):
