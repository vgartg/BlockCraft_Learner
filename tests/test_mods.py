from mods.my_blocks import BLOCKS
from mods.my_config import GAME_CONFIG
from mods.my_player import PLAYER_CONFIG


def test_game_config_has_required_keys():
    expected = {
        'SCREEN_WIDTH',
        'SCREEN_HEIGHT',
        'GAME_TITLE',
        'BLOCK_SIZE',
        'WORLD_WIDTH',
        'WORLD_HEIGHT',
        'GRAVITY',
        'FPS',
        'SKY_COLOR',
    }
    assert expected <= GAME_CONFIG.keys()
    assert GAME_CONFIG['BLOCK_SIZE'] > 0
    assert GAME_CONFIG['FPS'] > 0


def test_player_config_has_required_keys():
    expected = {'START_X', 'START_Y', 'COLOR', 'SPEED', 'JUMP_POWER'}
    assert expected <= PLAYER_CONFIG.keys()
    assert PLAYER_CONFIG['SPEED'] > 0
    assert PLAYER_CONFIG['JUMP_POWER'] > 0
    assert len(PLAYER_CONFIG['COLOR']) == 3


def test_blocks_contract():
    assert 'air' in BLOCKS
    for name, props in BLOCKS.items():
        assert 'name' in props, f"block {name} missing 'name'"
        assert 'breakable' in props, f"block {name} missing 'breakable'"
        assert 'solid' in props, f"block {name} missing 'solid'"
    assert BLOCKS['air']['solid'] is False
    assert BLOCKS['air']['breakable'] is False
