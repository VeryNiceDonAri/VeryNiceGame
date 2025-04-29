import pygame
import sys

# 초기화
pygame.init()

# 화면 설정
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("중력 가속도 운동 시뮬레이션")

# 색상
WHITE = (255, 255, 255)
RED = (255, 0, 0)

# 물체 속성
x = WIDTH // 2
y = 100          # 초기 높이
radius = 20

# 운동 관련 변수
velocity_y = 0    # 초기 속도
g = 9.8           # 중력가속도 (m/s²)
dt = 0.016        # 시간 간격 (초) (약 60fps)

# 바닥
floor = HEIGHT - radius

# 메인 루프
clock = pygame.time.Clock()
running = True
while running:
    clock.tick(60)  # 60 FPS

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # 중력 적용 (속도 증가)
    velocity_y += g * dt

    # 위치 업데이트
    y += velocity_y

    # 바닥에 닿으면 멈추게
    if y >= floor:
        y = floor
        velocity_y = 0

    # 화면 그리기
    screen.fill(WHITE)
    pygame.draw.circle(screen, RED, (int(x), int(y)), radius)
    pygame.display.update()

# 종료
pygame.quit()
sys.exit()
