# Adventure IDE - User Guide

A complete graphical IDE for creating and editing adventures.

## Quick Start

```bash
./launch_ide.sh
```

The IDE will open in a new window.

## Features

### Visual Adventure Editor
- **Tabbed interface** - Easy navigation between adventure components
- **Real-time editing** - See changes immediately
- **JSON preview** - View the generated adventure data
- **Built-in testing** - Test your adventure without leaving the IDE

### Adventure Components

**1. Adventure Info Tab**
- Set title, author, and introduction text
- Configure starting room
- Edit general adventure properties

**2. Rooms Tab**
- Create and edit rooms visually
- Set room names and descriptions
- Define exits (north, south, east, west, up, down)
- Manage room properties

**3. Items Tab**
- Add weapons, treasures, and objects
- Set weight, value, and location
- Configure item properties
- Mark as weapon or treasure

**4. Monsters Tab**
- Create NPCs and enemies
- Set stats (hardiness, agility)
- Choose friendliness (friendly/neutral/hostile)
- Place in rooms
- Set gold rewards

**5. Preview Tab**
- View complete JSON output
- Copy to clipboard
- Verify adventure structure

**6. Play Adventure Tab** ⭐ NEW!
- Play your adventure directly in the IDE
- Test changes without saving
- Retro terminal-style interface
- Instant feedback on your design

## Keyboard Shortcuts

- `Ctrl+N` - New Adventure
- `Ctrl+O` - Open Adventure
- `Ctrl+S` - Save Adventure
- `F5` - Test Adventure

## Workflow

### Creating a New Adventure

1. **Launch IDE**
   ```bash
   ./launch_ide.sh
   ```

2. **Set Adventure Info**
   - Go to "Adventure Info" tab
   - Enter title and author
   - Write introduction text
   - Click "Update Info"

3. **Create Rooms**
   - Go to "Rooms" tab
   - Click "Add Room"
   - Enter room name and description
   - Set exits (room IDs for each direction, 0 = no exit)
   - Click "Update Room"
   - Repeat for all rooms

4. **Add Items**
   - Go to "Items" tab
   - Click "Add Item"
   - Set name, description, and properties
   - Set location (room ID)
   - Click "Update Item"

5. **Add Monsters**
   - Go to "Monsters" tab
   - Click "Add Monster"
   - Set name, description, and stats
   - Choose friendliness level
   - Set room location
   - Click "Update Monster"

6. **Test** (Two ways!)
   - **In-IDE**: Go to "Play Adventure" tab → Click "▶ Start Game"
   - **External**: Press `F5` or Tools → Test Adventure
   - Play through to verify everything works

7. **Save**
   - Press `Ctrl+S` or File → Save
   - Choose filename in adventures/ directory

### Editing Existing Adventures

1. **Open Adventure**
   - File → Open (Ctrl+O)
   - Select JSON file
   - Edit in any tab

2. **Make Changes**
   - Select item from list on left
   - Edit properties on right
   - Click "Update" button

3. **Save Changes**
   - File → Save (Ctrl+S)

## Tips & Best Practices

### Room Design
- **Room IDs start at 1** and increment
- **Set start_room** to your entrance room ID
- **Exit value 0** means no exit
- **Exit to room 99** could be your "outside/victory" room
- **Keep descriptions concise** but evocative

### Item Placement
- **Location 0** = player starts with it
- **Location = room ID** = item in that room
- **Weight** affects carry capacity
- **Value** is gold value
- **Mark weapons** with "Is Weapon" checkbox

### Monster Stats
- **Hardiness** = hit points (1-100)
- **Agility** = combat effectiveness (1-30)
- **Friendly** = won't attack
- **Neutral** = may or may not attack
- **Hostile** = always attacks
- **Gold** = reward for defeating

### Testing
- **Test early and often** - catch issues fast
- **Use the Play tab** - test without leaving the IDE
- **Try both methods** - in-IDE play and external testing (F5)
- **Play through completely** - ensure all paths work
- **Check all exits** - verify room connections
- **Try getting all items** - test locations
- **Fight all monsters** - balance difficulty

## Playing in the IDE

### Play Adventure Tab

The IDE now includes an integrated game player!

