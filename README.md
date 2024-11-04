# Treasure Hunt Board Game

<p align="center">
  <img src="https://github.com/GraysonMor31/Treasure-Hunt/blob/main/Images/Pirates.jpg" alt="Pirates finding treasure on a gameboard">
</p>


## Table of Contents
 
| [Intro](#Intro) | [How To](#How-To) | [Rules](#Rules) | [Technologies Used](#Technologies-Used) | [Progress](#Progress) | [Additional Resources](#Additional-Resources) | [Documentation](#Documentation) |
|-----------------|-------------------|-----------------|-----------------------------------------|-----------------------------------------------|-----------------------|-----------------------|

## Intro
This is a simple strategy based game that includes elements of Chess and a Choose your Own Adventure RPG. The objective is simple be the first to find the treasure hidden on the map, but be warned there is more to it than just moving in straight lines. Think out your moves, predict other players moves, and use anything available to you to achieve victory (kill/hurt each-other). The game utilizes socket programming in Python to allow for multiplayer capabilities this includes playing with others, a broadcast based game chat, and more. The game is played through a locally hosted web-page (Don't worry the code and server will handle all of that). You play by selecting the movement buttons corresponding to the way you wish to move.
## How To
### Prerequisites
* Compliant OS
  * Windows 10/11
  * MacOS Sonoma or Newer
  * Linux
* Python 3.6+
* Git 2.46.1+
* Web Browser (Chrome, Mozilla, Safari)
### Download
1. Clone the repository
```bash
git clone https://github.com/GraysonMor31/Treasure-Hunt.git
```
### Run
1. Start the server
```bash
python3 server.py <host> <port>
```
2. Start each client
```bash
python3 client.py <host> <port> <host> <action> <value>
```
3. A webpage with the address ```localhost:3001``` should open using your systems default browsers
* NOTE: We are assuming this port is open on your system, its not commonly used so it should be, but if its not, you may need to determine what is running on that port and stop it or, change the port in the code.

4. For our current message protocol, our 2 current actions are join_game and leave_game. Here is an example for running the client code:
```bash
python3 client.py localhost 12345 join_game username
```

### Play
* Use mouse to click on desired square to move to
* You are denoted by a colored dot, your dot will appear in the upper right hand corner of the web-page
* The "treasure" randomly spawns each game (don't do the same path twice...it won't work)

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
* HTML, CSS, JavaScript
* Sockets
* HTTP Servers
* HTTP Requests
* Local Web Severs
* Git

## Progress
| Sprint | Status | Notes |
|--------|--------|-------|
| 0 | :white_check_mark: | Sprint Successfully Completed - Tasks Missed: 1 - Backlog: Updated |
| 1 | :white_check_mark: | Sprint Successfully Completed - Tasks Missed: 0 - Backlog: Updated |
| 2 | :construction: | Spring Upcoming - Tasks Planned: 4 |
| 3 | :calendar: | Spring Upcoming - Tasks Planned: X |
| 4 | :calendar: | Spring Upcoming - Tasks Planned: X |

## Additional Resources
* Installation and Setup Video
  * **Coming Soon**
 
## Documentation
1. Team Docs
    * [Statement of Work](https://github.com/GraysonMor31/Treasure-Hunt/blob/main/Documentation/Statement%20of%20Work.pdf)

2. Python Docs
    *  [Socket](https://docs.python.org/3/library/socket.html)
    * [Selectors](https://docs.python.org/3/library/selectors.html)
    * [JSON](https://docs.python.org/3/library/json.html)
    * [Struct](https://docs.python.org/3/library/struct.html)
    * [OS](https://docs.python.org/3/library/os.html)
    * [Sys](https://docs.python.org/3/library/sys.html)
    * [HTTP Servers](https://docs.python.org/3/library/http.server.html)
    * [Unit Tests](https://docs.python.org/3/library/unittest.html)
    * [Flask](https://flask.palletsprojects.com/en/stable/installation/#python-version)

3. Code Docs
    * [Server]()
    * [Client]()
    * [Game Server]()
    * [Game Client]()
    * [Game State]()
    * [Web Server]()
    * [Index]()
  
