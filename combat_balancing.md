# Combat System Balancing and Tuning Parameters

## Overview
This document describes the balancing and tuning parameters for the combat system. These parameters control the difficulty, pacing, and overall feel of combat encounters.

## Core Combat Parameters

### Player Parameters
```python
class PlayerCombatStats:
    def __init__(self):
        # Base stats
        self.max_health = 100
        self.health = self.max_health
        self.max_mana = 50
        self.mana = self.max_mana
        self.mana_regen_rate = 5  # Mana regenerated per turn
        
        # Combat stats
        self.base_damage = 10
        self.critical_chance = 0.05  # 5% chance
        self.critical_multiplier = 2.0  # 2x damage on critical hit
        
        # Defense stats
        self.base_armor = 0
        self.dodge_chance = 0.05  # 5% chance to dodge attacks
        
        # Status effect resistances
        self.poison_resistance = 0.0
        self.paralysis_resistance = 0.0
        self.blindness_resistance = 0.0
        
        # Experience and leveling
        self.level = 1
        self.experience = 0
        self.experience_to_next_level = 100

# Player balancing parameters
PLAYER_BALANCING = {
    'health_per_level': 10,
    'mana_per_level': 5,
    'damage_per_level': 2,
    'armor_per_level': 1,
    'critical_chance_per_level': 0.01,
    'dodge_chance_per_level': 0.01,
}
```

### Enemy Parameters
```python
class EnemyCombatStats:
    def __init__(self, enemy_type):
        # Base stats by enemy type
        stats = ENEMY_STATS.get(enemy_type, ENEMY_STATS['basic'])
        
        self.max_health = stats['health']
        self.health = self.max_health
        self.damage = stats['damage']
        self.armor = stats['armor']
        self.speed = stats['speed']
        self.exp_value = stats['exp']
        
        # Status effect chances
        self.poison_chance = stats.get('poison_chance', 0.0)
        self.paralysis_chance = stats.get('paralysis_chance', 0.0)
        self.blindness_chance = stats.get('blindness_chance', 0.0)

# Enemy stats by type
ENEMY_STATS = {
    'basic': {
        'health': 50,
        'damage': 10,
        'armor': 0,
        'speed': 1,
        'exp': 10,
    },
    'fast': {
        'health': 30,
        'damage': 8,
        'armor': 0,
        'speed': 2,
        'exp': 15,
        'poison_chance': 0.1,  # 10% chance to poison
    },
    'tank': {
        'health': 150,
        'damage': 15,
        'armor': 5,
        'speed': 0.5,
        'exp': 25,
        'paralysis_chance': 0.05,  # 5% chance to paralyze
    },
    'sniper': {
        'health': 40,
        'damage': 20,
        'armor': 2,
        'speed': 1,
        'exp': 20,
        'blindness_chance': 0.1,  # 10% chance to blind
    },
    'healer': {
        'health': 50,
        'damage': 5,
        'armor': 1,
        'speed': 1,
        'exp': 20,
    },
    'stealth': {
        'health': 35,
        'damage': 12,
        'armor': 0,
        'speed': 1.5,
        'exp': 18,
    }
}

# Enemy balancing multipliers by player level
ENEMY_BALANCING = {
    'health_multiplier_per_player_level': 0.1,  # 10% more health per player level
    'damage_multiplier_per_player_level': 0.05,  # 5% more damage per player level
    'exp_multiplier_per_player_level': 0.02,    # 2% more exp per player level
}
```

## Status Effect Parameters

