# Combat Log System Design

## Overview
This document describes the design and implementation of the combat log system, which displays combat events to the player in a clear and informative manner.

## Requirements
1. Display combat events in real-time
2. Maintain a history of events
3. Support different types of events (damage, healing, status effects, etc.)
4. Provide visual distinction between different event types
5. Support scrolling through history
6. Integrate with UI layout
7. Handle large volumes of events efficiently

## Design

### Combat Log Entry Structure
```python
import time
from enum import Enum

class LogEventType(Enum):
    DAMAGE = 1
    HEALING = 2
    STATUS_APPLIED = 3
    STATUS_REMOVED = 4
    ACTION = 5
    DEATH = 6
    VICTORY = 7
    DEFEAT = 8
    MISSED = 9
    CRITICAL = 10

class CombatLogEntry:
    def __init__(self, event_type, message, source=None, target=None, value=None, timestamp=None):
        self.event_type = event_type
        self.message = message
        self.source = source  # Entity that caused the event
        self.target = target  # Entity affected by the event
        self.value = value    # Numerical value (damage, healing, etc.)
        self.timestamp = timestamp or time.time()
        self.round_number = 0  # Round when event occurred
        self.turn_number = 0   # Turn when event occurred
    
    def __str__(self):
        """String representation for display"""
        # Format: [Round X, Turn Y] Message
        return f"[Round {self.round_number}, Turn {self.turn_number}] {self.message}"
    
    def get_color_pair(self):
        """Get color pair based on event type"""
        color_map = {
            LogEventType.DAMAGE: 1,      # Red
            LogEventType.HEALING: 2,     # Green
            LogEventType.STATUS_APPLIED: 3,  # Yellow
            LogEventType.STATUS_REMOVED: 4,  # Cyan
            LogEventType.ACTION: 5,      # White
            LogEventType.DEATH: 6,       # Dark red
            LogEventType.VICTORY: 7,     # Bright green
            LogEventType.DEFEAT: 8,      # Dark red
            LogEventType.MISSED: 9,      # Gray
            LogEventType.CRITICAL: 10    # Bright red
        }
        return color_map.get(self.event_type, 5)  # Default to white
```

### Combat Log Manager
```python
class CombatLogManager:
    def __init__(self, max_entries=50):
        self.entries = []
        self.max_entries = max_entries
        self.display_offset = 0  # For scrolling
        self.filters = set()  # Event types to filter out
    
    def add_entry(self, entry):
        """Add a new entry to the log"""
        # Set round and turn numbers if not already set
        if entry.round_number == 0 and hasattr(self, 'current_round'):
            entry.round_number = self.current_round
        if entry.turn_number == 0 and hasattr(self, 'current_turn'):
            entry.turn_number = self.current_turn
        
        self.entries.append(entry)
        
        # Maintain maximum size
        if len(self.entries) > self.max_entries:
            # Remove oldest entries
            excess = len(self.entries) - self.max_entries
            self.entries = self.entries[excess:]
            # Adjust display offset
            self.display_offset = max(0, self.display_offset - excess)
    
    def add_event(self, event_type, message, source=None, target=None, value=None):
        """Convenience method to add an event"""
        entry = CombatLogEntry(event_type, message, source, target, value)
        self.add_entry(entry)
        return entry
    
    def get_visible_entries(self, max_display=10):
        """Get entries that should be displayed"""
        # Apply filters
        filtered_entries = [e for e in self.entries if e.event_type not in self.filters]
        
        # Apply display offset for scrolling
        start_index = max(0, len(filtered_entries) - max_display - self.display_offset)
        end_index = len(filtered_entries) - self.display_offset
        
        return filtered_entries[start_index:end_index]
    
    def scroll_up(self, lines=1):
        """Scroll up through the log"""
        max_scroll = max(0, len(self.entries) - 10)  # Assuming 10 visible lines
        self.display_offset = min(max_scroll, self.display_offset + lines)
    
    def scroll_down(self, lines=1):
        """Scroll down through the log"""
        self.display_offset = max(0, self.display_offset - lines)
    
    def clear(self):
        """Clear all entries"""
        self.entries.clear()
        self.display_offset = 0
    
    def set_filter(self, event_type, enabled):
        """Enable or disable filtering of an event type"""
        if enabled:
            self.filters.discard(event_type)
        else:
            self.filters.add(event_type)
    
    def get_stats(self):
        """Get statistics about the log"""
        return {
            'total_entries': len(self.entries),
            'visible_entries': len(self.get_visible_entries()),
            'display_offset': self.display_offset,
            'filtered_types': len(self.filters)
        }
```

