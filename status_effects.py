#!/usr/bin/env python3
"""
Status Effects module for the combat system.
"""

import random

class StatusEffect:
    def __init__(self, name, duration, intensity=1.0):
        self.name = name
        self.base_duration = duration
        self.duration = duration
        self.intensity = intensity
        self.max_intensity = intensity * 3  # For intensity-based effects
        self.max_duration = duration * 2    # For duration-based effects
        self.applied = False  # Track if effect has been initially applied
    
    def apply_effect(self, entity):
        """Apply the effect to the entity when first added"""
        pass
    
    def remove_effect(self, entity):
        """Remove the effect from the entity when duration expires"""
        pass
    
    def on_turn_start(self, entity):
        """Called at the start of the entity's turn"""
        pass
    
    def on_turn_end(self, entity):
        """Called at the end of the entity's turn"""
        self.duration -= 1
        return self.duration <= 0  # Return True if effect should be removed
    
    def stack_effect(self, existing_effect):
        """Apply stacking rules when this effect is applied over an existing one"""
        # For duration-based effects, extend duration
        if self.name in ["Paralysis", "Blindness", "Confusion", "Haste", "Slow"]:
            duration_extension = self.base_duration * random.uniform(0.5, 1.0)
            existing_effect.duration = min(
                existing_effect.duration + duration_extension,
                existing_effect.max_duration
            )
        # For intensity-based effects, increase intensity
        elif self.name in ["Poison", "Regeneration", "Strength", "Weakness", "Protection"]:
            intensity_increase = self.intensity * random.uniform(0.5, 1.0)
            existing_effect.intensity = min(
                existing_effect.intensity + intensity_increase,
                existing_effect.max_intensity
            )
            # Reset duration to maximum of current and new
            existing_effect.duration = max(existing_effect.duration, self.base_duration)


class PoisonEffect(StatusEffect):
    def __init__(self, duration=3, intensity=1.0):
        super().__init__("Poison", duration, intensity)
    
    def apply_effect(self, entity):
        """Poison has no initial effect when applied"""
        pass
    
    def on_turn_start(self, entity):
        """Deal damage at the start of each turn"""
        # Calculate damage based on intensity
        damage = int(5 * self.intensity)
        # Apply damage (poison damage typically ignores protection)
        entity.take_damage(damage, ignore_protection=True)
        # Log the damage
        if hasattr(entity, 'combat_log'):
            entity.combat_log.append(f"{self.get_entity_name(entity)} takes {damage} poison damage!")
    
    def get_entity_name(self, entity):
        """Get display name for entity"""
        if hasattr(entity, 'name'):
            return entity.name
        elif hasattr(entity, '__class__'):
            return entity.__class__.__name__
        else:
            return "Entity"


class ParalysisEffect(StatusEffect):
    def __init__(self, duration=1):
        super().__init__("Paralysis", duration)
    
    def apply_effect(self, entity):
        """Mark the entity as paralyzed"""
        entity.paralyzed = True
        if hasattr(entity, 'combat_log'):
            entity.combat_log.append(f"{self.get_entity_name(entity)} is paralyzed!")
    
    def remove_effect(self, entity):
        """Remove paralysis"""
        entity.paralyzed = False
        if hasattr(entity, 'combat_log'):
            entity.combat_log.append(f"{self.get_entity_name(entity)} is no longer paralyzed!")
    
    def get_entity_name(self, entity):
        """Get display name for entity"""
        if hasattr(entity, 'name'):
            return entity.name
        elif hasattr(entity, '__class__'):
            return entity.__class__.__name__
        else:
            return "Entity"


class BlindnessEffect(StatusEffect):
    def __init__(self, duration=2):
        super().__init__("Blindness", duration)
    
    def apply_effect(self, entity):
        """Mark the entity as blinded"""
        entity.blinded = True
        if hasattr(entity, 'combat_log'):
            entity.combat_log.append(f"{self.get_entity_name(entity)} is blinded!")
    
    def remove_effect(self, entity):
        """Remove blindness"""
        entity.blinded = False
        if hasattr(entity, 'combat_log'):
            entity.combat_log.append(f"{self.get_entity_name(entity)} can see again!")
    
    def get_entity_name(self, entity):
        """Get display name for entity"""
        if hasattr(entity, 'name'):
            return entity.name
        elif hasattr(entity, '__class__'):
            return entity.__class__.__name__
        else:
            return "Entity"


