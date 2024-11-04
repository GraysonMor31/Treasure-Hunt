class GameState: 
    def __init__(self):
        self.curr_players = []
        self.player_count = 0
        self.player_dict = {}
        self.game_over = False
        self.winner = None
        self.recent_changes = []  # To track recent player changes
        
             
    def add_player(self, player, address):
        self.curr_players.append(player)
        self.player_count += 1
        self.player_dict[address] = player  # Store the address and name
        self.recent_changes.append({"name": player, "status": "joined", "current_turn": self.get_curr_turn()})
        
        
        
    def remove_player(self, player):
        if player in self.curr_players:
            self.curr_players.remove(player)
            self.player_count -= 1
            address = self.get_player_address(player)
            if address:
                del self.player_dict[address]  # Remove from player_dict as well
            self.recent_changes.append({"name": player, "status": "left"})
    
    def get_players(self):
        return [{"name": player} for player in self.curr_players]
    
    def get_recent_changes(self):
        changes = self.recent_changes.copy()
        self.recent_changes.clear()  # Clear changes after fetching
        return changes

    def get_player_name(self, address):
        return self.player_dict.get(address, None)

    def get_player_address(self, player):
        for addr, name in self.player_dict.items():
            if name == player:
                return addr
        return None

    def get_state(self):
        return {
            "players": self.get_players(),
            "player_count": self.player_count,
            "game_over": self.game_over,
            "winner": self.winner,
            "current_turn": self.get_curr_turn()
        }
        
    def get_curr_turn(self):
        if  self.curr_players:
            return  self.curr_players[self.player_count % len(self.curr_players)]
        
    
    def get_next_turn(self):
        if not self.game_over and self.curr_players:
            self.player_count =  (self.player_count + 1) % (len(self.curr_players))
            return self.get_curr_turn()
    
  
        
    def get_winner(self, player):
        self.winner = player 
        self.game_over = True; 
    
   
    
