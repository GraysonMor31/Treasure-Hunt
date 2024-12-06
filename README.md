# Treasure Hunt Board Game

<p align="center">
  <img src="https://github.com/GraysonMor31/Treasure-Hunt/blob/main/Images/Pirates.jpg" alt="Pirates finding treasure on a gameboard">
</p>


## Table of Contents
 
| [Intro](#Intro) | [How To](#How-To) | [Rules](#Rules) | [Technologies Used](#Technologies-Used) | [Progress](#Progress) | [Additional Resources](#Additional-Resources) | [Future Roadmap](#Future-Roadmap)| [Retrospective](#Retrospective) |[Documentation](#Documentation) |
|-----------------|-------------------|-----------------|-----------------------------------------|-----------------------------------------------|-----------------------|-----------------------|------------------|------------------|

## Intro
This is a simple strategy based game that includes elements of Chess and a Choose your Own Adventure RPG. The objective is simple be the first to find the treasure hidden on the map, but be warned there is more to it than just moving in straight lines. Think out your moves, predict other players moves, and use anything available to you to achieve victory (kill/hurt each-other). The game utilizes socket programming in Python to allow for multiplayer capabilities this includes playing with others, a broadcast based game chat, and more. The game is played through a locally ran terminal instance on each players machine. (Don't worry the code and server will handle all of that). You play by either selecting move or attack. To move, type "move <direction>" in to the CLI/terminal, directions in include N/S/E/W/NE/NW/SE/SW and work just like a compass on a map, N (North) is up, S (South) is down, and so forth (really playing into this whole pirate thing.

**NOTE: ** The game was far more involved than this, due to time constraints we took the idea and reduced what were planning to do, we had originally wanted to use a web based interface. JavaSccript proved to be a massive pain to work with and get to play nicely with Flask. We scrapped that idea and are going in a new direction with this using a terminal or CLI style GUI. This simplified our game as a whole and is better for us. Thanks for understanding.

## How To
### Prerequisites
* Compliant OS
  * Windows 10/11
  * MacOS Sonoma or Newer
  * Linux
* Python 3.11
* Git 2.46.1+
* Web Browser (Chrome, Mozilla, Safari)
### Download
1. Clone the repository
```bash
git clone https://github.com/GraysonMor31/Treasure-Hunt.git
```
2. Change Directories to "Treasure-Hunt"
```bash
cd Teasure-Hunt
```
3. Install Dependancies using PIP
```bash
pip install -r requirements.txt
```
4. Change Directories to Networking
```bash
cd Networking
```
### Run
1. Start the server
```bash
python3 server.py -p <port>
```
* The port can be any value > 1023 and < 65535
* The server IP is hard-coded to 0.0.0.0 (Listen on all)
2. Start each client
```bash
python3 client.py -i <host-ip-address> -p <port> 
```
* The IP Host Address is the IP of the server and the port is the same port specified in the server start command

### Play
* Enter a command when prompted move to move your player or attack to attack another player, or quit to quit the game
* Then based on the pervious input enter a direction or a number of a player to attack (this is like a compass where **N** is **UP**, **S** is **DOWN**, **E** is right, and so on and so forth, you can choose any major cardinal direction N, S, E, W, NW, SW, NE, SE (the direction **MUST** be CAPITALIZED like prompted)
* Keep moving around the grid until the treasure is found
* Once a player wins the game you will be prompted if you want to play again (yes/no) select what you wanna do and have at it
* *NOTE:* If a player joins after the first player the first players game board wont update until they have made their move this is due to how the server is storing the game state. After the first move both players will be synced, this will also be true for the four players
  
## Rules
1. You can only move 1 square per turn
2. You can only move in straight lines (up, down, left, right, diaganols)
3. You can not move to a square another player is already on
4. Players may choose to attack other players if their squares is immediately adjacent to each other (left, right, top, bottom), an attack counts as your turn
5. If attacked 2 times the player dies (Is out of that game)
6. First to find the "Treasure" wins

## Technologies Used
* Python
* Sockets
* JSON
* IP Addresses
* CLI
* Git

## Progress
| Sprint | Status | Notes |
|--------|--------|-------|
| 0 | :white_check_mark: | Sprint Successfully Completed - Tasks Missed: 1 - Backlog: Updated |
| 1 | :white_check_mark: | Sprint Successfully Completed - Tasks Missed: 0 - Backlog: Updated |
| 2 | :white_check_mark: | Sprint Successfully Completed - Tasks Missed: 0 - Backlog: Updated |
| 3 | :white_check_mark: | Sprint Successfully Completed - Tasks Missed: 1 - Backlog: Updated |
| 4 | :white_check_mark: | Sprint Successfully Completed - Tasks Missed: 1 - Backlog: updated |
| 5 | :building_construction: | Tasks Planned: 6 - Tasks In Progress: 2 |

## Additional Resources
* Installation and Setup Video
  * **Coming Soon**
* Game Play Video
  * **Coming Soon**
 
## Future Roadmap
1. Webserver/GUI
   * Impliment a web interface using Flask routines
   * Integrate JavaScript for dynamic client-side interactions and updates
2. Enhanced Game Features:
   * Add visual elements like a graphical grid to represent the game board.
   * Include animations for player moves and attacks.
3. AI Opponent:
   * Develop a basic AI to allow single-player mode against the computer.
4. Expanded Networking:
   * Implement NAT traversal for seamless connections over the internet.
   * Add support for secure communication using TLS encryption.
5. Game Modes and Mechanics:
   * Introduce alternative game modes (e.g., team-based treasure hunts).
   * Add power-ups and environmental challenges like traps or obstacles.

## Retrospective
### Accomplishments:
We successfully implemented a working multiplayer game using Python sockets. However, due to constrained deadlines we had to simplify the game's mechanics and interface to meet project requirements. This obviously is a let down but better than not having a working project. This taught us as a group about valuable lessons in managing scope and adapting to challenges on the fly. As well as not getting to ambistious and setting realistic goals when formulating the project.
### Challenges:
Like previously mentioned we faced issues with the game interface being in a webserver. The biggest issue we faced was getting the TCP (socket) server to interact and send data to the the Web server. We are not entirely sure why this was as we did not have a ton of time to debug the issues, but we believe the issue had to do with our JavaScript functions and how it was making "on-click" calls back to the TCP server to recieve the data. We also faced a few issues when rescoping the projet since we started from scratch halfway through the semester. This decision put a lot of stress on us as a team, but was worth it since we got a decent final product.
### Teamwork:
We collaborated effectively to divide tasks and meet sprint goals. We were diligent about creating and assigning tasks to be done through our project's Kanban board. This ensured that progress was tracked and issues were promptly addressed. This also allowed us to document progress and bugs.
 
## Documentation
1. Team Docs
    * [Statement of Work](https://github.com/GraysonMor31/Treasure-Hunt/blob/main/Documentation/Statement%20of%20Work.pdf)

2. Python Docs
    * [Socket](https://docs.python.org/3/library/socket.html)
    * [Selectors](https://docs.python.org/3/library/selectors.html)
    * [JSON](https://docs.python.org/3/library/json.html)
    * [Struct](https://docs.python.org/3/library/struct.html)
    * [OS](https://docs.python.org/3/library/os.html)
    * [Sys](https://docs.python.org/3/library/sys.html)
    * [Unit Tests](https://docs.python.org/3/library/unittest.html)

3. Code Docs
    * [Server](https://github.com/GraysonMor31/Treasure-Hunt/blob/main/Documentation/Server.md)
    * [Client](https://github.com/GraysonMor31/Treasure-Hunt/blob/main/Documentation/Client.md)
    * [Game](https://github.com/GraysonMor31/Treasure-Hunt/blob/main/Documentation/Game.md)
    * [Utils](https://github.com/GraysonMor31/Treasure-Hunt/blob/main/Documentation/Utils.md)
    * [Protocol](https://github.com/GraysonMor31/Treasure-Hunt/blob/main/Documentation/Protocol.md)
    
  
