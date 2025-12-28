"""
Phase V: Procedural Generation Engine - Comprehensive Tests

Tests for procedural generation including:
- BSP dungeon generation
- Cellular automata generation
- Simple random generation
- Area themes and templates
- Encounter and quest generation
- Seed reproducibility
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from sagacraft.systems.procedural import (
    AlgorithmType, RoomType, AreaTheme, Room, Corridor, DungeonMap,
    BSPDungeonGenerator, CellularAutomataDungeonGenerator, SimpleRandomDungeonGenerator,
    AreaTemplate, AreaGenerator, ProcedureGenerator
)


def test_room_creation():
    """Test room creation and properties."""
    room = Room(10, 20, 15, 10, room_type=RoomType.CHAMBER)
    
    assert room.x == 10
    assert room.y == 20
    assert room.width == 15
    assert room.height == 10
    assert room.center() == (17, 25)


def test_room_intersection():
    """Test room intersection detection."""
    room1 = Room(0, 0, 10, 10)
    room2 = Room(8, 8, 10, 10)
    room3 = Room(20, 20, 10, 10)
    
    assert room1.intersects(room2), "Overlapping rooms should intersect"
    assert not room1.intersects(room3), "Non-overlapping rooms should not intersect"


def test_room_overlap_with_padding():
    """Test room overlap with padding."""
    room1 = Room(0, 0, 10, 10)
    room2 = Room(12, 12, 10, 10)
    room3 = Room(15, 15, 10, 10)
    
    assert room1.overlaps_with_padding(room2, 2), "Rooms with padding should overlap"
    assert not room1.overlaps_with_padding(room3, 2), "Distant rooms should not overlap with padding"


def test_corridor_creation():
    """Test corridor path creation."""
    corridor = Corridor(0, 0, 5, 5)
    corridor.create_path()
    
    assert len(corridor.cells) > 0, "Corridor should have cells"
    assert corridor.cells[0] == (0, 0), "Corridor should start at start position"
    assert corridor.cells[-1] == (5, 5), "Corridor should end at end position"


def test_dungeon_map_initialization():
    """Test dungeon map tile initialization."""
    dungeon = DungeonMap(20, 20)
    dungeon.initialize_tiles()
    
    assert len(dungeon.tiles) == 20, "Map should have correct height"
    assert len(dungeon.tiles[0]) == 20, "Map should have correct width"
    assert all(dungeon.tiles[y][x] == '#' for y in range(20) for x in range(20))


def test_dungeon_map_room_carving():
    """Test carving rooms into dungeon map."""
    dungeon = DungeonMap(30, 30)
    dungeon.initialize_tiles()
    
    room = Room(5, 5, 10, 10)
    dungeon.carve_room(room)
    
    # Check that room is carved
    for x in range(5, 15):
        for y in range(5, 15):
            assert dungeon.tiles[y][x] == '.', "Room tiles should be floor"
    
    # Check that surrounding tiles are walls
    assert dungeon.tiles[4][5] == '#', "Border should be walls"


def test_bsp_generator():
    """Test BSP dungeon generation."""
    generator = BSPDungeonGenerator(min_room_size=6, theme=AreaTheme.DUNGEON)
    dungeon = generator.generate(50, 50, seed=42)
    
    assert dungeon.width == 50
    assert dungeon.height == 50
    assert len(dungeon.rooms) > 0, "BSP should generate rooms"
    assert len(dungeon.corridors) > 0, "BSP should generate corridors"
    assert dungeon.count_open_tiles() > 0, "Map should have floor tiles"


def test_bsp_reproducibility():
    """Test that BSP generation is reproducible with same seed."""
    generator = BSPDungeonGenerator()
    
    dungeon1 = generator.generate(40, 40, seed=100)
    dungeon2 = generator.generate(40, 40, seed=100)
    
    # Check that both have same room count
    assert len(dungeon1.rooms) == len(dungeon2.rooms), "Same seed should generate same room count"
    
    # Check that tiles are identical
    for y in range(40):
        for x in range(40):
            assert dungeon1.tiles[y][x] == dungeon2.tiles[y][x], "Same seed should generate identical maps"


def test_cellular_automata_generator():
    """Test cellular automata dungeon generation."""
    generator = CellularAutomataDungeonGenerator(fill_probability=0.45, iterations=3, theme=AreaTheme.CAVE)
    dungeon = generator.generate(50, 50, seed=42)
    
    assert dungeon.width == 50
    assert dungeon.height == 50
    assert len(dungeon.rooms) > 0, "Cellular automata should extract rooms"
    assert dungeon.count_open_tiles() > 0, "Map should have floor tiles"


def test_cellular_automata_reproducibility():
    """Test that cellular automata generation is reproducible."""
    generator = CellularAutomataDungeonGenerator()
    
    dungeon1 = generator.generate(40, 40, seed=200)
    dungeon2 = generator.generate(40, 40, seed=200)
    
    for y in range(40):
        for x in range(40):
            assert dungeon1.tiles[y][x] == dungeon2.tiles[y][x], "Same seed should generate identical maps"


def test_simple_random_generator():
    """Test simple random dungeon generation."""
    generator = SimpleRandomDungeonGenerator(min_rooms=8, max_rooms=15, theme=AreaTheme.DUNGEON)
    dungeon = generator.generate(60, 60, seed=42)
    
    assert dungeon.width == 60
    assert dungeon.height == 60
    assert len(dungeon.rooms) >= 8, "Should generate minimum rooms"
    assert len(dungeon.rooms) <= 15, "Should respect maximum rooms"
    assert len(dungeon.corridors) > 0, "Should generate corridors"


def test_simple_random_reproducibility():
    """Test that simple random generation is reproducible."""
    generator = SimpleRandomDungeonGenerator()
    
    dungeon1 = generator.generate(40, 40, seed=300)
    dungeon2 = generator.generate(40, 40, seed=300)
    
    assert len(dungeon1.rooms) == len(dungeon2.rooms), "Same seed should generate same room count"


def test_room_features():
    """Test that room features are populated."""
    generator = SimpleRandomDungeonGenerator(min_rooms=10)
    dungeon = generator.generate(40, 40, seed=42)
    
    # Check that rooms have types assigned
    has_spawn = any(room.room_type == RoomType.SPAWN for room in dungeon.rooms)
    has_boss = any(room.room_type == RoomType.BOSS for room in dungeon.rooms)
    
    assert has_spawn, "Should have spawn room"
    assert has_boss, "Should have boss room"


def test_area_templates():
    """Test area template creation."""
    generator = AreaGenerator()
    
    # Check that templates exist for all themes
    assert AreaTheme.DUNGEON in generator.templates
    assert AreaTheme.CAVE in generator.templates
    assert AreaTheme.FOREST in generator.templates
    assert AreaTheme.RUINS in generator.templates
    assert AreaTheme.CASTLE in generator.templates
    assert AreaTheme.TEMPLE in generator.templates
    assert AreaTheme.SEWERS in generator.templates
    assert AreaTheme.UNDERGROUND_CITY in generator.templates


def test_area_generation_dungeon():
    """Test area generation with dungeon theme."""
    generator = AreaGenerator()
    dungeon = generator.generate_area(AreaTheme.DUNGEON, 40, 40, seed=42)
    
    assert dungeon.theme == AreaTheme.DUNGEON
    assert len(dungeon.rooms) > 0
    assert all(room.description != "" for room in dungeon.rooms)


def test_area_generation_cave():
    """Test area generation with cave theme."""
    generator = AreaGenerator()
    dungeon = generator.generate_area(AreaTheme.CAVE, 40, 40, seed=42)
    
    assert dungeon.theme == AreaTheme.CAVE
    assert len(dungeon.rooms) > 0


def test_area_generation_all_themes():
    """Test area generation for all themes."""
    generator = AreaGenerator()
    
    for theme in AreaTheme:
        dungeon = generator.generate_area(theme, 35, 35, seed=42)
        assert dungeon.theme == theme, f"Generated area should have theme {theme}"
        assert len(dungeon.rooms) > 0, f"Theme {theme} should generate rooms"


def test_procedure_encounter_generation():
    """Test encounter generation."""
    dungeon = DungeonMap(40, 40, theme=AreaTheme.DUNGEON)
    encounter = ProcedureGenerator.generate_encounter(dungeon, seed=42)
    
    assert "type" in encounter
    assert "difficulty" in encounter
    assert encounter["difficulty"] <= 1.0


def test_procedure_quest_generation():
    """Test quest generation."""
    dungeon = DungeonMap(40, 40, theme=AreaTheme.DUNGEON)
    quest = ProcedureGenerator.generate_quest(dungeon, seed=42)
    
    assert "name" in quest
    assert "difficulty" in quest
    assert "reward" in quest
    assert quest["difficulty"] >= 1 and quest["difficulty"] <= 10


def test_different_seeds_different_maps():
    """Test that different seeds produce different maps."""
    generator = SimpleRandomDungeonGenerator()
    
    dungeon1 = generator.generate(40, 40, seed=100)
    dungeon2 = generator.generate(40, 40, seed=200)
    
    # Different seeds might have different room counts
    tiles_match = 0
    total_tiles = 40 * 40
    
    for y in range(40):
        for x in range(40):
            if dungeon1.tiles[y][x] == dungeon2.tiles[y][x]:
                tiles_match += 1
    
    # Allow some similarity but maps should be different
    assert tiles_match < total_tiles - 50, "Different seeds should produce mostly different maps"


def test_dungeon_map_tile_access():
    """Test tile access with bounds checking."""
    dungeon = DungeonMap(20, 20)
    dungeon.initialize_tiles()
    
    # In bounds
    assert dungeon.get_tile(10, 10) == '#'
    
    # Out of bounds
    assert dungeon.get_tile(-1, 10) == '#'
    assert dungeon.get_tile(10, -1) == '#'
    assert dungeon.get_tile(100, 100) == '#'


def test_complex_generation_scenario():
    """Test complex scenario: generate dungeon, add features, validate."""
    # Create a 60x60 dungeon with BSP
    generator = BSPDungeonGenerator(min_room_size=8, theme=AreaTheme.CASTLE)
    dungeon = generator.generate(60, 60, seed=555)
    
    # Verify structure
    assert dungeon.seed == 555
    assert dungeon.width == 60
    assert dungeon.height == 60
    assert len(dungeon.rooms) > 3
    assert len(dungeon.corridors) > 0
    
    # Check all rooms are inside bounds
    for room in dungeon.rooms:
        assert room.x >= 0 and room.x + room.width <= dungeon.width
        assert room.y >= 0 and room.y + room.height <= dungeon.height
    
    # Check all corridors connect rooms
    assert len(dungeon.corridors) == len(dungeon.rooms) - 1


def test_area_density_parameters():
    """Test that area templates have density parameters."""
    generator = AreaGenerator()
    
    for theme, template in generator.templates.items():
        assert 0 <= template.monster_density <= 1
        assert 0 <= template.treasure_density <= 1
        assert 0 <= template.trap_density <= 1
        assert template.recommended_level > 0


def run_all_tests():
    """Run all procedural generation tests."""
    tests = [
        ("Room Creation", test_room_creation),
        ("Room Intersection", test_room_intersection),
        ("Room Overlap with Padding", test_room_overlap_with_padding),
        ("Corridor Creation", test_corridor_creation),
        ("Dungeon Map Initialization", test_dungeon_map_initialization),
        ("Dungeon Room Carving", test_dungeon_map_room_carving),
        ("BSP Generator", test_bsp_generator),
        ("BSP Reproducibility", test_bsp_reproducibility),
        ("Cellular Automata Generator", test_cellular_automata_generator),
        ("Cellular Automata Reproducibility", test_cellular_automata_reproducibility),
        ("Simple Random Generator", test_simple_random_generator),
        ("Simple Random Reproducibility", test_simple_random_reproducibility),
        ("Room Features", test_room_features),
        ("Area Templates", test_area_templates),
        ("Area Generation: Dungeon", test_area_generation_dungeon),
        ("Area Generation: Cave", test_area_generation_cave),
        ("Area Generation: All Themes", test_area_generation_all_themes),
        ("Procedure Encounter Generation", test_procedure_encounter_generation),
        ("Procedure Quest Generation", test_procedure_quest_generation),
        ("Different Seeds Different Maps", test_different_seeds_different_maps),
        ("Dungeon Tile Access", test_dungeon_map_tile_access),
        ("Complex Generation Scenario", test_complex_generation_scenario),
        ("Area Density Parameters", test_area_density_parameters),
    ]
    
    passed = 0
    failed = 0
    
    print("\n" + "="*70)
    print("PHASE V: PROCEDURAL GENERATION ENGINE - TEST RESULTS")
    print("="*70 + "\n")
    
    for test_name, test_func in tests:
        try:
            test_func()
            print(f"✓ {test_name}")
            passed += 1
        except AssertionError as e:
            print(f"✗ {test_name}: {str(e)}")
            failed += 1
        except Exception as e:
            print(f"✗ {test_name}: {type(e).__name__}: {str(e)}")
            failed += 1
    
    print("\n" + "="*70)
    print(f"RESULTS: {passed} passed, {failed} failed out of {len(tests)}")
    print("="*70 + "\n")
    
    return failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
