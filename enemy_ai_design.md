# Enemy AI Combat Decision System Design

## Overview
This document describes the design and implementation of the enemy AI combat decision system. The system will enable enemies to make intelligent decisions during combat based on their type, current state, and the combat situation.

## Requirements
1. Different enemy types should have distinct combat behaviors
2. AI should consider current status effects when making decisions
3. AI should adapt to changing combat situations
4. AI should be challenging but fair
5. AI should be extensible for new enemy types
6. AI decisions should be deterministic enough for testing but varied enough to be interesting

## Design

### AI Decision Framework
```python
import random
from enum import Enum
from abc import ABC, abstractmethod

class CombatActionType(Enum):
    ATTACK = 1
    DEFEND = 2
    USE_ABILITY = 3
    MOVE = 4
    WAIT = 5

class CombatAction:
    def __init__(self, action_type, target=None, ability=None):
        self.action_type = action_type
        self.target = target
        self.ability = ability
        self.priority = 0  # Higher priority actions are chosen first

class AIBehavior(ABC):
    """Base class for AI behaviors"""
    
    @abstractmethod
    def decide_action(self, enemy, player, allies, enemies, combat_state):
        """Decide on a combat action"""
        pass
    
    @abstractmethod
    def get_behavior_name(self):
        """Get the name of this behavior"""
        pass

class AIContext:
    """Context object containing all information needed for AI decisions"""
    def __init__(self, enemy, player, allies, enemies, combat_state):
        self.enemy = enemy
        self.player = player
        self.allies = allies
        self.enemies = enemies
        self.combat_state = combat_state
        self.current_round = combat_state.round_count if combat_state else 1
        self.current_turn = combat_state.current_turn_index if combat_state else 0
```

### Base Enemy AI Class
```python
class EnemyAI:
    def __init__(self, behavior=None):
        self.behavior = behavior or AggressiveBehavior()
        self.memory = {}  # For tracking past events
        self.personality = {
            'aggression': 0.5,  # How likely to attack
            'caution': 0.3,     # How likely to defend
            'intelligence': 0.7 # How well it assesses situations
        }
    
    def decide_action(self, enemy, player, allies, enemies, combat_state):
        """Main decision method"""
        # Create context
        context = AIContext(enemy, player, allies, enemies, combat_state)
        
        # Update memory
        self._update_memory(context)
        
        # Get action from behavior
        action = self.behavior.decide_action(enemy, player, allies, enemies, combat_state)
        
        # Apply personality modifiers
        action = self._apply_personality_modifiers(action, context)
        
        return action
    
    def _update_memory(self, context):
        """Update AI memory with recent events"""
        # Track player behavior
        if 'player_last_action' not in self.memory:
            self.memory['player_last_action'] = None
        # ... memory update logic ...
    
    def _apply_personality_modifiers(self, action, context):
        """Apply personality-based modifications to actions"""
        # For example, cautious enemies might prefer defending
        if action.action_type == CombatActionType.ATTACK and self.personality['caution'] > 0.7:
            if random.random() < self.personality['caution'] * 0.3:
                action.action_type = CombatActionType.DEFEND
                action.priority -= 10  # Lower priority
        
        return action
    
    def set_behavior(self, behavior):
        """Change the AI behavior"""
        self.behavior = behavior
```

### Specific AI Behaviors

#### Aggressive Behavior
```python
class AggressiveBehavior(AIBehavior):
    def decide_action(self, enemy, player, allies, enemies, combat_state):
        """Aggressive enemies focus on dealing damage"""
        # Check if enemy can act
        if not enemy.can_act():
            return CombatAction(CombatActionType.WAIT)
        
        # Prioritize attacking the player
        if self._can_attack(enemy, player):
            return CombatAction(CombatActionType.ATTACK, target=player, priority=90)
        
        # If player is out of range, try to move closer
        if self._should_move_closer(enemy, player):
            return CombatAction(CombatActionType.MOVE, target=player, priority=70)
        
        # Default to waiting
        return CombatAction(CombatActionType.WAIT, priority=10)
    
    def _can_attack(self, enemy, target):
        """Check if enemy can attack target"""
        distance = abs(enemy.x - target.x) + abs(enemy.y - target.y)
        # Assuming melee range is 1
        return distance <= 1
    
    def _should_move_closer(self, enemy, target):
        """Check if enemy should move closer to target"""
        distance = abs(enemy.x - target.x) + abs(enemy.y - target.y)
        # Move closer if too far
        return distance > 1
    
    def get_behavior_name(self):
        return "Aggressive"
```

