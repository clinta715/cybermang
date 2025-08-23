# Turn Management System Design

## Overview
This document describes the turn management system for the turn-based combat system. The system will manage the order of turns between the player and enemies, handle combat state transitions, and integrate with the existing game loop.

## Requirements
1. Clear turn order between player and enemies
2. Integration with status effects that modify turn behavior (Haste, Slow)
3. Combat state management (entering/exiting combat)
4. Proper handling of player and enemy actions
5. Cooldown management for abilities

## Design

### Turn Order System
The turn-based system will follow this order:
1. Player turn
2. All enemy turns (in a consistent order)
3. Repeat

#### Player Turn
- Player selects and executes one action
- Status effects are updated
- Cooldowns are updated
- Check for combat end conditions

#### Enemy Turns
- Each enemy takes one turn in sequence
- Status effects are updated for each enemy
- Enemy AI decides and executes action
- Cooldowns are updated for each enemy
- Check for combat end conditions after each enemy

### Combat State Management
The game will have two main states:
1. **Exploration Mode**: Standard movement and interaction
2. **Combat Mode**: Turn-based combat with specific UI and controls

#### State Transitions
- **Entering Combat**: When player and enemy are adjacent
- **Exiting Combat**: When all enemies are defeated or player flees

### Implementation Plan

#### Game Class Modifications
The main game loop in game.py will be modified to handle turn management:

```python
class Game:
    def __init__(self):
        self.combat_mode = False
        self.turn_order = []
        self.current_turn_index = 0
        self.combat_log = []
        # ... other existing attributes
    
    def update(self):
        """Main update method"""
        if self.combat_mode:
            self.update_combat()
        else:
            self.update_exploration()
    
    def update_exploration(self):
        """Standard exploration update"""
        # Existing exploration logic
        # Check for combat initiation
        if self.check_combat_start():
            self.enter_combat()
    
    def update_combat(self):
        """Combat-specific update"""
        # Handle current turn
        current_entity = self.turn_order[self.current_turn_index]
        
        if isinstance(current_entity, Player):
            # Player turn - wait for input
            self.handle_player_turn()
        else:
            # Enemy turn - AI decision
            self.handle_enemy_turn(current_entity)
            
            # Move to next turn
            self.next_turn()
    
    def check_combat_start(self):
        """Check if combat should start"""
        # Combat starts when player is adjacent to any enemy
        for enemy in self.enemies:
            distance = abs(self.player.x - enemy.x) + abs(self.player.y - enemy.y)
            if distance <= 1:
                return True
        return False
    
    def enter_combat(self):
        """Enter combat mode"""
        self.combat_mode = True
        self.build_turn_order()
        self.current_turn_index = 0
        self.combat_log = []
        self.log_combat_event("Combat started!")
        
        # UI changes for combat mode
        # ... update UI ...
    
    def exit_combat(self):
        """Exit combat mode"""
        self.combat_mode = False
        self.turn_order = []
        self.current_turn_index = 0
        
        # UI changes for exploration mode
        # ... update UI ...
    
    def build_turn_order(self):
        """Build the turn order for combat"""
        # Player always goes first
        self.turn_order = [self.player]
        
        # Add enemies, sorted by some criteria (e.g., speed, type)
        # For now, we'll add them in their current order
        self.turn_order.extend(self.enemies)
    
    def next_turn(self):
        """Move to the next turn"""
        # Update cooldowns for all actions
        current_entity = self.turn_order[self.current_turn_index]
        if hasattr(current_entity, 'actions'):
            for action in current_entity.actions:
                action.update_cooldown()
        
        # Move to next entity
        self.current_turn_index = (self.current_turn_index + 1) % len(self.turn_order)
        
        # If we're back to the first entity, it's a new round
        if self.current_turn_index == 0:
            self.new_round()
    
    def new_round(self):
        """Called at the start of each new round"""
        # Update status effects for all entities
        for entity in self.turn_order:
            entity.on_turn_end()
            entity.on_turn_start()
        
        # Check for combat end conditions
        self.check_combat_end()
    
    def check_combat_end(self):
        """Check if combat should end"""
        # Combat ends when all enemies are defeated
        if not self.enemies:
            self.log_combat_event("All enemies defeated!")
            self.exit_combat()
            return
        
        # Combat might end if player flees (implementation dependent)
        # ... check flee conditions ...
    
    def handle_player_turn(self):
        """Handle player's turn in combat"""
        # In combat mode, player input is different
        # Player selects an action, then a target
        # This would be handled in the input system
        pass
    
    def handle_enemy_turn(self, enemy):
        """Handle an enemy's turn in combat"""
        # Update enemy status effects
        enemy.on_turn_start()
        
        # Let AI decide action
        action, target = self.enemy_ai.decide_action(enemy, self.player, self.enemies)
        
        # Execute action
        if action and target:
            result = action.execute(enemy, target, self)
            self.log_combat_event(result)
        
        # Update status effects at end of turn
        enemy.on_turn_end()
        
        # Check for combat end
        self.check_combat_end()
    
    def log_combat_event(self, event):
        """Add an event to the combat log"""
        self.combat_log.append(f"Turn {self.get_current_turn_number()}: {event}")
        # Keep log at reasonable size
        if len(self.combat_log) > 20:
            self.combat_log.pop(0)
    
    def get_current_turn_number(self):
        """Get the current turn number (1-indexed)"""
        return (self.current_turn_index // len(self.turn_order)) + 1
```

