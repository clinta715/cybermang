#!/usr/bin/env python3
"""
Enemy module for handling enemy AI and behavior.
"""

import random
from status_effects import *
from combat_actions import *

class Enemy:
    def __init__(self, x, y, health=50):
        self.x = x
        self.y = y
        self.health = health
        self.move_cooldown = 0
        self.strategy = random.choice(['direct', 'flanking', 'circling'])
        # Status effect attributes
        self.status_effects = []
        self.paralyzed = False
        self.blinded = False
        self.confused = False
        self.hasted = False
        self.slowed = False
        self.strengthened = False
        self.weakened = False
        self.protected = False
        self.combat_log = []  # For logging combat events
        # Combat actions
        self.actions = [AttackAction()]

    def move_towards(self, target_x, target_y, game_map, player, all_enemies=None):
        """Improved pathfinding with strategic movement patterns."""
        # Check if enemy can act (affected by status effects)
        if not self.can_act():
            return
            
        if self.move_cooldown > 0:
            self.move_cooldown -= 1
            return

        dx = target_x - self.x
        dy = target_y - self.y
        distance = abs(dx) + abs(dy)

        # Strategy-based movement
        if self.strategy == 'direct':
            # Direct pursuit
            self._direct_move(dx, dy, game_map, player, all_enemies)
        elif self.strategy == 'flanking':
            # Try to flank the target
            self._flanking_move(dx, dy, game_map, player, all_enemies)
        elif self.strategy == 'circling':
            # Try to circle around the target
            self._circling_move(dx, dy, game_map, player, all_enemies)

        # Occasionally change strategy
        if random.random() < 0.05:
            self.strategy = random.choice(['direct', 'flanking', 'circling'])

        # Add some randomness to movement
        self.move_cooldown = random.randint(0, 2)

    def _direct_move(self, dx, dy, game_map, player, all_enemies=None):
        """Direct movement towards target with terrain effects."""
        if abs(dx) > abs(dy):
            new_x = self.x + (1 if dx > 0 else -1)
            if (not game_map.is_blocked(new_x, self.y) and
                not (new_x == player.x and self.y == player.y) and
                not self._would_collide_with_enemy(new_x, self.y, all_enemies)):
                # Apply terrain damage when moving
                terrain_damage = game_map.get_terrain_damage(new_x, self.y)
                if terrain_damage > 0:
                    self.take_damage(terrain_damage)
                self.x = new_x
                return
            new_y = self.y + (1 if dy > 0 else -1)
            if (not game_map.is_blocked(self.x, new_y) and
                not (self.x == player.x and new_y == player.y) and
                not self._would_collide_with_enemy(self.x, new_y, all_enemies)):
                # Apply terrain damage when moving
                terrain_damage = game_map.get_terrain_damage(self.x, new_y)
                if terrain_damage > 0:
                    self.take_damage(terrain_damage)
                self.y = new_y
        else:
            new_y = self.y + (1 if dy > 0 else -1)
            if (not game_map.is_blocked(self.x, new_y) and
                not (self.x == player.x and new_y == player.y) and
                not self._would_collide_with_enemy(self.x, new_y, all_enemies)):
                # Apply terrain damage when moving
                terrain_damage = game_map.get_terrain_damage(self.x, new_y)
                if terrain_damage > 0:
                    self.take_damage(terrain_damage)
                self.y = new_y
                return
            new_x = self.x + (1 if dx > 0 else -1)
            if (not game_map.is_blocked(new_x, self.y) and
                not (new_x == player.x and self.y == player.y) and
                not self._would_collide_with_enemy(new_x, self.y, all_enemies)):
                # Apply terrain damage when moving
                terrain_damage = game_map.get_terrain_damage(new_x, self.y)
                if terrain_damage > 0:
                    self.take_damage(terrain_damage)
                self.x = new_x

    def _flanking_move(self, dx, dy, game_map, player, all_enemies=None):
        """Try to flank the target by moving perpendicular with terrain effects."""
        # Try to move perpendicular to the direct path
        if abs(dx) > abs(dy):
            # Target is more horizontal, so try vertical flanking
            new_y = self.y + (1 if random.random() > 0.5 else -1)
            if (not game_map.is_blocked(self.x, new_y) and
                not (self.x == player.x and new_y == player.y) and
                not self._would_collide_with_enemy(self.x, new_y, all_enemies)):
                # Apply terrain damage when moving
                terrain_damage = game_map.get_terrain_damage(self.x, new_y)
                if terrain_damage > 0:
                    self.take_damage(terrain_damage)
                self.y = new_y
                return
            # Fall back to direct movement
            self._direct_move(dx, dy, game_map, player, all_enemies)
        else:
            # Target is more vertical, so try horizontal flanking
            new_x = self.x + (1 if random.random() > 0.5 else -1)
            if (not game_map.is_blocked(new_x, self.y) and
                not (new_x == player.x and self.y == player.y) and
                not self._would_collide_with_enemy(new_x, self.y, all_enemies)):
                # Apply terrain damage when moving
                terrain_damage = game_map.get_terrain_damage(new_x, self.y)
                if terrain_damage > 0:
                    self.take_damage(terrain_damage)
                self.x = new_x
                return
            # Fall back to direct movement
            self._direct_move(dx, dy, game_map, player, all_enemies)

    def _circling_move(self, dx, dy, game_map, player, all_enemies=None):
        """Try to circle around the target with terrain effects."""
        # Choose a circling direction based on position
        circle_dir = 1 if (self.x + self.y) % 2 == 0 else -1

        # Try circling movement
        if abs(dx) > abs(dy):
            # Circle vertically
            new_y = self.y + circle_dir
            if (not game_map.is_blocked(self.x, new_y) and
                not (self.x == player.x and new_y == player.y) and
                not self._would_collide_with_enemy(self.x, new_y, all_enemies)):
                # Apply terrain damage when moving
                terrain_damage = game_map.get_terrain_damage(self.x, new_y)
                if terrain_damage > 0:
                    self.take_damage(terrain_damage)
                self.y = new_y
                return
        else:
            # Circle horizontally
            new_x = self.x + circle_dir
            if (not game_map.is_blocked(new_x, self.y) and
                not (new_x == player.x and self.y == player.y) and
                not self._would_collide_with_enemy(new_x, self.y, all_enemies)):
                # Apply terrain damage when moving
                terrain_damage = game_map.get_terrain_damage(new_x, self.y)
                if terrain_damage > 0:
                    self.take_damage(terrain_damage)
                self.x = new_x
                return

        # Fall back to direct movement if circling is blocked
        self._direct_move(dx, dy, game_map, player, all_enemies)

    def check_collision(self, player):
        """Check if enemy is touching the player."""
        return self.x == player.x and self.y == player.y

    def _would_collide_with_enemy(self, x, y, all_enemies):
        """Check if moving to position would collide with another enemy."""
        if not all_enemies:
            return False
        for enemy in all_enemies:
            if enemy is not self and enemy.x == x and enemy.y == y:
                return True
        return False

    def take_damage(self, damage, ignore_protection=False):
        """Reduce enemy health, considering protection status effect."""
        # Apply protection effect if active and not ignoring protection
        if self.protected and not ignore_protection:
            # Reduce damage by 30%
            damage = int(damage * 0.7)
            
        self.health -= damage

    def apply_status_effect(self, effect):
        """Apply a status effect to the enemy"""
        # Check if effect already exists
        existing_effect = None
        for e in self.status_effects:
            if e.name == effect.name:
                existing_effect = e
                break
        
        if existing_effect:
            # Apply stacking rules
            effect.stack_effect(existing_effect)
            # Log the stacking
            self.combat_log.append(f"{self.get_entity_name()} {effect.name} effect intensified!")
        else:
            # Add new effect
            self.status_effects.append(effect)
            effect.apply_effect(self)
            # Log the application
            self.combat_log.append(f"{self.get_entity_name()} is affected by {effect.name}!")

    def remove_status_effect(self, effect_name):
        """Remove a specific status effect by name"""
        for effect in self.status_effects[:]:  # Use slice copy to avoid modification during iteration
            if effect.name == effect_name:
                effect.remove_effect(self)
                self.status_effects.remove(effect)
                return True
        return False

    def clear_all_status_effects(self):
        """Remove all status effects"""
        for effect in self.status_effects[:]:
            effect.remove_effect(self)
        self.status_effects.clear()

    def update_status_effects(self):
        """Update all status effects at the start of the enemy's turn"""
        for effect in self.status_effects[:]:  # Use slice copy to avoid modification during iteration
            if effect.on_turn_end(self):
                effect.remove_effect(self)
                self.status_effects.remove(effect)
                # Log the removal
                self.combat_log.append(f"{self.get_entity_name()} is no longer affected by {effect.name}!")

    def get_active_effects(self):
        """Return a list of all active status effect names"""
        return [effect.name for effect in self.status_effects]

    def has_status_effect(self, effect_name):
        """Check if a specific effect is active"""
        return any(effect.name == effect_name for effect in self.status_effects)

    def on_turn_start(self):
        """Called at the beginning of each turn"""
        for effect in self.status_effects:
            effect.on_turn_start(self)

    def on_turn_end(self):
        """Called at the end of each turn"""
        self.update_status_effects()

    def can_act(self):
        """Check if the enemy can perform actions"""
        # Check for paralysis
        if self.paralyzed:
            return False
        
        # Check for slow effect (50% chance to skip turn)
        if self.slowed and random.random() < 0.5:
            return False
        
        return True

    def get_entity_name(self):
        """Get display name for enemy"""
        return self.__class__.__name__