#### Defensive Behavior
```python
class DefensiveBehavior(AIBehavior):
    def decide_action(self, enemy, player, allies, enemies, combat_state):
        """Defensive enemies prioritize survival"""
        # Check if enemy can act
        if not enemy.can_act():
            return CombatAction(CombatActionType.WAIT)
        
        # Check health status
        health_ratio = enemy.health / getattr(enemy, 'max_health', enemy.health)
        
        # If low health, consider defensive actions
        if health_ratio < 0.3:
            # 50% chance to defend when low health
            if random.random() < 0.5:
                return CombatAction(CombatActionType.DEFEND, priority=80)
        
        # If moderate health, attack with caution
        if health_ratio < 0.6:
            # 30% chance to defend instead of attack
            if random.random() < 0.3 and self._can_attack(enemy, player):
                return CombatAction(CombatActionType.DEFEND, priority=60)
        
        # Otherwise, attack if possible
        if self._can_attack(enemy, player):
            return CombatAction(CombatActionType.ATTACK, target=player, priority=70)
        
        # If player is out of range, try to move closer
        if self._should_move_closer(enemy, player):
            return CombatAction(CombatActionType.MOVE, target=player, priority=50)
        
        # Default to waiting
        return CombatAction(CombatActionType.WAIT, priority=10)
    
    def _can_attack(self, enemy, target):
        """Check if enemy can attack target"""
        distance = abs(enemy.x - target.x) + abs(enemy.y - target.y)
        return distance <= 1
    
    def _should_move_closer(self, enemy, target):
        """Check if enemy should move closer to target"""
        distance = abs(enemy.x - target.x) + abs(enemy.y - target.y)
        return distance > 1
    
    def get_behavior_name(self):
        return "Defensive"
```

#### Support Behavior
```python
class SupportBehavior(AIBehavior):
    def decide_action(self, enemy, player, allies, enemies, combat_state):
        """Support enemies focus on helping allies"""
        # Check if enemy can act
        if not enemy.can_act():
            return CombatAction(CombatActionType.WAIT)
        
        # Check for allies that need help
        ally_to_help = self._find_injured_ally(allies)
        if ally_to_help:
            # Check if we can heal the ally
            if hasattr(enemy, 'heal_ability') and enemy.heal_ability.can_use():
                return CombatAction(CombatActionType.USE_ABILITY, target=ally_to_help, 
                                  ability=enemy.heal_ability, priority=90)
        
        # If no allies need help, act aggressively
        if self._can_attack(enemy, player):
            return CombatAction(CombatActionType.ATTACK, target=player, priority=70)
        
        # If player is out of range, try to move closer
        if self._should_move_closer(enemy, player):
            return CombatAction(CombatActionType.MOVE, target=player, priority=50)
        
        # Default to waiting
        return CombatAction(CombatActionType.WAIT, priority=10)
    
    def _find_injured_ally(self, allies):
        """Find the most injured ally that needs help"""
        injured_allies = [ally for ally in allies if ally.health < getattr(ally, 'max_health', ally.health) * 0.5]
        if injured_allies:
            # Return the most injured ally
            return min(injured_allies, key=lambda a: a.health)
        return None
    
    def _can_attack(self, enemy, target):
        """Check if enemy can attack target"""
        distance = abs(enemy.x - target.x) + abs(enemy.y - target.y)
        return distance <= 1
    
    def _should_move_closer(self, enemy, target):
        """Check if enemy should move closer to target"""
        distance = abs(enemy.x - target.x) + abs(enemy.y - target.y)
        return distance > 1
    
    def get_behavior_name(self):
        return "Support"
```

