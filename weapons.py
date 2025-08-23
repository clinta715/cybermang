#!/usr/bin/env python3
"""
Weapons module for handling different weapon types and shooting mechanics.
"""

import curses
import time

# Animation timing constants
LASER_ANIMATION_DURATION = 0.2  # 200ms for laser beam visibility
SHOTGUN_ANIMATION_DURATION = 0.15  # 150ms for shotgun spread
ANIMATION_FRAME_TIME = 1.0 / 30  # 30 FPS for smooth animations

def animate_with_timing(stdscr, positions, symbol, duration, game_map, enemies):
    """
    Animate positions with proper absolute timing.
    positions: list of (x, y) tuples to animate
    symbol: character to display for animation
    duration: animation duration in seconds
    Returns True if animation completed successfully
    """
    if not stdscr or not positions:
        return False

    start_time = time.time()
    frame_count = max(1, int(duration / ANIMATION_FRAME_TIME))
    frame_duration = duration / frame_count

    for frame in range(frame_count):
        frame_start = time.time()

        # Render current animation frame
        for x, y in positions:
            if game_map.is_blocked(x, y):
                continue
            try:
                stdscr.addch(y, x, symbol)
            except curses.error:
                pass

        stdscr.refresh()

        # Check for enemy hits during animation
        for enemy in enemies:
            if (enemy.x, enemy.y) in positions:
                enemy.take_damage(0)  # Just check collision, damage handled by weapon

        # Precise frame timing
        frame_time = time.time() - frame_start
        if frame_time < frame_duration:
            time.sleep(frame_duration - frame_time)

    # Clear animation
    for x, y in positions:
        if not game_map.is_blocked(x, y):
            try:
                # Restore original map character or empty space
                original_char = game_map.grid[y][x] if 0 <= y < game_map.height and 0 <= x < game_map.width else '.'
                stdscr.addch(y, x, original_char)
            except curses.error:
                pass

    return True

class Weapon:
    def __init__(self, name, damage, range, ammo_capacity=100, fire_rate=1):
        self.name = name
        self.damage = damage
        self.range = range
        self.ammo_capacity = ammo_capacity
        self.ammo = ammo_capacity
        self.fire_rate = fire_rate  # Shots per second
        self.last_shot_time = 0

    def can_shoot(self):
        """Check if weapon can shoot (has ammo and respects fire rate)."""
        current_time = time.time()
        return self.ammo > 0 and (current_time - self.last_shot_time) >= (1.0 / self.fire_rate)

    def shoot(self, x, y, direction, game_map, enemies, stdscr=None):
        """Base shoot method to be overridden."""
        pass

    def reload(self, amount):
        """Add ammo to the weapon."""
        self.ammo = min(self.ammo_capacity, self.ammo + amount)

class LaserPistol(Weapon):
    def __init__(self):
        super().__init__("Laser Pistol", 20, 10, 30, 2)  # 30 ammo, 2 shots/sec

    def shoot(self, x, y, direction, game_map, enemies, stdscr=None):
        """Shoot a beam in the specified direction."""
        if not self.can_shoot():
            return False

        self.last_shot_time = time.time()
        self.ammo -= 1

        # Define direction vectors
        directions = {
            'up': (0, -1),
            'down': (0, 1),
            'left': (-1, 0),
            'right': (1, 0),
            'up_left': (-1, -1),
            'up_right': (1, -1),
            'down_left': (-1, 1),
            'down_right': (1, 1)
        }

        if direction not in directions:
            direction = 'right'  # Default direction

        dx, dy = directions[direction]

        # Collect all positions for the beam
        beam_positions = []
        hit_enemy = False
        hit_trees = []

        for i in range(1, self.range + 1):
            tx = x + dx * i
            ty = y + dy * i

            # Check bounds
            if not (0 <= tx < game_map.width and 0 <= ty < game_map.height):
                break

            # Stop only at walls, not trees
            if game_map.grid[ty][tx] == '#':
                break

            beam_positions.append((tx, ty))

            # Check for tree destruction
            if game_map.grid[ty][tx] == 'T':
                hit_trees.append((tx, ty))

            # Check for enemy hits
            for enemy in enemies:
                if enemy.x == tx and enemy.y == ty:
                    enemy.take_damage(self.damage)
                    hit_enemy = True
                    break

            if hit_enemy:
                break

        # Destroy trees that were hit
        for tree_x, tree_y in hit_trees:
            game_map.destroy_terrain(tree_x, tree_y)

        # Animate the beam with proper timing
        if stdscr and beam_positions:
            animate_with_timing(stdscr, beam_positions, '-', LASER_ANIMATION_DURATION, game_map, enemies)

        return hit_enemy or len(beam_positions) > 0 or len(hit_trees) > 0

