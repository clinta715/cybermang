#!/usr/bin/env python3
"""
Test script for combat actions functionality.
"""

from player import Player
from enemy import Enemy
from combat_actions import *

def test_combat_actions():
    """Test combat action execution."""
    print("Testing combat actions...")
    
    # Create a player and enemy for testing
    player = Player(0, 0, health=100)
    enemy = Enemy(1, 1, health=50)
    
    # Test attack action
    print("\n1. Testing Attack action:")
    print("Enemy health before attack:", enemy.health)
    attack = AttackAction()
    # Add a mock weapon attribute to the player instance
    setattr(player, 'weapon', type('MockWeapon', (), {'damage': 15})())
    if attack.can_execute(player):
        result = attack.execute(player, enemy)
        print(result)
        print("Enemy health after attack:", enemy.health)
    
    # Test defend action
    print("\n2. Testing Defend action:")
    defend = DefendAction()
    print("Player protected before defend:", player.protected)
    if defend.can_execute(player):
        result = defend.execute(player)
        print(result)
        print("Player protected after defend:", player.protected)
    
    # Test use item action (health potion)
    print("\n3. Testing Use Item action (health potion):")
    print("Player health before potion:", player.health)
    use_item = UseItemAction("health_potion")
    if use_item.can_execute(player):
        result = use_item.execute(player)
        print(result)
        print("Player health after potion:", player.health)
    
    # Test cast spell action (fireball)
    print("\n4. Testing Cast Spell action (fireball):")
    print("Player mana before spell:", player.mana)
    fireball = CastSpellAction("fireball")
    if fireball.can_execute(player):
        result = fireball.execute(player, enemy)
        print(result)
        print("Player mana after spell:", player.mana)
        print("Enemy health after fireball:", enemy.health)
    
    # Test cast spell action (heal)
    print("\n5. Testing Cast Spell action (heal):")
    player.health = 50  # Lower player health for heal test
    print("Player health before heal:", player.health)
    heal = CastSpellAction("heal")
    if heal.can_execute(player):
        result = heal.execute(player)
        print(result)
        print("Player health after heal:", player.health)
    
    print("\nAll tests completed!")

if __name__ == "__main__":
    test_combat_actions()