#### Spellcaster Behavior
```python
class SpellcasterBehavior(AIBehavior):
    def decide_action(self, enemy, player, allies, enemies, combat_state):
        """Spellcaster enemies use abilities strategically"""
        # Check if enemy can act
        if not enemy.can_act():
            return CombatAction(CombatActionType.WAIT)
        
        # Check if we have any abilities available
        available_abilities = self._get_available_abilities(enemy)
        
        # If we have abilities, consider using them
        if available_abilities:
            # Choose ability based on situation
            best_ability = self._choose_best_ability(enemy, player, allies, enemies, available_abilities)
            if best_ability:
                target = self._choose_ability_target(best_ability, enemy, player, allies, enemies)
                if target:
                    return CombatAction(CombatActionType.USE_ABILITY, target=target, 
                                      ability=best_ability, priority=85)
        
        # If no good abilities, fall back to melee
        if self._can_attack(enemy, player):
            return CombatAction(CombatActionType.ATTACK, target=player, priority=70)
        
        # If player is out of range, try to move closer
        if self._should_move_closer(enemy, player):
            return CombatAction(CombatActionType.MOVE, target=player, priority=50)
        
        # Default to waiting
        return CombatAction(CombatActionType.WAIT, priority=10)
    
    def _get_available_abilities(self, enemy):
        """Get list of available abilities"""
        if hasattr(enemy, 'abilities'):
            return [a for a in enemy.abilities if a.can_use()]
        return []
    
    def _choose_best_ability(self, enemy, player, allies, enemies, available_abilities):
        """Choose the best ability to use"""
        # Simple heuristic: choose the most powerful available ability
        if available_abilities:
            return max(available_abilities, key=lambda a: getattr(a, 'power', 0))
        return None
    
    def _choose_ability_target(self, ability, enemy, player, allies, enemies):
        """Choose target for ability"""
        # For offensive abilities, target player
        if getattr(ability, 'is_offensive', True):
            return player
        # For defensive/healing abilities, target self or allies
        else:
            # Prefer self if injured, otherwise allies
            if enemy.health < getattr(enemy, 'max_health', enemy.health) * 0.7:
                return enemy
            # Find injured ally
            for ally in allies:
                if ally != enemy and ally.health < getattr(ally, 'max_health', ally.health) * 0.5:
                    return ally
            return enemy
    
    def _can_attack(self, enemy, target):
        """Check if enemy can attack target"""
        distance = abs(enemy.x - target.x) + abs(enemy.y - target.y)
        return distance <= 1
    
    def _should_move_closer(self, enemy, target):
        """Check if enemy should move closer to target"""
        distance = abs(enemy.x - target.x) + abs(enemy.y - target.y)
        return distance > 1
    
    def get_behavior_name(self):
        return "Spellcaster"
```

#### Cowardly Behavior
```python
class CowardlyBehavior(AIBehavior):
    def decide_action(self, enemy, player, allies, enemies, combat_state):
        """Cowardly enemies try to avoid combat"""
        # Check if enemy can act
        if not enemy.can_act():
            return CombatAction(CombatActionType.WAIT)
        
        # Check health status
        health_ratio = enemy.health / getattr(enemy, 'max_health', enemy.health)
        
        # If very low health, try to flee
        if health_ratio < 0.2:
            # 70% chance to try fleeing when very low health
            if random.random() < 0.7:
                flee_direction = self._choose_flee_direction(enemy, player)
                if flee_direction:
                    return CombatAction(CombatActionType.MOVE, target=flee_direction, priority=80)
        
        # If low health, defend
        if health_ratio < 0.4:
            # 50% chance to defend when low health
            if random.random() < 0.5:
                return CombatAction(CombatActionType.DEFEND, priority=70)
        
        # If moderate health, attack cautiously
        if health_ratio < 0.7:
            # 20% chance to attack
            if random.random() < 0.2 and self._can_attack(enemy, player):
                return CombatAction(CombatActionType.ATTACK, target=player, priority=60)
        
        # If high health, might attack
        if self._can_attack(enemy, player):
            # 10% chance to attack when healthy
            if random.random() < 0.1:
                return CombatAction(CombatActionType.ATTACK, target=player, priority=50)
        
        # Otherwise, try to move away from player
        if self._should_move_away(enemy, player):
            flee_direction = self._choose_flee_direction(enemy, player)
            if flee_direction:
                return CombatAction(CombatActionType.MOVE, target=flee_direction, priority=40)
        
        # Default to waiting
        return CombatAction(CombatActionType.WAIT, priority=10)
    
    def _can_attack(self, enemy, target):
        """Check if enemy can attack target"""
        distance = abs(enemy.x - target.x) + abs(enemy.y - target.y)
        return distance <= 1
    
    def _should_move_away(self, enemy, target):
        """Check if enemy should move away from target"""
        distance = abs(enemy.x - target.x) + abs(enemy.y - target.y)
        # Move away if too close
        return distance < 3
    
    def _choose_flee_direction(self, enemy, player):
        """Choose direction to flee"""
        # Move away from player
        dx = enemy.x - player.x
        dy = enemy.y - player.y
        
        # Prefer moving in the direction with the largest difference
        if abs(dx) > abs(dy):
            return (enemy.x + (1 if dx > 0 else -1), enemy.y)
        else:
            return (enemy.x, enemy.y + (1 if dy > 0 else -1))
    
    def get_behavior_name(self):
        return "Cowardly"
```