#### Input Handling Modifications
The input handling system will need to be modified to support combat actions:

```python
def handle_input(self, key):
    """Handle input based on current game mode"""
    if self.combat_mode:
        self.handle_combat_input(key)
    else:
        self.handle_exploration_input(key)

def handle_combat_input(self, key):
    """Handle input during combat"""
    # Action selection
    if key == ord('a'):
        # Attack action
        self.select_combat_action("attack")
    elif key == ord('d'):
        # Defend action
        self.select_combat_action("defend")
    elif key == ord('i'):
        # Item action
        self.select_combat_action("item")
    elif key == ord('s'):
        # Spell action
        self.select_combat_action("spell")
    # ... other combat actions
    
    # Target selection (after action is selected)
    elif self.selected_action:
        if key == ord('w'):  # Up
            self.select_target(0, -1)
        elif key == ord('s'):  # Down
            self.select_target(0, 1)
        elif key == ord('a'):  # Left
            self.select_target(-1, 0)
        elif key == ord('d'):  # Right
            self.select_target(1, 0)
        elif key == ord(' '):  # Confirm target
            self.execute_combat_action()
        elif key == 27:  # Escape
            self.cancel_combat_action()

def select_combat_action(self, action_type):
    """Select a combat action type"""
    self.selected_action = action_type
    # Highlight valid targets for this action
    self.highlight_targets(action_type)

def execute_combat_action(self):
    """Execute the selected combat action on the selected target"""
    if self.selected_action and self.selected_target:
        # Get current entity (should be player)
        current_entity = self.turn_order[self.current_turn_index]
        
        # Create action instance
        if self.selected_action == "attack":
            action = AttackAction()
        elif self.selected_action == "defend":
            action = DefendAction()
        # ... other actions
        
        # Execute action
        if action.can_execute(current_entity):
            result = action.execute(current_entity, self.selected_target, self)
            self.log_combat_event(result)
            
            # Move to next turn
            self.next_turn()
            
            # Clear selection
            self.selected_action = None
            self.selected_target = None
```

#### Turn-Based Status Effect Integration
Status effects that modify turn behavior need special handling:

```python
def handle_entity_turn(self, entity):
    """Handle a single entity's turn, considering status effects"""
    # Check if entity can act
    if not entity.can_act():
        # Entity is paralyzed or slowed and cannot act this turn
        self.log_combat_event(f"{entity.__class__.__name__} cannot act due to status effects")
        return
    
    # Entity can act normally
    if isinstance(entity, Player):
        self.handle_player_turn()
    else:
        self.handle_enemy_turn(entity)

def next_turn(self):
    """Move to the next turn, handling entities that might skip turns"""
    # Update cooldowns for current entity
    current_entity = self.turn_order[self.current_turn_index]
    if hasattr(current_entity, 'actions'):
        for action in current_entity.actions:
            action.update_cooldown()
    
    # Move to next entity that can act
    next_index = (self.current_turn_index + 1) % len(self.turn_order)
    
    # If we're back to the first entity, it's a new round
    if next_index == 0:
        self.new_round()
    
    self.current_turn_index = next_index
```

## Integration Points

### With Player and Enemy Classes
Both Player and Enemy classes need to support:
- Turn start/end methods for status effect updates
- Action cooldown management
- Combat state awareness

### With UI System
The UI needs to:
- Display different interfaces for exploration vs combat
- Show turn order and current turn indicator
- Highlight valid targets for actions
- Display combat log
- Show entity status (HP, MP, status effects)

### With AI System
The AI needs to:
- Make decisions based on combat state
- Select appropriate actions for enemy type
- Target selection based on threat and positioning

## Testing Considerations
1. Test turn order with different numbers of enemies
2. Test status effects that modify turn behavior (Haste, Slow)
3. Test combat state transitions (entering/exiting combat)
4. Test combat end conditions (victory/defeat)
5. Test action cooldowns and mana costs
6. Test UI changes between exploration and combat modes
7. Test edge cases like all enemies being defeated during an enemy's turn