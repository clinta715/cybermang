#!/usr/bin/env python3
"""
Map module for generating and managing the game world.
Includes terrain types and rendering.
"""

import curses
import random
import time

class Map:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.grid = self.generate_maze()
        self.light_radius = 8  # How far the player can see
        self.animation_frame = 0
        self.last_animation_update = time.time()
        self.animation_frame_duration = 1.0 / 4  # 4 FPS for map animations (slower for performance)
        self.zoom_factor = 1  # Zoom factor: 1 = normal, 2 = zoomed (doubled)

    def generate_maze(self, use_rooms=False):
        """Generate a guaranteed-connected maze with proper paths and no dead ends.
        If use_rooms is True, generate rooms and corridors instead of a maze."""
        if use_rooms:
            grid = [['#' for _ in range(self.width)] for _ in range(self.height)]
            self.grid = grid
            self.generate_rooms()
            return grid
        grid = [['#' for _ in range(self.width)] for _ in range(self.height)]

        # Create a guaranteed path from start to a few key areas
        def create_main_path():
            # Start from center and create paths to edges
            center_x, center_y = self.width // 2, self.height // 2
            grid[center_y][center_x] = '.'

            # Create paths to all four corners and edges
            corners = [
                (5, 5),  # Top-left
                (self.width - 6, 5),  # Top-right
                (5, self.height - 6),  # Bottom-left
                (self.width - 6, self.height - 6)  # Bottom-right
            ]

            for target_x, target_y in corners:
                current_x, current_y = center_x, center_y
                while current_x != target_x or current_y != target_y:
                    if abs(target_x - current_x) > abs(target_y - current_y):
                        current_x += 1 if target_x > current_x else -1
                    else:
                        current_y += 1 if target_y > current_y else -1
                    if 0 < current_x < self.width - 1 and 0 < current_y < self.height - 1:
                        grid[current_y][current_x] = '.'

        create_main_path()

        # Fill in the rest with a simpler, more reliable algorithm - WIDER PATHS
        def carve_passages(x, y):
            directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]
            random.shuffle(directions)

            for dx, dy in directions:
                # Create wider paths by using step size of 3 instead of 2
                nx, ny = x + dx * 3, y + dy * 3
                if (0 < nx < self.width - 1 and 0 < ny < self.height - 1 and
                    grid[ny][nx] == '#'):
                    # Carve wider passages - create 2-cell wide paths
                    grid[y + dy][x + dx] = '.'
                    grid[y + dy * 2][x + dx * 2] = '.'  # Extra space for width
                    grid[ny][nx] = '.'
                    # Also clear adjacent cells to make paths wider
                    if abs(dx) > 0:  # Horizontal movement
                        grid[y + dy][x + dx - 1] = '.'
                        grid[y + dy][x + dx + 1] = '.'
                        grid[y + dy * 2][x + dx * 2 - 1] = '.'
                        grid[y + dy * 2][x + dx * 2 + 1] = '.'
                    else:  # Vertical movement
                        grid[y + dy - 1][x + dx] = '.'
                        grid[y + dy + 1][x + dx] = '.'
                        grid[y + dy * 2 - 1][x + dx * 2] = '.'
                        grid[y + dy * 2 + 1][x + dx * 2] = '.'
                    carve_passages(nx, ny)

        # Start carving from multiple points - adjusted for wider paths
        start_points = [
            (self.width // 2, self.height // 2),
            (self.width // 3, self.height // 3),
            (2 * self.width // 3, self.height // 3),
            (self.width // 3, 2 * self.height // 3),
            (2 * self.width // 3, 2 * self.height // 3)
        ]

        for start_x, start_y in start_points:
            if grid[start_y][start_x] == '#':
                grid[start_y][start_x] = '.'
                carve_passages(start_x, start_y)

        # Ensure connectivity by connecting any isolated areas
        def flood_fill_connect():
            visited = set()
            def visit(x, y):
                if (x, y) in visited or not (0 <= x < self.width and 0 <= y < self.height):
                    return
                if grid[y][x] == '#':
                    return
                visited.add((x, y))
                for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
                    visit(x + dx, y + dy)

            # Find all open areas and connect them
            open_areas = []
            for y in range(1, self.height - 1):
                for x in range(1, self.width - 1):
                    if grid[y][x] != '#' and (x, y) not in visited:
                        area = set()
                        def collect_area(ax, ay):
                            if (ax, ay) in area or not (0 <= ax < self.width and 0 <= ay < self.height):
                                return
                            if grid[ay][ax] == '#':
                                return
                            area.add((ax, ay))
                            for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
                                collect_area(ax + dx, ay + dy)
                        collect_area(x, y)
                        if area:
                            open_areas.append(area)
                        visited.update(area)

            # Connect areas if there are multiple
            if len(open_areas) > 1:
                for i in range(len(open_areas) - 1):
                    # Find closest points between areas and connect them
                    area1, area2 = open_areas[i], open_areas[i + 1]
                    min_dist = float('inf')
                    connect_points = None

                    for p1 in area1:
                        for p2 in area2:
                            dist = abs(p1[0] - p2[0]) + abs(p1[1] - p2[1])
                            if dist < min_dist:
                                min_dist = dist
                                connect_points = (p1, p2)

                    if connect_points:
                        p1, p2 = connect_points
                        # Create a simple path between points
                        current = p1
                        while current != p2:
                            if current[0] < p2[0]:
                                current = (current[0] + 1, current[1])
                            elif current[0] > p2[0]:
                                current = (current[0] - 1, current[1])
                            elif current[1] < p2[1]:
                                current = (current[0], current[1] + 1)
                            else:
                                current = (current[0], current[1] - 1)
                            if 0 < current[0] < self.width - 1 and 0 < current[1] < self.height - 1:
                                grid[current[1]][current[0]] = '.'

        flood_fill_connect()

        # Add terrain variations according to dungeon_architecture.md specifications
        for y in range(self.height):
            for x in range(self.width):
                if grid[y][x] == '.':
                    rand_val = random.random()
                    if rand_val < 0.08:  # Water (W): 8% of open areas
                        grid[y][x] = 'W'
                    elif rand_val < 0.23:  # Trees/Foliage (T): 15% of open areas (cumulative 23%)
                        grid[y][x] = 'T'
                    elif rand_val < 0.48:  # Rough terrain (R): 25% of open areas (cumulative 48%)
                        grid[y][x] = 'R'
                    elif rand_val < 0.83:  # Health pickups (H): 35% of open areas (cumulative 83%)
                        grid[y][x] = 'H'
                    elif rand_val < 0.95:  # Ammo pickups (A): 42% of open areas (cumulative 95%)
                        grid[y][x] = 'A'
                    elif rand_val < 0.98:  # Power-ups (P): 45% of open areas (cumulative 98%)
                        grid[y][x] = 'P'
                    elif rand_val < 0.99:  # Lava (L): 48% of open areas (cumulative 99%)
                        grid[y][x] = 'L'
                    elif rand_val < 1.0:  # Spikes (S): 54% of open areas (cumulative 100%)
                        grid[y][x] = 'S'

        return grid

    def is_blocked(self, x, y):
        """Check if a position is blocked."""
        if not (0 <= x < self.width and 0 <= y < self.height):
            return True
        cell = self.grid[y][x]
        return cell == '#'  # Only walls block movement, trees are now passable

    def get_terrain_effect(self, x, y):
        """Get movement effect based on terrain."""
        if not (0 <= x < self.width and 0 <= y < self.height):
            return 1.0
        terrain = self.grid[y][x]
        if terrain == 'R':  # Rough
            return 0.5  # 50% slower
        elif terrain == 'W':  # Water
            return 0.3  # 70% slower, hard to move through
        elif terrain == 'T':  # Trees/vegetation
            return 0.7  # 30% slower
        elif terrain == 'L':  # Lava
            return 0.4  # 60% slower, very dangerous
        elif terrain == 'S':  # Spikes
            return 0.9  # Only slightly slower but very dangerous
        return 1.0

    def get_terrain_damage(self, x, y):
        """Get damage dealt by terrain."""
        if not (0 <= x < self.width and 0 <= y < self.height):
            return 0
        terrain = self.grid[y][x]
        if terrain == 'L':  # Lava
            return 15  # High damage
        elif terrain == 'S':  # Spikes
            return 8   # Moderate damage
        return 0

    def generate_rooms(self):
        """Generate multiple rooms in the dungeon using NetHack-style room placement."""
        rooms = []
        attempts = 0
        max_attempts = 100  # Prevent infinite loop
        
        # Ensure we have at least 5 rooms
        while len(rooms) < 5 and attempts < max_attempts:
            width = random.randint(4, 8)
            height = random.randint(4, 6)
            x = random.randint(1, self.width - width - 1)
            y = random.randint(1, self.height - height - 1)
            new_room = [(x, y), (x + width, y + height)]

            # Check if room overlaps with existing rooms
            if any(self.room_overlap(new_room, existing) for existing in rooms):
                attempts += 1
                continue

            rooms.append(new_room)
            self.create_room(new_room)
            attempts += 1

        # Connect rooms with corridors using center-point connection algorithm
        # Horizontal-first, then vertical corridor creation
        for i in range(len(rooms) - 1):
            self.connect_rooms(rooms[i], rooms[i + 1])

        # Add terrain variations according to dungeon_architecture.md specifications
        for y in range(self.height):
            for x in range(self.width):
                if self.grid[y][x] == '.':
                    rand_val = random.random()
                    if rand_val < 0.08:  # Water (W): 8% of open areas
                        self.grid[y][x] = 'W'
                    elif rand_val < 0.23:  # Trees/Foliage (T): 15% of open areas (cumulative 23%)
                        self.grid[y][x] = 'T'
                    elif rand_val < 0.48:  # Rough terrain (R): 25% of open areas (cumulative 48%)
                        self.grid[y][x] = 'R'
                    elif rand_val < 0.83:  # Health pickups (H): 35% of open areas (cumulative 83%)
                        self.grid[y][x] = 'H'
                    elif rand_val < 0.95:  # Ammo pickups (A): 42% of open areas (cumulative 95%)
                        self.grid[y][x] = 'A'
                    elif rand_val < 0.98:  # Power-ups (P): 45% of open areas (cumulative 98%)
                        self.grid[y][x] = 'P'
                    elif rand_val < 0.99:  # Lava (L): 48% of open areas (cumulative 99%)
                        self.grid[y][x] = 'L'
                    elif rand_val < 1.0:  # Spikes (S): 54% of open areas (cumulative 100%)
                        self.grid[y][x] = 'S'

    def room_overlap(self, room1, room2):
        """Check if two rooms overlap."""
        (x1, y1), (x2, y2) = room1
        (x3, y3), (x4, y4) = room2

        return not (x2 <= x3 or x4 <= x1 or y2 <= y3 or y4 <= y1)

    def create_room(self, room):
        """Create a room in the dungeon."""
        (x1, y1), (x2, y2) = room
        for y in range(y1, y2):
            for x in range(x1, x2):
                if 0 < x < self.width - 1 and 0 < y < self.height - 1:
                    self.grid[y][x] = '.'

        # Add room walls
        for x in range(x1, x2):
            if 0 < y1 < self.height - 1:
                self.grid[y1][x] = '#'
                self.grid[y2 - 1][x] = '#'
        for y in range(y1, y2):
            if 0 < x1 < self.width - 1:
                self.grid[y][x1] = '#'
                self.grid[y][x2 - 1] = '#'

    def connect_rooms(self, room1, room2):
        """Connect two rooms with a corridor using horizontal-first, then vertical strategy."""
        (x1, y1), (x2, y2) = room1
        center_x1, center_y1 = (x1 + x2) // 2, (y1 + y2) // 2
        (x3, y3), (x4, y4) = room2
        center_x2, center_y2 = (x3 + x4) // 2, (y3 + y4) // 2

        # Create horizontal corridor first
        for x in range(min(center_x1, center_x2), max(center_x1, center_x2) + 1):
            if 0 < x < self.width - 1 and 0 < center_y1 < self.height - 1:
                self.grid[center_y1][x] = '.'

        # Create vertical corridor
        for y in range(min(center_y1, center_y2), max(center_y1, center_y2) + 1):
            if 0 < center_x2 < self.width - 1 and 0 < y < self.height - 1:
                self.grid[y][center_x2] = '.'

    def collect_item(self, x, y):
        """Collect an item at the given position and return what was collected."""
        if not (0 <= x < self.width and 0 <= y < self.height):
            return None

        item = self.grid[y][x]
        if item in ['H', 'A', 'P']:
            self.grid[y][x] = '.'  # Remove the item
            return item
        return None

    def destroy_terrain(self, x, y):
        """Destroy destructible terrain at the given position and return what was destroyed."""
        if not (0 <= x < self.width and 0 <= y < self.height):
            return None

        terrain = self.grid[y][x]
        if terrain == 'T':  # Trees can be destroyed
            self.grid[y][x] = '.'  # Convert tree to normal ground
            return 'T'
        return None

    def get_lighting_level(self, x, y, player_x, player_y):
        """Calculate lighting level based on distance from player."""
        distance = ((x - player_x) ** 2 + (y - player_y) ** 2) ** 0.5
        if distance <= self.light_radius:
            # Gradual falloff from full brightness to darkness
            return max(0.0, 1.0 - (distance / self.light_radius) ** 1.5)
        return 0.0

    def update_animation(self):
        """Update animation frame for visual effects with proper timing."""
        current_time = time.time()
        if current_time - self.last_animation_update >= self.animation_frame_duration:
            self.animation_frame = (self.animation_frame + 1) % 4
            self.last_animation_update = current_time

    def render(self, stdscr, colors=False, player_x=None, player_y=None):
        """Render the map to the screen with zoom support."""
        max_y, max_x = stdscr.getmaxyx()

        # Adjust render dimensions based on zoom
        render_height = min(self.height, (max_y - 1) // self.zoom_factor)
        render_width = min(self.width, max_x // self.zoom_factor)

        # Initialize colors if supported
        if colors and curses.has_colors():
            curses.start_color()
            curses.init_pair(1, curses.COLOR_RED, curses.COLOR_BLACK)      # Walls
            curses.init_pair(2, curses.COLOR_GREEN, curses.COLOR_BLACK)    # Rough terrain
            curses.init_pair(3, curses.COLOR_YELLOW, curses.COLOR_BLACK)   # Health
            curses.init_pair(4, curses.COLOR_BLUE, curses.COLOR_BLACK)     # Ammo
            curses.init_pair(5, curses.COLOR_MAGENTA, curses.COLOR_BLACK)  # Power-up
            curses.init_pair(6, curses.COLOR_CYAN, curses.COLOR_BLACK)     # Water
            curses.init_pair(7, curses.COLOR_GREEN, curses.COLOR_BLACK)    # Trees (darker green)
            curses.init_pair(8, curses.COLOR_RED, curses.COLOR_YELLOW)     # Lava (red on yellow)
            curses.init_pair(9, curses.COLOR_YELLOW, curses.COLOR_RED)     # Spikes (yellow on red)

        for y in range(render_height):
            for x in range(render_width):
                char = self.grid[y][x]
                # Calculate lighting if player position is provided
                lighting = 1.0
                if player_x is not None and player_y is not None:
                    lighting = self.get_lighting_level(x, y, player_x, player_y)

                # Skip rendering if completely dark (lighting = 0)
                if lighting == 0.0:
                    continue

                # Get the appropriate character based on terrain type
                display_char = self._get_display_char(char)

                # Render the character with zoom (repeat it zoom_factor times in both directions)
                for zy in range(self.zoom_factor):
                    for zx in range(self.zoom_factor):
                        render_y = y * self.zoom_factor + zy
                        render_x = x * self.zoom_factor + zx

                        # Skip if outside screen bounds
                        if render_y >= max_y - 1 or render_x >= max_x:
                            continue

                        try:
                            if colors and curses.has_colors():
                                color_pair = self._get_color_pair(char)
                                stdscr.addch(render_y, render_x, display_char, color_pair)
                            else:
                                stdscr.addch(render_y, render_x, display_char)
                        except curses.error:
                            pass  # Ignore errors if we can't write to screen

    def _get_display_char(self, char):
        """Get the display character for a given terrain type."""
        if char == 'R':
            return '~'  # Rough terrain
        elif char == 'H':
            return '+'  # Health pickup
        elif char == 'A':
            return '◊'  # Ammo pickup
        elif char == 'P':
            return '⚡'  # Power-up
        elif char == 'W':
            # Animated water
            water_symbols = ['~', '≈', '≋', '∼']
            return water_symbols[self.animation_frame % len(water_symbols)]
        elif char == 'T':
            # Foliage animation
            tree_symbols = ['♣', '♠', '♦', '♥']
            return tree_symbols[self.animation_frame % len(tree_symbols)]
        elif char == 'L':
            # Lava animation
            lava_symbols = ['^', 'v', '<', '>']
            return lava_symbols[self.animation_frame % len(lava_symbols)]
        elif char == 'S':
            # Spikes animation
            spike_symbols = ['▲', '▼', '◄', '►']
            return spike_symbols[self.animation_frame % len(spike_symbols)]
        elif char == '#':
            return '#'  # Wall
        else:
            return '.'  # Default floor

    def _get_color_pair(self, char):
        """Get the color pair for a given terrain type."""
        if char == '#':
            return curses.color_pair(1)  # Walls (red)
        elif char == 'R':
            return curses.color_pair(2)  # Rough terrain (green)
        elif char == 'H':
            return curses.color_pair(3)  # Health (yellow)
        elif char == 'A':
            return curses.color_pair(4)  # Ammo (blue)
        elif char == 'P':
            return curses.color_pair(5)  # Power-up (magenta)
        elif char == 'W':
            return curses.color_pair(6)  # Water (cyan)
        elif char == 'T':
            return curses.color_pair(7)  # Trees (green)
        elif char == 'L':
            return curses.color_pair(8)  # Lava (red on yellow)
        elif char == 'S':
            return curses.color_pair(9)  # Spikes (yellow on red)
        else:
            return 0  # Default color