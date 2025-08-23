# Combat State Management System Design

## Overview
This document describes the combat state management system, which handles the transition between exploration and combat modes, manages combat-specific data, and coordinates the various combat systems.

## Requirements
1. Clear distinction between exploration and combat states
2. Proper initialization and cleanup of combat state
3. Management of combat-specific data (turn order, combat log, etc.)
4. Integration with existing game systems
5. Smooth transitions between states

## Design

### Combat States
The system will define several combat states:

1. **Exploration**: Normal gameplay mode
2. **Combat_Init**: Transitioning from exploration to combat
3. **Combat_Active**: Active turn-based combat
4. **Combat_Resolution**: Resolving combat outcomes
5. **Combat_Exit**: Transitioning from combat to exploration

### State Machine Design
```python
class CombatState(Enum):
    EXPLORATION = 1
    COMBAT_INIT = 2
    COMBAT_ACTIVE = 3
    COMBAT_RESOLUTION = 4
    COMBAT_EXIT = 5

class CombatStateManager:
    def __init__(self, game):
        self.game = game
        self.state = CombatState.EXPLORATION
        self.turn_order = []
        self.current_turn_index = 0
        self.combat_log = []
        self.selected_action = None
        self.selected_target = None
        self.valid_targets = []
        self.round_count = 0
    
    def update(self):
        """Update based on current state"""
        if self.state == CombatState.EXPLORATION:
            self.update_exploration()
        elif self.state == CombatState.COMBAT_INIT:
            self.update_combat_init()
        elif self.state == CombatState.COMBAT_ACTIVE:
            self.update_combat_active()
        elif self.state == CombatState.COMBAT_RESOLUTION:
            self.update_combat_resolution()
        elif self.state == CombatState.COMBAT_EXIT:
            self.update_combat_exit()
    
    def change_state(self, new_state):
        """Change to a new combat state"""
        # Handle exit logic for current state
        self.exit_state(self.state)
        
        # Change state
        old_state = self.state
        self.state = new_state
        
        # Handle entry logic for new state
        self.enter_state(new_state, old_state)
    
    def enter_state(self, new_state, old_state):
        """Handle entry logic for a state"""
        if new_state == CombatState.COMBAT_INIT:
            self.enter_combat_init()
        elif new_state == CombatState.COMBAT_ACTIVE:
            self.enter_combat_active()
        elif new_state == CombatState.COMBAT_RESOLUTION:
            self.enter_combat_resolution()
        elif new_state == CombatState.COMBAT_EXIT:
            self.enter_combat_exit()
        elif new_state == CombatState.EXPLORATION:
            self.enter_exploration()
    
    def exit_state(self, old_state):
        """Handle exit logic for a state"""
        if old_state == CombatState.COMBAT_ACTIVE:
            self.exit_combat_active()
        elif old_state == CombatState.COMBAT_INIT:
            self.exit_combat_init()
        # ... other exit logic
    
    # State-specific methods
    def update_exploration(self):
        """Update logic for exploration state"""
        # Check for combat initiation conditions
        if self.check_combat_start():
            self.change_state(CombatState.COMBAT_INIT)
    
    def enter_combat_init(self):
        """Enter combat initialization state"""
        # Build turn order
        self.build_turn_order()
        
        # Initialize combat data
        self.current_turn_index = 0
        self.combat_log = []
        self.round_count = 1
        
        # Log combat start
        self.log_combat_event("Combat started!")
        
        # Update UI for combat
        self.game.update_ui_combat_start()
        
        # Move to active combat
        self.change_state(CombatState.COMBAT_ACTIVE)
    
    def enter_combat_active(self):
        """Enter active combat state"""
        # Start first turn
        self.start_current_turn()
    
    def update_combat_active(self):
        """Update logic for active combat state"""
        # Handle current turn
        current_entity = self.turn_order[self.current_turn_index]
        
        # Check if entity can act
        if not current_entity.can_act():
            self.log_combat_event(f"{self.get_entity_name(current_entity)} cannot act due to status effects")
            self.end_current_turn()
            return
        
        # Handle player vs enemy turns
        if isinstance(current_entity, Player):
            # Wait for player input
            # This is handled by the input system
            pass
        else:
            # AI turn
            self.handle_enemy_turn(current_entity)
    
    def enter_combat_resolution(self):
        """Enter combat resolution state"""
        # Determine combat outcome
        if not self.game.enemies:
            self.combat_result = "victory"
        elif self.game.player.health <= 0:
            self.combat_result = "defeat"
        else:
            self.combat_result = "flee"  # Player fled
        
        # Apply combat rewards/punishments
        self.apply_combat_resolution()
        
        # Log result
        if self.combat_result == "victory":
            self.log_combat_event("Victory! All enemies defeated.")
        elif self.combat_result == "defeat":
            self.log_combat_event("Defeat! You have been slain.")
        else:
            self.log_combat_event("You fled from combat.")
        
        # Move to exit state
        self.change_state(CombatState.COMBAT_EXIT)
    
    def enter_combat_exit(self):
        """Enter combat exit state"""
        # Clean up combat data
        self.cleanup_combat()
        
        # Update UI for exploration
        self.game.update_ui_exploration()
        
        # Move back to exploration
        self.change_state(CombatState.EXPLORATION)
    
    def enter_exploration(self):
        """Enter exploration state"""
        # Ensure all combat data is cleaned up
        pass
```

