#!/usr/bin/env python3
"""
Combat Actions module for the turn-based combat system.
"""

from status_effects import *

class CombatAction:
    def __init__(self, name, description, mana_cost=0, cooldown=0):
        self.name = name
        self.description = description
        self.mana_cost = mana_cost
        self.cooldown = cooldown
        self.current_cooldown = 0
    
    def can_execute(self, entity):
        """Check if the entity can execute this action"""
        # Check mana cost
        if hasattr(entity, 'mana') and entity.mana < self.mana_cost:
            return False
        
        # Check cooldown
        if self.current_cooldown > 0:
            return False
        
        return True
    
    def execute(self, entity, target=None, game_state=None):
        """Execute the action"""
        # Pay mana cost
        if hasattr(entity, 'mana'):
            entity.mana -= self.mana_cost
        
        # Set cooldown
        self.current_cooldown = self.cooldown
        
        # Execute specific action logic
        return self._perform_action(entity, target, game_state)
    
    def _perform_action(self, entity, target, game_state):
        """Override this method to implement specific action logic"""
        pass
    
    def update_cooldown(self):
        """Update cooldown at the end of turn"""
        if self.current_cooldown > 0:
            self.current_cooldown -= 1


class AttackAction(CombatAction):
    def __init__(self):
        super().__init__("Attack", "Deal damage to an enemy with your weapon")
    
    def _perform_action(self, entity, target, game_state):
        # For player, this would use the current weapon
        if hasattr(entity, 'weapon'):  # Player with weapon
            # Player attack logic using current weapon
            damage = entity.weapon.damage
            
            # Apply strength/weakness effects
            if entity.has_status_effect("Strength"):
                for effect in entity.status_effects:
                    if effect.name == "Strength":
                        damage = int(damage * (1 + 0.1 * effect.intensity))
                        break
            if entity.has_status_effect("Weakness"):
                for effect in entity.status_effects:
                    if effect.name == "Weakness":
                        damage = int(damage * (1 - 0.1 * effect.intensity))
                        break
            
            target.take_damage(damage)
            return f"{entity.get_entity_name()} attacks for {damage} damage!"
        # For enemy, this would deal direct damage
        elif hasattr(entity, '__class__') and 'Enemy' in entity.__class__.__name__:
            # Enemy attack logic
            if target:
                # Calculate damage with strength/weakness effects
                base_damage = 10  # Base enemy damage
                if entity.has_status_effect("Strength"):
                    for effect in entity.status_effects:
                        if effect.name == "Strength":
                            base_damage = int(base_damage * (1 + 0.1 * effect.intensity))
                            break
                if entity.has_status_effect("Weakness"):
                    for effect in entity.status_effects:
                        if effect.name == "Weakness":
                            base_damage = int(base_damage * (1 - 0.1 * effect.intensity))
                            break
                
                target.take_damage(base_damage)
                return f"{entity.get_entity_name()} attacks for {base_damage} damage!"
        
        return "Attack performed"


class DefendAction(CombatAction):
    def __init__(self):
        super().__init__("Defend", "Reduce damage taken for 2 turns", cooldown=3)
    
    def _perform_action(self, entity, target, game_state):
        # Apply defense effect
        defense_effect = ProtectionEffect(duration=2, intensity=2.0)  # 20% damage reduction
        entity.apply_status_effect(defense_effect)
        return f"{entity.get_entity_name()} takes a defensive stance!"


class UseItemAction(CombatAction):
    def __init__(self, item_type):
        self.item_type = item_type
        if item_type == "health_potion":
            super().__init__("Use Health Potion", "Restore 30 HP")
        elif item_type == "mana_potion":
            super().__init__("Use Mana Potion", "Restore 20 MP")
        elif item_type == "antidote":
            super().__init__("Use Antidote", "Remove Poison effect")
        # ... other items
    
    def _perform_action(self, entity, target, game_state):
        if self.item_type == "health_potion":
            entity.health = min(entity.max_health, entity.health + 30)
            return f"{entity.get_entity_name()} restored 30 HP!"
        elif self.item_type == "mana_potion":
            if hasattr(entity, 'mana') and hasattr(entity, 'max_mana'):
                entity.mana = min(entity.max_mana, entity.mana + 20)
            return f"{entity.get_entity_name()} restored 20 MP!"
        elif self.item_type == "antidote":
            entity.remove_status_effect("Poison")
            return f"{entity.get_entity_name()} cured poison!"
        # ... other items


class CastSpellAction(CombatAction):
    def __init__(self, spell_name):
        self.spell_name = spell_name
        if spell_name == "fireball":
            super().__init__("Fireball", "Deal area damage", mana_cost=15, cooldown=2)
        elif spell_name == "heal":
            super().__init__("Heal", "Restore HP", mana_cost=10, cooldown=1)
        elif spell_name == "paralyze":
            super().__init__("Paralyze", "Paralyze an enemy", mana_cost=20, cooldown=3)
        # ... other spells
    
    def _perform_action(self, entity, target, game_state):
        if self.spell_name == "fireball":
            # Deal area damage around target
            damage = 25
            # Apply to target and nearby enemies
            if target:
                target.take_damage(damage)
                # Also damage nearby enemies
                # ... logic to find nearby enemies
            return f"{entity.get_entity_name()} casts Fireball for {damage} damage!"
        elif self.spell_name == "heal":
            # Heal target (could be self or ally)
            heal_amount = 30
            if target:
                target.health = min(getattr(target, 'max_health', target.health), target.health + heal_amount)
            else:
                entity.health = min(entity.max_health, entity.health + heal_amount)
            return f"{entity.get_entity_name()} casts Heal and restores {heal_amount} HP!"
        elif self.spell_name == "paralyze":
            # Apply paralysis to target
            if target:
                paralysis = ParalysisEffect(duration=2)
                target.apply_status_effect(paralysis)
            return f"{entity.get_entity_name()} casts Paralyze!"
        # ... other spells