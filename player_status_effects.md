# Player Status Effects Extension Design

## Overview
This document describes how to extend the Player class in player.py to handle status effects as defined in status_effects.md.

## Requirements
1. Players must be able to have multiple status effects applied simultaneously
2. Status effects must be updated each turn
3. Status effects must be able to modify player behavior (damage, movement, actions, etc.)
4. Status effects must follow the stacking rules defined in status_effects.md

## Design

### Player Class Extension
The Player class will be extended with the following attributes and methods:

#### New Attributes
- `status_effects`: A list of active StatusEffect instances
- `is_in_combat`: A boolean indicating if the player is currently in combat

#### New Methods
- `apply_status_effect(effect)`: Apply a status effect to the player
- `remove_status_effect(effect_name)`: Remove a specific status effect by name
- `clear_all_status_effects()`: Remove all status effects
- `update_status_effects()`: Update all status effects at the start of the player's turn
- `get_active_effects()`: Return a list of all active status effect names
- `has_status_effect(effect_name)`: Check if a specific effect is active

### Status Effect Integration Points

#### Movement
- Modify the `move()` method to check for effects that affect movement (Paralysis, Slow, Confusion)
- Apply terrain effects after status effect modifications

#### Combat Actions
- Modify combat-related methods to check for effects that affect combat (Blindness, Weakness, Strength)
- Apply status effects before and after combat actions

#### Damage Calculation
- Modify `take_damage()` to check for effects that modify damage taken (Protection)
- Add methods for calculating damage output with Strength/Weakness effects

#### Turn Management
- Add a method `on_turn_start()` that is called at the beginning of each turn
- Add a method `on_turn_end()` that is called at the end of each turn

## Implementation Plan

### 1. Status Effect Base Class
First, we need to create a base StatusEffect class that all specific effects will inherit from:

```python
class StatusEffect:
    def __init__(self, name, duration, intensity=1.0):
        self.name = name
        self.base_duration = duration
        self.duration = duration
        self.intensity = intensity
        self.max_intensity = intensity * 3
        self.max_duration = duration * 2
    
    def apply_effect(self, entity):
        """Apply the effect to the entity"""
        pass
    
    def remove_effect(self, entity):
        """Remove the effect from the entity"""
        pass
    
    def on_turn_start(self, entity):
        """Called at the start of the entity's turn"""
        pass
    
    def on_turn_end(self, entity):
        """Called at the end of the entity's turn"""
        self.duration -= 1
        return self.duration <= 0  # Return True if effect should be removed
```

### 2. Specific Status Effect Classes
We'll need to implement specific classes for each status effect type:

```python
class PoisonEffect(StatusEffect):
    def __init__(self, duration=3, intensity=1.0):
        super().__init__("Poison", duration, intensity)
    
    def on_turn_start(self, entity):
        # Apply damage based on intensity
        damage = int(5 * self.intensity)
        entity.take_damage(damage, ignore_protection=True)  # Poison damage ignores protection
        # Call parent implementation to handle duration
        return super().on_turn_end(entity)

class ParalysisEffect(StatusEffect):
    def __init__(self, duration=1):
        super().__init__("Paralysis", duration)
    
    def apply_effect(self, entity):
        # Mark the entity as paralyzed
        entity.paralyzed = True
    
    def remove_effect(self, entity):
        # Remove paralysis
        entity.paralyzed = False

# ... other effect classes ...
```

### 3. Player Class Modifications
The Player class will be modified to include status effect handling:

```python
class Player:
    def __init__(self, x, y, health=100):
        self.x = x
        self.y = y
        self.health = health
        self.max_health = health
        self.status_effects = []
        self.paralyzed = False  # For paralysis effect
        # ... other existing attributes ...
    
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
            self._stack_status_effect(existing_effect, effect)
        else:
            # Add new effect
            self.status_effects.append(effect)
            effect.apply_effect(self)
    
    def _stack_status_effect(self, existing_effect, new_effect):
        """Apply stacking rules for status effects"""
        # For duration-based effects, extend duration
        if new_effect.name in ["Paralysis", "Blindness", "Confusion", "Haste", "Slow"]:
            duration_extension = new_effect.base_duration * random.uniform(0.5, 1.0)
            existing_effect.duration = min(
                existing_effect.duration + duration_extension,
                existing_effect.max_duration
            )
        # For intensity-based effects, increase intensity
        elif new_effect.name in ["Poison", "Regeneration", "Strength", "Weakness", "Protection"]:
            intensity_increase = new_effect.intensity * random.uniform(0.5, 1.0)
            existing_effect.intensity = min(
                existing_effect.intensity + intensity_increase,
                existing_effect.max_intensity
            )
            # Reset duration to maximum of current and new
            existing_effect.duration = max(existing_effect.duration, new_effect.base_duration)
    
    def remove_status_effect(self, effect_name):
        """Remove a specific status effect by name"""
        for effect in self.status_effects[:]:  # Use slice copy to avoid modification during iteration
            if effect.name == effect_name:
                effect.remove_effect(self)
                self.status_effects.remove(effect)
                return True
        return False
    
    def update_status_effects(self):
        """Update all status effects at the start of the player's turn"""
        for effect in self.status_effects[:]:  # Use slice copy to avoid modification during iteration
            if effect.on_turn_end(self):
                effect.remove_effect(self)
                self.status_effects.remove(effect)
    
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
        """Check if the player can perform actions (not paralyzed or slowed)"""
        # Check for paralysis
        if self.paralyzed:
            return False
        
        # Check for slow effect (50% chance to skip turn)
        if self.has_status_effect("Slow") and random.random() < 0.5:
            return False
        
        return True
    
    # Modified existing methods
    def move(self, dx, dy, game_map, weapons, enemies=None):
        """Move the player if possible, considering terrain and enemy collisions."""
        # Check if player can act
        if not self.can_act():
            return False
        
        # Check for confusion effect
        if self.has_status_effect("Confusion") and random.random() < 0.5:
            # Randomize direction
            dx = random.choice([-1, 0, 1])
            dy = random.choice([-1, 0, 1])
        
        # ... rest of existing move logic ...
    
    def take_damage(self, damage):
        """Reduce player health, considering protection effects."""
        # Apply protection effect if active
        if self.has_status_effect("Protection"):
            # Find the protection effect
            for effect in self.status_effects:
                if effect.name == "Protection":
                    damage = int(damage * (1 - 0.1 * effect.intensity))  # 10-30% damage reduction
                    break
        
        self.health -= damage
        if self.health < 0:
            self.health = 0
```

## Integration Points

### With Game Loop
The game loop in game.py will need to be modified to call the player's turn start/end methods:

```python
# In the game loop, when it's the player's turn:
player.on_turn_start()
# ... player actions ...
player.on_turn_end()
```

### With UI
The UI will need to display active status effects. This can be added to the status bar or as a separate display element.

## Testing Considerations
1. Test applying multiple status effects simultaneously
2. Test stacking rules for both duration-based and intensity-based effects
3. Test that effects properly modify player behavior
4. Test that effects are removed when their duration expires
5. Test edge cases like applying the same effect multiple times in one turn