class FastEnemy(Enemy):
    """Quick, aggressive enemy that pursues relentlessly."""
    def __init__(self, x, y):
        super().__init__(x, y, health=30)
        self.move_cooldown = 0
        self.strategy = 'direct'  # Always direct pursuit
        self.char = 'F'  # Fast enemy character
        self.speed = 2  # Moves every other turn
        # Combat actions
        self.actions = [AttackAction()]

    def move_towards(self, target_x, target_y, game_map, player, all_enemies=None):
        """Fast movement - moves every other turn."""
        # Check if enemy can act (affected by status effects)
        if not self.can_act():
            return
            
        if self.move_cooldown > 0:
            self.move_cooldown -= 1
            return

        dx = target_x - self.x
        dy = target_y - self.y

        # Fast enemies always use direct movement
        self._direct_move(dx, dy, game_map, player, all_enemies)
        self.move_cooldown = self.speed - 1  # Reset cooldown


class TankEnemy(Enemy):
    """Slow but durable enemy with high health."""
    def __init__(self, x, y):
        super().__init__(x, y, health=150)
        self.move_cooldown = 0
        self.strategy = 'circling'  # Defensive circling
        self.char = 'T'  # Tank enemy character
        self.speed = 3  # Moves every 3 turns
        # Combat actions
        self.actions = [AttackAction(), DefendAction()]

    def move_towards(self, target_x, target_y, game_map, player, all_enemies=None):
        """Slow but deliberate movement."""
        # Check if enemy can act (affected by status effects)
        if not self.can_act():
            return
            
        if self.move_cooldown > 0:
            self.move_cooldown -= 1
            return

        dx = target_x - self.x
        dy = target_y - self.y

        # Tank enemies prefer circling to avoid direct confrontation
        self._circling_move(dx, dy, game_map, player, all_enemies)
        self.move_cooldown = self.speed - 1


