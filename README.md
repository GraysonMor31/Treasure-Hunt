# Treasure Hunt Board Game

<p align="center">
  <img src="https://github.com/GraysonMor31/Treasure-Hunt/blob/main/Images/Pirates.jpg" alt="Pirates finding treasure on a gameboard">
</p>


## Table of Contents
 
| [Intro](#Intro) | [How To](#How-To) | [Rules](#Rules) | [Technologies Used](#Technologies-Used) | [Progress](#Progress) | [Additional Resources](#Additional-Resources) | [Documentation](#Documentation) |
|-----------------|-------------------|-----------------|-----------------------------------------|-----------------------------------------------|-----------------------|-----------------------|

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
2. Install Dependancies using PIP
```bash
pip install -r requirements.txt
```
### Run
1. Start the server
```bash
python3 server.py -p <port>
```
* The port can be any value > 1023 and < 65535
* The server IP is hard-coded to 0.0.0.0
2. Start each client
```bash
python3 client.py -i <host-ip-address> -p <port> -u <username>
```
* The IP Host Address is the IP of the server and the port is the same port specified in the server start command

### Play (UNDER CONSTRUCTION)
* Enter a command when prompted M for Move and A for attack
* Then based on the pervious input enter a direction or a numer of a player to attack
* Keep moving around the grid until the treasure is found
  
## Rules
1. You can only move 1 square per turn
2. You can only move in straight lines (up, down, left, right, diaganol)
3. You can not move to a square another player is already on
4. Players may choose to attack other players if their squares is immediately adjacent to each other (left, right, top, bottom), an attack counts as your turn
5. If attacked 2 times the player dies (Is out of that game)
6. If attacked once, that player will lose a turn
7. First to find the "Treasure" wins

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
| 4 | :construction: | Spring Upcoming - Tasks Planned: 8 - Tasks In Progess: 2 |

## Additional Resources
* Installation and Setup Video
  * **Coming Soon**
 
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
    * [Server]()
    * [Client]()
    * [Game Server]()
    * [Game Client]()
    * [Game State]()
    * [Web Server]()
    * [Index]()
  