### Combat Data Management

#### Turn Order Management
```python
def build_turn_order(self):
    """Build the turn order for combat"""
    # Start with player
    self.turn_order = [self.game.player]
    
    # Add enemies, potentially sorted by speed or other criteria
    # For now, we'll add them in their current order
    self.turn_order.extend(self.game.enemies[:])  # Copy to avoid reference issues

def get_current_entity(self):
    """Get the entity whose turn it currently is"""
    if 0 <= self.current_turn_index < len(self.turn_order):
        return self.turn_order[self.current_turn_index]
    return None

def start_current_turn(self):
    """Start the current entity's turn"""
    entity = self.get_current_entity()
    if entity:
        # Update status effects at start of turn
        entity.on_turn_start()
        
        # Notify UI
        self.game.update_ui_turn_start(entity)
        
        # Log turn start
        self.log_combat_event(f"{self.get_entity_name(entity)}'s turn")

def end_current_turn(self):
    """End the current entity's turn"""
    entity = self.get_current_entity()
    if entity:
        # Update status effects at end of turn
        entity.on_turn_end()
        
        # Update action cooldowns
        if hasattr(entity, 'actions'):
            for action in entity.actions:
                action.update_cooldown()
        
        # Notify UI
        self.game.update_ui_turn_end(entity)
        
        # Move to next turn
        self.next_turn()

def next_turn(self):
    """Move to the next turn"""
    # Move to next entity
    self.current_turn_index = (self.current_turn_index + 1) % len(self.turn_order)
    
    # Check if we've completed a round
    if self.current_turn_index == 0:
        self.round_count += 1
        # Update status effects for all entities at round start
        for entity in self.turn_order:
            if hasattr(entity, 'on_round_start'):
                entity.on_round_start()
    
    # Start the new turn
    self.start_current_turn()
```

#### Combat Log Management
```python
def log_combat_event(self, event):
    """Add an event to the combat log"""
    # Add timestamp and round information
    log_entry = f"Round {self.round_count}, Turn {self.current_turn_index + 1}: {event}"
    self.combat_log.append(log_entry)
    
    # Keep log at reasonable size
    if len(self.combat_log) > 30:
        self.combat_log.pop(0)
    
    # Notify UI of new log entry
    self.game.update_ui_combat_log(log_entry)

def get_combat_log(self):
    """Get the current combat log"""
    return self.combat_log[:]

def clear_combat_log(self):
    """Clear the combat log"""
    self.combat_log = []
```

#### Action Management
```python
def select_action(self, action_type):
    """Select a combat action"""
    self.selected_action = action_type
    
    # Determine valid targets for this action
    self.valid_targets = self.get_valid_targets(action_type)
    
    # Update UI to show valid targets
    self.game.update_ui_valid_targets(self.valid_targets)
    
    # Highlight targets
    self.game.highlight_targets(self.valid_targets)

def select_target(self, target):
    """Select a target for the current action"""
    if target in self.valid_targets:
        self.selected_target = target
        # Highlight selected target
        self.game.highlight_selected_target(target)
        return True
    return False

def execute_action(self):
    """Execute the selected action on the selected target"""
    if not self.selected_action or not self.selected_target:
        return False
    
    # Get current entity
    current_entity = self.get_current_entity()
    if not current_entity:
        return False
    
    # Create and execute action
    action = self.create_action(self.selected_action)
    if action and action.can_execute(current_entity):
        result = action.execute(current_entity, self.selected_target, self.game)
        self.log_combat_event(result)
        
        # Clear selection
        self.clear_action_selection()
        
        # End turn
        self.end_current_turn()
        
        # Check for combat end
        self.check_combat_end()
        
        return True
    
    return False

def clear_action_selection(self):
    """Clear the current action selection"""
    self.selected_action = None
    self.selected_target = None
    self.valid_targets = []
    
    # Update UI
    self.game.clear_target_highlights()
    self.game.update_ui_valid_targets([])
```