class ConfusionEffect(StatusEffect):
    def __init__(self, duration=2):
        super().__init__("Confusion", duration)
    
    def apply_effect(self, entity):
        """Mark the entity as confused"""
        entity.confused = True
        if hasattr(entity, 'combat_log'):
            entity.combat_log.append(f"{self.get_entity_name(entity)} is confused!")
    
    def remove_effect(self, entity):
        """Remove confusion"""
        entity.confused = False
        if hasattr(entity, 'combat_log'):
            entity.combat_log.append(f"{self.get_entity_name(entity)} is no longer confused!")
    
    def get_entity_name(self, entity):
        """Get display name for entity"""
        if hasattr(entity, 'name'):
            return entity.name
        elif hasattr(entity, '__class__'):
            return entity.__class__.__name__
        else:
            return "Entity"


class HasteEffect(StatusEffect):
    def __init__(self, duration=3):
        super().__init__("Haste", duration)
    
    def apply_effect(self, entity):
        """Mark the entity as hasted"""
        entity.hasted = True
        if hasattr(entity, 'combat_log'):
            entity.combat_log.append(f"{self.get_entity_name(entity)} is hasted!")
    
    def remove_effect(self, entity):
        """Remove haste"""
        entity.hasted = False
        if hasattr(entity, 'combat_log'):
            entity.combat_log.append(f"{self.get_entity_name(entity)} is no longer hasted!")
    
    def get_entity_name(self, entity):
        """Get display name for entity"""
        if hasattr(entity, 'name'):
            return entity.name
        elif hasattr(entity, '__class__'):
            return entity.__class__.__name__
        else:
            return "Entity"


class SlowEffect(StatusEffect):
    def __init__(self, duration=3):
        super().__init__("Slow", duration)
    
    def apply_effect(self, entity):
        """Mark the entity as slowed"""
        entity.slowed = True
        if hasattr(entity, 'combat_log'):
            entity.combat_log.append(f"{self.get_entity_name(entity)} is slowed!")
    
    def remove_effect(self, entity):
        """Remove slow"""
        entity.slowed = False
        if hasattr(entity, 'combat_log'):
            entity.combat_log.append(f"{self.get_entity_name(entity)} is no longer slowed!")
    
    def get_entity_name(self, entity):
        """Get display name for entity"""
        if hasattr(entity, 'name'):
            return entity.name
        elif hasattr(entity, '__class__'):
            return entity.__class__.__name__
        else:
            return "Entity"


class RegenerationEffect(StatusEffect):
    def __init__(self, duration=3, intensity=1.0):
        super().__init__("Regeneration", duration, intensity)
    
    def on_turn_start(self, entity):
        """Heal at the start of each turn"""
        # Calculate healing based on intensity
        healing = int(3 * self.intensity)
        # Apply healing
        entity.health = min(getattr(entity, 'max_health', entity.health), entity.health + healing)
        # Log the healing
        if hasattr(entity, 'combat_log'):
            entity.combat_log.append(f"{self.get_entity_name(entity)} regenerates {healing} HP!")
    
    def get_entity_name(self, entity):
        """Get display name for entity"""
        if hasattr(entity, 'name'):
            return entity.name
        elif hasattr(entity, '__class__'):
            return entity.__class__.__name__
        else:
            return "Entity"


class StrengthEffect(StatusEffect):
    def __init__(self, duration=2, intensity=1.0):
        super().__init__("Strength", duration, intensity)
    
    def apply_effect(self, entity):
        """Mark the entity as strengthened"""
        entity.strengthened = True
        if hasattr(entity, 'combat_log'):
            entity.combat_log.append(f"{self.get_entity_name(entity)} is strengthened!")
    
    def remove_effect(self, entity):
        """Remove strength"""
        entity.strengthened = False
        if hasattr(entity, 'combat_log'):
            entity.combat_log.append(f"{self.get_entity_name(entity)} is no longer strengthened!")
    
    def get_entity_name(self, entity):
        """Get display name for entity"""
        if hasattr(entity, 'name'):
            return entity.name
        elif hasattr(entity, '__class__'):
            return entity.__class__.__name__
        else:
            return "Entity"


