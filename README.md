# Berzerk-like Game

A simple text-based game similar to the classic Atari 2600 game Berzerk, implemented in Python.

## Features

- Procedurally generated maze-like rooms with interconnected paths
- Player character (P) that can be controlled with WASD keys in real-time
- Two types of enemies:
  - Random enemies (R) that move in random directions
  - Chaser enemies (C) that pursue the player
- Exit (X) that must be reached to advance to the next level
- Lives system (3 lives)
- Score tracking (100 points per level completed)
- High score persistence
- Colorful text-based interface with ANSI escape codes
- Sound effects using Pygame

## How to Play

1. Run the game with `python berzerk_game.py`
2. Use WASD keys to move your character (P):
   - W: Move up
   - A: Move left
   - S: Move down
   - D: Move right
3. Avoid touching enemies (R and C) or you'll lose a life
4. Reach the exit (X) to advance to the next level
5. Press 'Q' to quit the game at any time
6. Try to achieve the highest score possible!

## Requirements

- Python 3.6 or higher
- Pygame library (for sound effects)

## Installation

1. Install the required dependencies:
   ```
   pip install pygame
   ```

2. Run the game:
   ```
   python berzerk_game.py
   ```

## Game Mechanics

- Each level has 4-5 enemies
- Enemies move after each player move
- Random enemies (R) move in random directions
- Chaser enemies (C) try to follow the player
- If an enemy touches the player, the player loses a life
- If the player touches an enemy, the player loses a life
- When all lives are lost, the game ends
- High scores are saved between sessions

## File Structure

- `berzerk_game.py`: Main game implementation
- `high_score.json`: Saved high score (created automatically)
- `README.md`: This file

## Implementation Details

The game uses a grid-based system where:
- Walls are displayed in white
- Empty spaces are displayed in blue
- Player is displayed in green
- Random enemies (R) are displayed in magenta
- Chaser enemies (C) are displayed in red
- Exit is displayed in yellow

The room generation algorithm creates:
- Border walls around the entire room
- A proper maze structure with interconnected paths using a randomized depth-first search
- One exit on a random border position (at a path cell)
- Player placed at a random valid position
- Enemies placed at random valid positions

Enjoy the game!