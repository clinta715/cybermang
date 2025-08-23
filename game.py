#!/usr/bin/env python3
""" 
Main game file for the sci-fi/cyberpunk ASCII-based game.
Handles the game loop, initialization, and integration of all components.
""" 

import curses
import time
import random
import math
from map import Map
from player import Player
from enemy import Enemy, FastEnemy, TankEnemy, SniperEnemy, HealerEnemy, StealthEnemy, ENEMY_TYPES
from weapons import LaserPistol, Shotgun, PlasmaRifle, GrenadeLauncher, RailGun, Flamethrower, Crossbow
from status_effects import *
from combat_actions import *

# Animation timing constants (in seconds)
TARGET_FPS = 60
FRAME_TIME = 1.0 / TARGET_FPS  # ~16.67ms per frame
MIN_ANIMATION_DURATION = 0.1  # Minimum 100ms for animations to be visible
MAX_ANIMATION_DURATION = 0.5  # Maximum 500ms to prevent too slow animations

# Improved animation visibility
LASER_ANIMATION_DURATION = 0.3  # 300ms for laser beam visibility
SHOTGUN_ANIMATION_DURATION = 0.25  # 250ms for shotgun spread

# Combat state
class CombatState:
    EXPLORATION = 1
    COMBAT_INIT = 2
    COMBAT_ACTIVE = 3
    COMBAT_RESOLUTION = 4
    COMBAT_EXIT = 5

# Item classes
class HealthPack:
    def __init__(self, x, y, heal_amount=25):
        self.x = x
        self.y = y
        self.heal_amount = heal_amount
        self.symbol = '+'
        self.name = "Health Pack"

class AmmoPack:
    def __init__(self, x, y, ammo_amount=10):
        self.x = x
        self.y = y
        self.ammo_amount = ammo_amount
        self.symbol = 'A'
        self.name = "Ammo Pack"

MAX_ENEMIES = 5

def is_position_occupied_by_player(x, y, player):
    """Check if a position is occupied by the player."""
    return player.x == x and player.y == y

def check_item_pickup(player, items, activity_log, weapons, max_log_entries, status_message):
    """Check if player is on an item and pick it up."""
    for item in items[:]:
        if player.x == item.x and player.y == item.y:
            if isinstance(item, HealthPack):
                old_health = player.health
                player.health = min(100, player.health + item.heal_amount)
                pickup_message = f"Picked up {item.name}! Health: {old_health} -> {player.health} (+{item.heal_amount})"
                activity_log.append(pickup_message)
                status_message[0] = pickup_message  # Update status message
                items.remove(item)
            elif isinstance(item, AmmoPack):
                total_ammo_added = 0
                for weapon in weapons:
                    old_ammo = weapon.ammo
                    weapon.ammo = min(weapon.ammo_capacity, weapon.ammo + item.ammo_amount)
                    total_ammo_added += weapon.ammo - old_ammo
                pickup_message = f"Picked up {item.name}! Restored {total_ammo_added} ammo to weapons"
                activity_log.append(pickup_message)
                status_message[0] = pickup_message  # Update status message
                items.remove(item)
            if len(activity_log) > max_log_entries:
                activity_log.pop(0)
            return True
    return False

def find_open_position(game_map):
    """Find a random open position in the map that is not blocked."""
    attempts = 0
    max_attempts = 1000
    while attempts < max_attempts:
        x = random.randint(1, game_map.width - 2)
        y = random.randint(1, game_map.height - 2)
        if not game_map.is_blocked(x, y):
            return x, y
        attempts += 1
    # Fallback: return center position if no open position found
    return game_map.width // 2, game_map.height // 2

