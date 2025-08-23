# Combat Animations and Visual Feedback Design

## Overview
This document describes the design and implementation of combat-specific animations and visual feedback for the turn-based combat system. These animations will enhance the player's understanding of combat events and provide satisfying visual feedback.

## Animation System Design

### Core Animation Framework
```python
import time
import curses

class Animation:
    def __init__(self, duration, delay=0):
        self.duration = duration
        self.delay = delay
        self.start_time = None
        self.finished = False
    
    def start(self):
        """Start the animation"""
        self.start_time = time.time()
    
    def update(self, current_time):
        """Update the animation state"""
        if self.start_time is None:
            return False
        
        elapsed = current_time - self.start_time
        
        if elapsed < self.delay:
            return False
        
        if elapsed >= self.delay + self.duration:
            self.finished = True
            return True
        
        # Calculate progress (0.0 to 1.0)
        self.progress = min(1.0, (elapsed - self.delay) / self.duration)
        return True
    
    def render(self, stdscr):
        """Render the animation - to be overridden by subclasses"""
        pass

class AnimationManager:
    def __init__(self):
        self.active_animations = []
        self.pending_animations = []
    
    def add_animation(self, animation):
        """Add an animation to be started"""
        self.pending_animations.append(animation)
    
    def update(self, stdscr):
        """Update and render all active animations"""
        current_time = time.time()
        
        # Start pending animations
        for anim in self.pending_animations:
            anim.start()
            self.active_animations.append(anim)
        self.pending_animations.clear()
        
        # Update active animations
        finished_animations = []
        for anim in self.active_animations:
            if anim.update(current_time):
                anim.render(stdscr)
            
            if anim.finished:
                finished_animations.append(anim)
        
        # Remove finished animations
        for anim in finished_animations:
            self.active_animations.remove(anim)
        
        return len(self.active_animations) > 0  # Return True if animations are still active
    
    def clear(self):
        """Clear all animations"""
        self.active_animations.clear()
        self.pending_animations.clear()
```

### Combat-Specific Animations

#### Damage Animation
```python
class DamageAnimation(Animation):
    def __init__(self, x, y, damage, color_pair=1, duration=1.0, delay=0):
        super().__init__(duration, delay)
        self.x = x
        self.y = y
        self.damage = damage
        self.color_pair = color_pair
        self.symbol = str(damage)
    
    def render(self, stdscr):
        """Render the damage animation"""
        if self.start_time is None:
            return
        
        try:
            # Calculate position with float offset for smooth movement
            offset_y = -2 * self.progress  # Move upward
            display_y = int(self.y + offset_y)
            
            # Fade out alpha (0-1 to 0-255-like)
            if self.progress > 0.5:
                # Don't render if too faded
                return
            
            # Render damage number
            if curses.has_colors():
                stdscr.addstr(display_y, self.x, self.symbol, curses.color_pair(self.color_pair))
            else:
                stdscr.addstr(display_y, self.x, self.symbol)
        except curses.error:
            pass  # Ignore rendering errors
```

#### Status Effect Animation
```python
class StatusEffectAnimation(Animation):
    def __init__(self, x, y, effect_name, color_pair=2, duration=1.5, delay=0):
        super().__init__(duration, delay)
        self.x = x
        self.y = y
        self.effect_name = effect_name
        self.color_pair = color_pair
        # Simple icons for status effects
        self.icons = {
            "Poison": "☠",
            "Paralysis": "⚡",
            "Blindness": "👁",
            "Confusion": "⁇",
            "Haste": "⏩",
            "Slow": "⏪",
            "Regeneration": "❤",
            "Strength": "💪",
            "Weakness": "💔",
            "Protection": "🛡"
        }
        self.symbol = self.icons.get(effect_name, "★")
    
    def render(self, stdscr):
        """Render the status effect animation"""
        if self.start_time is None:
            return
        
        try:
            # Calculate position with circular motion
            angle = self.progress * 3.14159 * 2  # Full circle
            radius = 1 + self.progress  # Expand outward
            display_x = int(self.x + radius * math.cos(angle))
            display_y = int(self.y + radius * math.sin(angle))
            
            # Fade out in the last 25% of animation
            if self.progress > 0.75:
                return
            
            # Render status effect icon
            if curses.has_colors():
                stdscr.addstr(display_y, display_x, self.symbol, curses.color_pair(self.color_pair))
            else:
                stdscr.addstr(display_y, display_x, self.symbol)
        except curses.error:
            pass  # Ignore rendering errors
```

#### Healing Animation
```python
class HealingAnimation(Animation):
    def __init__(self, x, y, healing, color_pair=3, duration=1.0, delay=0):
        super().__init__(duration, delay)
        self.x = x
        self.y = y
        self.healing = healing
        self.color_pair = color_pair
        self.symbol = f"+{healing}"
    
    def render(self, stdscr):
        """Render the healing animation"""
        if self.start_time is None:
            return
        
        try:
            # Calculate position with float offset for smooth movement
            offset_y = -2 * self.progress  # Move upward
            display_y = int(self.y + offset_y)
            
            # Fade out alpha (0-1 to 0-255-like)
            if self.progress > 0.5:
                # Don't render if too faded
                return
            
            # Render healing number in green
            if curses.has_colors():
                stdscr.addstr(display_y, self.x, self.symbol, curses.color_pair(self.color_pair))
            else:
                stdscr.addstr(display_y, self.x, self.symbol)
        except curses.error:
            pass  # Ignore rendering errors
```

