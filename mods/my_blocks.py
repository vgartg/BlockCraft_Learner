"""
Блоки игры
Здесь определяются все типы блоков в игре
"""

BLOCKS = { # Определяется список блоков
    'air': { # Названия для обращения к блоку
        'name': 'Воздух', # Название блока на русском для отображения
        'breakable': False, # Можно ли сломать блок (False - нельзя сломать; True - можно)
        'solid': False,  # Является ли блок твердым (False - не твердый, можно проходить через него; True - твердый, нельзя проходить насквозь)
    },
    
    'grass': {
        'name': 'Трава',
        'breakable': True,
        'solid': True,
        'texture': 'assets/textures/grass.png',  # Путь к файлу текстуры из папки /assets/textures
        # Если не указывать текстуру, будет подставляться RGB-цвет, который определен в функции ядра игры get_block_color
    },
    
    'dirt': {
        'name': 'Земля',
        'breakable': True,
        'solid': True,
        'texture': 'assets/textures/dirt.png',
    },
    
    'stone': {
        'name': 'Камень',
        'breakable': True,
        'solid': True,
        'texture': 'assets/textures/stone.png',
    },
    
    'wood': {
        'name': 'Дерево',
        'breakable': True,
        'solid': True,
        'texture': 'assets/textures/wood.png',
    },
    
    'leaf': {
        'name': 'Листва',
        'breakable': True,
        'solid': False,  # Листва не твердая - можно пройти сквозь (аналогично воздуху)
        'texture': 'assets/textures/leaf.png',
    },

    # Можно добавить новые блоки со своими параметрами. Например:
    # 'brick': {
    #     'name': 'Кирпич',
    #     'breakable': True,
    #     'solid': True,
    #     'texture': 'path/to/file.png',
    # }
}