### Enemy-Specific AI Implementations

#### FastEnemy AI
```python
class FastEnemyAI(EnemyAI):
    def __init__(self):
        super().__init__(AggressiveBehavior())
        # Fast enemies are more aggressive
        self.personality['aggression'] = 0.8
        self.personality['caution'] = 0.2

class FastEnemy(Enemy):
    def __init__(self, x, y):
        super().__init__(x, y, health=30)
        self.ai = FastEnemyAI()
        # ... other FastEnemy attributes ...
```

#### TankEnemy AI
```python
class TankEnemyAI(EnemyAI):
    def __init__(self):
        super().__init__(DefensiveBehavior())
        # Tank enemies are more defensive
        self.personality['aggression'] = 0.4
        self.personality['caution'] = 0.8

class TankEnemy(Enemy):
    def __init__(self, x, y):
        super().__init__(x, y, health=150)
        self.ai = TankEnemyAI()
        # ... other TankEnemy attributes ...
```

#### HealerEnemy AI
```python
class HealerEnemyAI(EnemyAI):
    def __init__(self):
        super().__init__(SupportBehavior())
        # Healer enemies prioritize support
        self.personality['aggression'] = 0.3
        self.personality['caution'] = 0.6

class HealerEnemy(Enemy):
    def __init__(self, x, y):
        super().__init__(x, y, health=50)
        self.ai = HealerEnemyAI()
        # ... other HealerEnemy attributes ...
```

#### SniperEnemy AI
```python
class SniperEnemyAI(EnemyAI):
    def __init__(self):
        super().__init__(DefensiveBehavior())
        # Sniper enemies are cautious and prefer distance
        self.personality['aggression'] = 0.6
        self.personality['caution'] = 0.7

class SniperEnemy(Enemy):
    def __init__(self, x, y):
        super().__init__(x, y, health=40)
        self.ai = SniperEnemyAI()
        # ... other SniperEnemy attributes ...
```

#### StealthEnemy AI
```python
class StealthEnemyAI(EnemyAI):
    def __init__(self):
        super().__init__(CowardlyBehavior())
        # Stealth enemies are cautious
        self.personality['aggression'] = 0.3
        self.personality['caution'] = 0.9

class StealthEnemy(Enemy):
    def __init__(self, x, y):
        super().__init__(x, y, health=35)
        self.ai = StealthEnemyAI()
        # ... other StealthEnemy attributes ...
```

## Integration with Combat System