#### Attack Animation
```python
class AttackAnimation(Animation):
    def __init__(self, start_x, start_y, end_x, end_y, symbol="*", color_pair=4, duration=0.5, delay=0):
        super().__init__(duration, delay)
        self.start_x = start_x
        self.start_y = start_y
        self.end_x = end_x
        self.end_y = end_y
        self.symbol = symbol
        self.color_pair = color_pair
    
    def render(self, stdscr):
        """Render the attack animation"""
        if self.start_time is None:
            return
        
        try:
            # Calculate position along the line from start to end
            current_x = self.start_x + (self.end_x - self.start_x) * self.progress
            current_y = self.start_y + (self.end_y - self.start_y) * self.progress
            
            display_x = int(current_x)
            display_y = int(current_y)
            
            # Render attack symbol
            if curses.has_colors():
                stdscr.addstr(display_y, display_x, self.symbol, curses.color_pair(self.color_pair))
            else:
                stdscr.addstr(display_y, display_x, self.symbol)
        except curses.error:
            pass  # Ignore rendering errors
```

#### Area Effect Animation
```python
class AreaEffectAnimation(Animation):
    def __init__(self, center_x, center_y, radius=2, symbol="*", color_pair=5, duration=1.0, delay=0):
        super().__init__(duration, delay)
        self.center_x = center_x
        self.center_y = center_y
        self.radius = radius
        self.symbol = symbol
        self.color_pair = color_pair
        self.positions = self._calculate_positions()
    
    def _calculate_positions(self):
        """Calculate all positions in the area"""
        positions = []
        for y in range(self.center_y - self.radius, self.center_y + self.radius + 1):
            for x in range(self.center_x - self.radius, self.center_x + self.radius + 1):
                # Simple circular area
                distance = ((x - self.center_x) ** 2 + (y - self.center_y) ** 2) ** 0.5
                if distance <= self.radius:
                    positions.append((x, y))
        return positions
    
    def render(self, stdscr):
        """Render the area effect animation"""
        if self.start_time is None:
            return
        
        try:
            # Calculate intensity based on progress
            intensity = 1.0
            if self.progress < 0.2:
                # Fade in
                intensity = self.progress / 0.2
            elif self.progress > 0.8:
                # Fade out
                intensity = (1.0 - self.progress) / 0.2
            
            # Only render every other frame for pulsing effect
            if int(self.progress * 10) % 2 == 0:
                for x, y in self.positions:
                    # Add some randomness to make it more dynamic
                    if random.random() < intensity:
                        if curses.has_colors():
                            stdscr.addstr(y, x, self.symbol, curses.color_pair(self.color_pair))
                        else:
                            stdscr.addstr(y, x, self.symbol)
        except curses.error:
            pass  # Ignore rendering errors
```

## Visual Feedback System

### Entity Highlighting
```python
class EntityHighlight:
    def __init__(self, entity, color_pair, duration=0.5):
        self.entity = entity
        self.color_pair = color_pair
        self.duration = duration
        self.start_time = None
    
    def start(self):
        """Start the highlight"""
        self.start_time = time.time()
    
    def is_active(self, current_time):
        """Check if highlight is still active"""
        if self.start_time is None:
            return False
        return (current_time - self.start_time) < self.duration
    
    def get_color_pair(self):
        """Get the color pair for highlighting"""
        return self.color_pair
```

### Targeting Reticle
```python
class TargetingReticle:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.animation_time = 0
    
    def update(self, x, y):
        """Update reticle position"""
        self.x = x
        self.y = y
    
    def render(self, stdscr, current_time):
        """Render the targeting reticle"""
        self.animation_time += 0.1
        # Pulsing effect
        pulse = abs(math.sin(self.animation_time)) * 0.5 + 0.5
        
        try:
            # Draw reticle with pulsing effect
            char = '+' if pulse > 0.7 else 'x'
            if curses.has_colors():
                stdscr.addstr(self.y, self.x, char, curses.color_pair(6))  # Yellow for targeting
            else:
                stdscr.addstr(self.y, self.x, char)
        except curses.error:
            pass  # Ignore rendering errors
```

## Integration with Combat Systems

