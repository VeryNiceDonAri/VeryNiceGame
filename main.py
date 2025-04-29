import os

import pygame
import math
from data import Facing

# 기본 설정
WIDTH = 1920
HEIGHT = 1080
TILE_SIZE = 40
FPS = 60

# 파이게임 초기화
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Platformer Game")
clock = pygame.time.Clock()

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
        self.acceleration = 0.5
        self.friction = 0.5
        self.is_jumping = False
        self.on_ground = False

    def update(self, keys):
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

        self.velocity_y += self.gravity_const
        self.rect.y += self.velocity_y

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
        print(self.facing_clamp)

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

# 메인 코드
player = Player()
all_sprites = pygame.sprite.Group()

all_sprites.add(player)

running = True
mousePos = (0, 0)
while running:
    clock.tick(FPS)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    keys = pygame.key.get_pressed()
    player.update(keys)

    screen.fill((0, 0, 0))
    all_sprites.draw(screen)
    pygame.display.update()

pygame.quit()
