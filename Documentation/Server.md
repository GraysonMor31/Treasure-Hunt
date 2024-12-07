# Server Module Documentation

## Overview
This module defines the server for a simple multiplayer game where players move around a grid to find a treasure. Players can also attack each other. The server manages player connections, game state, and communication with clients.

## Classes

### `Server`
Represents the game server.

#### Attributes
- `host` (str): The IP address to bind the server.
- `port` (int): The port to bind the server.
- `sel` (selectors.DefaultSelector): The selector for managing multiple connections.
- `game` (GameState): The current state of the game.
- `server_socket` (socket): The socket used to accept client connections.
- `player_count` (int): The number of players connected to the server.
- `player_connections` (dict): A dictionary mapping client sockets to player names.

#### Methods

- `__init__(self, host, port)`
  - Initializes the server with the host and port.
  - **Parameters**: 
    - `host` (str): The IP address to bind the server.
    - `port` (int): The port to bind the server.

- `create_server_socket(self)`
  - Creates and binds the server socket.
  - **Returns**: 
    - `socket`: The created server socket.
  - **Raises**: 
    - `socket.error`: If there is an error creating the server socket.

- `accept_connection(self, server_socket, mask)`
  - Accepts a new client connection.
  - **Parameters**: 
    - `server_socket` (socket): The server socket.
    - `mask` (int): The event mask.

- `reset_game(self)`
  - Resets the game state and re-adds all players.

- `handle_client(self, conn, mask)`
  - Handles messages from a client.
  - **Parameters**: 
    - `conn` (socket): The client socket.
    - `mask` (int): The event mask.

- `handle_move(self, conn, content)`
  - Handles a move action from a client.
  - **Parameters**: 
    - `conn` (socket): The client socket.
    - `content` (dict): The content of the move action.

- `handle_attack(self, conn, content)`
  - Handles an attack action from a client.
  - **Parameters**: 
    - `conn` (socket): The client socket.
    - `content` (dict): The content of the attack action.

- `send_game_state(self, conn)`
  - Sends the current game state to a client.
  - **Parameters**: 
    - `conn` (socket): The client socket.

- `send_game_state_to_all(self)`
  - Sends the current game state to all connected clients.

- `send_to_all(self, message)`
  - Sends a message to all connected clients.
  - **Parameters**: 
    - `message` (dict): The message to send.

- `disconnect_client(self, conn)`
  - Disconnects a client and cleans up resources.
  - **Parameters**: 
    - `conn` (socket): The client socket.

- `run(self)`
  - Runs the server, accepting and handling client connections.
  - **Raises**: 
    - `KeyboardInterrupt`: If the server is interrupted.
    - `Exception`: If there is an unexpected error.

## Functions

### `main()`
Parses command-line arguments and starts the server.