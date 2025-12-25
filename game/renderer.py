import pygame
from game.utils import draw_text, load_image

class Renderer:
    def __init__(self, config):
        """Инициализация"""
        self.config = config
        self.screen = pygame.display.set_mode(
            (config['SCREEN_WIDTH'], config['SCREEN_HEIGHT'])
        )
        pygame.display.set_caption(config['GAME_TITLE'])
        
        self.block_textures = {}
        
    def load_block_texture(self, block_type, texture_path):
        try:
            texture = load_image(texture_path, (self.config['BLOCK_SIZE'], self.config['BLOCK_SIZE']))
            self.block_textures[block_type] = texture
        except Exception as e:
            print(f"Не удалось загрузить текстуру для {block_type}: {e}. Подгружаем RGB-текстуру!")
            texture = pygame.Surface((self.config['BLOCK_SIZE'], self.config['BLOCK_SIZE']), pygame.SRCALPHA)
            texture.fill((100, 100, 100))
            pygame.draw.rect(texture, (50, 50, 50), texture.get_rect(), 2)
            self.block_textures[block_type] = texture
    
    def draw_block(self, x, y, block_type):
        """Отрисовка блока"""
        x_int = int(x)
        y_int = int(y)
        
        if block_type in self.block_textures:
            self.screen.blit(self.block_textures[block_type], (x_int, y_int))
        else:
            color = self.get_block_color(block_type)
            pygame.draw.rect(self.screen, color, 
                           (x_int, y_int, self.config['BLOCK_SIZE'], self.config['BLOCK_SIZE']))
            pygame.draw.rect(self.screen, (color[0]//2, color[1]//2, color[2]//2), 
                           (x_int, y_int, self.config['BLOCK_SIZE'], self.config['BLOCK_SIZE']), 2)
    
    def get_block_color(self, block_type):
        """Отрисовка текстуры блока"""
        colors = {
            'air': (100, 150, 255),
            'grass': (100, 200, 100),
            'dirt': (139, 69, 19),
            'stone': (128, 128, 128),
            'wood': (101, 67, 33),
            'leaf': (50, 150, 50),
            'glass': (150, 200, 255),
            'brick': (200, 100, 100),
        }
        return colors.get(block_type, (255, 0, 255))  # Для неизвестных блоков
    
    def draw_world(self, world, camera_x, camera_y):
        """Отрисовка мира"""
        self.screen.fill(self.config['SKY_COLOR'])
        
        # Отрисовка блоков
        block_size = self.config['BLOCK_SIZE']
        screen_width = self.config['SCREEN_WIDTH']
        screen_height = self.config['SCREEN_HEIGHT']
        
        start_x = max(0, int(camera_x // block_size) - 1)
        end_x = min(len(world[0]), int((camera_x + screen_width) // block_size) + 2)
        start_y = max(0, int(camera_y // block_size) - 1)
        end_y = min(len(world), int((camera_y + screen_height) // block_size) + 2)
        
        for y in range(start_y, end_y):
            for x in range(start_x, end_x):
                block = world[y][x]
                screen_x = x * block_size - camera_x
                screen_y = y * block_size - camera_y
                
                screen_x_int = int(screen_x)
                screen_y_int = int(screen_y)
                
                if (-block_size <= screen_x_int <= screen_width and
                    -block_size <= screen_y_int <= screen_height):
                    self.draw_block(screen_x_int, screen_y_int, block)
    
    def draw_player(self, player, camera_x, camera_y):
        """Отрисовка игрока"""
        screen_x = int(player['x'] - camera_x)
        screen_y = int(player['y'] - camera_y)

        pygame.draw.rect(self.screen, player['color'], # Тело игрока
                        (screen_x, screen_y, 
                         self.config['BLOCK_SIZE'], 
                         self.config['BLOCK_SIZE'] * 2))
        
        # Глаза (Белым блоком)
        eye_size = self.config['BLOCK_SIZE'] // 4
        pygame.draw.rect(self.screen, (255, 255, 255), 
                        (screen_x + eye_size, screen_y + eye_size, 
                         eye_size, eye_size))
        pygame.draw.rect(self.screen, (255, 255, 255),
                        (screen_x + self.config['BLOCK_SIZE'] - eye_size*2, 
                         screen_y + eye_size, eye_size, eye_size))
    
    def draw_hud(self, player, selected_block, inventory, fps, blocks):
        """Отрисовка UI"""
        # Панель выбора блока
        panel_height = 60
        pygame.draw.rect(self.screen, (50, 50, 50, 200), 
                        (0, self.config['SCREEN_HEIGHT'] - panel_height, 
                         self.config['SCREEN_WIDTH'], panel_height))
        
        # Отображение выбранного блока
        selected_x = 20
        selected_y = self.config['SCREEN_HEIGHT'] - panel_height + 10
        color = (255, 255, 255) if inventory.get(selected_block, 0) > 0 else (255, 0, 0) # В зависимости от количества выбранного блока
        pygame.draw.rect(self.screen, color, 
                        (selected_x - 2, selected_y - 2, 
                         44, 44), 2)
        self.draw_block(selected_x, selected_y, selected_block)
        
        # Название выбранного блока
        block_info = blocks.get(selected_block, {})
        block_name = block_info.get('name', selected_block)
        draw_text(self.screen, f"Выбран: {block_name}", 
                 (selected_x + 50, selected_y + 10), 24, (255, 255, 255))
        
        # Координаты игрока
        draw_text(self.screen, f"X: {int(player['x'])} Y: {int(player['y'])}", 
                 (10, 10), 20, (255, 255, 255))
        
        # FPS
        draw_text(self.screen, f"FPS: {fps}", 
                 (self.config['SCREEN_WIDTH'] - 100, 10), 20, (255, 255, 255))
        
        # Инвентарь
        inv_x = 210
        for i, (block_type, count) in enumerate(inventory.items()):
            block_color = (255, 255, 255) if count > 0 else (255, 0, 0)
            text_color = (255, 255, 0) if count > 0 else (255, 0, 0)
            if selected_block == block_type:
                    pygame.draw.rect(self.screen, block_color, 
                        (inv_x + i * 60 - 2, selected_y - 2, 
                         44, 44), 2)
            self.draw_block(inv_x + i * 60, selected_y, block_type)
            draw_text(self.screen, str(count),
                        (inv_x + i * 60 + 30, selected_y + 30), 16, text_color)