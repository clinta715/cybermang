import random
import os
import json
import pygame
import io
import math

# Constants
GRID_WIDTH = 40
GRID_HEIGHT = 30

# ANSI color codes
class Colors:
    RESET = '\033[0m'
    BLACK = '\033[30m'
    RED = '\033[31m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    BLUE = '\033[34m'
    MAGENTA = '\033[35m'
    CYAN = '\033[36m'
    WHITE = '\033[37m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

# Player character
class Player:
    def __init__(self, x, y):
        self.x = x
        self.y = y
    
    def move(self, dx, dy, room):
        new_x = self.x + dx
        new_y = self.y + dy
        
        # Check if move is valid (within bounds and not a wall)
        if 0 <= new_x < GRID_WIDTH and 0 <= new_y < GRID_HEIGHT:
            if not room.is_wall(new_x, new_y):
                self.x = new_x
                self.y = new_y
                return True
        return False
    
    def get_position(self):
        return (self.x, self.y)

# Base Enemy class
class Enemy:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.symbol = 'E'
    
    def move(self, room, player):
        pass  # To be implemented by subclasses
    
    def get_position(self):
        return (self.x, self.y)

# Chaser enemy that follows the player
class ChaserEnemy(Enemy):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.symbol = 'C'
    
    def move(self, room, player):
        # Simple pathfinding - move towards player
        dx = 0
        dy = 0
        
        if self.x < player.x:
            dx = 1
        elif self.x > player.x:
            dx = -1
            
        if self.y < player.y:
            dy = 1
        elif self.y > player.y:
            dy = -1
            
        # Try to move horizontally first, then vertically
        new_x = self.x + dx
        new_y = self.y
        
        if 0 <= new_x < GRID_WIDTH and 0 <= new_y < GRID_HEIGHT:
            if not room.is_wall(new_x, new_y):
                self.x = new_x
                self.y = new_y
                return
        
        # If horizontal move failed, try vertical
        new_x = self.x
        new_y = self.y + dy
        
        if 0 <= new_x < GRID_WIDTH and 0 <= new_y < GRID_HEIGHT:
            if not room.is_wall(new_x, new_y):
                self.x = new_x
                self.y = new_y

# Random enemy that moves randomly
class RandomEnemy(Enemy):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.symbol = 'R'
    
    def move(self, room, player):
        # Move in a random direction
        directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]  # Down, Right, Up, Left
        random.shuffle(directions)
        
        for dx, dy in directions:
            new_x = self.x + dx
            new_y = self.y + dy
            
            if 0 <= new_x < GRID_WIDTH and 0 <= new_y < GRID_HEIGHT:
                if not room.is_wall(new_x, new_y):
                    self.x = new_x
                    self.y = new_y
                    return

