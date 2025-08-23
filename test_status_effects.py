#!/usr/bin/env python3
"""
Test script for status effects functionality.
"""

from player import Player
from enemy import Enemy
from status_effects import *

def test_status_effects():
    """Test status effect application and removal."""
    print("Testing status effects...")
    
    # Create a player and enemy for testing
    player = Player(0, 0, health=100)
    enemy = Enemy(1, 1, health=50)
    
    # Test applying a poison effect to player
    print("\n1. Testing Poison effect:")
    poison = PoisonEffect(duration=3, intensity=2.0)
    player.apply_status_effect(poison)
    print(f"Player status effects: {player.get_active_effects()}")
    
    # Test that poison deals damage over time
    print("Player health before poison tick:", player.health)
    player.on_turn_start()  # This should deal poison damage
    print("Player health after poison tick:", player.health)
    
    # Test updating status effects (should reduce duration)
    player.update_status_effects()
    print("Player status effects after update:", player.get_active_effects())
    
    # Test applying a protection effect
    print("\n2. Testing Protection effect:")
    protection = ProtectionEffect(duration=2, intensity=1.0)
    enemy.apply_status_effect(protection)
    print(f"Enemy status effects: {enemy.get_active_effects()}")
    print("Enemy protected:", enemy.protected)
    
    # Test that protection reduces damage
    print("Enemy health before protected attack:", enemy.health)
    enemy.take_damage(20)  # Should be reduced by protection
    print("Enemy health after protected attack:", enemy.health)
    
    # Test removing a status effect
    print("\n3. Testing status effect removal:")
    enemy.remove_status_effect("Protection")
    print(f"Enemy status effects after removal: {enemy.get_active_effects()}")
    print("Enemy protected:", enemy.protected)
    
    # Test applying a strength effect
    print("\n4. Testing Strength effect:")
    strength = StrengthEffect(duration=2, intensity=1.0)
    player.apply_status_effect(strength)
    print(f"Player status effects: {player.get_active_effects()}")
    print("Player strengthened:", player.strengthened)
    
    print("\nAll tests completed!")

if __name__ == "__main__":
    test_status_effects()