### Combat System AI Integration
```python
class CombatSystemWithAI:
    def __init__(self):
        self.ai_controller = EnemyAIController()
        # ... other combat system attributes ...
    
    def handle_enemy_turn(self, enemy):
        """Handle an enemy's turn using AI"""
        # Update enemy status effects
        enemy.on_turn_start()
        
        # Get AI decision
        action = self.ai_controller.get_enemy_action(enemy, self.player, self.enemies)
        
        # Execute action
        if action:
            self.execute_enemy_action(enemy, action)
        
        # Update status effects at end of turn
        enemy.on_turn_end()
    
    def execute_enemy_action(self, enemy, action):
        """Execute an enemy's chosen action"""
        if action.action_type == CombatActionType.ATTACK:
            self.execute_enemy_attack(enemy, action.target)
        elif action.action_type == CombatActionType.DEFEND:
            self.execute_enemy_defend(enemy)
        elif action.action_type == CombatActionType.USE_ABILITY:
            self.execute_enemy_ability(enemy, action.ability, action.target)
        elif action.action_type == CombatActionType.MOVE:
            self.execute_enemy_move(enemy, action.target)
        elif action.action_type == CombatActionType.WAIT:
            self.execute_enemy_wait(enemy)
    
    def execute_enemy_attack(self, enemy, target):
        """Execute enemy attack"""
        # Calculate damage
        damage = enemy.calculate_damage()
        
        # Apply damage
        actual_damage = target.take_damage(damage)
        
        # Log the action
        if hasattr(self, 'combat_log'):
            self.combat_log.add_event(
                LogEventType.DAMAGE,
                f"{self.get_entity_name(enemy)} attacks {self.get_entity_name(target)} for {actual_damage} damage!",
                enemy, target, actual_damage
            )
    
    def execute_enemy_defend(self, enemy):
        """Execute enemy defend action"""
        # Apply defense effect
        defense_effect = ProtectionEffect(duration=1, intensity=1.5)
        enemy.apply_status_effect(defense_effect)
        
        # Log the action
        if hasattr(self, 'combat_log'):
            self.combat_log.add_event(
                LogEventType.ACTION,
                f"{self.get_entity_name(enemy)} takes a defensive stance!",
                enemy
            )
    
    def execute_enemy_ability(self, enemy, ability, target):
        """Execute enemy ability"""
        if ability.can_use():
            ability.use(enemy, target)
            
            # Log the action
            if hasattr(self, 'combat_log'):
                self.combat_log.add_event(
                    LogEventType.ACTION,
                    f"{self.get_entity_name(enemy)} uses {ability.name} on {self.get_entity_name(target)}!",
                    enemy, target
                )
    
    def execute_enemy_move(self, enemy, target):
        """Execute enemy movement"""
        # For AI, target might be a position tuple or another entity
        if isinstance(target, tuple):
            # Move to position
            new_x, new_y = target
            enemy.x = new_x
            enemy.y = new_y
        else:
            # Move toward entity
            # Simple movement logic
            dx = target.x - enemy.x
            dy = target.y - enemy.y
            
            # Move one step closer
            if abs(dx) > abs(dy):
                enemy.x += 1 if dx > 0 else -1
            else:
                enemy.y += 1 if dy > 0 else -1
        
        # Log the action
        if hasattr(self, 'combat_log'):
            self.combat_log.add_event(
                LogEventType.ACTION,
                f"{self.get_entity_name(enemy)} moves.",
                enemy
            )
    
    def execute_enemy_wait(self, enemy):
        """Execute enemy wait action"""
        # Do nothing
        if hasattr(self, 'combat_log'):
            self.combat_log.add_event(
                LogEventType.ACTION,
                f"{self.get_entity_name(enemy)} waits.",
                enemy
            )
```

### AI Controller
```python
class EnemyAIController:
    def get_enemy_action(self, enemy, player, all_enemies):
        """Get the action for an enemy using its AI"""
        # Separate allies and enemies (allies are other enemies)
        allies = [e for e in all_enemies if e != enemy]
        enemies = [player]  # Player is the enemy of all enemies
        
        # Get action from enemy's AI
        if hasattr(enemy, 'ai') and enemy.ai:
            # Pass combat state if available
            combat_state = getattr(enemy, 'combat_state', None)
            return enemy.ai.decide_action(enemy, player, allies, enemies, combat_state)
        else:
            # Default to simple aggressive behavior
            return self.get_default_action(enemy, player)
    
    def get_default_action(self, enemy, player):
        """Default action for enemies without AI"""
        # Simple behavior: attack if adjacent, move closer if not
        distance = abs(enemy.x - player.x) + abs(enemy.y - player.y)
        
        if distance <= 1:
            return CombatAction(CombatActionType.ATTACK, target=player, priority=50)
        else:
            # Move toward player
            return CombatAction(CombatActionType.MOVE, target=player, priority=30)
```