class SniperEnemy(Enemy):
    """Long-range enemy that keeps distance and shoots."""
    def __init__(self, x, y):
        super().__init__(x, y, health=40)
        self.move_cooldown = 0
        self.strategy = 'flanking'
        self.char = 'S'  # Sniper enemy character
        self.speed = 2
        self.preferred_distance = 8  # Tries to stay 8 tiles away
        # Combat actions
        self.actions = [AttackAction()]

    def move_towards(self, target_x, target_y, game_map, player, all_enemies=None):
        """Try to maintain optimal distance from target."""
        # Check if enemy can act (affected by status effects)
        if not self.can_act():
            return
            
        if self.move_cooldown > 0:
            self.move_cooldown -= 1
            return

        dx = target_x - self.x
        dy = target_y - self.y
        distance = abs(dx) + abs(dy)

        if distance < self.preferred_distance:
            # Too close, move away
            if abs(dx) > abs(dy):
                new_x = self.x - (1 if dx > 0 else -1)
                if (not game_map.is_blocked(new_x, self.y) and
                    not (new_x == player.x and self.y == player.y) and
                    not self._would_collide_with_enemy(new_x, self.y, all_enemies)):
                    terrain_damage = game_map.get_terrain_damage(new_x, self.y)
                    if terrain_damage > 0:
                        self.take_damage(terrain_damage)
                    self.x = new_x
            else:
                new_y = self.y - (1 if dy > 0 else -1)
                if (not game_map.is_blocked(self.x, new_y) and
                    not (self.x == player.x and new_y == player.y) and
                    not self._would_collide_with_enemy(self.x, new_y, all_enemies)):
                    terrain_damage = game_map.get_terrain_damage(self.x, new_y)
                    if terrain_damage > 0:
                        self.take_damage(terrain_damage)
                    self.y = new_y
        else:
            # Use flanking movement to circle around
            self._flanking_move(dx, dy, game_map, player, all_enemies)

        self.move_cooldown = self.speed - 1


