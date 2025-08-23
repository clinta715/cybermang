# Status Effect Application and Removal Logic Design

## Overview
This document describes the implementation details for applying and removing status effects in the combat system. It covers the core logic for effect application, stacking rules, duration management, and effect execution.

## Core Status Effect Classes

### Base StatusEffect Class
```python
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
```

### Specific Status Effect Implementations

#### PoisonEffect
```python
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
```

#### ParalysisEffect
```python
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
```

#### BlindnessEffect
```python
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
```

#### ConfusionEffect
```python
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
```

#### HasteEffect
```python
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
```

#### SlowEffect
```python
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
```

#### RegenerationEffect
```python
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
```

#### StrengthEffect
```python
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
```

#### WeaknessEffect
```python
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
```

#### ProtectionEffect
```python
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
```

## Entity Integration

### Entity Base Class Extensions
Entities (Player and Enemy) need to be extended to handle status effects:

```python
class EntityWithStatusEffects:
    def __init__(self):
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
    
    def apply_status_effect(self, effect):
        """Apply a status effect to the entity"""
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
        """Update all status effects at the start of the entity's turn"""
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
        """Check if the entity can perform actions"""
        # Check for paralysis
        if self.paralyzed:
            return False
        
        # Check for slow effect (50% chance to skip turn)
        if self.slowed and random.random() < 0.5:
            return False
        
        return True
    
    def get_entity_name(self):
        """Get display name for entity"""
        if hasattr(self, 'name'):
            return self.name
        elif hasattr(self, '__class__'):
            return self.__class__.__name__
        else:
            return "Entity"
```

## Application Logic

### Effect Application Process
```python
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
```

### Effect Removal Process
```python
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
```

## Integration with Combat Systems

### Weapon Integration
Weapons can apply status effects on hit:

```python
class WeaponWithStatusEffects:
    def __init__(self, name, damage, range, ammo_capacity=100, fire_rate=1):
        self.name = name
        self.damage = damage
        self.range = range
        self.ammo_capacity = ammo_capacity
        self.ammo = ammo_capacity
        self.fire_rate = fire_rate
        self.last_shot_time = 0
        # Status effects that can be applied by this weapon
        self.status_effects = []  # List of (effect_class, chance, duration, intensity) tuples
    
    def add_status_effect(self, effect_class, chance, duration, intensity=1.0):
        """Add a status effect that this weapon can apply"""
        self.status_effects.append((effect_class, chance, duration, intensity))
    
    def apply_weapon_status_effects(self, attacker, defender):
        """Apply any status effects from this weapon"""
        for effect_class, chance, duration, intensity in self.status_effects:
            if random.random() < chance:
                apply_status_effect_from_attack(attacker, defender, effect_class, duration, intensity)
```

### Spell Integration
Spells can also apply status effects:

```python
class SpellWithStatusEffects:
    def __init__(self, name, mana_cost, description):
        self.name = name
        self.mana_cost = mana_cost
        self.description = description
        # Status effects that can be applied by this spell
        self.status_effects = []  # List of (effect_class, chance, duration, intensity) tuples
    
    def add_status_effect(self, effect_class, chance, duration, intensity=1.0):
        """Add a status effect that this spell can apply"""
        self.status_effects.append((effect_class, chance, duration, intensity))
    
    def apply_spell_status_effects(self, caster, target):
        """Apply any status effects from this spell"""
        for effect_class, chance, duration, intensity in self.status_effects:
            if random.random() < chance:
                apply_status_effect_from_attack(caster, target, effect_class, duration, intensity)
```

## Testing Considerations

### Unit Tests
1. Test effect application and removal
2. Test stacking rules for all effect types
3. Test duration management
4. Test effect interactions (e.g., Protection reducing Poison damage)
5. Test entity behavior modifications
6. Test edge cases (applying same effect multiple times)

### Integration Tests
1. Test weapon-based status effect application
2. Test spell-based status effect application
3. Test combat log entries for status effects
4. Test UI updates when status effects are applied/removed
5. Test turn-based effect execution
6. Test combat end conditions with status effects active

### Performance Tests
1. Test with many status effects active
2. Test effect application/removal performance
3. Test memory usage with many effects
4. Test UI rendering with many status effects