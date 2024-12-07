import random
from collections import defaultdict

class GameState:
    def __init__(self, grid_size=10):
        self.grid_size = grid_size
        self.players = {}
        self.treasure = self.random_position()
        self.turn = 0
        self.game_over = False
        self.winner = None

    # add a new player to the game if there is space (up to 4 players)
    def add_player(self, username):
        if len(self.players) < 4:  # Maximum 4 players for now
            x, y = self.get_corner_position()
            self.players[username] = {"position": (x, y), "health": 2}
            return True
        return False

    # generate a random position on the grid
    def random_position(self):
        return (random.randint(0, self.grid_size - 1), random.randint(0, self.grid_size - 1))

    # assign players to one of the four corners of the grid, cycling through them
    def get_corner_position(self):
        corners = [(0, 0), (0, self.grid_size - 1), (self.grid_size - 1, 0), (self.grid_size - 1, self.grid_size - 1)]
        return corners[len(self.players) % 4]
    
    # move a player in the specified direction (N/S/E/W/NE/NW/SE/SW)
    def move_player(self, username, direction):
        x, y = self.players[username]["position"]
        if direction == "N":
            y -= 1
        elif direction == "S":
            y += 1
        elif direction == "E":
            x += 1
        elif direction == "W":
            x -= 1
        elif direction == "NE":
            x += 1
            y -= 1
        elif direction == "NW":
            x -= 1
            y -= 1
        elif direction == "SE":
            x += 1
            y += 1
        elif direction == "SW":
            x -= 1
            y += 1

        # Implement wrap-around
        x %= self.grid_size
        y %= self.grid_size

        self.players[username]["position"] = (x, y)

        # Check for win condition
        if (x, y) == self.treasure:
            self.game_over = True
            self.winner = username
            return f"{username} has found the treasure and wins the game!"

        return True

    # attack another player, reducing their health by 1. If health reaches 0, the player is eliminated
    def attack_player(self, username, target):
        if target in self.players:
            self.players[target]["health"] -= 1
            if self.players[target]["health"] <= 0:
                del self.players[target]
                if len(self.players) == 1:
                    self.game_over = True
                    self.winner = username
                    return f"{username} wins the game!"
            return f"{username} attacked {target}. {target} has {self.players[target]['health']} health remaining."
        return f"Player {target} does not exist."

    # return the current game state, including players, treasure, and game status
    def get_game_state(self):
        return {"players": self.players, "treasure": self.treasure, "game_over": self.game_over, "winner": self.winner}

    # Increment the turn counter for the next turn (this could be used for turn-based play)
    def next_turn(self):
        self.turn += 1