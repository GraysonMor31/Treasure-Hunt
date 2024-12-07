# Client Module Documentation

## Overview
This module defines the client for a simple multiplayer game where players move around a grid to find a treasure. Players can also attack each other. The client connects to the game server, sends actions, and receives updates.

## Classes

### `Client`
Represents the client that connects to the game server.

#### Attributes
- `server_ip` (str): The IP address of the game server.
- `server_port` (int): The port of the game server.
- `sock` (socket): The socket used to connect to the server.
- `running` (bool): A flag to control the listener thread.
- `buffer` (bytes): A buffer to handle partial message reads.
- `game_state` (dict or None): Holds the current game state.

#### Methods

- `__init__(self, server_ip, server_port)`
  - Initializes the client with the server IP and port.
  - **Parameters**: 
    - `server_ip` (str): The IP address of the server.
    - `server_port` (int): The port of the server.

- `connect_to_server(self)`
  - Connects to the game server and sends a join request.
  - **Raises**: 
    - `Exception`: If there is an error connecting to the server.

- `send_join_request(self)`
  - Sends a join request to the server.
  - **Raises**: 
    - `Exception`: If there is an error sending the join request.

- `send_action(self, action, target=None)`
  - Sends an action to the server.
  - **Parameters**: 
    - `action` (str): The action to send ('join', 'move', 'attack', 'replay', 'quit').
    - `target` (str, optional): The target of the action, if applicable.
  - **Raises**: 
    - `Exception`: If there is an error sending the action.

- `listen_for_updates(self)`
  - Listens for updates from the server in a separate thread.
  - **Raises**: 
    - `Exception`: If there is an error receiving or processing a message.

- `handle_server_message(self, content)`
  - Handles messages received from the server.
  - **Parameters**: 
    - `content` (dict): The content of the message.

- `display_game_state(self)`
  - Displays the current game state in a grid format.

- `prompt_for_action(self)`
  - Prompts the user to enter an action.

- `prompt_for_replay(self)`
  - Prompts the user to decide if they want to play again.
  - **Raises**: 
    - `KeyboardInterrupt`: If the user interrupts the input.

- `run(self)`
  - Main loop for user interaction.
  - **Raises**: 
    - `KeyboardInterrupt`: If the user interrupts the input.
    - `Exception`: If there is an unexpected error.