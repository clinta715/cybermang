# Status Effects System Design

## Overview
This document defines the status effects system for the turn-based combat system. Status effects are temporary conditions that affect entities (players and enemies) during combat.

## Status Effect Types

### 1. Poison
- **Effect**: Deals damage over time
- **Duration**: 3-5 turns
- **Stacking**: Intensity stacks (damage per turn increases), duration resets to maximum
- **Damage**: 5-10 HP per turn

### 2. Paralysis
- **Effect**: Prevents taking actions
- **Duration**: 1-3 turns
- **Stacking**: Duration extends
- **Special**: Immobilizes the target completely

### 3. Blindness
- **Effect**: Reduces accuracy of attacks
- **Duration**: 2-4 turns
- **Stacking**: Duration extends
- **Accuracy Reduction**: 50% reduction in hit chance

### 4. Confusion
- **Effect**: Randomizes movement and attack directions
- **Duration**: 2-3 turns
- **Stacking**: Duration extends
- **Special**: 50% chance to act in a random direction

### 5. Haste
- **Effect**: Increases action speed
- **Duration**: 3-5 turns
- **Stacking**: Duration extends
- **Special**: Allows an extra action per turn

### 6. Slow
- **Effect**: Decreases action speed
- **Duration**: 3-5 turns
- **Stacking**: Duration extends
- **Special**: Skips every other turn

### 7. Regeneration
- **Effect**: Heals over time
- **Duration**: 3-6 turns
- **Stacking**: Intensity stacks (healing per turn increases), duration resets to maximum
- **Healing**: 3-8 HP per turn

### 8. Strength
- **Effect**: Increases damage dealt
- **Duration**: 2-4 turns
- **Stacking**: Intensity stacks (damage bonus increases), duration resets to maximum
- **Damage Bonus**: 10-20% increase

### 9. Weakness
- **Effect**: Decreases damage dealt
- **Duration**: 2-4 turns
- **Stacking**: Intensity stacks (damage penalty increases), duration resets to maximum
- **Damage Penalty**: 10-20% decrease

### 10. Protection
- **Effect**: Reduces damage taken
- **Duration**: 2-4 turns
- **Stacking**: Intensity stacks (damage reduction increases), duration resets to maximum
- **Damage Reduction**: 10-25% reduction

## Stacking Rules

### Duration-Based Stacking
For effects like Paralysis, Blindness, Confusion, Haste, and Slow:
- Applying the same effect again extends the duration
- The duration is extended by 50-100% of the new effect's base duration
- Maximum duration is capped at 2x the base maximum duration

### Intensity-Based Stacking
For effects like Poison, Regeneration, Strength, Weakness, and Protection:
- Applying the same effect again increases the intensity
- The intensity is increased by 50-100% of the new effect's base intensity
- Duration is reset to the maximum of the current duration and the new effect's base duration
- Maximum intensity is capped at 3x the base maximum intensity

### No Stacking
Some effects may not stack at all:
- If the effect is already applied, the new application is ignored
- This is used for effects that are either on or off with no gradation

## Implementation Details

### StatusEffect Base Class
```python
class StatusEffect:
    def __init__(self, name, duration, intensity=1.0):
        self.name = name
        self.base_duration = duration
        self.duration = duration
        self.intensity = intensity
        self.max_intensity = intensity * 3  # For intensity-based effects
        self.max_duration = duration * 2    # For duration-based effects
    
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

### Effect Application Process
1. Check if the effect already exists on the entity
2. If it exists, apply stacking rules
3. If it doesn't exist, add the new effect
4. Apply the effect immediately upon application

### Effect Removal Process
1. Call `on_turn_end()` for each effect
2. If `on_turn_end()` returns True, remove the effect
3. Call `remove_effect()` when removing the effect