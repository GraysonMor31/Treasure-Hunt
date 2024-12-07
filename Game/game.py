import random
from collections import defaultdict

class GameState:
    # Initialize the game state variables
    def __init__(self, grid_size=10):
        self.grid_size = grid_size
        self.players = {}
        self.treasure = self.random_position()
        self.turn = 0
        self.game_over = False
        self.winner = None

    # Add a player to a list (denotes they are playing the game)
    def add_player(self, username):
        if len(self.players) < 4:  # Maximum 4 players for now
            x, y = self.get_corner_position()
            self.players[username] = {"position": (x, y), "health": 2}
            return True
        return False

    # Generate a random position on the grid
    def random_position(self):
        return (random.randint(0, self.grid_size - 1), random.randint(0, self.grid_size - 1))

    # Determine where the players start on the grid
    def get_corner_position(self):
        corners = [(0, 0), (0, self.grid_size - 1), (self.grid_size - 1, 0), (self.grid_size - 1, self.grid_size - 1)]
        return corners[len(self.players) % 4]

    # Move the player in a direction
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

        # The grid should wrap around
        x %= self.grid_size
        y %= self.grid_size

        self.players[username]["position"] = (x, y)

        # Check for win condition
        if (x, y) == self.treasure:
            self.game_over = True
            self.winner = username
            return f"{username} has found the treasure and wins the game!"

        return True

    # Attack another player, this is a simple health decrement nothing crazy
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

    # Reset the game state to original values
    def get_game_state(self):
        return {"players": self.players, "treasure": self.treasure, "game_over": self.game_over, "winner": self.winner}

    # Reset the game state to original values
    def next_turn(self):
        self.turn += 1