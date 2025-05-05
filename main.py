import os
import pygame
import math
from data import Facing
from map_editor.core import load_platforms
from value_plotter import plot_value

# 기본 설정
WIDTH = 640
HEIGHT = 480
FPS = 60
TILE_SIZE = 40

# 파이게임 초기화
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Platformer Game")
clock = pygame.time.Clock()

# 폰트 초기화
font = pygame.font.SysFont(None, 24)

# Platform 클래스
class Platform(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height, color=(0,255,0)):
        super().__init__()
        self.image = pygame.Surface((width, height))
        self.image.fill(color)
        self.rect = self.image.get_rect(topleft=(x,y))

# Player 클래스
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image_idle = pygame.image.load(os.path.join('assets', 'Idle.png')).convert_alpha()
        self.image_idle = pygame.transform.scale(self.image_idle, (TILE_SIZE, TILE_SIZE))
        self.image_move = pygame.image.load(os.path.join('assets', 'Move.png')).convert_alpha()
        self.image_move = pygame.transform.scale(self.image_move, (TILE_SIZE, TILE_SIZE))
        self.image = self.image_idle
        self.rect = self.image.get_rect()
        self.rect.x = 100
        self.rect.y = 100
        self.facing_right = True
        self.facing_angle_deg = 0
        self.facing_clamp = Facing.NORTH

        self.velocity_x = 0
        self.velocity_y = 0
        self.max_velocity_x = 6
        self.gravity_const = 0.5
        self.jump_power = -12
        self.push_skill_power = 7
        self.acceleration = 0.5
        self.friction = 0.5
        self.is_jumping = False
        self.can_push = True  # 새로운 변수 추가: 푸시 스킬 사용 가능 여부
        self.on_ground = False

    def update(self, keys):
        # 이동 처리
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.velocity_x -= self.acceleration
            if self.facing_right:
                self.facing_right = False
        elif keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.velocity_x += self.acceleration
            if not self.facing_right:
                self.facing_right = True
        elif keys[pygame.K_c] and self.can_push:
            self.can_push = False
            if self.facing_clamp == Facing.NORTH:
                self.velocity_y = self.push_skill_power
            elif self.facing_clamp == Facing.SOUTH:
                self.velocity_y = -self.push_skill_power
            elif self.facing_clamp == Facing.EAST:
                self.velocity_x = -self.push_skill_power
            elif self.facing_clamp == Facing.WEST:
                self.velocity_x = self.push_skill_power
        else:
            self.apply_friction()

        self.velocity_x = max(-self.max_velocity_x, min(self.velocity_x, self.max_velocity_x))

        if keys[pygame.K_UP] or keys[pygame.K_w] or keys[pygame.K_SPACE]:
            if self.on_ground:
                self.jump()

        # X축 이동
        self.rect.x += self.velocity_x

        # Y축 이동
        self.velocity_y += self.gravity_const
        old_bottom = self.rect.bottom
        self.rect.y += self.velocity_y

        # 플랫폼 충돌 처리
        self.on_ground = False
        for platform in platforms:
            if self.rect.colliderect(platform.rect):
                # 위에서 떨어질 때 (착지)
                if self.velocity_y > 0 and old_bottom <= platform.rect.top < self.rect.bottom:
                    self.rect.bottom = platform.rect.top
                    self.velocity_y = 0
                    self.on_ground = True
                    self.can_push = True
                # 아래에서 점프해 부딪힐 때
                elif self.velocity_y < 0 and self.rect.top <= platform.rect.bottom < self.rect.top - self.velocity_y:
                    self.rect.top = platform.rect.bottom
                    self.velocity_y = 0
                # 왼쪽 또는 오른쪽으로 부딪힐 때 (수평 충돌 처리)
                if self.velocity_x > 0 and self.rect.right > platform.rect.left and self.rect.left < platform.rect.left:
                    self.rect.right = platform.rect.left
                    self.velocity_x = 0  # 수평 속도 0
                elif self.velocity_x < 0 and self.rect.left < platform.rect.right and self.rect.right > platform.rect.right:
                    self.rect.left = platform.rect.right
                    self.velocity_x = 0  # 수평 속도 0

        # 바닥과 충돌
        if self.rect.bottom > HEIGHT:
            self.rect.bottom = HEIGHT
            self.velocity_y = 0
            self.on_ground = True
            self.can_push = True

        # 이미지 설정
        if abs(self.velocity_x) > 0.5:
            self.image = self.image_move if self.facing_right else pygame.transform.flip(self.image_move, True, False)
        else:
            self.image = self.image_idle if self.facing_right else pygame.transform.flip(self.image_idle, True, False)

        # 화면 경계 제한
        if self.rect.left < 0:
            self.rect.left = 0
            self.velocity_x = 0
        if self.rect.right > WIDTH:
            self.rect.right = WIDTH
            self.velocity_x = 0
        if self.rect.top < 0:
            self.rect.top = 0
            self.velocity_y = 0

        # 마우스 방향 계산
        mousePos = pygame.mouse.get_pos()
        self.facing_angle_deg = math.degrees(
            math.atan2(
                -(mousePos[1] - self.rect.y),
                mousePos[0] - self.rect.x
            )
        )
        self.facing_angle_deg = (self.facing_angle_deg + 360) % 360
        if 45 <= self.facing_angle_deg < 135:
            self.facing_clamp = Facing.NORTH
        elif 135 <= self.facing_angle_deg < 225:
            self.facing_clamp = Facing.WEST
        elif 225 <= self.facing_angle_deg < 315:
            self.facing_clamp = Facing.SOUTH
        else:
            self.facing_clamp = Facing.EAST

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

# 맵 데이터 로드
platforms = pygame.sprite.Group()
loaded = load_platforms("./map_editor/tester.json")
for p in loaded:
    platforms.add(Platform(p.x, p.y, p.width, p.height, p.color))

# 스프라이트 그룹
all_sprites = pygame.sprite.Group()
player = Player()
all_sprites.add(player)
all_sprites.add(*platforms)

# 메인 루프
running = True
while running:
    clock.tick(FPS)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    keys = pygame.key.get_pressed()
    player.update(keys)
    screen.fill((0, 0, 0))
    all_sprites.draw(screen)
    fps_text = font.render(f"FPS: {clock.get_fps():.1f}", True, (255,255,255))
    screen.blit(fps_text, (10,10))
    pygame.display.flip()

pygame.quit()