class WeaknessEffect(StatusEffect):
    def __init__(self, duration=2, intensity=1.0):
        super().__init__("Weakness", duration, intensity)
    
    def apply_effect(self, entity):
        """Mark the entity as weakened"""
        entity.weakened = True
        if hasattr(entity, 'combat_log'):
            entity.combat_log.append(f"{self.get_entity_name(entity)} is weakened!")
    
    def remove_effect(self, entity):
        """Remove weakness"""
        entity.weakened = False
        if hasattr(entity, 'combat_log'):
            entity.combat_log.append(f"{self.get_entity_name(entity)} is no longer weakened!")
    
    def get_entity_name(self, entity):
        """Get display name for entity"""
        if hasattr(entity, 'name'):
            return entity.name
        elif hasattr(entity, '__class__'):
            return entity.__class__.__name__
        else:
            return "Entity"


class ProtectionEffect(StatusEffect):
    def __init__(self, duration=2, intensity=1.0):
        super().__init__("Protection", duration, intensity)
    
    def apply_effect(self, entity):
        """Mark the entity as protected"""
        entity.protected = True
        if hasattr(entity, 'combat_log'):
            entity.combat_log.append(f"{self.get_entity_name(entity)} is protected!")
    
    def remove_effect(self, entity):
        """Remove protection"""
        entity.protected = False
        if hasattr(entity, 'combat_log'):
            entity.combat_log.append(f"{self.get_entity_name(entity)} is no longer protected!")
    
    def get_entity_name(self, entity):
        """Get display name for entity"""
        if hasattr(entity, 'name'):
            return entity.name
        elif hasattr(entity, '__class__'):
            return entity.__class__.__name__
        else:
            return "Entity"


def apply_status_effect_to_entity(entity, effect):
    """Apply a status effect to an entity with full logic"""
    # Validate entity and effect
    if not entity or not effect:
        return False
    
    # Check for immunity or resistance
    if hasattr(entity, 'is_immune_to') and entity.is_immune_to(effect.name):
        if hasattr(entity, 'combat_log'):
            entity.combat_log.append(f"{entity.get_entity_name()} is immune to {effect.name}!")
        return False
    
    # Apply the effect
    entity.apply_status_effect(effect)
    return True


def apply_status_effect_from_attack(attacker, defender, effect_class, base_duration, base_intensity):
    """Apply a status effect from an attack with potential modifiers"""
    # Calculate modified duration and intensity based on attacker's stats
    modified_duration = base_duration
    modified_intensity = base_intensity
    
    # Apply attacker's strength modifier if applicable
    if attacker.has_status_effect("Strength"):
        for effect in attacker.status_effects:
            if effect.name == "Strength":
                modified_intensity *= (1 + 0.1 * effect.intensity)
                break
    
    # Apply defender's resistance if applicable
    # This would depend on the specific implementation
    
    # Create and apply effect
    effect = effect_class(duration=int(modified_duration), intensity=modified_intensity)
    return apply_status_effect_to_entity(defender, effect)


def remove_status_effect_from_entity(entity, effect_name):
    """Remove a status effect from an entity"""
    # Validate entity and effect name
    if not entity or not effect_name:
        return False
    
    # Remove the effect
    result = entity.remove_status_effect(effect_name)
    
    # Log the removal if successful
    if result and hasattr(entity, 'combat_log'):
        entity.combat_log.append(f"{entity.get_entity_name()} is no longer affected by {effect_name}!")
    
    return result


def remove_all_status_effects_from_entity(entity):
    """Remove all status effects from an entity"""
    # Validate entity
    if not entity:
        return False
    
    # Remove all effects
    count = len(entity.status_effects)
    entity.clear_all_status_effects()
    
    # Log the removal
    if count > 0 and hasattr(entity, 'combat_log'):
        entity.combat_log.append(f"All status effects removed from {entity.get_entity_name()}!")
    
    return count > 0