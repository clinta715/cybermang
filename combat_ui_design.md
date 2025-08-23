# Combat UI Design

## Overview
This document describes the user interface design for the turn-based combat system. The UI will provide players with all necessary information and controls to make informed decisions during combat.

## UI Layout

### Screen Division
The screen will be divided into several key areas during combat:

```
+-------------------------------------------------------------+
| Player Stats | Turn Order | Combat Log | Action Menu        |
+-------------------------------------------------------------+
|                                                             |
|                    Combat Arena                             |
|                                                             |
|                                                             |
|                                                             |
+-------------------------------------------------------------+
| Status Effects | Valid Targets | Selected Target | Controls |
+-------------------------------------------------------------+
```

### 1. Player Stats Panel (Top-Left)
Displays critical player information:
- Health: Current/Max HP with color-coded bar
- Mana: Current/Max MP with color-coded bar (if magic is enabled)
- Active Status Effects: Icons with remaining duration
- Armor Class/Defense: If applicable

### 2. Turn Order Panel (Top-Center)
Shows the order of turns:
- Player (highlighted when it's their turn)
- Enemies (sorted by turn order)
- Visual indicator for current turn
- Enemy health bars (simplified)

### 3. Combat Log Panel (Top-Right)
Displays recent combat events:
- Timestamped messages
- Damage dealt/received
- Status effects applied/removed
- Action results
- Scrollable history

### 4. Action Menu (Top-Far Right)
Lists available actions:
- Attack (weapon-based)
- Defend
- Items
- Spells (if magic is enabled)
- Flee (contextual)
- Keyboard shortcuts for each action

### 5. Combat Arena (Center)
Main visualization area:
- Player character (@ symbol)
- Enemy characters (with type indicators)
- Terrain features
- Action effects (animations)
- Targeting reticles

### 6. Status Effects Panel (Bottom-Left)
Detailed view of active status effects:
- Effect name
- Remaining duration
- Intensity level (for stackable effects)
- Visual icons

### 7. Valid Targets Panel (Bottom-Center)
When selecting a target:
- List of valid targets
- Target health/status
- Highlighting of selected target
- Range indicators

### 8. Controls Panel (Bottom-Right)
Current control instructions:
- Context-sensitive help
- Keyboard shortcuts
- Action confirm/cancel instructions

## Visual Design

### Color Scheme
- Player: Cyan (consistent with existing game)
- Enemies: Red (consistent with existing game)
- Status Effects: Color-coded by type
  - Poison: Green
  - Paralysis: Yellow
  - Blindness: Gray
  - Haste: Blue
  - etc.
- UI Elements: White/Gray with colored accents

### Icons and Symbols
- Status Effects: Unicode symbols or ASCII art
- Actions: Descriptive text with keyboard shortcuts
- Health/Mana: Bar graphs using ASCII characters
- Turn Order: Simple list with arrow indicator

### Animations
- Damage numbers: Briefly appear and fade
- Status effect application: Flash effect
- Action effects: Temporary animations in combat arena
- Turn transitions: Smooth highlighting changes

## State-Specific UI Elements

### Exploration Mode UI
- Standard game view with map, player, enemies, items
- Status bar with health, weapons, score
- Activity log on the right side

### Combat Initiation UI
- Transition animation
- "Combat Started" message
- Reorganization of screen elements
- Highlighting of adjacent enemies

### Player Turn UI
- "Your Turn" indicator
- Action menu becomes active
- Valid targets are highlighted
- Status effects panel updates
- Turn order panel highlights player

### Action Selection UI
- Action menu shows selected action
- Valid targets are highlighted in combat arena
- Target selection reticle appears
- Controls panel shows targeting instructions

### Target Selection UI
- Selected target is prominently highlighted
- Target's health/status is displayed
- Confirmation/cancellation instructions
- Range/damage preview (if applicable)

### Enemy Turn UI
- Current enemy is highlighted
- "Enemy Turn" message
- Action menu is disabled
- Combat log shows enemy actions
- Visual effects for enemy actions

### Combat Resolution UI
- Victory/Defeat message
- Experience/loot display
- Option to continue or return to game
- Summary of combat events

## Interaction Design

### Keyboard Controls
#### Exploration Mode
- WASD/Arrow Keys: Move player
- Space: Shoot weapon
- 1-7: Switch weapons
- R: Reload
- Z: Toggle zoom
- Q: Quit game

#### Combat Mode
- WASD/Arrow Keys: Navigate targeting reticle
- Space: Confirm target selection
- Escape: Cancel action/return to action menu
- A: Attack action
- D: Defend action
- I: Item action
- S: Spell action
- F: Flee action
- Tab: Cycle through UI panels

#### Action Menu Navigation
- Up/Down Arrow Keys: Navigate actions
- Enter: Select action
- Escape: Return to previous menu

### Mouse Controls (if supported)
- Click on action menu items to select
- Click on targets to select them
- Click on UI panels to focus them
- Right-click to cancel/return

## UI Components

### Health/Mana Bars
```
HP: [██████████████████████████████████████████████████] 100/100
MP: [██████████████████████████████████████████████████] 50/50
```

### Status Effects Display
```
Status: [Poison(3) ⚠] [Protection(2) ⛨] [Haste(4) ⚡]
```

### Turn Order Display
```
Turn Order:
→ Player (@)
  Enemy 1 (F)
  Enemy 2 (T) [███.......] 30/100
```

### Combat Log Display
```
[Round 1, Turn 2] Player attacks Enemy 1 for 25 damage!
[Round 1, Turn 3] Enemy 1 bites Player for 15 damage!
[Round 2, Turn 1] Player uses Health Potion and restores 30 HP!
```

### Action Menu Display
```
Actions:
[A] Attack (Weapon: Laser Pistol - 30/30)
[D] Defend (Cooldown: 0)
[I] Item (Health Potion x2, Mana Potion x1)
[S] Spell (Fireball, Heal, Paralyze)
[F] Flee (50% chance)
[ESC] Cancel
```

## UI State Transitions

### Exploration to Combat
1. Adjacent enemy detection
2. "Combat Started!" message animation
3. UI elements reorganize
4. Turn order panel appears
5. Action menu becomes visible
6. Combat arena highlights

### Combat to Exploration
1. All enemies defeated or player flees
2. "Combat Ended" message
3. Victory/Defeat summary
4. UI elements return to exploration layout
5. Experience/items awarded
6. Normal gameplay resumes

### Turn Transitions
1. Current entity highlight fades
2. Next entity highlight appears
3. "X's Turn" message
4. Status effects update
5. Action availability updates

### Action Execution
1. Action selection highlight
2. Target selection mode
3. Target highlighting
4. Action execution animation
5. Combat log update
6. Turn end transition

## Accessibility Considerations

### Visual
- High contrast between UI elements and background
- Clear, readable fonts
- Colorblind-friendly color schemes
- Sufficient text size

### Keyboard Navigation
- Full keyboard control
- Logical tab order
- Clear keyboard shortcuts
- Visual focus indicators

### Screen Reader Support
- Semantic UI structure
- Descriptive labels
- Dynamic content announcements
- Keyboard shortcut documentation

## Performance Considerations

### Rendering
- Efficient UI element rendering
- Minimal redraws
- Smart update mechanisms
- Animation frame rate management

### Memory
- UI element reuse
- Efficient data structures
- Minimal object creation
- Proper cleanup

## Testing Considerations

### Usability
- Test all keyboard controls
- Verify clear visual feedback
- Check UI readability at different resolutions
- Validate accessibility features

### Performance
- Test UI rendering performance
- Verify smooth animations
- Check memory usage
- Validate responsiveness

### Edge Cases
- Test with many status effects
- Verify UI with many enemies
- Check layout with long combat logs
- Validate UI during rapid state changes