### Duration and Intensity
```python
# Status effect base parameters
STATUS_EFFECT_PARAMS = {
    'Poison': {
        'base_duration': 3,
        'base_intensity': 1.0,
        'damage_per_intensity': 5,
        'stacking': 'intensity',  # intensity-based stacking
    },
    'Paralysis': {
        'base_duration': 1,
        'base_intensity': 1.0,
        'stacking': 'duration',   # duration-based stacking
    },
    'Blindness': {
        'base_duration': 2,
        'base_intensity': 1.0,
        'accuracy_reduction': 0.5,  # 50% reduction in accuracy
        'stacking': 'duration',
    },
    'Confusion': {
        'base_duration': 2,
        'base_intensity': 1.0,
        'confusion_chance': 0.5,   # 50% chance to act randomly
        'stacking': 'duration',
    },
    'Haste': {
        'base_duration': 3,
        'base_intensity': 1.0,
        'action_bonus': 1,         # Extra action per turn
        'stacking': 'duration',
    },
    'Slow': {
        'base_duration': 3,
        'base_intensity': 1.0,
        'skip_chance': 0.5,        # 50% chance to skip turn
        'stacking': 'duration',
    },
    'Regeneration': {
        'base_duration': 3,
        'base_intensity': 1.0,
        'healing_per_intensity': 3,
        'stacking': 'intensity',
    },
    'Strength': {
        'base_duration': 2,
        'base_intensity': 1.0,
        'damage_bonus_per_intensity': 0.1,  # 10% damage bonus per intensity
        'stacking': 'intensity',
    },
    'Weakness': {
        'base_duration': 2,
        'base_intensity': 1.0,
        'damage_penalty_per_intensity': 0.1,  # 10% damage penalty per intensity
        'stacking': 'intensity',
    },
    'Protection': {
        'base_duration': 2,
        'base_intensity': 1.0,
        'damage_reduction_per_intensity': 0.1,  # 10% damage reduction per intensity
        'stacking': 'intensity',
    }
}

# Status effect resistance parameters
STATUS_RESISTANCE_PARAMS = {
    'resistance_per_level': 0.02,  # 2% resistance per player level
    'max_resistance': 0.75,        # Maximum 75% resistance
}
```

## Combat Action Parameters

### Action Costs and Effects
```python
# Combat action parameters
ACTION_PARAMS = {
    'Attack': {
        'mana_cost': 0,
        'cooldown': 0,
        'description': 'Deal damage to an enemy',
    },
    'Defend': {
        'mana_cost': 0,
        'cooldown': 3,  # 3-turn cooldown
        'defense_bonus': 0.5,  # 50% damage reduction
        'description': 'Reduce damage taken for 2 turns',
    },
    'UseItem': {
        'mana_cost': 0,
        'cooldown': 1,  # 1-turn cooldown
        'description': 'Consume an item to gain benefits',
    },
    'CastSpell': {
        'mana_cost': 10,  # Base mana cost, spells have individual costs
        'cooldown': 0,    # Spells have individual cooldowns
        'description': 'Use magical abilities that consume mana',
    }
}

# Spell parameters
SPELL_PARAMS = {
    'Fireball': {
        'mana_cost': 15,
        'cooldown': 2,
        'damage': 25,
        'area_of_effect': True,
        'radius': 1,  # 3x3 area
    },
    'Heal': {
        'mana_cost': 10,
        'cooldown': 1,
        'healing': 30,
        'target_type': 'ally',  # Can target allies
    },
    'Paralyze': {
        'mana_cost': 20,
        'cooldown': 3,
        'effect': 'Paralysis',
        'duration': 2,
        'success_chance': 0.8,  # 80% chance to succeed
    },
    'Invisibility': {
        'mana_cost': 25,
        'cooldown': 5,
        'effect': 'Invisibility',
        'duration': 3,
        'description': 'Become invisible for 3 turns',
    },
    'Teleport': {
        'mana_cost': 15,
        'cooldown': 4,
        'max_distance': 5,
        'description': 'Move to a nearby location',
    }
}

# Item parameters
ITEM_PARAMS = {
    'HealthPotion': {
        'healing': 30,
        'description': 'Restore 30 HP',
    },
    'ManaPotion': {
        'mana_restore': 20,
        'description': 'Restore 20 MP',
    },
    'Antidote': {
        'cures': ['Poison'],
        'description': 'Remove Poison effect',
    },
    'StrengthPotion': {
        'effect': 'Strength',
        'duration': 3,
        'intensity': 1.5,
        'description': 'Apply temporary Strength effect',
    },
    'ProtectionPotion': {
        'effect': 'Protection',
        'duration': 3,
        'intensity': 1.5,
        'description': 'Apply temporary Protection effect',
    }
}
```

## Weapon Parameters

