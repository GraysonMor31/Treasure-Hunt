# Game Module Documentation

## Overview
This module defines a simple multiplayer game where players move around a grid to find a treasure. Players can also attack each other. The game ends when a player finds the treasure or when only one player remains.

## Classes

### `GameState`
Represents the state of the game.

#### Attributes
- `grid_size` (int): The size of the game grid.
- `players` (dict): A dictionary of players with their positions and health.
- `treasure` (tuple): The position of the treasure.
- `turn` (int): The current turn number.
- `game_over` (bool): Indicates if the game is over.
- `winner` (str or None): The username of the winner, if any.

#### Methods

- `__init__(self, grid_size=10)`: Initializes the game state with a grid size.
- `add_player(self, username)`: Adds a player to the game.
  - **Parameters**: 
    - `username` (str): The username of the player.
  - **Returns**: 
    - `bool`: `True` if the player was added, `False` otherwise.
- `random_position(self)`: Generates a random position on the grid.
  - **Returns**: 
    - `tuple`: A tuple representing the random position.
- `get_corner_position(self)`: Gets a corner position for a new player.
  - **Returns**: 
    - `tuple`: A tuple representing the corner position.
- `move_player(self, username, direction)`: Moves a player in the specified direction.
  - **Parameters**: 
    - `username` (str): The username of the player.
    - `direction` (str): The direction to move ('N', 'S', 'E', 'W', 'NE', 'NW', 'SE', 'SW').
  - **Returns**: 
    - `str` or `bool`: A message if the player wins, `True` otherwise.
- `attack_player(self, username, target)`: Attacks another player.
  - **Parameters**: 
    - `username` (str): The username of the attacking player.
    - `target` (str): The username of the target player.
  - **Returns**: 
    - `str`: A message indicating the result of the attack.
- `get_game_state(self)`: Gets the current state of the game.
  - **Returns**: 
    - `dict`: A dictionary representing the game state.
- `next_turn(self)`: Advances the game to the next turn.