class HealerEnemy(Enemy):
    """Enemy that can heal nearby allies."""
    def __init__(self, x, y):
        super().__init__(x, y, health=50)
        self.move_cooldown = 0
        self.strategy = 'flanking'
        self.char = 'H'  # Healer enemy character
        self.speed = 2
        self.heal_cooldown = 0
        self.heal_range = 5
        # Combat actions
        self.actions = [AttackAction()]

    def move_towards(self, target_x, target_y, game_map, player, all_enemies=None):
        """Move and try to heal nearby allies."""
        # Check if enemy can act (affected by status effects)
        if not self.can_act():
            return
            
        if self.move_cooldown > 0:
            self.move_cooldown -= 1
            return

        # Try to heal nearby enemies first
        if self.heal_cooldown <= 0 and all_enemies:
            self._try_heal_allies(all_enemies)

        dx = target_x - self.x
        dy = target_y - self.y

        # Healers prefer flanking to stay out of direct combat
        self._flanking_move(dx, dy, game_map, player, all_enemies)
        self.move_cooldown = self.speed - 1
        self.heal_cooldown = max(0, self.heal_cooldown - 1)

    def _try_heal_allies(self, all_enemies):
        """Try to heal nearby damaged allies."""
        healed = False
        for enemy in all_enemies:
            if (enemy is not self and
                abs(enemy.x - self.x) + abs(enemy.y - self.y) <= self.heal_range and
                enemy.health < 50):  # Only heal if below half health
                enemy.health = min(enemy.health + 20, 100)
                healed = True

        if healed:
            self.heal_cooldown = 8  # 8 turns between heals


class StealthEnemy(Enemy):
    """Enemy that is hard to see until close."""
    def __init__(self, x, y):
        super().__init__(x, y, health=35)
        self.move_cooldown = 0
        self.strategy = 'flanking'
        self.char = 'X'  # Stealth enemy character (could be made invisible)
        self.speed = 1
        self.detection_range = 6
        # Combat actions
        self.actions = [AttackAction()]

    def move_towards(self, target_x, target_y, game_map, player, all_enemies=None):
        """Stealthy movement, prefers to stay hidden."""
        # Check if enemy can act (affected by status effects)
        if not self.can_act():
            return
            
        if self.move_cooldown > 0:
            self.move_cooldown -= 1
            return

        dx = target_x - self.x
        dy = target_y - self.y
        distance = abs(dx) + abs(dy)

        if distance <= self.detection_range:
            # Close enough to attack, use flanking
            self._flanking_move(dx, dy, game_map, player, all_enemies)
        else:
            # Stay hidden, move cautiously
            if random.random() < 0.3:  # Only move 30% of the time when far
                self._direct_move(dx, dy, game_map, player, all_enemies)

        self.move_cooldown = self.speed - 1


# Dictionary to map enemy types for spawning
ENEMY_TYPES = {
    'basic': Enemy,
    'fast': FastEnemy,
    'tank': TankEnemy,
    'sniper': SniperEnemy,
    'healer': HealerEnemy,
    'stealth': StealthEnemy
}
