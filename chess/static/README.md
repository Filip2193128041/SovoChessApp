# SovoChess - Assignment 2

a chess app for assignment 2 where you get the play chess against a bot


-----

## Features

**- register and login securely - could not make admin imc-admin due to django saying password is too similar (since django is epic you have password hashing for security for free as it has a built in pbkdf2 + salt hashing method)

**- login: krems-user1 mail: krems-user1@example.com pw: krems-user1 = to test the site or register manually**

- play chess against a bot
- move validation for chess logic (board.py, pieces.py,game.py)
- checkmate/stalemate checks
- pawn promoting to queen
- castling (king/queen side
- elo system
- opening detection
- post game page = result , opening, rating
- leaderboard
- game history (stored in database)
- *didnt end up using move.py as it was a part of my old model before I started using django so I replaced it with the database Move model*

---

## Technology Used

- python 3.13
- django 6.0.5
- sqlite3 (db)
- chessboard.js (frontend board render)
- jquery
- pytest + pytest django
- check requirements.txt

---

## Installing

1. Clone to repo
2. Create a venv 

python -m venv .venv

3. install dependencies
pip install -r requirements.txt
4. run migrations: python manage.py migrate
5. start the server: python manage.py runserver

6. Open the browser and go to the link given in the terminal (127.0.....)


## Registered User Test
login: krems-user1 mail: krems-user1@example.com pw: krems-user1

cd chess, pytest tests.py -v
---

## how to play

1. register an account or log in
2. click play chess on the home page
3. you play as white, the bot plays as black
4. drag and drop pieces to make moves
5. after checkmate or stalemate a modal appears showing the result and opening
6. you are then redirected to the post game page
7. your elo rating updates automatically after each game

---

## UML

the domain model includes 5 interrelated tables:
- **user** = stores username, password hash, and elo rating
- **playerprofile** = stores wins, losses, total games, favourite opening (one to one with user)
- **game** = stores white player, black player, winner, opening name, date played
- **move** = stores each individual move linked to a game
- **openingdatabase** = stores chess opening names and move sequences


