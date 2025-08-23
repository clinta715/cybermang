# Combat Actions System Design

## Overview
This document defines the combat actions available to players and enemies in the turn-based combat system. These actions include attack, defend, use item, and cast spell.

## Combat Action Types

### 1. Attack
- **Description**: Deal damage to an enemy
- **Player Implementation**: 
  - Use current weapon to attack in a specified direction
  - Affected by status effects (Blindness reduces accuracy, Strength/Weakness modifies damage)
  - Can apply status effects based on weapon or player abilities
- **Enemy Implementation**:
  - Move adjacent to player and deal damage
  - Different enemy types may have different attack patterns
  - Can apply status effects based on enemy type or abilities

### 2. Defend
- **Description**: Temporarily reduce damage taken
- **Player Implementation**:
  - Activate a defensive stance for 1-2 turns
  - Reduces incoming damage by 30-50%
  - May have a cooldown period
- **Enemy Implementation**:
  - Some enemy types may use defensive actions
  - Tank enemies might have a "defend" action that reduces damage taken

### 3. Use Item
- **Description**: Consume an item to gain benefits
- **Player Implementation**:
  - Health potions: Restore 20-50 HP
  - Mana potions: Restore 20-30 MP (for spell casting)
  - Antidote: Remove Poison effect
  - Strength potion: Apply temporary Strength effect
  - Protection potion: Apply temporary Protection effect
- **Enemy Implementation**:
  - Enemies generally don't use items in this system
  - Could be extended for special enemy types in the future

### 4. Cast Spell
- **Description**: Use magical abilities that consume mana
- **Player Implementation**:
  - Fireball: Area damage spell (3x3 area)
  - Heal: Restore HP to self or ally
  - Paralyze: Apply Paralysis effect to enemy
  - Invisibility: Apply temporary invisibility effect
  - Teleport: Move to a nearby location
- **Enemy Implementation**:
  - Special enemy types (e.g., HealerEnemy) may cast spells
  - Spells would be predefined for each enemy type

## Implementation Design

### CombatAction Base Class
```python
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
```

### Specific Action Classes

#### AttackAction
```python
class AttackAction(CombatAction):
    def __init__(self):
        super().__init__("Attack", "Deal damage to an enemy with your weapon")
    
    def _perform_action(self, entity, target, game_state):
        # For player, this would use the current weapon
        if isinstance(entity, Player):
            # Player attack logic using current weapon
            # This would integrate with existing weapon system
            pass
        # For enemy, this would deal direct damage
        elif isinstance(entity, Enemy):
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
                return f"{entity.__class__.__name__} attacks for {base_damage} damage!"
        
        return "Attack performed"
```

#### DefendAction
```python
class DefendAction(CombatAction):
    def __init__(self):
        super().__init__("Defend", "Reduce damage taken for 2 turns", cooldown=3)
    
    def _perform_action(self, entity, target, game_state):
        # Apply defense effect
        defense_effect = ProtectionEffect(duration=2, intensity=2.0)  # 20% damage reduction
        entity.apply_status_effect(defense_effect)
        return f"{entity.__class__.__name__} takes a defensive stance!"
```

#### UseItemAction
```python
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
            return f"{entity.__class__.__name__} restored 30 HP!"
        elif self.item_type == "mana_potion":
            if hasattr(entity, 'mana'):
                entity.mana = min(entity.max_mana, entity.mana + 20)
            return f"{entity.__class__.__name__} restored 20 MP!"
        elif self.item_type == "antidote":
            entity.remove_status_effect("Poison")
            return f"{entity.__class__.__name__} cured poison!"
        # ... other items
```

#### CastSpellAction
```python
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
            return f"{entity.__class__.__name__} casts Fireball for {damage} damage!"
        elif self.spell_name == "heal":
            # Heal target (could be self or ally)
            heal_amount = 30
            if target:
                target.health = min(getattr(target, 'max_health', target.health), target.health + heal_amount)
            else:
                entity.health = min(entity.max_health, entity.health + heal_amount)
            return f"{entity.__class__.__name__} casts Heal and restores {heal_amount} HP!"
        elif self.spell_name == "paralyze":
            # Apply paralysis to target
            if target:
                paralysis = ParalysisEffect(duration=2)
                target.apply_status_effect(paralysis)
            return f"{entity.__class__.__name__} casts Paralyze!"
        # ... other spells
```

## Integration with Existing Systems

### Player Integration
The Player class will be extended with:

1. **Action Management**:
   - `available_actions`: List of available combat actions
   - `current_action`: Currently selected action
   - `select_action(action)`: Select an action to perform
   - `perform_action(target)`: Execute the selected action

2. **Resource Management**:
   - `mana`: Current mana points
   - `max_mana`: Maximum mana points
   - `mana_regeneration`: Amount of mana regenerated per turn

3. **Action Execution**:
   - Modify input handling in game.py to support combat actions
   - Add new key bindings for action selection

### Enemy Integration
Enemies will have predefined action sets based on their type:

1. **Basic Enemy**: Attack
2. **Fast Enemy**: Attack (higher chance)
3. **Tank Enemy**: Attack, Defend
4. **Healer Enemy**: Attack, Heal (self or allies)
5. **Stealth Enemy**: Attack, Invisibility

### Game State Integration
The game state will need to track:

1. **Combat Mode**: Whether the game is in exploration mode or combat mode
2. **Turn Order**: Which entity's turn it is
3. **Action Selection**: Current action being selected/confirmed
4. **Targets**: Valid targets for the current action

## UI Considerations

### Action Selection Interface
- Display available actions with key bindings
- Show mana costs and cooldowns
- Highlight valid targets for area effects

### Visual Feedback
- Different animations for different actions
- Status indicators for active effects
- Damage numbers and healing amounts
- Cooldown timers for actions

## Balancing Considerations

### Action Costs
- **Attack**: No mana cost, no cooldown (basic action)
- **Defend**: No mana cost, 3-turn cooldown
- **Items**: No mana cost, item consumption cost
- **Spells**: Mana cost, cooldown based on power

### Damage Scaling
- Player weapon damage: 15-45 (depending on weapon)
- Enemy base damage: 10-25 (depending on enemy type)
- Spell damage: 20-50 (depending on spell)
- Status effect damage: 5-15 per turn (Poison)

### Resource Management
- Player starting mana: 50
- Mana regeneration: 5 per turn
- Mana potion restore: 20
- Health potion restore: 30