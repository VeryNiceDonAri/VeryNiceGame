import os
import pygame

# 기본 설정
WIDTH = 640
HEIGHT = 480
TILE_SIZE = 40
FPS = 60

# 파이게임 초기화
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Platformer Game")
clock = pygame.time.Clock()

# 레벨 데이터 (2차원 배열)
level_map = [
    "000000000000000",
    "000000000000000",
    "000001110000000",
    "000000010000000",
    "001111111110000",
    "000000000000000",
    "000000000011100",
    "000000000001000",
    "111111111111111",
]

# Player 클래스
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image_idle = pygame.image.load(os.path.join('../assets', 'Idle.png')).convert_alpha()
        self.image_idle = pygame.transform.scale(self.image_idle, (TILE_SIZE, TILE_SIZE))
        self.image_move = pygame.image.load(os.path.join('../assets', 'Move.png')).convert_alpha()
        self.image_move = pygame.transform.scale(self.image_move, (TILE_SIZE, TILE_SIZE))
        self.image = self.image_idle
        self.rect = self.image.get_rect()
        self.rect.x = 100
        self.rect.y = 100
        self.facing_right = True

        self.velocity_x = 0
        self.velocity_y = 0
        self.max_velocity_x = 6
        self.gravity_const = 0.5
        self.jump_power = -12
        self.acceleration = 0.5
        self.friction = 0.5
        self.is_jumping = False
        self.on_ground = False

    def update(self, keys, platforms):
        # 이동
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.velocity_x -= self.acceleration
            if self.facing_right:
                self.facing_right = False
        elif keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.velocity_x += self.acceleration
            if not self.facing_right:
                self.facing_right = True
        else:
            self.apply_friction()

        self.velocity_x = max(-self.max_velocity_x, min(self.velocity_x, self.max_velocity_x))

        if (keys[pygame.K_UP] or keys[pygame.K_w] or keys[pygame.K_SPACE]):
            if self.on_ground:
                self.jump()

        self.rect.x += self.velocity_x
        self.check_collision_x(platforms)

        self.velocity_y += self.gravity_const
        self.rect.y += self.velocity_y
        self.check_collision_y(platforms)

        if abs(self.velocity_x) > 0.5:
            self.image = self.image_move if self.facing_right else pygame.transform.flip(self.image_move, True, False)
        else:
            self.image = self.image_idle if self.facing_right else pygame.transform.flip(self.image_idle, True, False)

        # 화면 밖 제한
        if self.rect.left < 0:
            self.rect.left = 0
            self.velocity_x = 0
        if self.rect.right > WIDTH:
            self.rect.right = WIDTH
            self.velocity_x = 0
        if self.rect.top < 0:
            self.rect.top = 0
            self.velocity_y = 0
        if self.rect.bottom > HEIGHT:
            self.rect.bottom = HEIGHT
            self.velocity_y = 0
            self.on_ground = True

    def apply_friction(self):
        if abs(self.velocity_x) > 0:
            if self.velocity_x > 0:
                self.velocity_x -= self.friction
                if self.velocity_x < 0:
                    self.velocity_x = 0
            else:
                self.velocity_x += self.friction
                if self.velocity_x > 0:
                    self.velocity_x = 0

    def jump(self):
        self.velocity_y = self.jump_power
        self.is_jumping = True
        self.on_ground = False

    def check_collision_x(self, platforms):
        hits = pygame.sprite.spritecollide(self, platforms, False)
        for platform in hits:
            if self.velocity_x > 0:
                self.rect.right = platform.rect.left
            elif self.velocity_x < 0:
                self.rect.left = platform.rect.right
            self.velocity_x = 0

    def check_collision_y(self, platforms):
        self.on_ground = False
        hits = pygame.sprite.spritecollide(self, platforms, False)
        for platform in hits:
            if self.velocity_y > 0:
                self.rect.bottom = platform.rect.top
                self.velocity_y = 0
                self.on_ground = True
                self.is_jumping = False
            elif self.velocity_y < 0:
                self.rect.top = platform.rect.bottom
                self.velocity_y = 0

# Platform 클래스
class Platform(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height):
        super().__init__()
        self.image = pygame.Surface((width, height))
        self.image.fill((0, 255, 0))  # 초록색
        self.rect = self.image.get_rect(topleft=(x, y))

# 맵 만들기
def load_map(level_data):
    platforms = pygame.sprite.Group()
    for row_idx, row in enumerate(level_data):
        for col_idx, tile in enumerate(row):
            if tile == "1":
                x = col_idx * TILE_SIZE
                y = row_idx * TILE_SIZE
                platform = Platform(x, y, TILE_SIZE, TILE_SIZE)
                platforms.add(platform)
    return platforms

# 메인 코드
player = Player()
all_sprites = pygame.sprite.Group()
platforms = load_map(level_map)

all_sprites.add(player)
all_sprites.add(platforms)

running = True
while running:
    clock.tick(FPS)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    keys = pygame.key.get_pressed()
    player.update(keys, platforms)

    screen.fill((0, 0, 0))
    all_sprites.draw(screen)
    pygame.display.update()

pygame.quit()
