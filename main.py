# main.py
import pygame
import sys
from settings import *
from entities.player import Player


def draw_grid(screen, camera_x, camera_y):
    """
    Vẽ hệ thống lưới bối cảnh.
    Lưới sẽ cuộn theo Camera để tạo cảm giác nhân vật đang di chuyển.
    """
    grid_size = 100  # Khoảng cách giữa các ô vuông

    # Tính toán tọa độ bắt đầu vẽ lưới dựa trên vị trí camera
    start_x = -int(camera_x % grid_size)
    start_y = -int(camera_y % grid_size)

    # Vẽ các đường dọc và ngang
    for x in range(start_x, WIDTH, grid_size):
        pygame.draw.line(screen, GRID_COLOR, (x, 0), (x, HEIGHT))
    for y in range(start_y, HEIGHT, grid_size):
        pygame.draw.line(screen, GRID_COLOR, (0, y), (WIDTH, y))


def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Đồ án DSA - Survival Game")
    clock = pygame.time.Clock()

    # Sinh ra nhân vật ở giữa bản đồ lớn
    player = Player(MAP_WIDTH // 2, MAP_HEIGHT // 2)

    running = True
    while running:
        # 1. XỬ LÝ SỰ KIỆN
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        keys = pygame.key.get_pressed()

        # 2. CẬP NHẬT LOGIC
        player.move(keys, MAP_WIDTH, MAP_HEIGHT)

        # LOGIC CAMERA: Camera luôn đặt nhân vật ở giữa màn hình
        # Tọa độ camera = Tọa độ nhân vật - Một nửa màn hình
        camera_x = player.x - (WIDTH // 2) + (player.size // 2)
        camera_y = player.y - (HEIGHT // 2) + (player.size // 2)

        # Giới hạn Camera không quay ra khỏi viền của Map lớn
        camera_x = max(0, min(MAP_WIDTH - WIDTH, camera_x))
        camera_y = max(0, min(MAP_HEIGHT - HEIGHT, camera_y))

        # 3. VẼ LÊN MÀN HÌNH (RENDER)
        screen.fill(BG_COLOR)
        draw_grid(screen, camera_x, camera_y)

        # Vẽ nhân vật: Tọa độ vẽ = Tọa độ thực tế - Tọa độ camera
        draw_x = player.x - camera_x
        draw_y = player.y - camera_y
        pygame.draw.rect(screen, player.color, (draw_x, draw_y, player.size, player.size))

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()