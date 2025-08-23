#!/usr/bin/env python3
"""
Test script for turn-based combat flow.
"""

from player import Player
from enemy import Enemy
from combat_actions import *

def test_combat_flow():
    """Test turn-based combat flow."""
    print("Testing turn-based combat flow...")
    
    # Create a player and enemy for testing
    player = Player(0, 0, health=100)
    enemy = Enemy(1, 1, health=50)
    
    # Simulate a simple combat turn order
    turn_order = [player, enemy]
    current_turn_index = 0
    
    print("\nStarting combat simulation...")
    print(f"Player health: {player.health}")
    print(f"Enemy health: {enemy.health}")
    
    # Simulate 5 turns of combat
    for turn in range(5):
        print(f"\n--- Turn {turn + 1} ---")
        current_entity = turn_order[current_turn_index]
        
        if isinstance(current_entity, Player):
            print("Player's turn")
            # Player attacks
            attack = AttackAction()
            setattr(player, 'weapon', type('MockWeapon', (), {'damage': 15})())
            if attack.can_execute(player):
                result = attack.execute(player, enemy)
                print(result)
        else:
            print("Enemy's turn")
            # Enemy attacks
            attack = AttackAction()
            if attack.can_execute(enemy):
                result = attack.execute(enemy, player)
                print(result)
        
        # Update status effects for both entities
        player.on_turn_end()
        player.on_turn_start()
        enemy.on_turn_end()
        enemy.on_turn_start()
        
        # Show current health
        print(f"Player health: {player.health}")
        print(f"Enemy health: {enemy.health}")
        
        # Check for combat end
        if player.health <= 0:
            print("Player defeated! Combat ended.")
            break
        if enemy.health <= 0:
            print("Enemy defeated! Combat ended.")
            break
        
        # Move to next turn
        current_turn_index = (current_turn_index + 1) % len(turn_order)
    
    print("\nCombat simulation completed!")

if __name__ == "__main__":
    test_combat_flow()