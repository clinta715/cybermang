#!/usr/bin/env python3
"""
Skills module for the skill progression tree system.
"""

import random
from typing import List, Dict, Optional

class Skill:
    def __init__(self, name: str, category: str, description: str, 
                 level: int = 1, max_level: int = 10, 
                 required_skills: Optional[Dict[str, int]] = None,
                 experience_required: int = 100):
        self.name = name
        self.category = category
        self.description = description
        self.level = level
        self.max_level = max_level
        self.required_skills = required_skills or {}
        self.experience_required = experience_required
        self.experience_gained = 0
    
    def can_upgrade(self, player_skills: Dict[str, 'Skill']) -> bool:
        """Check if this skill can be upgraded based on prerequisites"""
        # Check if already at max level
        if self.level >= self.max_level:
            return False
            
        # Check if required skills are met
        for skill_name, required_level in self.required_skills.items():
            if skill_name not in player_skills:
                return False
            if player_skills[skill_name].level < required_level:
                return False
                
        # Check if enough experience has been gained
        return self.experience_gained >= self.experience_required
    
    def upgrade(self) -> bool:
        """Upgrade the skill if possible"""
        if self.level < self.max_level:
            self.level += 1
            self.experience_gained = 0
            # Increase experience required for next level
            self.experience_required = int(self.experience_required * 1.5)
            return True
        return False
    
    def add_experience(self, amount: int):
        """Add experience to this skill"""
        self.experience_gained += amount

class SkillCategory:
    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description
        self.skills: List[Skill] = []
    
    def add_skill(self, skill: Skill):
        """Add a skill to this category"""
        self.skills.append(skill)
    
    def get_skills(self) -> List[Skill]:
        """Get all skills in this category"""
        return self.skills

class SkillTree:
    def __init__(self):
        self.categories: Dict[str, SkillCategory] = {}
        self.skills: Dict[str, Skill] = {}
        self._initialize_skill_tree()
    
    def _initialize_skill_tree(self):
        """Initialize the skill tree with categories and skills"""
        # Create categories
        combat_category = SkillCategory("Combat", "Skills related to combat effectiveness")
        self.categories[combat_category.name] = combat_category
        
        magic_category = SkillCategory("Magic", "Skills related to magical abilities")
        self.categories[magic_category.name] = magic_category
        
        survival_category = SkillCategory("Survival", "Skills related to survivability")
        self.categories[survival_category.name] = survival_category
        
        # Create combat skills
        melee_skill = Skill(
            name="Melee Mastery",
            category="Combat",
            description="Improves melee weapon damage and accuracy",
            max_level=10,
            experience_required=100
        )
        
        ranged_skill = Skill(
            name="Ranged Expertise",
            category="Combat",
            description="Improves ranged weapon damage and accuracy",
            max_level=10,
            experience_required=100
        )
        
        defense_skill = Skill(
            name="Defensive Stance",
            category="Combat",
            description="Reduces damage taken and improves blocking",
            max_level=10,
            experience_required=150
        )
        
        # Create magic skills
        fire_magic_skill = Skill(
            name="Fire Magic",
            category="Magic",
            description="Enhances fire-based spells and effects",
            max_level=10,
            experience_required=120
        )
        
        healing_magic_skill = Skill(
            name="Healing Magic",
            category="Magic",
            description="Improves healing spells and effects",
            max_level=10,
            experience_required=120
        )
        
        # Create survival skills
        health_skill = Skill(
            name="Vitality",
            category="Survival",
            description="Increases maximum health",
            max_level=10,
            experience_required=100
        )
        
        mana_skill = Skill(
            name="Arcane Knowledge",
            category="Survival",
            description="Increases maximum mana",
            max_level=10,
            experience_required=100,
            required_skills={"Magic": 3}  # Requires some magic skill
        )
        
        # Add skills to categories
        combat_category.add_skill(melee_skill)
        combat_category.add_skill(ranged_skill)
        combat_category.add_skill(defense_skill)
        
        magic_category.add_skill(fire_magic_skill)
        magic_category.add_skill(healing_magic_skill)
        
        survival_category.add_skill(health_skill)
        survival_category.add_skill(mana_skill)
        
        # Add skills to skill dictionary
        for skill in [melee_skill, ranged_skill, defense_skill, 
                      fire_magic_skill, healing_magic_skill,
                      health_skill, mana_skill]:
            self.skills[skill.name] = skill
    
    def get_category(self, category_name: str) -> Optional[SkillCategory]:
        """Get a skill category by name"""
        return self.categories.get(category_name)
    
    def get_skill(self, skill_name: str) -> Optional[Skill]:
        """Get a skill by name"""
        return self.skills.get(skill_name)
    
    def get_all_skills(self) -> List[Skill]:
        """Get all skills"""
        return list(self.skills.values())
    
    def get_upgradable_skills(self, player_skills: Dict[str, Skill]) -> List[Skill]:
        """Get a list of skills that can be upgraded"""
        upgradable = []
        for skill in self.skills.values():
            if skill.can_upgrade(player_skills):
                upgradable.append(skill)
        return upgradable

# Global skill tree instance
SKILL_TREE = SkillTree()

def award_skill_experience(player_skills: Dict[str, Skill], skill_name: str, amount: int):
    """Award experience to a specific skill"""
    if skill_name in player_skills:
        player_skills[skill_name].add_experience(amount)
        return True
    return False

def try_upgrade_skill(player_skills: Dict[str, Skill], skill_name: str) -> bool:
    """Try to upgrade a skill if possible"""
    if skill_name in player_skills:
        skill = player_skills[skill_name]
        if skill.can_upgrade(player_skills):
            return skill.upgrade()
    return False