class Shotgun(Weapon):
    def __init__(self):
        super().__init__("Shotgun", 15, 5, 8, 1)  # 8 shells, 1 shot/sec

    def shoot(self, x, y, direction, game_map, enemies, stdscr=None):
        """Shoot in an area with splash effect in the specified direction."""
        if not self.can_shoot():
            return False

        self.last_shot_time = time.time()
        self.ammo -= 1

        # Define direction vectors
        directions = {
            'up': (0, -1),
            'down': (0, 1),
            'left': (-1, 0),
            'right': (1, 0)
        }

        if direction not in directions:
            direction = 'right'  # Default direction

        dx, dy = directions[direction]

        # Create a cone pattern for shotgun
        if direction in ['up', 'down']:
            # Vertical spread
            spread = [(-1, dy), (0, dy), (1, dy)]
        else:
            # Horizontal spread
            spread = [(dx, -1), (dx, 0), (dx, 1)]

        # Collect all positions for the shotgun spread
        shotgun_positions = []
        hit_trees = []

        for spread_dx, spread_dy in spread:
            for i in range(1, self.range + 1):
                tx = x + spread_dx * i
                ty = y + spread_dy * i

                # Check bounds
                if not (0 <= tx < game_map.width and 0 <= ty < game_map.height):
                    break

                # Stop only at walls, not trees
                if game_map.grid[ty][tx] == '#':
                    break

                shotgun_positions.append((tx, ty))

                # Check for tree destruction
                if game_map.grid[ty][tx] == 'T':
                    hit_trees.append((tx, ty))

                # Check for enemy hits
                for enemy in enemies:
                    if enemy.x == tx and enemy.y == ty:
                        enemy.take_damage(self.damage)
                        break

        # Destroy trees that were hit
        for tree_x, tree_y in hit_trees:
            game_map.destroy_terrain(tree_x, tree_y)

        # Animate the shotgun spread with proper timing
        if stdscr and shotgun_positions:
            animate_with_timing(stdscr, shotgun_positions, '*', SHOTGUN_ANIMATION_DURATION, game_map, enemies)

        return len(shotgun_positions) > 0 or len(hit_trees) > 0


class PlasmaRifle(Weapon):
    """Plasma rifle with high damage and longer range."""
    def __init__(self):
        super().__init__("Plasma Rifle", 35, 15, 25, 2)  # 25 ammo, ~0.5 shots/sec (fire_rate=2 means every 2 turns)

    def shoot(self, x, y, direction, game_map, enemies, stdscr=None):
        """Shoot a plasma beam that can damage multiple enemies in a line."""
        if not self.can_shoot():
            return False

        self.last_shot_time = time.time()
        self.ammo -= 1

        # Define direction vectors
        directions = {
            'up': (0, -1),
            'down': (0, 1),
            'left': (-1, 0),
            'right': (1, 0),
            'up_left': (-1, -1),
            'up_right': (1, -1),
            'down_left': (-1, 1),
            'down_right': (1, 1)
        }

        if direction not in directions:
            direction = 'right'

        dx, dy = directions[direction]

        # Collect all positions for the plasma beam
        beam_positions = []
        hit_enemies = []
        hit_trees = []

        for i in range(1, self.range + 1):
            tx = x + dx * i
            ty = y + dy * i

            # Check bounds
            if not (0 <= tx < game_map.width and 0 <= ty < game_map.height):
                break

            # Stop only at walls, not trees
            if game_map.grid[ty][tx] == '#':
                break

            beam_positions.append((tx, ty))

            # Check for tree destruction
            if game_map.grid[ty][tx] == 'T':
                hit_trees.append((tx, ty))

            # Check for enemy hits (plasma can hit multiple enemies)
            for enemy in enemies:
                if enemy.x == tx and enemy.y == ty and enemy not in hit_enemies:
                    enemy.take_damage(self.damage)
                    hit_enemies.append(enemy)

        # Destroy trees that were hit
        for tree_x, tree_y in hit_trees:
            game_map.destroy_terrain(tree_x, tree_y)

        # Animate the plasma beam with proper timing
        if stdscr and beam_positions:
            animate_with_timing(stdscr, beam_positions, '⌘', LASER_ANIMATION_DURATION * 1.2, game_map, enemies)

        return len(hit_enemies) > 0 or len(beam_positions) > 0 or len(hit_trees) > 0