class Game:
    def __init__(self, stdscr):
        self.stdscr = stdscr
        self.combat_mode = False
        self.turn_order = []
        self.current_turn_index = 0
        self.combat_log = []
        self.selected_action = None
        self.selected_target = None
        self.valid_targets = []
        
        # Initialize color support
        if curses.has_colors():
            curses.start_color()
            curses.init_pair(1, curses.COLOR_CYAN, curses.COLOR_BLACK) # Player
            curses.init_pair(2, curses.COLOR_RED, curses.COLOR_BLACK) # Enemies
            curses.init_pair(3, curses.COLOR_WHITE, curses.COLOR_BLACK) # Status text
            curses.init_pair(4, curses.COLOR_GREEN, curses.COLOR_BLACK) # Items
            curses.init_pair(5, curses.COLOR_YELLOW, curses.COLOR_BLACK) # Health packs
            curses.init_pair(6, curses.COLOR_BLUE, curses.COLOR_BLACK) # Ammo packs
            curses.init_pair(7, curses.COLOR_MAGENTA, curses.COLOR_BLACK) # Power-ups
            curses.init_pair(8, curses.COLOR_WHITE, curses.COLOR_BLUE) # Water effect
            curses.init_pair(9, curses.COLOR_GREEN, curses.COLOR_BLACK) # Trees
            curses.init_pair(10, curses.COLOR_RED, curses.COLOR_YELLOW) # Lava
            curses.init_pair(11, curses.COLOR_YELLOW, curses.COLOR_RED) # Spikes

        # Initialize timing system
        self.last_frame_time = time.time()
        self.current_time = time.time()
        self.frame_count = 0
        self.fps_timer = time.time()
        self.actual_fps = 0

        # Initialize game components with rooms-based map
        self.game_map = Map(width=80, height=30)
        self.game_map.grid = self.game_map.generate_maze(use_rooms=True)
        
        # Find a good central location for the player in an open area
        player_x, player_y = find_open_position(self.game_map)
        self.player = Player(x=player_x, y=player_y, health=100)
        
        # Initialize enemies at random open positions
        self.enemies = []
        for _ in range(2):  # Start with 2 enemies
            x, y = find_open_position(self.game_map)
            # Choose a random enemy type for initial enemies
            enemy_types = [FastEnemy, TankEnemy, SniperEnemy, HealerEnemy, StealthEnemy]
            enemy_class = random.choice(enemy_types)
            self.enemies.append(enemy_class(x=x, y=y))

        self.weapons = [LaserPistol(), Shotgun(), PlasmaRifle(), GrenadeLauncher(), RailGun(), Flamethrower(), Crossbow()]
        self.current_weapon = self.weapons[0]
        self.score = 0
        self.direction = 'right' # Default shooting direction
        self.status_message = "Welcome to Cyberfucker!"

        # Initialize items at random open positions
        self.items = []
        for _ in range(12):  # Spawn 12 health packs
            x, y = find_open_position(self.game_map)
            self.items.append(HealthPack(x, y))
        for _ in range(8):  # Spawn 8 ammo packs
            x, y = find_open_position(self.game_map)
            self.items.append(AmmoPack(x, y))

        # Activity log for notifications
        self.activity_log = []
        self.max_log_entries = 10
        
        # Combat actions available to player
        self.player_actions = [
            AttackAction(),
            DefendAction(),
            UseItemAction("health_potion"),
            CastSpellAction("fireball"),
            CastSpellAction("heal")
        ]

    def update(self):
        """Main update method"""
        if self.combat_mode:
            self.update_combat()
        else:
            self.update_exploration()

    def update_exploration(self):
        """Standard exploration update"""
        # Existing exploration logic would go here
        # Check for combat initiation
        if self.check_combat_start():
            self.enter_combat()

    def update_combat(self):
        """Combat-specific update"""
        # Handle current turn
        if self.current_turn_index < len(self.turn_order):
            current_entity = self.turn_order[self.current_turn_index]
            
            if isinstance(current_entity, Player):
                # Player turn - wait for input
                # In this implementation, we'll handle player input in the main loop
                pass
            else:
                # Enemy turn - AI decision
                self.handle_enemy_turn(current_entity)
                
                # Move to next turn
                self.next_turn()

    def check_combat_start(self):
        """Check if combat should start"""
        # Combat starts when player is adjacent to any enemy
        for enemy in self.enemies:
            distance = abs(self.player.x - enemy.x) + abs(self.player.y - enemy.y)
            if distance <= 1:
                return True
        return False

    def enter_combat(self):
        """Enter combat mode"""
        self.combat_mode = True
        self.build_turn_order()
        self.current_turn_index = 0
        self.combat_log = []
        self.log_combat_event("Combat started!")
        
        # UI changes for combat mode
        self.status_message = "Combat started! Select an action."

    def exit_combat(self):
        """Exit combat mode"""
        self.combat_mode = False
        self.turn_order = []
        self.current_turn_index = 0
        self.combat_log = []
        
        # UI changes for exploration mode
        self.status_message = "Combat ended!"

    def build_turn_order(self):
        """Build the turn order for combat"""
        # Player always goes first
        self.turn_order = [self.player]
        
        # Add enemies, sorted by some criteria (e.g., speed, type)
        # For now, we'll add them in their current order
        self.turn_order.extend(self.enemies)

    def next_turn(self):
        """Move to the next turn"""
        # Update cooldowns for current entity
        if self.current_turn_index < len(self.turn_order):
            current_entity = self.turn_order[self.current_turn_index]
            if hasattr(current_entity, 'actions'):
                for action in current_entity.actions:
                    action.update_cooldown()
        
        # Move to next entity
        self.current_turn_index = (self.current_turn_index + 1) % len(self.turn_order)
        
        # If we're back to the first entity, it's a new round
        if self.current_turn_index == 0:
            self.new_round()

    def new_round(self):
        """Called at the start of each new round"""
        # Update status effects for all entities
        for entity in self.turn_order:
            entity.on_turn_end()
            entity.on_turn_start()
        
        # Check for combat end conditions
        self.check_combat_end()

    def check_combat_end(self):
        """Check if combat should end"""
        # Combat ends when all enemies are defeated
        if not self.enemies:
            self.log_combat_event("All enemies defeated!")
            self.exit_combat()
            return
        
        # Combat ends if player is defeated
        if self.player.health <= 0:
            self.log_combat_event("Player defeated!")
            self.exit_combat()
            return

    def handle_player_turn(self):
        """Handle player's turn in combat"""
        # In combat mode, player input is different
        # Player selects an action, then a target
        # This would be handled in the input system
        pass

    def handle_enemy_turn(self, enemy):
        """Handle an enemy's turn in combat"""
        # Update enemy status effects
        enemy.on_turn_start()
        
        # Simple AI decision - choose a random available action
        if enemy.actions and self.player in self.turn_order:
            # Filter actions that can be executed
            available_actions = [action for action in enemy.actions if action.can_execute(enemy)]
            
            if available_actions:
                # Choose a random action
                action = random.choice(available_actions)
                
                # For attack actions, target the player
                target = self.player if isinstance(action, AttackAction) else None
                
                # Execute action
                if action.can_execute(enemy):
                    result = action.execute(enemy, target, self)
                    self.log_combat_event(result)
        
        # Update status effects at end of turn
        enemy.on_turn_end()
        
        # Check for combat end
        self.check_combat_end()

    def log_combat_event(self, event):
        """Add an event to the combat log"""
        self.combat_log.append(f"Turn {self.get_current_turn_number()}: {event}")
        # Keep log at reasonable size
        if len(self.combat_log) > 20:
            self.combat_log.pop(0)
        
        # Also add to activity log
        self.activity_log.append(event)
        if len(self.activity_log) > self.max_log_entries:
            self.activity_log.pop(0)

    def get_current_turn_number(self):
        """Get the current turn number (1-indexed)"""
        return (self.current_turn_index // len(self.turn_order)) + 1

    def handle_combat_input(self, key):
        """Handle input during combat"""
        # Action selection
        if key == ord('a'):
            # Attack action
            self.select_combat_action("attack")
        elif key == ord('d'):
            # Defend action
            self.select_combat_action("defend")
        elif key == ord('i'):
            # Item action
            self.select_combat_action("item")
        elif key == ord('s'):
            # Spell action
            self.select_combat_action("spell")
        # ... other combat actions
        
        # Target selection (after action is selected)
        elif self.selected_action:
            if key == ord('w'):  # Up
                self.select_target(0, -1)
            elif key == ord('s'):  # Down
                self.select_target(0, 1)
            elif key == ord('a'):  # Left
                self.select_target(-1, 0)
            elif key == ord('d'):  # Right
                self.select_target(1, 0)
            elif key == ord(' '):  # Confirm target
                self.execute_combat_action()
            elif key == 27:  # Escape
                self.cancel_combat_action()

    def select_combat_action(self, action_type):
        """Select a combat action type"""
        self.selected_action = action_type
        # Highlight valid targets for this action
        self.highlight_targets(action_type)

    def execute_combat_action(self):
        """Execute the selected combat action on the selected target"""
        if self.selected_action and self.selected_target:
            # Get current entity (should be player)
            current_entity = self.turn_order[self.current_turn_index]
            
            # Create action instance
            if self.selected_action == "attack":
                action = AttackAction()
            elif self.selected_action == "defend":
                action = DefendAction()
            # ... other actions
            
            # Execute action
            if action.can_execute(current_entity):
                result = action.execute(current_entity, self.selected_target, self)
                self.log_combat_event(result)
                
                # Move to next turn
                self.next_turn()
                
                # Clear selection
                self.selected_action = None
                self.selected_target = None

    def highlight_targets(self, action_type):
        """Highlight valid targets for an action"""
        # For now, just set valid targets to all enemies
        self.valid_targets = self.enemies[:]

    def select_target(self, dx, dy):
        """Select a target based on direction"""
        # Simple target selection for now
        if self.valid_targets:
            self.selected_target = self.valid_targets[0]

    def cancel_combat_action(self):
        """Cancel the current combat action selection"""
        self.selected_action = None
        self.selected_target = None
        self.valid_targets = []

    def handle_input(self, key):
        """Handle input based on current game mode"""
        if self.combat_mode:
            self.handle_combat_input(key)
        else:
            self.handle_exploration_input(key)

    def handle_exploration_input(self, key):
        """Handle input during exploration"""
        if key == ord('q'):
            return False
        elif key in [curses.KEY_UP, ord('w')]:
            # Check for diagonal movement (w + a or w + d)
            next_key = self.stdscr.getch()
            if next_key in [curses.KEY_LEFT, ord('a')]:
                self.player.move(-1, -1, self.game_map, self.weapons, self.enemies)
                check_item_pickup(self.player, self.items, self.activity_log, self.weapons, self.max_log_entries, [self.status_message])
                self.direction = 'up-left'
            elif next_key in [curses.KEY_RIGHT, ord('d')]:
                self.player.move(1, -1, self.game_map, self.weapons, self.enemies)
                check_item_pickup(self.player, self.items, self.activity_log, self.weapons, self.max_log_entries, [self.status_message])
                self.direction = 'up-right'
            else:
                self.player.move(0, -1, self.game_map, self.weapons, self.enemies)
                check_item_pickup(self.player, self.items, self.activity_log, self.weapons, self.max_log_entries, [self.status_message])
                self.direction = 'up'
        elif key in [curses.KEY_DOWN, ord('s')]:
            # Check for diagonal movement (s + a or s + d)
            next_key = self.stdscr.getch()
            if next_key in [curses.KEY_LEFT, ord('a')]:
                self.player.move(-1, 1, self.game_map, self.weapons, self.enemies)
                check_item_pickup(self.player, self.items, self.activity_log, self.weapons, self.max_log_entries, [self.status_message])
                self.direction = 'down-left'
            elif next_key in [curses.KEY_RIGHT, ord('d')]:
                self.player.move(1, 1, self.game_map, self.weapons, self.enemies)
                check_item_pickup(self.player, self.items, self.activity_log, self.weapons, self.max_log_entries, [self.status_message])
                self.direction = 'down-right'
            else:
                self.player.move(0, 1, self.game_map, self.weapons, self.enemies)
                check_item_pickup(self.player, self.items, self.activity_log, self.weapons, self.max_log_entries, [self.status_message])
                self.direction = 'down'
        elif key in [curses.KEY_LEFT, ord('a')]:
            self.player.move(-1, 0, self.game_map, self.weapons, self.enemies)
            check_item_pickup(self.player, self.items, self.activity_log, self.weapons, self.max_log_entries, [self.status_message])
            self.direction = 'left'
        elif key in [curses.KEY_RIGHT, ord('d')]:
            self.player.move(1, 0, self.game_map, self.weapons, self.enemies)
            check_item_pickup(self.player, self.items, self.activity_log, self.weapons, self.max_log_entries, [self.status_message])
            self.direction = 'right'
        elif key == ord(' '): # Shoot in current direction
            if self.current_weapon.shoot(self.player.x, self.player.y, self.direction, self.game_map, self.enemies, self.stdscr):
                self.status_message = f"Fired {self.current_weapon.name}! Ammo: {self.current_weapon.ammo}/{self.current_weapon.ammo_capacity}"
                self.activity_log.append(f"Fired {self.current_weapon.name} {self.direction.upper()}")
                if len(self.activity_log) > self.max_log_entries:
                    self.activity_log.pop(0)
            else:
                self.status_message = f"No ammo for {self.current_weapon.name}!"
        elif key == ord('i'): # Shoot up
            shoot_direction = 'up'
            if self.current_weapon.shoot(self.player.x, self.player.y, shoot_direction, self.game_map, self.enemies, self.stdscr):
                self.status_message = f"Fired {self.current_weapon.name} up! Ammo: {self.current_weapon.ammo}/{self.current_weapon.ammo_capacity}"
                self.activity_log.append(f"Fired {self.current_weapon.name} UP")
                if len(self.activity_log) > self.max_log_entries:
                    self.activity_log.pop(0)
            else:
                self.status_message = f"No ammo for {self.current_weapon.name}!"
        elif key == ord('k'): # Shoot down
            shoot_direction = 'down'
            if self.current_weapon.shoot(self.player.x, self.player.y, shoot_direction, self.game_map, self.enemies, self.stdscr):
                self.status_message = f"Fired {self.current_weapon.name} down! Ammo: {self.current_weapon.ammo}/{self.current_weapon.ammo_capacity}"
                self.activity_log.append(f"Fired {self.current_weapon.name} DOWN")
                if len(self.activity_log) > self.max_log_entries:
                    self.activity_log.pop(0)
            else:
                self.status_message = f"No ammo for {self.current_weapon.name}!"
        elif key == ord('j'): # Shoot left
            shoot_direction = 'left'
            if self.current_weapon.shoot(self.player.x, self.player.y, shoot_direction, self.game_map, self.enemies, self.stdscr):
                self.status_message = f"Fired {self.current_weapon.name} left! Ammo: {self.current_weapon.ammo}/{self.current_weapon.ammo_capacity}"
                self.activity_log.append(f"Fired {self.current_weapon.name} LEFT")
                if len(self.activity_log) > self.max_log_entries:
                    self.activity_log.pop(0)
            else:
                self.status_message = f"No ammo for {self.current_weapon.name}!"
        elif key == ord('l'): # Shoot right
            shoot_direction = 'right'
            if self.current_weapon.shoot(self.player.x, self.player.y, shoot_direction, self.game_map, self.enemies, self.stdscr):
                self.status_message = f"Fired {self.current_weapon.name} right! Ammo: {self.current_weapon.ammo}/{self.current_weapon.ammo_capacity}"
                self.activity_log.append(f"Fired {self.current_weapon.name} RIGHT")
                if len(self.activity_log) > self.max_log_entries:
                    self.activity_log.pop(0)
            else:
                self.status_message = f"No ammo for {self.current_weapon.name}!"
        elif key == ord('1'): # Switch to Laser Pistol
            self.current_weapon = self.weapons[0]
            self.status_message = f"Switched to {self.current_weapon.name}"
        elif key == ord('2'): # Switch to Shotgun
            self.current_weapon = self.weapons[1]
            self.status_message = f"Switched to {self.current_weapon.name}"
        elif key == ord('3'): # Switch to Plasma Rifle
            self.current_weapon = self.weapons[2]
            self.status_message = f"Switched to {self.current_weapon.name}"
        elif key == ord('4'): # Switch to Grenade Launcher
            self.current_weapon = self.weapons[3]
            self.status_message = f"Switched to {self.current_weapon.name}"
        elif key == ord('5'): # Switch to Rail Gun
            self.current_weapon = self.weapons[4]
            self.status_message = f"Switched to {self.current_weapon.name}"
        elif key == ord('6'): # Switch to Flamethrower
            self.current_weapon = self.weapons[5]
            self.status_message = f"Switched to {self.current_weapon.name}"
        elif key == ord('7'): # Switch to Crossbow
            self.current_weapon = self.weapons[6]
            self.status_message = f"Switched to {self.current_weapon.name}"
        elif key == ord('r'): # Reload all weapons
            for weapon in self.weapons:
                weapon.reload(weapon.ammo_capacity // 2) # Partial reload
            self.status_message = "Reloaded weapons!"
        elif key == ord('z'): # Toggle zoom
            self.game_map.zoom_factor = 2 if self.game_map.zoom_factor == 1 else 1
            zoom_status = "ON" if self.game_map.zoom_factor == 2 else "OFF"
            self.status_message = f"Zoom {zoom_status}!"
        
        # Check if player performed an action (turn-based enemy movement)
        player_action = False
        if key in [ord('w'), ord('a'), ord('s'), ord('d'), curses.KEY_UP, curses.KEY_DOWN, curses.KEY_LEFT, curses.KEY_RIGHT, ord(' '), ord('r')]:
            player_action = True
        
        # Update enemies only when player acts (turn-based)
        if player_action and not self.combat_mode:
            for enemy in self.enemies[:]:
                # Improved enemy AI - better encircling behavior
                dx = self.player.x - enemy.x
                dy = self.player.y - enemy.y
                distance = abs(dx) + abs(dy)

                # If close to player, try to encircle
                if distance < 8:
                    # Choose direction that gets closer to player but with some randomness
                    if abs(dx) > abs(dy):
                        if dx > 0:
                            enemy.move_towards(self.player.x - 1, self.player.y, self.game_map, self.player, self.enemies) # Try to flank
                        else:
                            enemy.move_towards(self.player.x + 1, self.player.y, self.game_map, self.player, self.enemies)
                    else:
                        if dy > 0:
                            enemy.move_towards(self.player.x, self.player.y - 1, self.game_map, self.player, self.enemies)
                        else:
                            enemy.move_towards(self.player.x, self.player.y + 1, self.game_map, self.player, self.enemies)
                else:
                    # Normal pursuit
                    enemy.move_towards(self.player.x, self.player.y, self.game_map, self.player, self.enemies)

                if enemy.check_collision(self.player):
                    self.player.take_damage(10)
                    self.status_message = "You're being attacked!"
                    self.activity_log.append("Player took 10 damage from enemy!")
                    if len(self.activity_log) > self.max_log_entries:
                        self.activity_log.pop(0)

                if enemy.health <= 0:
                    self.enemies.remove(enemy)
                    self.score += 10
                    self.status_message = f"Enemy defeated! Score: {self.score}"
                    self.activity_log.append(f"Enemy defeated! Score: {self.score}")
                    if len(self.activity_log) > self.max_log_entries:
                        self.activity_log.pop(0)

            # Spawn new enemy occasionally (limited to MAX_ENEMIES) - moved outside enemy loop
            # Lower spawn rate and only when we have fewer enemies than max
            if len(self.enemies) < MAX_ENEMIES and random.random() < 0.05:  # Reduced from 20% to 5%
                # Spawn enemies around the player but not too close
                angle = random.random() * 2 * 3.14159
                distance = random.randint(15, 25)
                new_x = int(self.player.x + distance * math.cos(angle))
                new_y = int(self.player.y + distance * math.sin(angle))
                # Keep within map bounds
                new_x = max(1, min(new_x, self.game_map.width - 2))
                new_y = max(1, min(new_y, self.game_map.height - 2))
                if not self.game_map.is_blocked(new_x, new_y):
                    # Randomly select enemy type with weighted probabilities
                    enemy_weights = {
                        'basic': 0.3,   # 30% basic enemies
                        'fast': 0.25,   # 25% fast enemies
                        'tank': 0.15,   # 15% tank enemies
                        'sniper': 0.15, # 15% sniper enemies
                        'healer': 0.1,  # 10% healer enemies
                        'stealth': 0.05 # 5% stealth enemies
                    }

                    # Select enemy type based on weights
                    rand_val = random.random()
                    cumulative = 0
                    selected_type = 'basic'
                    for enemy_type, weight in enemy_weights.items():
                        cumulative += weight
                        if rand_val <= cumulative:
                            selected_type = enemy_type
                            break

                    # Create the selected enemy type
                    enemy_class = ENEMY_TYPES[selected_type]
                    new_enemy = enemy_class(x=new_x, y=new_y)
                    self.enemies.append(new_enemy)
                    self.activity_log.append(f"New {selected_type} enemy spawned! Total enemies: {len(self.enemies)}")
                    if len(self.activity_log) > self.max_log_entries:
                        self.activity_log.pop(0)
        
        return True

    def update_map_animation(self):
        """Update map animation"""
        self.game_map.update_animation()

    def render(self):
        """Render the game"""
        self.stdscr.clear()
        self.game_map.render(self.stdscr, colors=True, player_x=self.player.x, player_y=self.player.y)
        
        # Render player with color (adjusted for zoom)
        max_y, max_x = self.stdscr.getmaxyx()
        player_render_y = self.player.y * self.game_map.zoom_factor
        player_render_x = self.player.x * self.game_map.zoom_factor

        # Render player as a zoomed block
        for zy in range(self.game_map.zoom_factor):
            for zx in range(self.game_map.zoom_factor):
                render_y = player_render_y + zy
                render_x = player_render_x + zx
                if 0 <= render_x < max_x and 0 <= render_y < max_y - 1: # Leave room for status bar
                    try:
                        if curses.has_colors():
                            self.stdscr.addch(render_y, render_x, '@', curses.color_pair(1))
                        else:
                            self.stdscr.addch(render_y, render_x, '@')
                    except curses.error:
                        pass
        
        # Render items with specific colors (adjusted for zoom)
        for item in self.items:
            max_y, max_x = self.stdscr.getmaxyx()
            item_render_y = item.y * self.game_map.zoom_factor
            item_render_x = item.x * self.game_map.zoom_factor

            # Render item as a zoomed block
            for zy in range(self.game_map.zoom_factor):
                for zx in range(self.game_map.zoom_factor):
                    render_y = item_render_y + zy
                    render_x = item_render_x + zx
                    if 0 <= render_x < max_x and 0 <= render_y < max_y - 1:
                        try:
                            if curses.has_colors():
                                if isinstance(item, HealthPack):
                                    color_pair = curses.color_pair(5)  # Yellow for health
                                elif isinstance(item, AmmoPack):
                                    color_pair = curses.color_pair(6)  # Blue for ammo
                                else:
                                    color_pair = curses.color_pair(7)  # Magenta for others
                                self.stdscr.addch(render_y, render_x, item.symbol, color_pair)
                            else:
                                self.stdscr.addch(render_y, render_x, item.symbol)
                        except curses.error:
                            pass

        # Render enemies with color (adjusted for zoom)
        for enemy in self.enemies:
            max_y, max_x = self.stdscr.getmaxyx()
            # Ensure enemy positions are within bounds
            enemy.x = max(0, min(enemy.x, self.game_map.width - 1))
            enemy.y = max(0, min(enemy.y, self.game_map.height - 1))

            enemy_render_y = enemy.y * self.game_map.zoom_factor
            enemy_render_x = enemy.x * self.game_map.zoom_factor

            # Render enemy as a zoomed block
            for zy in range(self.game_map.zoom_factor):
                for zx in range(self.game_map.zoom_factor):
                    render_y = enemy_render_y + zy
                    render_x = enemy_render_x + zx
                    if 0 <= render_x < max_x and 0 <= render_y < max_y - 2:  # Leave room for status bar
                        try:
                            # Use the enemy's character attribute for rendering
                            enemy_char = getattr(enemy, 'char', 'E')  # Default to 'E' if no char attribute
                            if curses.has_colors():
                                self.stdscr.addch(render_y, render_x, enemy_char, curses.color_pair(2))
                            else:
                                self.stdscr.addch(render_y, render_x, enemy_char)
                        except curses.error:
                            pass  # Ignore curses errors for out-of-bounds characters
        
        # Status bar with enhanced information - optimized for horizontal space
        # Create compact weapon info
        weapon_info = []
        for w in self.weapons:
            if w == self.current_weapon:
                weapon_info.append(f"[{w.name}: {w.ammo}/{w.ammo_capacity}]")  # Current weapon in brackets
            else:
                weapon_info.append(f"{w.name}: {w.ammo}/{w.ammo_capacity}")

        ammo_info = " | ".join(weapon_info)
        fps_info = f"FPS:{self.actual_fps}" if self.actual_fps > 0 else "FPS:--"

        # Check for nearby items to show in status
        nearby_items = []
        for item in self.items:
            distance = abs(self.player.x - item.x) + abs(self.player.y - item.y)
            if distance <= 3:  # Items within 3 tiles
                nearby_items.append(item.symbol)  # Use symbols instead of full names

        items_info = ""
        if nearby_items:
            items_info = f" | Items:{''.join(nearby_items)}"

        # Add terrain info to status
        current_terrain = self.game_map.grid[self.player.y][self.player.x] if 0 <= self.player.x < self.game_map.width and 0 <= self.player.y < self.game_map.height else '.'
        terrain_names = {
            'W': 'Water', 'R': 'Rough', 'T': 'Trees',
            'L': 'LAVA!', 'S': 'Spikes!', '.': 'Normal'
        }
        terrain_info = terrain_names.get(current_terrain, 'Unknown')

        # Create compact status text with better space utilization
        status_text = (f"HP:{self.player.health} | Score:{self.score} | Dir:{self.direction.upper()} | "
                           f"Terrain:{terrain_info} | {ammo_info}{items_info} | {fps_info} | {self.status_message}")

        max_y, max_x = self.stdscr.getmaxyx()
        status_y = max_y - 1 # Always put status bar at the very bottom
        log_x = max_x // 2  # Start activity log from middle of screen
        try:
            if curses.has_colors():
                self.stdscr.addstr(status_y, 0, status_text[:log_x-1], curses.color_pair(3))
            else:
                self.stdscr.addstr(status_y, 0, status_text[:log_x-1])
        except curses.error:
            pass # Ignore if we can't write to status bar

        # Activity log on the right side - optimized for space
        log_y = 0
        available_log_width = max_x - log_x - 1  # Space available for log entries

        for i, log_entry in enumerate(reversed(self.activity_log[-self.max_log_entries:])):
            if log_y + i >= max_y - 2:  # Leave room for status bar
                break
            # Truncate log entries to fit available space, but show most important part
            if len(log_entry) > available_log_width:
                truncated_entry = "..." + log_entry[-(available_log_width-3):]
            else:
                truncated_entry = log_entry

            try:
                if curses.has_colors():
                    self.stdscr.addstr(log_y + i, log_x, f" {truncated_entry}", curses.color_pair(3))
                else:
                    self.stdscr.addstr(log_y + i, log_x, f" {truncated_entry}")
            except curses.error:
                pass
        
        self.stdscr.refresh()

    def run(self):
        """Main game loop"""
        curses.curs_set(0) # Hide cursor
        self.stdscr.nodelay(1) # Non-blocking input
        self.stdscr.timeout(100) # Input timeout

        running = True
        while running:
            # Handle input
            key = self.stdscr.getch()
            running = self.handle_input(key)
            
            # Update game state
            self.update()
            
            # Update map animation
            self.update_map_animation()
            
            # Render
            self.render()
            
            # Frame rate control using absolute timing
            self.current_time = time.time()
            frame_time = self.current_time - self.last_frame_time

            # Performance monitoring
            self.frame_count += 1
            if self.current_time - self.fps_timer >= 1.0:  # Update FPS every second
                self.actual_fps = self.frame_count
                self.frame_count = 0
                self.fps_timer = self.current_time

            # Maintain target frame rate with performance optimization
            if frame_time < FRAME_TIME:
                time.sleep(FRAME_TIME - frame_time)
            elif frame_time > FRAME_TIME * 2:  # If frame took more than double the target time
                # Skip frame timing to prevent game freeze
                pass  # Don't sleep, just continue

            self.last_frame_time = time.time()

            # Check game over
            if self.player.health <= 0:
                max_y, max_x = self.stdscr.getmaxyx()
                game_over_text = f"Game Over! Final Score: {self.score}"
                try:
                    self.stdscr.addstr(max_y // 2, max_x // 2 - len(game_over_text) // 2, game_over_text)
                    self.stdscr.addstr(max_y // 2 + 1, max_x // 2 - 5, "Press 'q' to quit.")
                    self.stdscr.refresh()
                except curses.error:
                    pass
                while self.stdscr.getch() != ord('q'):
                    pass
                running = False

def main(stdscr):
    """Main game function using curses for terminal display."""
    game = Game(stdscr)
    game.run()

if __name__ == "__main__":
    curses.wrapper(main)