### Event Generation Functions
```python
class CombatEventGenerator:
    def __init__(self, log_manager):
        self.log_manager = log_manager
    
    def entity_takes_damage(self, entity, damage, attacker=None, is_critical=False):
        """Generate a damage event"""
        entity_name = self.get_entity_name(entity)
        attacker_name = self.get_entity_name(attacker) if attacker else None
        
        if is_critical:
            message = f"{attacker_name} critically hits {entity_name} for {damage} damage!"
            event_type = LogEventType.CRITICAL
        else:
            message = f"{attacker_name} hits {entity_name} for {damage} damage."
            event_type = LogEventType.DAMAGE
        
        return self.log_manager.add_event(event_type, message, attacker, entity, damage)
    
    def entity_healed(self, entity, healing, healer=None):
        """Generate a healing event"""
        entity_name = self.get_entity_name(entity)
        healer_name = self.get_entity_name(healer) if healer else None
        
        if healer:
            message = f"{healer_name} heals {entity_name} for {healing} HP."
        else:
            message = f"{entity_name} regenerates {healing} HP."
        
        return self.log_manager.add_event(LogEventType.HEALING, message, healer, entity, healing)
    
    def status_effect_applied(self, entity, effect_name, duration=None):
        """Generate a status effect applied event"""
        entity_name = self.get_entity_name(entity)
        
        if duration:
            message = f"{entity_name} is affected by {effect_name} for {duration} turns."
        else:
            message = f"{entity_name} is affected by {effect_name}."
        
        return self.log_manager.add_event(LogEventType.STATUS_APPLIED, message, None, entity, duration)
    
    def status_effect_removed(self, entity, effect_name):
        """Generate a status effect removed event"""
        entity_name = self.get_entity_name(entity)
        message = f"{entity_name} is no longer affected by {effect_name}."
        
        return self.log_manager.add_event(LogEventType.STATUS_REMOVED, message, None, entity)
    
    def entity_died(self, entity, killer=None):
        """Generate a death event"""
        entity_name = self.get_entity_name(entity)
        killer_name = self.get_entity_name(killer) if killer else None
        
        if killer:
            message = f"{entity_name} is slain by {killer_name}!"
        else:
            message = f"{entity_name} has died!"
        
        return self.log_manager.add_event(LogEventType.DEATH, message, killer, entity)
    
    def action_performed(self, entity, action_name, target=None):
        """Generate an action event"""
        entity_name = self.get_entity_name(entity)
        target_name = self.get_entity_name(target) if target else None
        
        if target:
            message = f"{entity_name} uses {action_name} on {target_name}."
        else:
            message = f"{entity_name} uses {action_name}."
        
        return self.log_manager.add_event(LogEventType.ACTION, message, entity, target)
    
    def combat_victory(self, entities_defeated):
        """Generate a victory event"""
        if len(entities_defeated) == 1:
            message = f"Victory! {self.get_entity_name(entities_defeated[0])} is defeated."
        else:
            message = f"Victory! {len(entities_defeated)} enemies are defeated."
        
        return self.log_manager.add_event(LogEventType.VICTORY, message)
    
    def combat_defeat(self, player):
        """Generate a defeat event"""
        player_name = self.get_entity_name(player)
        message = f"Defeat! {player_name} has fallen in battle."
        
        return self.log_manager.add_event(LogEventType.DEFEAT, message, None, player)
    
    def attack_missed(self, attacker, target):
        """Generate a miss event"""
        attacker_name = self.get_entity_name(attacker)
        target_name = self.get_entity_name(target)
        message = f"{attacker_name}'s attack misses {target_name}."
        
        return self.log_manager.add_event(LogEventType.MISSED, message, attacker, target)
    
    def get_entity_name(self, entity):
        """Get display name for entity"""
        if not entity:
            return "Unknown"
        
        if hasattr(entity, 'name') and entity.name:
            return entity.name
        elif hasattr(entity, '__class__'):
            if hasattr(entity, 'char'):
                return f"{entity.__class__.__name__} ({entity.char})"
            return entity.__class__.__name__
        else:
            return str(entity)
```

## UI Integration

