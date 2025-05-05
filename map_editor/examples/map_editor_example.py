import pygame
from map_editor import generate_map
from data import Facing

# 게임용 Platform 클래스
class Platform(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height, color=(0,255,0)):
        super().__init__()
        self.image = pygame.Surface((width, height))
        self.image.fill(color)
        self.rect = self.image.get_rect(topleft=(x,y))

# 맵 설계(spec) 정의
spec = {
    "rows": 3,
    "cols": 5,
    "tile_size": 64,
    "gap": 0,
    "start_x": 50,
    "start_y": 350,
    "color": [0,255,0]
}

# generate_map 으로 플랫폼 데이터 생성
platform_data = generate_map(spec)
platforms = pygame.sprite.Group()
for p in platform_data:
    platforms.add(Platform(p.x, p.y, p.width, p.height, p.color))

# Pygame 초기화
pygame.init()
WIDTH, HEIGHT = 640, 480
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    screen.fill((0, 0, 0))
    platforms.draw(screen)
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