### Weapon Stats and Effects
```python
# Weapon parameters
WEAPON_PARAMS = {
    'LaserPistol': {
        'damage': 20,
        'range': 10,
        'ammo_capacity': 30,
        'fire_rate': 2,  # 2 shots per turn
        'status_effects': [
            {'effect': 'Blindness', 'chance': 0.1, 'duration': 1}  # 10% chance to blind
        ]
    },
    'Shotgun': {
        'damage': 15,
        'range': 5,
        'ammo_capacity': 8,
        'fire_rate': 1,  # 1 shot per turn
        'area_of_effect': True,
        'spread_pattern': 'cone',
        'status_effects': []
    },
    'PlasmaRifle': {
        'damage': 35,
        'range': 15,
        'ammo_capacity': 25,
        'fire_rate': 0.5,  # 1 shot every 2 turns
        'piercing': True,  # Can hit multiple enemies
        'status_effects': [
            {'effect': 'Burn', 'chance': 0.2, 'duration': 2}  # 20% chance to apply burn
        ]
    },
    'GrenadeLauncher': {
        'damage': 25,
        'range': 8,
        'ammo_capacity': 12,
        'fire_rate': 1,  # 1 shot per turn
        'area_of_effect': True,
        'radius': 1,  # 3x3 area
        'status_effects': [
            {'effect': 'Stun', 'chance': 0.15, 'duration': 1}  # 15% chance to stun
        ]
    },
    'RailGun': {
        'damage': 45,
        'range': 12,
        'ammo_capacity': 8,
        'fire_rate': 0.33,  # 1 shot every 3 turns
        'piercing': True,  # Can hit multiple enemies
        'status_effects': []
    },
    'Flamethrower': {
        'damage': 8,
        'range': 4,
        'ammo_capacity': 50,
        'fire_rate': 3,  # 3 shots per turn
        'area_of_effect': True,
        'cone_width': 3,  # Width of flame cone
        'status_effects': [
            {'effect': 'Burn', 'chance': 0.3, 'duration': 3}  # 30% chance to apply burn
        ]
    },
    'Crossbow': {
        'damage': 40,
        'range': 10,
        'ammo_capacity': 20,
        'fire_rate': 1,  # 1 shot per turn
        'silent': True,  # No sound effect
        'status_effects': []
    }
}

# Weapon balancing parameters
WEAPON_BALANCING = {
    'damage_per_level': 2,      # Weapon damage increases with player level
    'ammo_capacity_per_level': 2,  # Ammo capacity increases with player level
}
```

## Combat Difficulty Parameters

### Difficulty Scaling
```python
# Combat difficulty parameters
DIFFICULTY_PARAMS = {
    'easy': {
        'enemy_health_multiplier': 0.8,
        'enemy_damage_multiplier': 0.8,
        'player_experience_multiplier': 1.2,
        'item_drop_chance': 0.3,
    },
    'normal': {
        'enemy_health_multiplier': 1.0,
        'enemy_damage_multiplier': 1.0,
        'player_experience_multiplier': 1.0,
        'item_drop_chance': 0.2,
    },
    'hard': {
        'enemy_health_multiplier': 1.2,
        'enemy_damage_multiplier': 1.2,
        'player_experience_multiplier': 0.8,
        'item_drop_chance': 0.1,
    },
    'nightmare': {
        'enemy_health_multiplier': 1.5,
        'enemy_damage_multiplier': 1.5,
        'player_experience_multiplier': 0.6,
        'item_drop_chance': 0.05,
    }
}

# Dynamic difficulty adjustment
DYNAMIC_DIFFICULTY = {
    'player_win_streak_threshold': 5,  # After 5 wins in a row
    'player_loss_streak_threshold': 3,  # After 3 losses in a row
    'difficulty_adjustment': 0.1,  # 10% difficulty change
    'max_difficulty_adjustment': 0.5,  # Maximum 50% adjustment
}
```

## Combat Pacing Parameters

### Turn and Round Timing
```python
# Combat pacing parameters
PACING_PARAMS = {
    'base_turn_duration': 1.0,  # Base seconds per turn
    'haste_turn_duration': 0.5,  # Turn duration with haste
    'slow_turn_duration': 2.0,   # Turn duration with slow
    'round_duration_bonus': 0.5,  # Bonus time per round
    
    # Action timing
    'attack_action_time': 0.5,
    'defend_action_time': 0.3,
    'spell_action_time': 1.0,
    'item_action_time': 0.5,
    
    # Animation timing
    'damage_animation_duration': 1.0,
    'healing_animation_duration': 1.0,
    'status_effect_animation_duration': 1.5,
    'area_effect_animation_duration': 2.0,
}
```

## Reward System Parameters