### Combat Log Display Component
```python
import curses

class CombatLogDisplay:
    def __init__(self, log_manager, x, y, width, height):
        self.log_manager = log_manager
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.title = "Combat Log"
    
    def render(self, stdscr):
        """Render the combat log display"""
        try:
            # Draw border
            self._draw_border(stdscr)
            
            # Draw title
            if curses.has_colors():
                stdscr.addstr(self.y, self.x + 2, self.title, curses.color_pair(5))
            else:
                stdscr.addstr(self.y, self.x + 2, self.title)
            
            # Get visible entries
            visible_entries = self.log_manager.get_visible_entries(self.height - 2)
            
            # Draw entries
            for i, entry in enumerate(visible_entries):
                if i >= self.height - 2:
                    break
                
                y_pos = self.y + 1 + i
                x_pos = self.x + 1
                
                # Truncate message to fit width
                message = str(entry)[:self.width - 2]
                
                # Render with color
                if curses.has_colors():
                    stdscr.addstr(y_pos, x_pos, message, curses.color_pair(entry.get_color_pair()))
                else:
                    stdscr.addstr(y_pos, x_pos, message)
        
        except curses.error:
            pass  # Ignore rendering errors
    
    def _draw_border(self, stdscr):
        """Draw the border around the log display"""
        try:
            # Draw corners
            stdscr.addch(self.y, self.x, curses.ACS_ULCORNER)
            stdscr.addch(self.y, self.x + self.width - 1, curses.ACS_URCORNER)
            stdscr.addch(self.y + self.height - 1, self.x, curses.ACS_LLCORNER)
            stdscr.addch(self.y + self.height - 1, self.x + self.width - 1, curses.ACS_LRCORNER)
            
            # Draw top and bottom lines
            for i in range(1, self.width - 1):
                stdscr.addch(self.y, self.x + i, curses.ACS_HLINE)
                stdscr.addch(self.y + self.height - 1, self.x + i, curses.ACS_HLINE)
            
            # Draw left and right lines
            for i in range(1, self.height - 1):
                stdscr.addch(self.y + i, self.x, curses.ACS_VLINE)
                stdscr.addch(self.y + i, self.x + self.width - 1, curses.ACS_VLINE)
        except curses.error:
            pass  # Ignore rendering errors
    
    def handle_input(self, key):
        """Handle input for log navigation"""
        if key == curses.KEY_UP or key == ord('k'):
            self.log_manager.scroll_up()
            return True
        elif key == curses.KEY_DOWN or key == ord('j'):
            self.log_manager.scroll_down()
            return True
        elif key == ord('K'):  # Page up
            self.log_manager.scroll_up(5)
            return True
        elif key == ord('J'):  # Page down
            self.log_manager.scroll_down(5)
            return True
        
        return False
```

### Log Filtering UI
```python
class LogFilterUI:
    def __init__(self, log_manager, x, y):
        self.log_manager = log_manager
        self.x = x
        self.y = y
        self.visible = False
        self.selected_filter = 0
        self.filter_options = [
            ("Damage", LogEventType.DAMAGE),
            ("Healing", LogEventType.HEALING),
            ("Status Effects", LogEventType.STATUS_APPLIED),
            ("Actions", LogEventType.ACTION),
            ("Deaths", LogEventType.DEATH),
            ("Misses", LogEventType.MISSED),
            ("Critical Hits", LogEventType.CRITICAL)
        ]
    
    def toggle_visibility(self):
        """Toggle filter UI visibility"""
        self.visible = not self.visible
    
    def render(self, stdscr):
        """Render the filter UI"""
        if not self.visible:
            return
        
        try:
            # Draw filter options
            for i, (name, event_type) in enumerate(self.filter_options):
                y_pos = self.y + i
                x_pos = self.x
                
                # Check if this filter is enabled
                enabled = event_type not in self.log_manager.filters
                
                # Add selection indicator
                indicator = "> " if i == self.selected_filter else "  "
                
                # Add enabled/disabled indicator
                status = "[x]" if enabled else "[ ]"
                
                message = f"{indicator}{status} {name}"
                
                if curses.has_colors():
                    color_pair = 3 if i == self.selected_filter else 5
                    stdscr.addstr(y_pos, x_pos, message, curses.color_pair(color_pair))
                else:
                    stdscr.addstr(y_pos, x_pos, message)
        
        except curses.error:
            pass  # Ignore rendering errors
    
    def handle_input(self, key):
        """Handle input for filter navigation"""
        if not self.visible:
            return False
        
        if key == curses.KEY_UP or key == ord('k'):
            self.selected_filter = max(0, self.selected_filter - 1)
            return True
        elif key == curses.KEY_DOWN or key == ord('j'):
            self.selected_filter = min(len(self.filter_options) - 1, self.selected_filter + 1)
            return True
        elif key == ord(' '):  # Toggle filter
            if 0 <= self.selected_filter < len(self.filter_options):
                _, event_type = self.filter_options[self.selected_filter]
                # Toggle the filter
                enabled = event_type in self.log_manager.filters
                self.log_manager.set_filter(event_type, enabled)
            return True
        elif key == 27:  # Escape
            self.visible = False
            return True
        
        return False
```

## Integration with Combat Systems

