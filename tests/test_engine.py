from blockcraft import GameEngine
from mods.my_blocks import BLOCKS
from mods.my_config import GAME_CONFIG
from mods.my_player import PLAYER_CONFIG


def make_engine():
    return GameEngine(GAME_CONFIG, BLOCKS, PLAYER_CONFIG)


def test_engine_initialises_world():
    engine = make_engine()
    assert len(engine.world) == GAME_CONFIG['WORLD_HEIGHT']
    assert len(engine.world[0]) == GAME_CONFIG['WORLD_WIDTH']
    assert engine.player['x'] == PLAYER_CONFIG['START_X']
    assert engine.player['y'] == PLAYER_CONFIG['START_Y']


def test_inventory_excludes_air():
    engine = make_engine()
    assert 'air' not in engine.inventory
    for block in BLOCKS:
        if block == 'air':
            continue
        assert engine.inventory[block] == 10


def test_get_block_at_inside_world():
    engine = make_engine()
    block, gx, gy = engine.get_block_at(0, 0)
    assert (gx, gy) == (0, 0)
    assert block in BLOCKS


def test_break_block_marks_air():
    engine = make_engine()
    bs = GAME_CONFIG['BLOCK_SIZE']
    target_x = 5 * bs
    target_y = (GAME_CONFIG['WORLD_HEIGHT'] - 10) * bs
    block, gx, gy = engine.get_block_at(target_x, target_y)
    assert block == 'grass'
    assert engine.break_block(target_x, target_y) is True
    assert engine.world[gy][gx] == 'air'