**How to use:**
1. Switch to the "Play Adventure" tab
2. Click "▶ Start Game" button
3. Enter commands in the command field
4. Press Enter to send commands

**Features:**
- Play your adventure without leaving the IDE
- Test changes instantly without saving
- Retro terminal look (green on black)
- All standard game commands work

**Control Buttons:**
- **▶ Start Game** - Begin playing the current adventure
- **⟳ Restart** - Restart from the beginning
- **⏸ Clear Output** - Clear the game display

**Why use it:**
- Faster testing workflow
- No window switching
- Immediate feedback
- Perfect for rapid prototyping

See `PLAY_IN_IDE_GUIDE.md` for complete Play tab documentation.

## Menu Reference

### File Menu
- **New Adventure** - Create blank adventure
- **Open...** - Load existing JSON file
- **Save** - Save current adventure
- **Save As...** - Save with new filename
- **Exit** - Quit IDE

### Tools Menu
- **Test Adventure (F5)** - Launch game with current adventure
- **Validate Adventure** - Check for errors
- **Import DSK File...** - Import Apple II .DSK disk image

### Help Menu
- **Quick Start Guide** - Basic instructions
- **About** - IDE information

## Validation

The IDE can validate your adventure for common issues:

**Tools → Validate Adventure** checks for:
- Missing title
- No rooms defined
- Invalid start room
- Broken room exits
- Other structural issues

Fix any errors before final save.

## Import DSK Files

The IDE supports importing adventure files:

1. **Tools → Import DSK File...**
2. Select a .dsk disk image
3. Adventure will be converted and loaded
4. Edit as needed
5. Save as JSON

See `DSK_CONVERSION_GUIDE.md` for details on DSK conversion.

## Advanced Features

### JSON Preview
- View complete adventure structure
- Copy to clipboard
- Verify formatting
- Check all IDs and references

### Batch Editing
- Edit multiple rooms/items/monsters
- Copy and modify existing entries
- Use preview to verify changes

## Troubleshooting

### IDE Won't Launch
**Problem:** `python3-tk not found`
**Solution:** Install tkinter:
```bash
# Ubuntu/Debian
sudo apt install python3-tk

# Fedora
sudo dnf install python3-tkinter

# Arch
sudo pacman -S tk
```

### Test Adventure Fails
**Problem:** Adventure won't run when testing
**Solution:** 
- Run validation first
- Check for errors in terminal
- Verify all room IDs exist
- Make sure start_room is valid

### Changes Not Saved
**Problem:** Edits don't persist
**Solution:**
- Click "Update" button after editing
- Save file (Ctrl+S)
- Check for unsaved indicator

## Examples

### Simple 3-Room Adventure

**Room 1** (Start):
- Name: "Forest Path"
- Description: "A narrow path through dark woods"
- Exits: north=2

**Room 2**:
- Name: "Clearing"
- Description: "A small clearing with an old chest"
- Exits: south=1, east=3
- Items: treasure chest

**Room 3**:
- Name: "Cave"
- Description: "A dark cave. Something moves inside."
- Exits: west=2
- Monsters: goblin

### Item Example
- Name: "rusty sword"
- Description: "An old but serviceable weapon"
- Weight: 5
- Value: 25
- Location: 2 (in clearing)
- Is Weapon: ✓

### Monster Example
- Name: "goblin"
- Description: "A small, mean-looking goblin"
- Room: 3
- Hardiness: 10
- Agility: 12
- Friendliness: hostile
- Gold: 15

## Integration with Command Line

The IDE works seamlessly with command-line tools:

```bash
# Create in IDE, test from command line
./play_adventure.sh my_adventure.json

# Import DSK, edit in IDE
./convert_dsk.sh old_adventure.dsk
./launch_ide.sh  # Open and edit

# Validate from command line
python -m json.tool adventures/my_adventure.json
```

## Performance Tips

- Save frequently
- Test in small increments
- Use validation before testing
- Keep backup copies
- Preview JSON to check structure

## Getting Help

- **In IDE:** Help → Quick Start Guide
- **Documentation:** `README.md`
- **Adventure Format:** See JSON examples in adventures/
- **DSK Import:** `DSK_CONVERSION_GUIDE.md`

---

**Ready to create?** Run `./launch_ide.sh` and start building your adventure!
