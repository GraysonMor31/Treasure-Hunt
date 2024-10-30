class GameState: 
    def __init__(self):
        self.curr_players = []
        self.player_count = 0
        self.player_dict = {}
        self.game_over = False
        self.winner = None
        self.recent_changes = []  # To track recent player changes
    
    def add_player(self, player):
        self.curr_players.append(player)
        self.player_count += 1
        
    def remove_player(self, player):
        self.curr_players.remove(player)
        self.player_count -= 1

    def get_players(self):
        # Returns a list of player data (names and addresses)
        return [{"name": player} for player in self.curr_players]
    
    def get_recent_changes(self):
        """
        Returns a list of recent player changes.
        
        Returns:
            list: A list of players who were recently added or removed.
        """
        return self.recent_changes
    
    def get_player_name(self, address):
        """
        Retrieve the player's name based on their address.
        
        Args:
            address: The address of the player.
        
        Returns:
            str: The player's name or None if not found.
        """
        return self.player_dict.get(address, None)

    def get_player_address(self, player):
        """
        Retrieve the player's address based on their name.
        
        Args:
            player: The player's name.
        
        Returns:
            The address of the player or None if not found.
        """
        for addr, name in self.player_dict.items():
            if name == player:
                return addr
        return None
    
    def get_state(self):
        """
        Returns the current game state as a dictionary.
        
        Returns:
            dict: A dictionary containing game state information.
        """
        return {
            "players": self.get_players(),
            "player_count": self.player_count,
            "game_over": self.game_over,
            "winner": self.winner
        }
    
    # TODO: Implement the following methods at a later time  
    # def send_chat(self, message):


    # def player_turn(self, player):
