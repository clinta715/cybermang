# Turn-Based Combat System with Status Effects - Design Summary

## Overview
This document summarizes the complete design for a turn-based combat system with status effects inspired by Dungeon Crawl. The system extends the existing combat mechanics in player.py and enemy.py, defines status effects with duration and stacking rules, includes combat actions, and specifies integration points with game.py for turn management.

## Key Components

### 1. Status Effects System
- **Defined Effects**: Poison, Paralysis, Blindness, Confusion, Haste, Slow, Regeneration, Strength, Weakness, Protection
- **Stacking Rules**: Duration-based stacking for effects like Paralysis, intensity-based stacking for effects like Poison
- **Implementation**: StatusEffect base class with specific implementations for each effect type
- **Integration**: Both Player and Enemy classes extended to handle status effects

### 2. Combat Actions
- **Core Actions**: Attack, Defend, Use Item, Cast Spell
- **Action System**: CombatAction base class with specific implementations
- **Resource Management**: Mana system for spell casting with cooldowns for abilities
- **Weapon Integration**: Weapons can apply status effects on hit

### 3. Turn Management
- **Turn Order**: Player acts first, followed by all enemies in sequence
- **State Management**: Clear state transitions between exploration and combat modes
- **Integration**: Modifications to game.py to handle turn-based combat flow

### 4. Combat UI
- **Layout**: Divided screen with player stats, turn order, combat log, and action menu
- **Visual Feedback**: Animations for damage, healing, status effects, and attacks
- **Targeting**: Visual reticle for target selection
- **Log System**: Comprehensive combat event logging with filtering and scrolling

### 5. Enemy AI
- **Behavior Types**: Aggressive, Defensive, Support, Spellcaster, Cowardly
- **Enemy-Specific AI**: Different AI implementations for each enemy type
- **Decision Making**: Context-aware action selection based on health, status effects, and combat situation
- **Group Coordination**: Enemies can coordinate actions in groups

### 6. Balancing and Tuning
- **Parameters**: Comprehensive set of parameters for player stats, enemy stats, status effects, actions, weapons, and difficulty
- **Scaling**: Dynamic difficulty adjustment based on player performance
- **Reward System**: Experience and loot calculations with drop chances

## Implementation Guidelines

### Player Extension
1. Add status_effects list to Player class
2. Implement apply_status_effect, remove_status_effect, and update_status_effects methods
3. Modify move() method to check for movement-affecting status effects
4. Modify take_damage() method to check for protection effects
5. Add mana system with regeneration

### Enemy Extension
1. Add status_effects list to Enemy base class
2. Implement apply_status_effect, remove_status_effect, and update_status_effects methods
3. Modify move_towards() method to check for movement-affecting status effects
4. Modify take_damage() method to check for protection effects
5. Ensure all enemy subclasses inherit status effect functionality

### Game Integration
1. Modify game.py to handle combat state transitions
2. Implement turn management system with clear player and enemy phases
3. Add input handling for combat actions
4. Integrate combat log system with UI
5. Add animation system for visual feedback

### UI Implementation
1. Create combat-specific UI layout
2. Implement action menu with keyboard navigation
3. Add targeting system with visual reticle
4. Create combat log display with scrolling and filtering
5. Add status effect indicators

## System Architecture

The combat system follows a modular architecture with clear separation of concerns:

```
Game Engine
├── Combat State Manager
│   ├── Turn Manager
│   ├── Combat Phase Controller
│   └── Combat Resolution
├── Entities
│   ├── Player Entity
│   └── Enemy Entities
├── UI System
├── Animation System
└── Log System
```

## Extensibility Features

### Adding New Status Effects
1. Create new StatusEffect subclass
2. Implement required methods (apply_effect, remove_effect, on_turn_start/end)
3. Add to entity's apply_status_effect method
4. Update UI to display new effect

### Adding New Combat Actions
1. Create new CombatAction subclass
2. Implement _perform_action method
3. Add to action selection system
4. Update UI to display new action

### Adding New Enemy Types
1. Create new Enemy subclass
2. Implement specific behavior and abilities
3. Add to enemy AI system
4. Configure stats and parameters

## Testing Considerations

### Unit Testing
- Status effect application and removal
- Combat action execution
- Damage and healing calculations
- AI decision making logic

### Integration Testing
- Combat system integration with game engine
- UI interaction with combat events
- Animation synchronization with actions
- Log system accuracy and completeness

### Playtesting
- Balance and difficulty tuning
- User experience and interface clarity
- Performance under various conditions
- Edge case handling and error recovery

## Conclusion

This design provides a comprehensive turn-based combat system with status effects that enhances the existing gameplay while maintaining compatibility with the current codebase. The modular architecture allows for easy extension and modification, and the detailed parameter system enables fine-tuned balancing.

The system includes all requested features:
1. Extension of existing combat mechanics in player.py and enemy.py
2. Status effects with duration and stacking rules
3. Combat actions (attack, defend, use item, cast spell)
4. Integration points with game.py for turn management

The design is ready for implementation in the code mode, with clear specifications for each component and how they interact.