### Combat Initiation and Resolution

#### Combat Initiation
```python
def check_combat_start(self):
    """Check if combat should start"""
    # Combat starts when player is adjacent to any enemy
    for enemy in self.game.enemies:
        distance = abs(self.game.player.x - enemy.x) + abs(self.game.player.y - enemy.y)
        if distance <= 1 and enemy.health > 0:
            return True
    return False

def get_entity_name(self, entity):
    """Get a display name for an entity"""
    if isinstance(entity, Player):
        return "Player"
    elif hasattr(entity, 'char'):
        return f"Enemy ({entity.char})"
    else:
        return entity.__class__.__name__
```

#### Combat Resolution
```python
def check_combat_end(self):
    """Check if combat should end"""
    # Combat ends when all enemies are defeated
    if not self.game.enemies or all(e.health <= 0 for e in self.game.enemies):
        self.change_state(CombatState.COMBAT_RESOLUTION)
        return True
    
    # Combat ends if player is defeated
    if self.game.player.health <= 0:
        self.change_state(CombatState.COMBAT_RESOLUTION)
        return True
    
    # Combat might end if player flees (implementation dependent)
    # This would be triggered by player input
    
    return False

def flee_combat(self):
    """Attempt to flee from combat"""
    # Simple flee mechanic - 50% chance to escape
    if random.random() < 0.5:
        self.log_combat_event("You successfully fled from combat!")
        self.change_state(CombatState.COMBAT_RESOLUTION)
    else:
        self.log_combat_event("You failed to flee!")
        # End player's turn, let enemies act
        self.end_current_turn()

def apply_combat_resolution(self):
    """Apply rewards or penalties based on combat result"""
    if self.combat_result == "victory":
        # Award experience, items, etc.
        self.award_victory_rewards()
    elif self.combat_result == "defeat":
        # Handle player death
        self.handle_player_defeat()
    # Flee has no special resolution

def award_victory_rewards(self):
    """Award rewards for winning combat"""
    # Calculate rewards based on defeated enemies
    total_exp = sum(getattr(e, 'exp_value', 10) for e in self.game.enemies if e.health <= 0)
    # Award experience
    # ... exp award logic ...
    
    # Chance for item drops
    # ... item drop logic ...

def handle_player_defeat(self):
    """Handle player defeat"""
    # Reset player health to 1 for "game over" state
    self.game.player.health = 1
    # ... other defeat logic ...
```

### Integration with Game Systems

#### UI Integration
```python
def update_ui_combat_start(self):
    """Update UI when combat starts"""
    # Switch to combat UI layout
    # Show turn order
    # Show combat log
    # Show action menu
    pass

def update_ui_exploration(self):
    """Update UI when returning to exploration"""
    # Switch back to exploration UI layout
    # Hide combat-specific elements
    pass

def update_ui_turn_start(self, entity):
    """Update UI when an entity's turn starts"""
    # Highlight current entity
    # Update action menu availability
    pass

def update_ui_turn_end(self, entity):
    """Update UI when an entity's turn ends"""
    # Remove highlight from entity
    pass

def update_ui_combat_log(self, entry):
    """Update UI with new combat log entry"""
    # Add entry to log display
    pass

def update_ui_valid_targets(self, targets):
    """Update UI to show valid targets"""
    # Highlight valid targets
    pass
```

#### Cleanup
```python
def cleanup_combat(self):
    """Clean up combat data"""
    self.turn_order = []
    self.current_turn_index = 0
    self.combat_log = []
    self.selected_action = None
    self.selected_target = None
    self.valid_targets = []
    self.round_count = 0
    self.combat_result = None
```

## Testing Considerations
1. Test state transitions between all combat states
2. Test combat initiation under various conditions
3. Test combat resolution for victory, defeat, and flee scenarios
4. Test turn order management with different numbers of enemies
5. Test combat log functionality and size limits
6. Test action selection and execution flow
7. Test UI updates for all state changes
8. Test edge cases like all enemies defeated during an enemy's turn
9. Test combat cleanup and return to exploration mode