### Combat System Integration
```python
class CombatSystemWithLogging:
    def __init__(self):
        self.log_manager = CombatLogManager()
        self.event_generator = CombatEventGenerator(self.log_manager)
        self.log_display = None  # Will be set by UI
        self.filter_ui = LogFilterUI(self.log_manager, 0, 0)
    
    def initialize_combat(self, player, enemies):
        """Initialize combat with logging"""
        self.log_manager.clear()
        self.log_manager.current_round = 1
        self.log_manager.current_turn = 1
        
        # Log combat start
        enemy_names = [self.event_generator.get_entity_name(e) for e in enemies]
        message = f"Combat started against {', '.join(enemy_names)}!"
        self.log_manager.add_event(LogEventType.ACTION, message)
    
    def entity_takes_damage(self, entity, damage, attacker=None, is_critical=False):
        """Handle damage with logging"""
        # Apply damage
        entity.health -= damage
        if entity.health < 0:
            entity.health = 0
        
        # Log the event
        self.event_generator.entity_takes_damage(entity, damage, attacker, is_critical)
        
        # Check for death
        if entity.health <= 0:
            self.entity_died(entity, attacker)
        
        return damage
    
    def entity_healed(self, entity, healing, healer=None):
        """Handle healing with logging"""
        # Apply healing
        old_health = entity.health
        entity.health = min(getattr(entity, 'max_health', entity.health), entity.health + healing)
        actual_healing = entity.health - old_health
        
        # Log the event
        self.event_generator.entity_healed(entity, actual_healing, healer)
        
        return actual_healing
    
    def apply_status_effect(self, entity, effect):
        """Apply status effect with logging"""
        # Apply the effect (implementation depends on entity)
        entity.apply_status_effect(effect)
        
        # Log the event
        self.event_generator.status_effect_applied(entity, effect.name, effect.duration)
    
    def remove_status_effect(self, entity, effect_name):
        """Remove status effect with logging"""
        # Remove the effect (implementation depends on entity)
        entity.remove_status_effect(effect_name)
        
        # Log the event
        self.event_generator.status_effect_removed(entity, effect_name)
    
    def entity_died(self, entity, killer=None):
        """Handle entity death with logging"""
        # Log the death
        self.event_generator.entity_died(entity, killer)
        
        # Handle death consequences (implementation depends on entity type)
        if hasattr(entity, 'on_death'):
            entity.on_death(killer)
    
    def combat_victory(self, defeated_enemies):
        """Handle combat victory with logging"""
        # Log victory
        self.event_generator.combat_victory(defeated_enemies)
        
        # Handle victory rewards (implementation depends on game system)
        # ... reward logic ...
    
    def combat_defeat(self, player):
        """Handle combat defeat with logging"""
        # Log defeat
        self.event_generator.combat_defeat(player)
        
        # Handle defeat consequences (implementation depends on game system)
        # ... defeat logic ...
```

## Performance Considerations

### Memory Management
1. **Entry Limit**: Maintain a maximum number of log entries
2. **String Interning**: Reuse common strings to reduce memory usage
3. **Lazy Formatting**: Format strings only when needed for display

### Rendering Optimization
1. **Dirty Rectangles**: Only redraw parts of the log that have changed
2. **Caching**: Cache formatted strings to avoid repeated formatting
3. **Clipping**: Don't render entries that are outside the visible area

### Efficient Data Structures
```python
class OptimizedCombatLogManager:
    def __init__(self, max_entries=50):
        self.entries = []  # Circular buffer would be more efficient
        self.max_entries = max_entries
        self.display_cache = {}  # Cache formatted strings
        self.dirty = True  # Flag for when cache needs updating
    
    def add_entry(self, entry):
        """Add entry with memory management"""
        self.entries.append(entry)
        
        # Maintain maximum size
        if len(self.entries) > self.max_entries:
            self.entries.pop(0)  # Remove oldest entry
        
        # Mark cache as dirty
        self.dirty = True
    
    def get_formatted_entries(self, max_display=10):
        """Get formatted entries with caching"""
        if self.dirty or 'formatted' not in self.display_cache:
            # Rebuild cache
            visible_entries = self.get_visible_entries(max_display)
            formatted = [str(entry) for entry in visible_entries]
            self.display_cache['formatted'] = formatted
            self.dirty = False
        else:
            formatted = self.display_cache['formatted']
        
        return formatted
```

## Testing Considerations

### Functionality Testing
1. Test adding and displaying log entries
2. Test scrolling through log history
3. Test filtering different event types
4. Test color coding of different event types
5. Test integration with combat events

### Performance Testing
1. Test log performance with many entries
2. Test rendering performance with large logs
3. Test memory usage with maximum entries
4. Test filtering performance with many event types

### UI Testing
1. Test log display in different screen sizes
2. Test log navigation with keyboard input
3. Test filter UI visibility and interaction
4. Test log integration with other UI elements
5. Test colorblind accessibility of log colors