### Animation Triggers
```python
class CombatAnimationManager:
    def __init__(self, animation_manager):
        self.animation_manager = animation_manager
        self.entity_highlights = {}
    
    def trigger_damage_animation(self, x, y, damage, is_player=False):
        """Trigger a damage animation"""
        color_pair = 1 if not is_player else 2  # Red for enemy, Blue for player
        animation = DamageAnimation(x, y, damage, color_pair)
        self.animation_manager.add_animation(animation)
    
    def trigger_healing_animation(self, x, y, healing):
        """Trigger a healing animation"""
        animation = HealingAnimation(x, y, healing, color_pair=3)  # Green for healing
        self.animation_manager.add_animation(animation)
    
    def trigger_status_effect_animation(self, x, y, effect_name):
        """Trigger a status effect animation"""
        color_pairs = {
            "Poison": 7,      # Dark green
            "Paralysis": 8,   # Yellow
            "Blindness": 9,   # Gray
            "Haste": 10,      # Blue
            "Slow": 11,       # Purple
            "Regeneration": 3 # Green
            # ... other effects
        }
        color_pair = color_pairs.get(effect_name, 5)  # Default to magenta
        animation = StatusEffectAnimation(x, y, effect_name, color_pair)
        self.animation_manager.add_animation(animation)
    
    def trigger_attack_animation(self, start_x, start_y, end_x, end_y):
        """Trigger an attack animation"""
        animation = AttackAnimation(start_x, start_y, end_x, end_y, symbol="*", color_pair=4)
        self.animation_manager.add_animation(animation)
    
    def trigger_area_effect_animation(self, center_x, center_y, radius=2):
        """Trigger an area effect animation"""
        animation = AreaEffectAnimation(center_x, center_y, radius, symbol="*", color_pair=5)
        self.animation_manager.add_animation(animation)
    
    def highlight_entity(self, entity, color_pair=6, duration=0.5):
        """Highlight an entity"""
        highlight = EntityHighlight(entity, color_pair, duration)
        highlight.start()
        self.entity_highlights[entity] = highlight
    
    def update_highlights(self, current_time):
        """Update entity highlights"""
        expired = []
        for entity, highlight in self.entity_highlights.items():
            if not highlight.is_active(current_time):
                expired.append(entity)
        
        for entity in expired:
            del self.entity_highlights[entity]
    
    def get_entity_highlight_color(self, entity, default_color):
        """Get the highlight color for an entity if it's highlighted"""
        highlight = self.entity_highlights.get(entity)
        if highlight and highlight.is_active(time.time()):
            return highlight.get_color_pair()
        return default_color
```

### UI Animation Integration
```python
class UIAnimationManager:
    def __init__(self):
        self.animations = {}
    
    def animate_health_change(self, entity, old_value, new_value):
        """Animate a health bar change"""
        # This would update the UI to show a smooth transition
        # between old and new health values
        pass
    
    def animate_mana_change(self, entity, old_value, new_value):
        """Animate a mana bar change"""
        # This would update the UI to show a smooth transition
        # between old and new mana values
        pass
    
    def animate_status_effect_added(self, effect_name):
        """Animate a status effect being added to the UI"""
        # This would flash or highlight the status effect in the UI
        pass
    
    def animate_status_effect_removed(self, effect_name):
        """Animate a status effect being removed from the UI"""
        # This would fade out or otherwise indicate removal
        pass
```

## Performance Considerations

### Animation Optimization
1. **Limit Concurrent Animations**: Cap the number of simultaneous animations
2. **Efficient Rendering**: Only render animations that are visible on screen
3. **Animation Reuse**: Reuse animation objects when possible
4. **Culling**: Remove animations that move off-screen

### Frame Rate Management
```python
class AnimationFrameManager:
    def __init__(self, target_fps=30):
        self.target_fps = target_fps
        self.frame_time = 1.0 / target_fps
        self.last_frame_time = time.time()
    
    def should_update(self):
        """Check if it's time for the next animation frame"""
        current_time = time.time()
        if current_time - self.last_frame_time >= self.frame_time:
            self.last_frame_time = current_time
            return True
        return False
```

## Visual Feedback for Status Effects

### Status Effect Indicators
1. **Icons**: Small symbols next to entity representing active effects
2. **Color Coding**: Different colors for different effect types
3. **Duration Bars**: Small bars showing remaining duration
4. **Pulsing Effects**: Visual pulse when effects are applied or expire

### Entity State Visualization
1. **Paralyzed**: Entity appears dimmed or grayed out
2. **Blind**: Reduced visibility around the entity
3. **Confused**: Random visual jitter or distortion
4. **Haste**: Fast animation or afterimage effects
5. **Slow**: Slow motion or delayed movement

## Testing Considerations

### Animation Testing
1. Test all animation types with various parameters
2. Test animation performance with many concurrent effects
3. Test animation cleanup and memory management
4. Test animation rendering at different screen sizes
5. Test animation timing and synchronization

### Visual Feedback Testing
1. Test entity highlighting visibility
2. Test targeting reticle clarity
3. Test status effect indicator readability
4. Test colorblind accessibility
5. Test animation performance on lower-end systems

### Integration Testing
1. Test animation triggers from combat actions
2. Test animation coordination with turn management
3. Test animation persistence across state changes
4. Test animation cleanup during combat exit
5. Test UI animation integration with combat animations