### Experience and Loot
```python
# Reward system parameters
REWARD_PARAMS = {
    # Experience calculation
    'base_exp_per_enemy': 10,
    'exp_per_enemy_level': 5,
    'exp_per_damage_dealt': 0.1,
    'exp_per_damage_taken': 0.05,
    'exp_for_victory': 50,
    'exp_for_survival': 20,  # Awarded if player survives combat
    
    # Loot drop chances
    'health_potion_drop_chance': 0.2,
    'mana_potion_drop_chance': 0.15,
    'antidote_drop_chance': 0.1,
    'strength_potion_drop_chance': 0.05,
    'protection_potion_drop_chance': 0.05,
    
    # Equipment drop chances
    'weapon_drop_chance': 0.1,
    'ammo_drop_chance': 0.25,
    
    # Gold/currency rewards
    'base_gold_per_enemy': 5,
    'gold_per_enemy_level': 2,
    'gold_for_victory': 25,
}
```

## Tuning and Configuration System

### Parameter Management
```python
class CombatParameters:
    def __init__(self):
        self.player_stats = PlayerCombatStats()
        self.enemy_stats = ENEMY_STATS
        self.status_effects = STATUS_EFFECT_PARAMS
        self.actions = ACTION_PARAMS
        self.spells = SPELL_PARAMS
        self.items = ITEM_PARAMS
        self.weapons = WEAPON_PARAMS
        self.difficulty = DIFFICULTY_PARAMS
        self.pacing = PACING_PARAMS
        self.rewards = REWARD_PARAMS
        self.balancing = {
            'player': PLAYER_BALANCING,
            'enemy': ENEMY_BALANCING,
            'weapon': WEAPON_BALANCING,
        }
    
    def get_parameter(self, category, name, sub_name=None):
        """Get a specific parameter value"""
        category_dict = getattr(self, category, {})
        if sub_name:
            return category_dict.get(name, {}).get(sub_name)
        return category_dict.get(name)
    
    def set_parameter(self, category, name, value, sub_name=None):
        """Set a specific parameter value"""
        category_dict = getattr(self, category, {})
        if sub_name:
            if name not in category_dict:
                category_dict[name] = {}
            category_dict[name][sub_name] = value
        else:
            category_dict[name] = value
    
    def apply_difficulty_scaling(self, difficulty_level, player_level=1):
        """Apply difficulty scaling to parameters"""
        if difficulty_level not in self.difficulty:
            return
        
        difficulty = self.difficulty[difficulty_level]
        
        # Scale enemy stats
        for enemy_type in self.enemy_stats:
            self.enemy_stats[enemy_type]['health'] = int(
                self.enemy_stats[enemy_type]['health'] * 
                difficulty['enemy_health_multiplier'] *
                (1 + ENEMY_BALANCING['health_multiplier_per_player_level'] * (player_level - 1))
            )
            self.enemy_stats[enemy_type]['damage'] = int(
                self.enemy_stats[enemy_type]['damage'] * 
                difficulty['enemy_damage_multiplier'] *
                (1 + ENEMY_BALANCING['damage_multiplier_per_player_level'] * (player_level - 1))
            )
            self.enemy_stats[enemy_type]['exp'] = int(
                self.enemy_stats[enemy_type]['exp'] * 
                difficulty['player_experience_multiplier'] *
                (1 + ENEMY_BALANCING['exp_multiplier_per_player_level'] * (player_level - 1))
            )

# Global parameter manager
combat_params = CombatParameters()
```

## Testing and Tuning Guidelines

### Balancing Process
1. **Start with Baseline Values**: Begin with the parameters defined above
2. **Playtesting**: Conduct extensive playtesting with different player levels
3. **Data Collection**: Track combat outcomes, player deaths, and completion times
4. **Iterative Adjustment**: Make small adjustments and retest
5. **Difficulty Curves**: Ensure difficulty increases appropriately with player progression

### Key Metrics to Monitor
- Average combat duration (turns and real time)
- Player win/loss ratio
- Average damage dealt/received per turn
- Status effect application/removal rates
- Resource consumption (mana, ammo, items)
- Experience gain rate
- Loot drop satisfaction

### Tuning Tools
- Configuration files for easy parameter adjustment
- In-game debug menus for real-time parameter modification
- Combat analytics logging
- Automated combat simulation for testing balance

## Conclusion

This comprehensive set of parameters provides fine-grained control over all aspects of the combat system. By adjusting these values, developers can tune the game's difficulty, pacing, and overall feel to create an engaging and balanced experience for players.