## Advanced AI Features

### Learning AI
```python
class LearningEnemyAI(EnemyAI):
    def __init__(self):
        super().__init__()
        self.tactics = {}  # Track successful tactics
        self.player_patterns = {}  # Track player behavior
    
    def decide_action(self, enemy, player, allies, enemies, combat_state):
        """AI that learns from combat experience"""
        # Analyze player patterns
        self._analyze_player_patterns(player)
        
        # Choose action based on learned tactics
        action = self._choose_learned_action(enemy, player)
        if action:
            return action
        
        # Fall back to base behavior
        return super().decide_action(enemy, player, allies, enemies, combat_state)
    
    def _analyze_player_patterns(self, player):
        """Analyze player behavior patterns"""
        # Track player actions over time
        # ... pattern analysis logic ...
        pass
    
    def _choose_learned_action(self, enemy, player):
        """Choose action based on learned tactics"""
        # Use successful tactics from memory
        # ... tactic selection logic ...
        return None
```

### Group AI Coordination
```python
class GroupAIController:
    def coordinate_group_actions(self, enemies, player):
        """Coordinate actions between multiple enemies"""
        actions = []
        
        # Analyze group situation
        group_analysis = self._analyze_group_situation(enemies, player)
        
        # Assign roles to enemies
        roles = self._assign_roles(enemies, group_analysis)
        
        # Get actions for each enemy based on role
        for enemy in enemies:
            role = roles.get(enemy, 'attacker')
            action = self._get_role_action(enemy, role, player, enemies)
            actions.append((enemy, action))
        
        return actions
    
    def _analyze_group_situation(self, enemies, player):
        """Analyze the tactical situation for the group"""
        # ... group analysis logic ...
        return {}
    
    def _assign_roles(self, enemies, group_analysis):
        """Assign tactical roles to enemies"""
        roles = {}
        
        # Sort enemies by health (strongest first)
        sorted_enemies = sorted(enemies, key=lambda e: e.health, reverse=True)
        
        # Assign roles
        for i, enemy in enumerate(sorted_enemies):
            if i == 0:
                roles[enemy] = 'leader'  # Strongest enemy leads
            elif i < len(sorted_enemies) // 2:
                roles[enemy] = 'attacker'
            else:
                roles[enemy] = 'support'
        
        return roles
    
    def _get_role_action(self, enemy, role, player, all_enemies):
        """Get action for enemy based on assigned role"""
        if role == 'leader':
            # Leaders are more aggressive
            return CombatAction(CombatActionType.ATTACK, target=player, priority=90)
        elif role == 'support':
            # Support enemies help allies
            injured_ally = self._find_injured_ally(all_enemies)
            if injured_ally and hasattr(enemy, 'heal_ability'):
                return CombatAction(CombatActionType.USE_ABILITY, target=injured_ally, 
                                  ability=enemy.heal_ability, priority=80)
            else:
                return CombatAction(CombatActionType.ATTACK, target=player, priority=60)
        else:  # attacker
            return CombatAction(CombatActionType.ATTACK, target=player, priority=70)
    
    def _find_injured_ally(self, allies):
        """Find the most injured ally"""
        injured_allies = [ally for ally in allies if ally.health < getattr(ally, 'max_health', ally.health) * 0.5]
        if injured_allies:
            return min(injured_allies, key=lambda a: a.health)
        return None
```

## Testing Considerations

### AI Behavior Testing
1. Test each behavior type in isolation
2. Test enemy-specific AI implementations
3. Test personality modifiers
4. Test AI decision making under various conditions
5. Test AI with different status effects
6. Test group coordination

### Combat Balance Testing
1. Test AI difficulty levels
2. Test AI effectiveness against player
3. Test AI resource management (abilities, etc.)
4. Test AI adaptability to changing situations
5. Test AI fairness and fun factor

### Performance Testing
1. Test AI decision time with many enemies
2. Test memory usage of AI systems
3. Test scalability of AI with increasing enemy counts
4. Test AI performance with complex behaviors