class GrenadeLauncher(Weapon):
    """Grenade launcher with area damage and splash effects."""
    def __init__(self):
        super().__init__("Grenade Launcher", 25, 8, 12, 1)  # 12 grenades, 1 shot/sec

    def shoot(self, x, y, direction, game_map, enemies, stdscr=None):
        """Launch a grenade that explodes in an area."""
        if not self.can_shoot():
            return False

        self.last_shot_time = time.time()
        self.ammo -= 1

        # Define direction vectors
        directions = {
            'up': (0, -1),
            'down': (0, 1),
            'left': (-1, 0),
            'right': (1, 0)
        }

        if direction not in directions:
            direction = 'right'

        dx, dy = directions[direction]

        # Calculate impact position (2/3 of the way to max range)
        impact_distance = self.range * 2 // 3
        impact_x = x + dx * impact_distance
        impact_y = y + dy * impact_distance

        # Ensure impact is within bounds
        impact_x = max(0, min(impact_x, game_map.width - 1))
        impact_y = max(0, min(impact_y, game_map.height - 1))

        # Create explosion area (3x3 around impact)
        explosion_positions = []
        hit_enemies = []
        hit_trees = []

        for ex in range(-1, 2):
            for ey in range(-1, 2):
                tx = impact_x + ex
                ty = impact_y + ey

                if (0 <= tx < game_map.width and 0 <= ty < game_map.height and
                    game_map.grid[ty][tx] != '#'):
                    explosion_positions.append((tx, ty))

                    # Check for tree destruction
                    if game_map.grid[ty][tx] == 'T':
                        hit_trees.append((tx, ty))

                    # Check for enemy hits
                    for enemy in enemies:
                        if enemy.x == tx and enemy.y == ty and enemy not in hit_enemies:
                            # Center gets full damage, edges get half
                            damage = self.damage if (ex == 0 and ey == 0) else self.damage // 2
                            enemy.take_damage(damage)
                            hit_enemies.append(enemy)

        # Destroy trees that were hit
        for tree_x, tree_y in hit_trees:
            game_map.destroy_terrain(tree_x, tree_y)

        # Animate the explosion with proper timing
        if stdscr and explosion_positions:
            animate_with_timing(stdscr, explosion_positions, '☄', SHOTGUN_ANIMATION_DURATION * 1.5, game_map, enemies)

        return len(hit_enemies) > 0 or len(explosion_positions) > 0 or len(hit_trees) > 0


class RailGun(Weapon):
    """Rail gun with piercing shots that go through multiple targets."""
    def __init__(self):
        super().__init__("Rail Gun", 45, 12, 8, 3)  # 8 shots, ~0.33 shots/sec (fire_rate=3 means every 3 turns)

    def shoot(self, x, y, direction, game_map, enemies, stdscr=None):
        """Shoot a piercing rail that goes through multiple enemies."""
        if not self.can_shoot():
            return False

        self.last_shot_time = time.time()
        self.ammo -= 1

        # Define direction vectors
        directions = {
            'up': (0, -1),
            'down': (0, 1),
            'left': (-1, 0),
            'right': (1, 0)
        }

        if direction not in directions:
            direction = 'right'

        dx, dy = directions[direction]

        # Collect all positions for the rail beam
        beam_positions = []
        hit_enemies = []
        hit_trees = []

        for i in range(1, self.range + 1):
            tx = x + dx * i
            ty = y + dy * i

            # Check bounds
            if not (0 <= tx < game_map.width and 0 <= ty < game_map.height):
                break

            # Stop only at walls, not trees or enemies
            if game_map.grid[ty][tx] == '#':
                break

            beam_positions.append((tx, ty))

            # Check for tree destruction
            if game_map.grid[ty][tx] == 'T':
                hit_trees.append((tx, ty))

            # Check for enemy hits (rail goes through enemies)
            for enemy in enemies:
                if enemy.x == tx and enemy.y == ty:
                    enemy.take_damage(self.damage)
                    hit_enemies.append(enemy)
                    # Rail continues through enemies, doesn't stop

        # Destroy trees that were hit
        for tree_x, tree_y in hit_trees:
            game_map.destroy_terrain(tree_x, tree_y)

        # Animate the rail beam with proper timing
        if stdscr and beam_positions:
            animate_with_timing(stdscr, beam_positions, '⚡', LASER_ANIMATION_DURATION * 0.8, game_map, enemies)

        return len(hit_enemies) > 0 or len(beam_positions) > 0 or len(hit_trees) > 0


