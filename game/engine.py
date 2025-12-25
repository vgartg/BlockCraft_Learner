import pygame
import sys
from game.renderer import Renderer

class GameEngine:    
    def __init__(self, config, blocks, player_config):
        """Инициализация"""
        pygame.init()
        
        self.config = config
        self.blocks = blocks
        self.player_config = player_config

        self.renderer = Renderer(config)
        self.load_textures()

        self.world = []
        self.generate_world()
        
        self.player = {
            'x': player_config['START_X'],
            'y': player_config['START_Y'],
            'color': player_config['COLOR'],
            'speed': player_config['SPEED'],
            'jump_power': player_config['JUMP_POWER'],
            'velocity_y': 0, # Скорость движения игрока по вертикали (=0 - стоит на месте; >0 - движется вверх; <0 - движется вниз)
            'on_ground': True # Находится ли игрок на земле
        }
        
        self.camera_x = 0
        self.camera_y = 0
        
        self.selected_block = 'grass' # Выбранный блок по умолчанию
        
        # Инвентарь
        self.inventory = {block: 10 for block in blocks.keys() if block != 'air'}
        
        self.clock = pygame.time.Clock() # FPS
        
        self.error_message = None # Состояние ошибки
        
        # Флаги для управления
        self.jump_just_pressed = False  # Флаг для одиночного нажатия прыжка
        self.jump_key_down = False  # Флаг для отслеживания состояния клавиши прыжка
    
    def load_textures(self):
        """Загружает текстуры"""
        for block_type, block_data in self.blocks.items():
            if 'texture' in block_data:
                self.renderer.load_block_texture(block_type, block_data['texture'])
    
    def generate_world(self):
        """Генерирует мир и всё его содержимое"""
        try:
            world_width = self.config['WORLD_WIDTH']
            world_height = self.config['WORLD_HEIGHT']
            
            # Создаем пустой мир (воздух)
            self.world = [['air' for _ in range(world_width)] 
                         for _ in range(world_height)]
            
            # Генерируем землю
            ground_level = world_height - 10
            for x in range(world_width):
                # Земля и трава
                for y in range(ground_level, world_height):
                    if y == ground_level:
                        self.world[y][x] = 'grass'
                    elif y < ground_level + 5:
                        self.world[y][x] = 'dirt'
                    else:
                        self.world[y][x] = 'stone'
                
                # Деревья
                if x % 10 == 0 and x > 10 and x < world_width - 10:
                    tree_height = 5
                    tree_x = x
                    tree_y = ground_level - 1
                    
                    # Ствол
                    for i in range(tree_height):
                        if tree_y - i >= 0:
                            self.world[tree_y - i][tree_x] = 'wood'
                    
                    # Листва вокруг ствола дерева
                    for dy in range(-2, 1):
                        for dx in range(-2, 3):
                            ly = tree_y - tree_height + dy
                            lx = tree_x + dx
                            if (0 <= lx < world_width and 0 <= ly < world_height and 
                                abs(dx) + abs(dy) < 4):
                                if self.world[ly][lx] == 'air':
                                    self.world[ly][lx] = 'leaf'
        except Exception as e:
            self.error_message = f"Произошла ошибка при генерации мира: {str(e)}"
            self.world = [['grass' if y == 10 else 'air' # Создаем простой мир при ошибке
                          for x in range(50)] 
                         for y in range(20)]
    
    def get_block_at(self, x, y):
        """Возвращает блок по координатам"""
        try:
            grid_x = int(x // self.config['BLOCK_SIZE'])
            grid_y = int(y // self.config['BLOCK_SIZE'])
            
            if (0 <= grid_y < len(self.world) and 
                0 <= grid_x < len(self.world[0])):
                return self.world[grid_y][grid_x], grid_x, grid_y
        except:
            pass
        return 'air', -1, -1
    
    def can_place_block(self, grid_x, grid_y):
        """Проверяет, можно ли поставить блок в указанную позицию"""
        # Проверяем, что блок ставится с опорой (есть блок снизу или сбоку)
        neighbors = [
            (grid_x, grid_y + 1),  # снизу
            (grid_x - 1, grid_y),  # слева
            (grid_x + 1, grid_y),  # справа
        ]
        
        for nx, ny in neighbors:
            if 0 <= ny < len(self.world) and 0 <= nx < len(self.world[0]):
                if self.world[ny][nx] != 'air':
                    return True
        
        return False
    
    def place_block(self, x, y, block_type):
        """Ставит блок в мире"""
        try:
            _, grid_x, grid_y = self.get_block_at(x, y)
            if (grid_x >= 0 and grid_y >= 0 and 
                block_type in self.inventory and 
                self.inventory[block_type] > 0):
                
                # Проверяем, что выбранная координата не занята другим блоком
                if self.world[grid_y][grid_x] != 'air':
                    return False
                
                # Проверяем, что блок можно поставить (есть опора)
                if not self.can_place_block(grid_x, grid_y):
                    return False
                
                # Проверяем, что блок не ставится внутри модельки игрока
                player_rect = pygame.Rect(
                    self.player['x'],
                    self.player['y'],
                    self.config['BLOCK_SIZE'],
                    self.config['BLOCK_SIZE'] * 2
                )
                
                block_rect = pygame.Rect(
                    grid_x * self.config['BLOCK_SIZE'],
                    grid_y * self.config['BLOCK_SIZE'],
                    self.config['BLOCK_SIZE'],
                    self.config['BLOCK_SIZE']
                )
                
                if player_rect.colliderect(block_rect):
                    return False
                
                self.world[grid_y][grid_x] = block_type
                self.inventory[block_type] -= 1
                return True
        except:
            pass
        return False

    def choose_block_in_ui(self, x, y):
        """Выбирает блок через нажатие мыши в UI"""
        try:
            inv_x = 210
            selected_y = self.config['SCREEN_HEIGHT'] - 50

            if not (selected_y <= y <= selected_y + 44): # Проверяем попадание по вертикали в раздел инвентаря
                return False
                
            # Создаем список блоков
            available_blocks = [block for block, count in self.inventory.items()]
            
            # Проверяем попадание по горизонтали
            for i, block_type in enumerate(available_blocks):
                block_x = inv_x + i * 60
                if block_x <= x <= block_x + 44:
                    self.selected_block = block_type
                    return True
        except:
            pass
        return False            
    
    def break_block(self, x, y):
        """Разрушает блок"""
        try:
            block_type, grid_x, grid_y = self.get_block_at(x, y)
            block_info = self.blocks.get(block_type, {})
            if (grid_x >= 0 and grid_y >= 0 and 
                block_type != 'air' and block_info.get('breakable')):

                self.world[grid_y][grid_x] = 'air'
                if block_type in self.inventory:
                    self.inventory[block_type] += 1
                else:
                    self.inventory[block_type] = 1
                return True
        except:
            pass
        return False
    
    def check_collision(self, x, y, width, height):
        """Проверяет столкновение игрока с блоками"""
        # Получаем индексы блоков, с которыми может пересекаться игрок
        left = int(x // self.config['BLOCK_SIZE'])
        right = int((x + width - 1) // self.config['BLOCK_SIZE'])
        top = int(y // self.config['BLOCK_SIZE'])
        bottom = int((y + height - 1) // self.config['BLOCK_SIZE'])
        
        # Перебираем блоки в этой области
        for block_y in range(top, bottom + 1):
            for block_x in range(left, right + 1):
                if (0 <= block_y < len(self.world) and 
                    0 <= block_x < len(self.world[0])):
                    
                    block_type = self.world[block_y][block_x]
                    # Проверяем, является ли блок твердым
                    if block_type != 'air' and self.blocks.get(block_type, {}).get('solid', True):
                        block_rect = pygame.Rect(
                            block_x * self.config['BLOCK_SIZE'],
                            block_y * self.config['BLOCK_SIZE'],
                            self.config['BLOCK_SIZE'],
                            self.config['BLOCK_SIZE']
                        )
                        
                        player_rect = pygame.Rect(x, y, width, height)
                        
                        if player_rect.colliderect(block_rect):
                            return True
        return False
    
    def handle_events(self):
        """Обрабатывает события"""
        self.jump_just_pressed = False # Сбрасываем флаг одиночного нажатия прыжка
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            
            elif event.type == pygame.KEYDOWN:
                # Выход из игры
                if event.key in [pygame.K_ESCAPE, pygame.K_F4]:
                    return False
                
                # Выбор блока
                if event.key in [pygame.K_1, pygame.K_KP1]:
                    self.selected_block = 'grass'
                elif event.key in [pygame.K_2, pygame.K_KP2]:
                    self.selected_block = 'dirt'
                elif event.key in [pygame.K_3, pygame.K_KP3]:
                    self.selected_block = 'stone'
                elif event.key in [pygame.K_4, pygame.K_KP4]:
                    self.selected_block = 'wood'
                elif event.key in [pygame.K_5, pygame.K_KP5]:
                    self.selected_block = 'leaf'
                elif event.key in [pygame.K_6, pygame.K_KP6]: # Ищем пользовательские блоки
                    custom_blocks = [b for b in self.blocks.keys() 
                                   if b not in ['air', 'grass', 'dirt', 'stone', 'wood', 'leaf']]
                    if custom_blocks:
                        self.selected_block = custom_blocks[0]
                elif event.key in [pygame.K_7, pygame.K_KP7]:
                    custom_blocks = [b for b in self.blocks.keys() 
                                   if b not in ['air', 'grass', 'dirt', 'stone', 'wood', 'leaf']]
                    if len(custom_blocks) > 1:
                        self.selected_block = custom_blocks[1]
                elif event.key in [pygame.K_8, pygame.K_KP8]:
                    custom_blocks = [b for b in self.blocks.keys() 
                                   if b not in ['air', 'grass', 'dirt', 'stone', 'wood', 'leaf']]
                    if len(custom_blocks) > 2:
                        self.selected_block = custom_blocks[2]
                
                # Прыжок
                if event.key in [pygame.K_w, pygame.K_UP, pygame.K_SPACE]:
                    self.jump_just_pressed = True
                    self.jump_key_down = True
            
            elif event.type == pygame.KEYUP: # Отслеживаем отпускание клавиши прыжка
                if event.key in [pygame.K_w, pygame.K_UP, pygame.K_SPACE]:
                    self.jump_key_down = False
            
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_x, mouse_y = pygame.mouse.get_pos()

                if mouse_y >= self.config['SCREEN_HEIGHT'] - 60 and event.button == 1: # Попали мышкой в UI-блок
                    self.choose_block_in_ui(mouse_x, mouse_y)
                else:
                    world_x = mouse_x + self.camera_x
                    world_y = mouse_y + self.camera_y
                    
                    if event.button == 1:  # Вызываем функцию разрушения блока
                        self.break_block(world_x, world_y)
                    elif event.button == 3:  # Вызываем функцию постановки блока
                        self.place_block(world_x, world_y, self.selected_block)

        return True
    
    def update_player(self):
        """Обновляет состояние игрока"""
        keys = pygame.key.get_pressed() # Получаем состояние всех клавиш
        
        dx = 0
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            dx -= self.player['speed']
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            dx += self.player['speed']
        
        if dx != 0:
            new_x = self.player['x'] + dx
            player_width = self.config['BLOCK_SIZE']
            player_height = self.config['BLOCK_SIZE'] * 2
            
            # Проверяем коллизию на новой позиции
            if not self.check_collision(new_x, self.player['y'], player_width, player_height):
                self.player['x'] = new_x
            else: # При наличии коллизии пробуем сдвинуться на 1 пиксель за несколько попыток
                for offset in range(1, int(abs(dx)) + 1):
                    test_x = self.player['x'] + (1 if dx > 0 else -1)
                    if not self.check_collision(test_x, self.player['y'], player_width, player_height):
                        self.player['x'] = test_x
                    else:
                        break
        
        if self.jump_just_pressed and self.player['on_ground']: # Прыжок
            self.player['velocity_y'] = -self.player['jump_power']
            self.player['on_ground'] = False
        
        
        self.player['velocity_y'] += self.config['GRAVITY'] # Гравитация
        dy = self.player['velocity_y'] # Движение по вертикали
        
        if dy != 0:
            new_y = self.player['y'] + dy
            player_width = self.config['BLOCK_SIZE']
            player_height = self.config['BLOCK_SIZE'] * 2
            
            # Проверяем коллизию на новой позиции
            if not self.check_collision(self.player['x'], new_y, player_width, player_height):
                self.player['y'] = new_y
                self.player['on_ground'] = False
            else: # Если нашли коллизия
                if dy > 0:  # Падение вниз
                    self.player['on_ground'] = True
                    self.player['velocity_y'] = 0
                    
                    # Находим точное положение над блоком
                    for offset in range(1, int(abs(dy)) + 1):
                        test_y = self.player['y'] + 1
                        if not self.check_collision(self.player['x'], test_y, player_width, player_height):
                            self.player['y'] = test_y
                        else:
                            break
                else:  # Движение вверх
                    self.player['velocity_y'] = 0
        
        # Проверяем, стоит ли игрок на земле
        if not self.player['on_ground']:
            player_width = self.config['BLOCK_SIZE']
            player_height = self.config['BLOCK_SIZE'] * 2
            if self.check_collision(self.player['x'], self.player['y'] + 1, player_width, player_height):
                self.player['on_ground'] = True
        
        # Ограничение мира по горизонтали
        world_width = self.config['WORLD_WIDTH'] * self.config['BLOCK_SIZE']
        self.player['x'] = max(0, min(self.player['x'], world_width - self.config['BLOCK_SIZE']))
        
        # Обновление камеры
        self.camera_x = self.player['x'] - self.config['SCREEN_WIDTH'] // 2
        self.camera_y = self.player['y'] - self.config['SCREEN_HEIGHT'] // 2
        
        # Ограничение камеры
        self.camera_x = max(0, min(self.camera_x, 
                                 world_width - self.config['SCREEN_WIDTH']))
        
        world_height = self.config['WORLD_HEIGHT'] * self.config['BLOCK_SIZE']
        self.camera_y = max(0, min(self.camera_y, 
                                 world_height - self.config['SCREEN_HEIGHT']))
    
    def run(self):
        """Запускает весь игровой цикл"""
        running = True
        
        while running:
            running = self.handle_events()

            self.update_player()

            self.renderer.draw_world(self.world, self.camera_x, self.camera_y)
            self.renderer.draw_player(self.player, self.camera_x, self.camera_y)

            fps = int(self.clock.get_fps())
            
            self.renderer.draw_hud(self.player, self.selected_block, 
                                 self.inventory, fps, self.blocks)
            
            if self.error_message:
                self.renderer.draw_error(self.error_message)
            
            pygame.display.flip()
            self.clock.tick(self.config['FPS'])