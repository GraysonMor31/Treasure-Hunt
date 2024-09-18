# Treasure Hunt Board Game
## Table of Contents
 
| [Intro](#Intro) | [How To](#How-To) | [Rules](#Rules) | [Technologies Used](#Technologies-Used) | [Progress](#Progress) | [Additional Resources](#Additional-Resources) |
|-----------------|-------------------|-----------------|-----------------------------------------|-----------------------------------------------|-----------------------|

## Intro
This is a simple strategy based game that includes elements of Chess and a Choose your Own Adventure RPG. The objective is simple be the first to find the treasure hidden on the map, but be warned there is more to it than just moving in straight lines. Think out your moves, predict other players moves, and use anything available to you to achieve victory. The game utilizes socket programming in Python to allow for multiplayer capabilities this includes playing with others, individual and game chats, and more. The game is played through a locally hosted web-page (Don't worry the code will handle all of that) with your mouse. 
## How To
### Prerequisites
* Compliant OS
  * Windows 10/11
  * MacOS Sonoma or Newer
  * Linux (Must have a Graphical Environment - XFCE, KDE, LXDE, GNOME, MATE)
* Python 3.10+
* Git 2.46.1+
### Download
1. Clone the repository
```bash
git clone https://github.com/GraysonMor31/Treasure-Hunt.git
```
### Run
1. Start the server
```bash
python3 server.py
```
2. Start each client
```bash
python3 client.py
```
3. A webpage with the address ```localhost:3000``` should open using your systems default browsers
### Play
* Use mouse to click on desired square to move to
* You are denoted by a colored dot, your dot will appear in the upper right hand corner of the web-page
* The "treasure" randomly spawns each game (don't do the same path twice...it won't work)

## Rules
1. You can only move 1 square per turn
2. You can only move in straight lines (up, down, left, right, diaganol)
3. You can not move to a square another player is already on
4. Players may choose to attack other players if their squares is immediately adjacent to each other (left, right, top, bottom)
5. If attacked 2 times the player dies (Is out of that game)
6. If attacked once, that player will lose a turn
7. First to find the "Treasure" wins

## Technologies Used
* Python
* Sockets
* Flask
* Local Web Severs
* Git

## Progress
| Sprint | Status | Notes |
|--------|--------|-------|
| 0 | :white_check_mark: | Sprint Successfully Completed - Tasks Missed: 0 |
| 1 | :construction: | Sprint in Progress - Tasks to Go: X |
| 2 | :calendar: | Spring Upcoming - Tasks Planned: X |
| 3 | :calendar: | Spring Upcoming - Tasks Planned: X |
| 4 | :calendar: | Spring Upcoming - Tasks Planned: X |

## Additional Resources
* Python Docs
  * [Socket](https://docs.python.org/3/library/socket.html)
  * [Flask](https://flask.palletsprojects.com/en/3.0.x/)
  * [OS](https://docs.python.org/3/library/os.html)
* Other Docs
  * [Statement of Work]([https://https://github.com/GraysonMor31/Treasure-Hunt/Documentation/Statement-of-Work.pdf](https://github.com/GraysonMor31/Treasure-Hunt/blob/main/Documentation/Statement%20of%20Work.pdf))
* Install Video
  * **Coming Soon**
 

