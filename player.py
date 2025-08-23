#!/usr/bin/env python3
"""
Player module for handling player character logic.
"""

from status_effects import *
from combat_actions import *

class Player:
    def __init__(self, x, y, health=100):
        self.x = x
        self.y = y
        self.health = health
        self.max_health = health
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
        # Combat action attributes
        self.mana = 50
        self.max_mana = 50
        self.mana_regeneration = 5
        # Combat actions
        self.actions = [
            AttackAction(),
            DefendAction(),
            UseItemAction("health_potion"),
            CastSpellAction("fireball"),
            CastSpellAction("heal")
        ]
        # Weapon for attacks
        self.weapon = None

    def move(self, dx, dy, game_map, weapons, enemies=None):
        """Move the player if possible, considering terrain and enemy collisions."""
        # Check if player can act (affected by status effects)
        if not self.can_act():
            return False
            
        new_x = self.x + dx
        new_y = self.y + dy

        # Check for terrain collision
        if game_map.is_blocked(new_x, new_y):
            return False

        # Check for enemy collision
        if enemies:
            for enemy in enemies:
                if enemy.x == new_x and enemy.y == new_y:
                    return False  # Can't move into enemy

        # Check for damaging terrain
        terrain_damage = game_map.get_terrain_damage(new_x, new_y)
        if terrain_damage > 0:
            self.take_damage(terrain_damage)

        terrain_effect = game_map.get_terrain_effect(new_x, new_y)
        # Apply terrain movement speed effect
        self.x = new_x
        self.y = new_y

        # Check for item collection
        item = game_map.collect_item(self.x, self.y)
        if item == 'H':  # Health pickup
            self.health = min(self.max_health, self.health + 20)
        elif item == 'A':  # Ammo pickup
            for weapon in weapons:
                weapon.reload(10)  # Add 10 ammo to each weapon
        elif item == 'P':  # Power-up
            self.health = min(self.max_health, self.health + 10)
            for weapon in weapons:
                weapon.reload(5)  # Add 5 ammo to each weapon

        return True

    def take_damage(self, damage, ignore_protection=False):
        """Reduce player health, considering protection status effect."""
        # Apply protection effect if active and not ignoring protection
        if self.protected and not ignore_protection:
            # Reduce damage by 30%
            damage = int(damage * 0.7)
            
        self.health -= damage
        if self.health < 0:
            self.health = 0

    def apply_status_effect(self, effect):
        """Apply a status effect to the player"""
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
        """Update all status effects at the start of the player's turn"""
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
        # Regenerate mana
        self.mana = min(self.max_mana, self.mana + self.mana_regeneration)
        
        for effect in self.status_effects:
            effect.on_turn_start(self)

    def on_turn_end(self):
        """Called at the end of each turn"""
        self.update_status_effects()

    def can_act(self):
        """Check if the player can perform actions"""
        # Check for paralysis
        if self.paralyzed:
            return False
        
        # Check for slow effect (50% chance to skip turn)
        if self.slowed and random.random() < 0.5:
            return False
        
        return True

    def get_entity_name(self):
        """Get display name for player"""
        return "Player"