# Enemy Status Effects Extension Design

## Overview
This document describes how to extend the Enemy class in enemy.py to handle status effects, similar to the Player class extension.

## Requirements
1. Enemies must be able to have multiple status effects applied simultaneously
2. Status effects must be updated each turn
3. Status effects must be able to modify enemy behavior (damage, movement, actions, etc.)
4. Status effects must follow the stacking rules defined in status_effects.md
5. All enemy subclasses (FastEnemy, TankEnemy, etc.) must support status effects

## Design

### Enemy Class Extension
The Enemy class will be extended with the following attributes and methods:

#### New Attributes
- `status_effects`: A list of active StatusEffect instances
- `paralyzed`: A boolean indicating if the enemy is paralyzed

#### New Methods
- `apply_status_effect(effect)`: Apply a status effect to the enemy
- `remove_status_effect(effect_name)`: Remove a specific status effect by name
- `clear_all_status_effects()`: Remove all status effects
- `update_status_effects()`: Update all status effects at the start of the enemy's turn
- `get_active_effects()`: Return a list of all active status effect names
- `has_status_effect(effect_name)`: Check if a specific effect is active
- `can_act()`: Check if the enemy can perform actions
- `on_turn_start()`: Called at the beginning of each turn
- `on_turn_end()`: Called at the end of each turn

### Status Effect Integration Points

#### Movement
- Modify the `move_towards()` method to check for effects that affect movement (Paralysis, Slow, Confusion)
- Apply terrain effects after status effect modifications

#### Combat Actions
- Modify combat-related methods to check for effects that affect combat (Blindness, Weakness, Strength)
- Apply status effects before and after combat actions

#### Damage Calculation
- Modify `take_damage()` to check for effects that modify damage taken (Protection)
- Add methods for calculating damage output with Strength/Weakness effects

#### AI Decision Making
- Modify AI methods to account for status effects when making decisions

## Implementation Plan

### 1. Enemy Base Class Modifications
The Enemy base class will be modified to include status effect handling:

```python
class Enemy:
    def __init__(self, x, y, health=50):
        self.x = x
        self.y = y
        self.health = health
        self.move_cooldown = 0
        self.strategy = random.choice(['direct', 'flanking', 'circling'])
        self.status_effects = []
        self.paralyzed = False  # For paralysis effect
    
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
        """Update all status effects at the start of the enemy's turn"""
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
        """Check if the enemy can perform actions (not paralyzed or slowed)"""
        # Check for paralysis
        if self.paralyzed:
            return False
        
        # Check for slow effect (50% chance to skip turn)
        if self.has_status_effect("Slow") and random.random() < 0.5:
            return False
        
        return True
    
    # Modified existing methods
    def move_towards(self, target_x, target_y, game_map, player, all_enemies=None):
        """Improved pathfinding with strategic movement patterns and status effects."""
        # Check if enemy can act
        if not self.can_act():
            return
        
        # Existing cooldown logic
        if self.move_cooldown > 0:
            self.move_cooldown -= 1
            return
        
        # Check for confusion effect
        if self.has_status_effect("Confusion") and random.random() < 0.5:
            # Randomize target position
            target_x = self.x + random.choice([-5, -5, 0, 5, 5])
            target_y = self.y + random.choice([-5, -5, 0, 5, 5])
        
        # ... rest of existing move_towards logic ...
    
    def take_damage(self, damage):
        """Reduce enemy health, considering protection effects."""
        # Apply protection effect if active
        if self.has_status_effect("Protection"):
            # Find the protection effect
            for effect in self.status_effects:
                if effect.name == "Protection":
                    damage = int(damage * (1 - 0.1 * effect.intensity))  # 10-30% damage reduction
                    break
        
        self.health -= damage
```

### 2. Enemy Subclass Considerations
All enemy subclasses will inherit the status effect functionality from the base Enemy class. However, some subclasses may need specific modifications:

```python
class FastEnemy(Enemy):
    def move_towards(self, target_x, target_y, game_map, player, all_enemies=None):
        """Fast movement - moves every other turn, with status effect considerations."""
        # Check if enemy can act (inherited from base class)
        if not self.can_act():
            return
        
        # Existing cooldown logic
        if self.move_cooldown > 0:
            self.move_cooldown -= 1
            return
        
        # ... rest of existing logic ...

class TankEnemy(Enemy):
    def move_towards(self, target_x, target_y, game_map, player, all_enemies=None):
        """Slow but deliberate movement, with status effect considerations."""
        # Check if enemy can act (inherited from base class)
        if not self.can_act():
            return
        
        # Existing cooldown logic
        if self.move_cooldown > 0:
            self.move_cooldown -= 1
            return
        
        # ... rest of existing logic ...

# Similar modifications for other subclasses...
```

## Integration Points

### With Game Loop
The game loop in game.py will need to be modified to call the enemy's turn start/end methods:

```python
# In the enemy update loop:
for enemy in enemies:
    enemy.on_turn_start()
    # ... enemy actions ...
    enemy.on_turn_end()
```

### With Player Combat
When the player attacks enemies, status effects can be applied:

```python
# In player attack logic:
if attack_hits:
    # Apply status effects based on weapon or player abilities
    if random.random() < 0.2:  # 20% chance to apply poison
        enemy.apply_status_effect(PoisonEffect(duration=3, intensity=1.0))
```

## Testing Considerations
1. Test applying multiple status effects to different enemy types
2. Test that all enemy subclasses properly handle status effects
3. Test stacking rules for both duration-based and intensity-based effects
4. Test that effects properly modify enemy behavior
5. Test that effects are removed when their duration expires
6. Test enemy AI behavior under various status effects
7. Test edge cases like applying the same effect multiple times in one turn