# Room class for procedural generation
class Room:
    def __init__(self):
        self.walls = set()
        self.exit_x = 0
        self.exit_y = 0
        self.generate_maze()
    
    def generate_maze(self):
        # Clear existing walls
        self.walls = set()
        
        # Add border walls
        for x in range(GRID_WIDTH):
            self.walls.add((x, 0))
            self.walls.add((x, GRID_HEIGHT - 1))
        
        for y in range(GRID_HEIGHT):
            self.walls.add((0, y))
            self.walls.add((GRID_WIDTH - 1, y))
        
        # Generate a maze using a simple algorithm
        # Create a grid with all cells as walls initially
        maze = [[1 for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
        
        # Carve out paths using a randomized depth-first search
        def carve_path(x, y):
            maze[y][x] = 0  # Mark as path
            directions = [(0, 2), (2, 0), (0, -2), (-2, 0)]
            random.shuffle(directions)
            
            for dx, dy in directions:
                nx, ny = x + dx, y + dy
                if 1 <= nx < GRID_WIDTH - 1 and 1 <= ny < GRID_HEIGHT - 1 and maze[ny][nx] == 1:
                    maze[y + dy // 2][x + dx // 2] = 0  # Remove wall between cells
                    carve_path(nx, ny)
        
        # Start carving from a random position
        start_x = random.randrange(1, GRID_WIDTH - 1, 2)
        start_y = random.randrange(1, GRID_HEIGHT - 1, 2)
        carve_path(start_x, start_y)
        
        # Convert maze to walls
        for y in range(GRID_HEIGHT):
            for x in range(GRID_WIDTH):
                if maze[y][x] == 1:
                    self.walls.add((x, y))
        
        # Create exit at a random border position (not a corner)
        side = random.randint(0, 3)
        if side == 0:  # Top
            # Find a path cell on the top border
            path_cells = [x for x in range(1, GRID_WIDTH - 1) if (x, 0) not in self.walls]
            if path_cells:
                self.exit_x = random.choice(path_cells)
                self.exit_y = 0
            else:
                self.exit_x = random.randint(1, GRID_WIDTH - 2)
                self.exit_y = 0
        elif side == 1:  # Right
            # Find a path cell on the right border
            path_cells = [y for y in range(1, GRID_HEIGHT - 1) if (GRID_WIDTH - 1, y) not in self.walls]
            if path_cells:
                self.exit_x = GRID_WIDTH - 1
                self.exit_y = random.choice(path_cells)
            else:
                self.exit_x = GRID_WIDTH - 1
                self.exit_y = random.randint(1, GRID_HEIGHT - 2)
        elif side == 2:  # Bottom
            # Find a path cell on the bottom border
            path_cells = [x for x in range(1, GRID_WIDTH - 1) if (x, GRID_HEIGHT - 1) not in self.walls]
            if path_cells:
                self.exit_x = random.choice(path_cells)
                self.exit_y = GRID_HEIGHT - 1
            else:
                self.exit_x = random.randint(1, GRID_WIDTH - 2)
                self.exit_y = GRID_HEIGHT - 1
        else:  # Left
            # Find a path cell on the left border
            path_cells = [y for y in range(1, GRID_HEIGHT - 1) if (0, y) not in self.walls]
            if path_cells:
                self.exit_x = 0
                self.exit_y = random.choice(path_cells)
            else:
                self.exit_x = 0
                self.exit_y = random.randint(1, GRID_HEIGHT - 2)
        
        # Ensure exit position is not a wall
        self.walls.discard((self.exit_x, self.exit_y))
    
    def is_wall(self, x, y):
        return (x, y) in self.walls
    
    def is_exit(self, x, y):
        return x == self.exit_x and y == self.exit_y

# Game state manager
class GameState:
    def __init__(self):
        self.player = None
        self.enemies = []
        self.room = None
        self.lives = 3
        self.score = 0
        self.level = 1
        self.high_score = self.load_high_score()
        self.game_over = False
        self.level_complete = False
        self.initialize_level()
    
    def initialize_level(self):
        self.room = Room()
        
        # Place player at a random position that's not a wall
        while True:
            player_x = random.randint(1, GRID_WIDTH - 2)
            player_y = random.randint(1, GRID_HEIGHT - 2)
            if not self.room.is_wall(player_x, player_y):
                self.player = Player(player_x, player_y)
                break
        
        # Place enemies
        self.enemies = []
        enemy_count = random.randint(4, 5)
        
        for _ in range(enemy_count):
            while True:
                enemy_x = random.randint(1, GRID_WIDTH - 2)
                enemy_y = random.randint(1, GRID_HEIGHT - 2)
                
                # Make sure enemy is not placed on player, wall, or another enemy
                if (not self.room.is_wall(enemy_x, enemy_y) and 
                    (enemy_x, enemy_y) != (self.player.x, self.player.y) and
                    (enemy_x, enemy_y) not in [(e.x, e.y) for e in self.enemies]):
                    
                    # Randomly choose enemy type (70% chance for random, 30% for chaser)
                    if random.random() < 0.7:
                        self.enemies.append(RandomEnemy(enemy_x, enemy_y))
                    else:
                        self.enemies.append(ChaserEnemy(enemy_x, enemy_y))
                    break
    
    def update(self):
        if self.game_over or self.level_complete:
            return
        
        # Ensure player and room are initialized
        if self.player is None or self.room is None:
            return
            
        # Move enemies
        for enemy in self.enemies:
            enemy.move(self.room, self.player)
            
            # Check for collision with player
            if enemy.x == self.player.x and enemy.y == self.player.y:
                self.lives -= 1
                if self.lives <= 0:
                    self.game_over = True
                    if self.score > self.high_score:
                        self.high_score = self.score
                        self.save_high_score()
                else:
                    # Reset level but keep score
                    self.initialize_level()
                return
        
        # Check if player reached exit
        if self.room.is_exit(self.player.x, self.player.y):
            self.score += 100 * self.level
            self.level += 1
            self.level_complete = True
    
    def move_player(self, dx, dy):
        if not self.game_over and not self.level_complete and self.player is not None and self.room is not None:
            # Move player
            if self.player.move(dx, dy, self.room):
                pass  # Move was successful
            
            # Check for collision with enemies immediately after player moves
            for enemy in self.enemies:
                if enemy.x == self.player.x and enemy.y == self.player.y:
                    self.lives -= 1
                    if self.lives <= 0:
                        self.game_over = True
                        if self.score > self.high_score:
                            self.high_score = self.score
                            self.save_high_score()
                    else:
                        # Reset level but keep score
                        self.initialize_level()
                    return
    
    def move_enemies(self):
        """Move enemies and handle collisions/checks after player moves"""
        if self.game_over or self.level_complete:
            return
        
        # Ensure player and room are initialized
        if self.player is None or self.room is None:
            return
            
        # Move enemies
        for enemy in self.enemies:
            enemy.move(self.room, self.player)
            
            # Check for collision with player
            if enemy.x == self.player.x and enemy.y == self.player.y:
                self.lives -= 1
                if self.lives <= 0:
                    self.game_over = True
                    if self.score > self.high_score:
                        self.high_score = self.score
                        self.save_high_score()
                else:
                    # Reset level but keep score
                    self.initialize_level()
                return
        
        # Check if player reached exit
        if self.room.is_exit(self.player.x, self.player.y):
            self.score += 100 * self.level
            self.level += 1
            self.level_complete = True
    def next_level(self):
        if self.level_complete:
            self.level_complete = False
            self.initialize_level()
    
    def restart_game(self):
        self.lives = 3
        self.score = 0
        self.level = 1
        self.game_over = False
        self.level_complete = False
        self.initialize_level()
    
    def load_high_score(self):
        try:
            if os.path.exists('high_score.json'):
                with open('high_score.json', 'r') as f:
                    data = json.load(f)
                    return data.get('high_score', 0)
        except:
            pass
        return 0
    
    def save_high_score(self):
        try:
            with open('high_score.json', 'w') as f:
                json.dump({'high_score': self.high_score}, f)
        except:
            pass

# Text-based renderer
class Renderer:
    def render(self, game_state):
        # Create a grid representation
        grid = [['.' for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
        
        # Draw walls
        for y in range(GRID_HEIGHT):
            for x in range(GRID_WIDTH):
                if game_state.room.is_wall(x, y):
                    grid[y][x] = '#'
        
        # Draw exit
        grid[game_state.room.exit_y][game_state.room.exit_x] = 'X'
        
        # Draw enemies
        for enemy in game_state.enemies:
            grid[enemy.y][enemy.x] = enemy.symbol
        
        # Draw player
        grid[game_state.player.y][game_state.player.x] = 'P'
        
        # Clear screen and print grid
        os.system('cls' if os.name == 'nt' else 'clear')
        
        # Print header with colors
        print(f"{Colors.BOLD}Level: {Colors.CYAN}{game_state.level}{Colors.RESET}  "
              f"{Colors.BOLD}Score: {Colors.YELLOW}{game_state.score}{Colors.RESET}  "
              f"{Colors.BOLD}Lives: {Colors.RED}{game_state.lives}{Colors.RESET}  "
              f"{Colors.BOLD}High Score: {Colors.MAGENTA}{game_state.high_score}{Colors.RESET}")
        print("=" * (GRID_WIDTH + 2))
        
        # Print grid with colors
        for y, row in enumerate(grid):
            colored_row = ""
            for x, cell in enumerate(row):
                if cell == '#':  # Wall
                    colored_row += Colors.WHITE + Colors.BOLD + cell + Colors.RESET
                elif cell == 'P':  # Player
                    colored_row += Colors.GREEN + Colors.BOLD + cell + Colors.RESET
                elif cell == 'X':  # Exit
                    colored_row += Colors.YELLOW + Colors.BOLD + cell + Colors.RESET
                elif cell == 'C':  # Chaser enemy
                    colored_row += Colors.RED + Colors.BOLD + cell + Colors.RESET
                elif cell == 'R':  # Random enemy
                    colored_row += Colors.MAGENTA + Colors.BOLD + cell + Colors.RESET
                else:  # Empty space
                    colored_row += Colors.BLUE + cell + Colors.RESET
            print("|" + colored_row + "|")
        
        print("=" * (GRID_WIDTH + 2))
        
        if game_state.game_over:
            print(f"{Colors.RED}{Colors.BOLD}GAME OVER!{Colors.RESET} Press '{Colors.CYAN}R{Colors.RESET}' to restart or '{Colors.CYAN}Q{Colors.RESET}' to quit.")
        elif game_state.level_complete:
            print(f"{Colors.GREEN}{Colors.BOLD}Level Complete!{Colors.RESET} Press '{Colors.CYAN}N{Colors.RESET}' for next level or '{Colors.CYAN}Q{Colors.RESET}' to quit.")
        else:
            print(f"Use {Colors.CYAN}{Colors.BOLD}WASD{Colors.RESET} to move, '{Colors.CYAN}Q{Colors.RESET}' to quit")

# Main game class
class BerzerkGame:
    def __init__(self):
        self.game_state = GameState()
        self.renderer = Renderer()
        self.running = True
    
    def run(self):
        print("Welcome to Berzerk-like game!")
        print("Use WASD keys to move, 'Q' to quit")
        input("Press Enter to start...")
        
        # Render initial game state
        self.renderer.render(self.game_state)
        print(f"\nUse {Colors.CYAN}{Colors.BOLD}WASD{Colors.RESET} to move, '{Colors.CYAN}Q{Colors.RESET}' to quit")
        
        import sys
        import time
        
        # Use different input methods based on platform
        if sys.platform == "win32":
            import msvcrt
            
            def get_input():
                if msvcrt.kbhit():
                    key = msvcrt.getch()
                    if key == b'\x03':  # Ctrl-C
                        return 'QUIT'
                    elif key == b'q' or key == b'Q':
                        return 'QUIT'
                    elif key == b'r' or key == b'R':
                        return 'RESTART'
                    elif key == b'n' or key == b'N':
                        return 'NEXT_LEVEL'
                    elif key == b'w' or key == b'W':
                        return 'UP'
                    elif key == b's' or key == b'S':
                        return 'DOWN'
                    elif key == b'a' or key == b'A':
                        return 'LEFT'
                    elif key == b'd' or key == b'D':
                        return 'RIGHT'
                return None
        else:
            import select
            import tty
            import termios
            
            def get_input():
                if select.select([sys.stdin], [], [], 0) == ([sys.stdin], [], []):
                    key = sys.stdin.read(1)
                    if key == '\x03':  # Ctrl-C
                        return 'QUIT'
                    elif key == 'q' or key == 'Q':
                        return 'QUIT'
                    elif key == 'r' or key == 'R':
                        return 'RESTART'
                    elif key == 'n' or key == 'N':
                        return 'NEXT_LEVEL'
                    elif key == 'w' or key == 'W':
                        return 'UP'
                    elif key == 's' or key == 'S':
                        return 'DOWN'
                    elif key == 'a' or key == 'A':
                        return 'LEFT'
                    elif key == 'd' or key == 'D':
                        return 'RIGHT'
                return None
        
        # Game loop
        while self.running:
            # Handle input
            key = get_input()
            
            if key == 'QUIT':
                self.running = False
            elif key == 'RESTART' and self.game_state.game_over:
                self.game_state.restart_game()
                # Render immediately after restart
                self.renderer.render(self.game_state)
                print(f"\n{Colors.RED}{Colors.BOLD}Game Over!{Colors.RESET} Press '{Colors.CYAN}R{Colors.RESET}' to restart or '{Colors.CYAN}Q{Colors.RESET}' to quit.")
            elif key == 'NEXT_LEVEL' and self.game_state.level_complete:
                self.game_state.next_level()
                # Render immediately after level complete
                self.renderer.render(self.game_state)
                print(f"\n{Colors.GREEN}{Colors.BOLD}Level Complete!{Colors.RESET} Press '{Colors.CYAN}N{Colors.RESET}' for next level or '{Colors.CYAN}Q{Colors.RESET}' to quit.")
            elif key in ['UP', 'DOWN', 'LEFT', 'RIGHT'] and not self.game_state.game_over and not self.game_state.level_complete:
                # Player movement
                player_moved = False
                if key == 'UP':
                    self.game_state.move_player(0, -1)
                    player_moved = True
                elif key == 'DOWN':
                    self.game_state.move_player(0, 1)
                    player_moved = True
                elif key == 'LEFT':
                    self.game_state.move_player(-1, 0)
                    player_moved = True
                elif key == 'RIGHT':
                    self.game_state.move_player(1, 0)
                    player_moved = True
                
                # If player moved, then process enemy movements and render
                if player_moved:
                    self.game_state.move_enemies()
                    self.renderer.render(self.game_state)
                    if self.game_state.game_over:
                        print(f"\n{Colors.RED}{Colors.BOLD}Game Over!{Colors.RESET} Press '{Colors.CYAN}R{Colors.RESET}' to restart or '{Colors.CYAN}Q{Colors.RESET}' to quit.")
                    elif self.game_state.level_complete:
                        print(f"\n{Colors.GREEN}{Colors.BOLD}Level Complete!{Colors.RESET} Press '{Colors.CYAN}N{Colors.RESET}' for next level or '{Colors.CYAN}Q{Colors.RESET}' to quit.")
                    else:
                        print(f"\nUse {Colors.CYAN}{Colors.BOLD}WASD{Colors.RESET} to move, '{Colors.CYAN}Q{Colors.RESET}' to quit")
            
            # Small delay to prevent high CPU usage
            time.sleep(0.01)

if __name__ == "__main__":
    game = BerzerkGame()
    game.run()