class Flamethrower(Weapon):
    """Flamethrower with close-range area damage."""
    def __init__(self):
        super().__init__("Flamethrower", 8, 4, 50, 3)  # 50 fuel, 3 shots/sec

    def shoot(self, x, y, direction, game_map, enemies, stdscr=None):
        """Shoot flames in a cone pattern."""
        if not self.can_shoot():
            return False

        self.last_shot_time = time.time()
        self.ammo -= 1

        # Define direction vectors
        directions = {
            'up': (0, -1),
            'down': (0, 1),
            'left': (-1, 0),
            'right': (1, 0)
        }

        if direction not in directions:
            direction = 'right'

        dx, dy = directions[direction]

        # Create flame cone pattern
        flame_positions = []
        hit_enemies = []

        # Flame spreads out as it goes
        for i in range(1, self.range + 1):
            spread = i // 2 + 1  # Spread increases with distance
            for s in range(-spread, spread + 1):
                if direction in ['up', 'down']:
                    tx = x + s
                    ty = y + dy * i
                else:
                    tx = x + dx * i
                    ty = y + s

                if (0 <= tx < game_map.width and 0 <= ty < game_map.height and
                    game_map.grid[ty][tx] != '#'):
                    flame_positions.append((tx, ty))

                    # Check for enemy hits
                    for enemy in enemies:
                        if enemy.x == tx and enemy.y == ty and enemy not in hit_enemies:
                            enemy.take_damage(self.damage)
                            hit_enemies.append(enemy)

        # Animate the flames with proper timing
        if stdscr and flame_positions:
            animate_with_timing(stdscr, flame_positions, '🔥', SHOTGUN_ANIMATION_DURATION * 2, game_map, enemies)

        return len(hit_enemies) > 0 or len(flame_positions) > 0


class Crossbow(Weapon):
    """Silent crossbow with high accuracy."""
    def __init__(self):
        super().__init__("Crossbow", 40, 10, 20, 1)  # 20 bolts, 1 shot/sec

    def shoot(self, x, y, direction, game_map, enemies, stdscr=None):
        """Shoot a silent, accurate bolt."""
        if not self.can_shoot():
            return False

        self.last_shot_time = time.time()
        self.ammo -= 1

        # Define direction vectors
        directions = {
            'up': (0, -1),
            'down': (0, 1),
            'left': (-1, 0),
            'right': (1, 0)
        }

        if direction not in directions:
            direction = 'right'

        dx, dy = directions[direction]

        # Collect all positions for the bolt
        bolt_positions = []
        hit_enemy = False
        hit_trees = []

        for i in range(1, self.range + 1):
            tx = x + dx * i
            ty = y + dy * i

            # Check bounds
            if not (0 <= tx < game_map.width and 0 <= ty < game_map.height):
                break

            # Stop only at walls, not trees
            if game_map.grid[ty][tx] == '#':
                break

            bolt_positions.append((tx, ty))

            # Check for tree destruction
            if game_map.grid[ty][tx] == 'T':
                hit_trees.append((tx, ty))

            # Check for enemy hits
            for enemy in enemies:
                if enemy.x == tx and enemy.y == ty:
                    enemy.take_damage(self.damage)
                    hit_enemy = True
                    break

            if hit_enemy:
                break

        # Destroy trees that were hit
        for tree_x, tree_y in hit_trees:
            game_map.destroy_terrain(tree_x, tree_y)

        # Animate the bolt with proper timing (silent, so shorter duration)
        if stdscr and bolt_positions:
            animate_with_timing(stdscr, bolt_positions, '↟', LASER_ANIMATION_DURATION * 0.6, game_map, enemies)

        return hit_enemy or len(bolt_positions) > 0 or len(hit_trees) > 0