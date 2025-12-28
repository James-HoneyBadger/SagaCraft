"""
Phase V: Procedural Generation Engine

Implements procedural dungeon and area generation with:
- Multiple generation algorithms (BSP, Cellular Automata, Simple Random)
- Seed-based reproducibility
- Themed area generation
- Procedural quest and encounter generation
- Configuration-driven generation
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import List, Set, Tuple, Dict, Optional, Any
import random
from abc import ABC, abstractmethod


class AlgorithmType(Enum):
    """Types of procedural generation algorithms."""
    BINARY_SPACE_PARTITION = "bsp"
    CELLULAR_AUTOMATA = "cellular"
    SIMPLE_RANDOM = "simple_random"
    CORRIDOR_LAYOUT = "corridor"


class RoomType(Enum):
    """Types of rooms that can be generated."""
    CORRIDOR = "corridor"
    CHAMBER = "chamber"
    TREASURE = "treasure"
    TRAP = "trap"
    SPAWN = "spawn"
    BOSS = "boss"
    SAFE = "safe"


class AreaTheme(Enum):
    """Visual and content themes for generated areas."""
    DUNGEON = "dungeon"
    CAVE = "cave"
    FOREST = "forest"
    RUINS = "ruins"
    CASTLE = "castle"
    TEMPLE = "temple"
    SEWERS = "sewers"
    UNDERGROUND_CITY = "underground_city"


@dataclass
class Room:
    """A generated room in a dungeon."""
    x: int
    y: int
    width: int
    height: int
    room_type: RoomType = RoomType.CHAMBER
    theme: AreaTheme = AreaTheme.DUNGEON
    has_treasure: bool = False
    has_trap: bool = False
    monster_count: int = 0
    description: str = ""
    
    def center(self) -> Tuple[int, int]:
        """Get the center coordinates of the room."""
        return (self.x + self.width // 2, self.y + self.height // 2)
    
    def intersects(self, other: 'Room') -> bool:
        """Check if this room intersects with another."""
        return not (self.x + self.width < other.x or
                   other.x + other.width < self.x or
                   self.y + self.height < other.y or
                   other.y + other.height < self.y)
    
    def overlaps_with_padding(self, other: 'Room', padding: int) -> bool:
        """Check if this room overlaps with another when given padding."""
        return not (self.x + self.width + padding < other.x or
                   other.x + other.width + padding < self.x or
                   self.y + self.height + padding < other.y or
                   other.y + other.height + padding < self.y)


@dataclass
class Corridor:
    """A corridor connecting two rooms."""
    start_x: int
    start_y: int
    end_x: int
    end_y: int
    cells: List[Tuple[int, int]] = field(default_factory=list)
    
    def create_path(self) -> None:
        """Create the cells that make up this corridor."""
        self.cells.clear()
        
        # L-shaped corridor
        x, y = self.start_x, self.start_y
        
        # Horizontal first
        if x < self.end_x:
            while x < self.end_x:
                self.cells.append((x, y))
                x += 1
        else:
            while x > self.end_x:
                self.cells.append((x, y))
                x -= 1
        
        self.cells.append((x, y))
        
        # Vertical second
        if y < self.end_y:
            while y < self.end_y:
                self.cells.append((x, y))
                y += 1
        else:
            while y > self.end_y:
                self.cells.append((x, y))
                y -= 1
        
        self.cells.append((x, y))


@dataclass
class DungeonMap:
    """A complete generated dungeon map."""
    width: int
    height: int
    rooms: List[Room] = field(default_factory=list)
    corridors: List[Corridor] = field(default_factory=list)
    tiles: List[List[str]] = field(default_factory=list)
    theme: AreaTheme = AreaTheme.DUNGEON
    seed: int = 0
    
    def initialize_tiles(self) -> None:
        """Initialize the tile grid with walls."""
        self.tiles = [['#' for _ in range(self.width)] for _ in range(self.height)]
    
    def carve_room(self, room: Room) -> None:
        """Carve a room into the tile map."""
        for x in range(max(0, room.x), min(self.width, room.x + room.width)):
            for y in range(max(0, room.y), min(self.height, room.y + room.height)):
                self.tiles[y][x] = '.'
    
    def carve_corridor(self, corridor: Corridor) -> None:
        """Carve a corridor into the tile map."""
        for x, y in corridor.cells:
            if 0 <= x < self.width and 0 <= y < self.height:
                self.tiles[y][x] = '.'
    
    def get_tile(self, x: int, y: int) -> str:
        """Get a tile, returning wall if out of bounds."""
        if 0 <= x < self.width and 0 <= y < self.height:
            return self.tiles[y][x]
        return '#'
    
    def count_open_tiles(self) -> int:
        """Count the number of floor tiles."""
        return sum(1 for row in self.tiles for tile in row if tile == '.')


class DungeonGenerator(ABC):
    """Base class for dungeon generation algorithms."""
    
    @abstractmethod
    def generate(self, width: int, height: int, seed: int) -> DungeonMap:
        """Generate a dungeon map."""
        pass


class BSPDungeonGenerator(DungeonGenerator):
    """Binary Space Partition dungeon generator."""
    
    def __init__(self, min_room_size: int = 6, theme: AreaTheme = AreaTheme.DUNGEON):
        """Initialize the BSP generator."""
        self.min_room_size = min_room_size
        self.theme = theme
    
    def generate(self, width: int, height: int, seed: int) -> DungeonMap:
        """Generate using BSP algorithm."""
        random.seed(seed)
        dungeon = DungeonMap(width, height, theme=self.theme, seed=seed)
        dungeon.initialize_tiles()
        
        # BSP algorithm
        rooms = self._partition_and_carve(0, 0, width, height, dungeon)
        dungeon.rooms = rooms
        
        # Connect rooms with corridors
        for i in range(len(rooms) - 1):
            start = rooms[i].center()
            end = rooms[i + 1].center()
            corridor = Corridor(start[0], start[1], end[0], end[1])
            corridor.create_path()
            dungeon.carve_corridor(corridor)
            dungeon.corridors.append(corridor)
        
        # Add features to rooms
        self._populate_rooms(dungeon)
        
        return dungeon
    
    def _partition_and_carve(self, x: int, y: int, width: int, height: int, 
                            dungeon: DungeonMap, depth: int = 0) -> List[Room]:
        """Recursively partition space and carve rooms."""
        rooms = []
        
        if width < self.min_room_size * 2 or height < self.min_room_size * 2:
            # Create a room in this space
            room_width = random.randint(self.min_room_size, max(self.min_room_size + 1, width - 1))
            room_height = random.randint(self.min_room_size, max(self.min_room_size + 1, height - 1))
            room_x = x + random.randint(0, max(0, width - room_width))
            room_y = y + random.randint(0, max(0, height - room_height))
            
            room = Room(room_x, room_y, room_width, room_height, theme=self.theme)
            dungeon.carve_room(room)
            rooms.append(room)
        else:
            # Split vertically or horizontally
            if random.choice([True, False]):
                # Vertical split
                split = x + width // 2
                rooms.extend(self._partition_and_carve(x, y, split - x, height, dungeon, depth + 1))
                rooms.extend(self._partition_and_carve(split, y, width - (split - x), height, dungeon, depth + 1))
            else:
                # Horizontal split
                split = y + height // 2
                rooms.extend(self._partition_and_carve(x, y, width, split - y, dungeon, depth + 1))
                rooms.extend(self._partition_and_carve(x, split, width, height - (split - y), dungeon, depth + 1))
        
        return rooms
    
    def _populate_rooms(self, dungeon: DungeonMap) -> None:
        """Add treasures, traps, and monsters to rooms."""
        for room in dungeon.rooms:
            if len(dungeon.rooms) > 0:
                # Last room is boss room
                if room == dungeon.rooms[-1]:
                    room.room_type = RoomType.BOSS
                    room.monster_count = random.randint(2, 4)
                # First room is spawn
                elif room == dungeon.rooms[0]:
                    room.room_type = RoomType.SPAWN
                else:
                    # Random room features
                    if random.random() < 0.3:
                        room.has_treasure = True
                    if random.random() < 0.2:
                        room.has_trap = True
                    room.monster_count = random.randint(0, 3)


class CellularAutomataDungeonGenerator(DungeonGenerator):
    """Cellular automata dungeon generator."""
    
    def __init__(self, fill_probability: float = 0.45, iterations: int = 3, 
                 theme: AreaTheme = AreaTheme.CAVE):
        """Initialize the cellular automata generator."""
        self.fill_probability = fill_probability
        self.iterations = iterations
        self.theme = theme
    
    def generate(self, width: int, height: int, seed: int) -> DungeonMap:
        """Generate using cellular automata."""
        random.seed(seed)
        dungeon = DungeonMap(width, height, theme=self.theme, seed=seed)
        
        # Initialize with random tiles
        dungeon.tiles = [['#' if random.random() < self.fill_probability else '.' 
                         for _ in range(width)] for _ in range(height)]
        
        # Apply automata iterations
        for _ in range(self.iterations):
            dungeon.tiles = self._apply_automata_rules(dungeon.tiles)
        
        # Extract rooms
        self._extract_rooms(dungeon)
        
        return dungeon
    
    def _apply_automata_rules(self, tiles: List[List[str]]) -> List[List[str]]:
        """Apply cellular automata smoothing rules."""
        height = len(tiles)
        width = len(tiles[0])
        new_tiles = [row[:] for row in tiles]
        
        for y in range(1, height - 1):
            for x in range(1, width - 1):
                wall_count = self._count_walls(tiles, x, y)
                
                if wall_count > 4:
                    new_tiles[y][x] = '#'
                else:
                    new_tiles[y][x] = '.'
        
        return new_tiles
    
    def _count_walls(self, tiles: List[List[str]], x: int, y: int) -> int:
        """Count walls in 3x3 area around coordinates."""
        count = 0
        for dy in [-1, 0, 1]:
            for dx in [-1, 0, 1]:
                if tiles[y + dy][x + dx] == '#':
                    count += 1
        return count
    
    def _extract_rooms(self, dungeon: DungeonMap) -> None:
        """Extract room regions from the cellular automata map."""
        visited = set()
        rooms = []
        
        for y in range(dungeon.height):
            for x in range(dungeon.width):
                if (x, y) not in visited and dungeon.tiles[y][x] == '.':
                    # Flood fill to find room bounds
                    room = self._flood_fill_room(dungeon.tiles, x, y, visited)
                    if room.width >= 3 and room.height >= 3:
                        rooms.append(room)
        
        dungeon.rooms = rooms
    
    def _flood_fill_room(self, tiles: List[List[str]], start_x: int, start_y: int, 
                        visited: Set[Tuple[int, int]]) -> Room:
        """Flood fill to extract a room."""
        stack = [(start_x, start_y)]
        min_x, max_x = start_x, start_x
        min_y, max_y = start_y, start_y
        
        while stack:
            x, y = stack.pop()
            if (x, y) in visited or not (0 <= x < len(tiles[0]) and 0 <= y < len(tiles)):
                continue
            if tiles[y][x] != '.':
                continue
            
            visited.add((x, y))
            min_x = min(min_x, x)
            max_x = max(max_x, x)
            min_y = min(min_y, y)
            max_y = max(max_y, y)
            
            for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
                stack.append((x + dx, y + dy))
        
        return Room(min_x, min_y, max_x - min_x + 1, max_y - min_y + 1, theme=self.theme)


class SimpleRandomDungeonGenerator(DungeonGenerator):
    """Simple random dungeon generator with random room placement."""
    
    def __init__(self, min_rooms: int = 8, max_rooms: int = 15, 
                 min_room_size: int = 5, theme: AreaTheme = AreaTheme.DUNGEON):
        """Initialize the simple random generator."""
        self.min_rooms = min_rooms
        self.max_rooms = max_rooms
        self.min_room_size = min_room_size
        self.theme = theme
    
    def generate(self, width: int, height: int, seed: int) -> DungeonMap:
        """Generate using simple random placement."""
        random.seed(seed)
        dungeon = DungeonMap(width, height, theme=self.theme, seed=seed)
        dungeon.initialize_tiles()
        
        # Generate random rooms
        num_rooms = random.randint(self.min_rooms, self.max_rooms)
        attempts = 0
        max_attempts = num_rooms * 10
        
        while len(dungeon.rooms) < num_rooms and attempts < max_attempts:
            width_room = random.randint(self.min_room_size, width // 3)
            height_room = random.randint(self.min_room_size, height // 3)
            x = random.randint(1, width - width_room - 1)
            y = random.randint(1, height - height_room - 1)
            
            room = Room(x, y, width_room, height_room, theme=self.theme)
            
            # Check overlap
            if not any(room.overlaps_with_padding(r, 2) for r in dungeon.rooms):
                dungeon.carve_room(room)
                dungeon.rooms.append(room)
            
            attempts += 1
        
        # Connect rooms
        for i in range(len(dungeon.rooms) - 1):
            start = dungeon.rooms[i].center()
            end = dungeon.rooms[i + 1].center()
            corridor = Corridor(start[0], start[1], end[0], end[1])
            corridor.create_path()
            dungeon.carve_corridor(corridor)
            dungeon.corridors.append(corridor)
        
        # Add features
        self._populate_rooms(dungeon)
        
        return dungeon
    
    def _populate_rooms(self, dungeon: DungeonMap) -> None:
        """Add features to rooms."""
        for i, room in enumerate(dungeon.rooms):
            if i == 0:
                room.room_type = RoomType.SPAWN
            elif i == len(dungeon.rooms) - 1:
                room.room_type = RoomType.BOSS
                room.monster_count = random.randint(2, 4)
            else:
                if random.random() < 0.3:
                    room.has_treasure = True
                if random.random() < 0.2:
                    room.has_trap = True
                room.monster_count = random.randint(0, 3)


@dataclass
class AreaTemplate:
    """A template for generating themed areas."""
    name: str
    theme: AreaTheme
    description: str
    algorithm: AlgorithmType = AlgorithmType.BINARY_SPACE_PARTITION
    monster_density: float = 0.5  # 0-1
    treasure_density: float = 0.3  # 0-1
    trap_density: float = 0.2  # 0-1
    recommended_level: int = 1


class AreaGenerator:
    """Generates complete areas with specific themes."""
    
    def __init__(self):
        """Initialize the area generator."""
        self.templates: Dict[AreaTheme, AreaTemplate] = self._create_templates()
    
    def _create_templates(self) -> Dict[AreaTheme, AreaTemplate]:
        """Create area templates for each theme."""
        return {
            AreaTheme.DUNGEON: AreaTemplate(
                "Dungeon", AreaTheme.DUNGEON,
                "A dark underground dungeon with stone walls",
                AlgorithmType.BINARY_SPACE_PARTITION,
                monster_density=0.6, treasure_density=0.3, trap_density=0.3
            ),
            AreaTheme.CAVE: AreaTemplate(
                "Cave", AreaTheme.CAVE,
                "A natural limestone cave with organic passages",
                AlgorithmType.CELLULAR_AUTOMATA,
                monster_density=0.4, treasure_density=0.2, trap_density=0.1
            ),
            AreaTheme.FOREST: AreaTemplate(
                "Forest", AreaTheme.FOREST,
                "A dense magical forest with twisted paths",
                AlgorithmType.SIMPLE_RANDOM,
                monster_density=0.3, treasure_density=0.2, trap_density=0.1
            ),
            AreaTheme.RUINS: AreaTemplate(
                "Ancient Ruins", AreaTheme.RUINS,
                "Crumbling ancient structures overgrown with nature",
                AlgorithmType.BINARY_SPACE_PARTITION,
                monster_density=0.5, treasure_density=0.4, trap_density=0.2
            ),
            AreaTheme.CASTLE: AreaTemplate(
                "Castle", AreaTheme.CASTLE,
                "An imposing fortress with fortified halls",
                AlgorithmType.BINARY_SPACE_PARTITION,
                monster_density=0.7, treasure_density=0.3, trap_density=0.2
            ),
            AreaTheme.TEMPLE: AreaTemplate(
                "Temple", AreaTheme.TEMPLE,
                "A sacred temple with mystical architecture",
                AlgorithmType.CELLULAR_AUTOMATA,
                monster_density=0.4, treasure_density=0.5, trap_density=0.3
            ),
            AreaTheme.SEWERS: AreaTemplate(
                "Sewers", AreaTheme.SEWERS,
                "Disgusting underground sewage tunnels",
                AlgorithmType.CELLULAR_AUTOMATA,
                monster_density=0.5, treasure_density=0.1, trap_density=0.2
            ),
            AreaTheme.UNDERGROUND_CITY: AreaTemplate(
                "Underground City", AreaTheme.UNDERGROUND_CITY,
                "An ancient dwarven city deep below the surface",
                AlgorithmType.SIMPLE_RANDOM,
                monster_density=0.3, treasure_density=0.4, trap_density=0.1
            ),
        }
    
    def generate_area(self, theme: AreaTheme, width: int, height: int, 
                     seed: int) -> DungeonMap:
        """Generate an area with the specified theme."""
        template = self.templates.get(theme)
        if not template:
            template = self.templates[AreaTheme.DUNGEON]
        
        # Create fresh generator for this theme
        generator = self._create_generator(template.algorithm, template.theme)
        
        # Generate map
        dungeon = generator.generate(width, height, seed)
        
        # Apply template features
        for room in dungeon.rooms:
            room.description = self._generate_room_description(room, template.theme)
        
        return dungeon
    
    def _create_generator(self, algorithm: AlgorithmType, theme: AreaTheme) -> DungeonGenerator:
        """Create a new generator for the specified algorithm."""
        if algorithm == AlgorithmType.BINARY_SPACE_PARTITION:
            return BSPDungeonGenerator(theme=theme)
        elif algorithm == AlgorithmType.CELLULAR_AUTOMATA:
            return CellularAutomataDungeonGenerator(theme=theme)
        else:
            return SimpleRandomDungeonGenerator(theme=theme)
    
    def _generate_room_description(self, room: Room, theme: AreaTheme) -> str:
        """Generate a descriptive text for a room based on theme."""
        descriptions = {
            AreaTheme.DUNGEON: f"A stone chamber {room.width}x{room.height} feet",
            AreaTheme.CAVE: f"A natural cavern with {room.width}x{room.height} feet of space",
            AreaTheme.FOREST: f"A clearing in the woods measuring {room.width}x{room.height} feet",
            AreaTheme.RUINS: f"Crumbling remains of an ancient structure {room.width}x{room.height} feet",
            AreaTheme.CASTLE: f"A fortress hall spanning {room.width}x{room.height} feet",
            AreaTheme.TEMPLE: f"A sacred chamber {room.width}x{room.height} feet across",
            AreaTheme.SEWERS: f"A fetid tunnel {room.width}x{room.height} feet long",
            AreaTheme.UNDERGROUND_CITY: f"A city plaza measuring {room.width}x{room.height} feet",
        }
        return descriptions.get(theme, f"A room {room.width}x{room.height} feet")


class ProcedureGenerator:
    """Generates procedures like quests and encounters."""
    
    QUEST_TEMPLATES = [
        "Slay {monster_count} {monsters}",
        "Find the {treasure_type} of {location}",
        "Rescue {npc_name} from {location}",
        "Retrieve the {artifact_name} for {npc_name}",
        "Explore the depths of {location}",
        "Survive {monster_count} encounters",
    ]
    
    ENCOUNTER_TEMPLATES = [
        {"type": "monster_pack", "difficulty": 0.5},
        {"type": "treasure_room", "difficulty": 0.3},
        {"type": "trap_gauntlet", "difficulty": 0.4},
        {"type": "boss_room", "difficulty": 0.9},
        {"type": "puzzle_chamber", "difficulty": 0.6},
    ]
    
    @staticmethod
    def generate_encounter(dungeon: DungeonMap, seed: int) -> Dict[str, Any]:
        """Generate a random encounter for the dungeon."""
        random.seed(seed)
        template = random.choice(ProcedureGenerator.ENCOUNTER_TEMPLATES)
        
        return {
            "type": template["type"],
            "difficulty": template["difficulty"],
            "location": f"Room in {dungeon.theme.value}",
            "seed": seed,
        }
    
    @staticmethod
    def generate_quest(dungeon: DungeonMap, seed: int) -> Dict[str, Any]:
        """Generate a random quest for the dungeon."""
        random.seed(seed)
        template = random.choice(ProcedureGenerator.QUEST_TEMPLATES)
        
        quest_name = template
        difficulty = random.randint(1, 10)
        reward = difficulty * 100
        
        return {
            "name": quest_name,
            "difficulty": difficulty,
            "reward": reward,
            "location": dungeon.theme.value,
            "seed": seed,
        }
