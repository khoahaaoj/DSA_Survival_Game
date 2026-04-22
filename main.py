import pygame
import sys
import os
import random
import math
from settings import *
from entities.player import Player
from entities.enemy import Enemy
from entities.weapon import Bullet
from algorithms.min_heap import MinHeap


# (Giữ nguyên các hàm load_grass_tile và draw_map từ Tuần 1)
def load_grass_tile():
    img_path = os.path.join("assets", "grass.png")
    if os.path.exists(img_path):
        img = pygame.image.load(img_path).convert()
        return pygame.transform.scale(img, (TILE_SIZE, TILE_SIZE))
    return None


def draw_map(screen, camera_x, camera_y, grass_img):
    start_col = int(camera_x // TILE_SIZE)
    start_row = int(camera_y // TILE_SIZE)
    cols = (WIDTH // TILE_SIZE) + 2
    rows = (HEIGHT // TILE_SIZE) + 2

    for row in range(start_row, start_row + rows):
        for col in range(start_col, start_col + cols):
            tile_x = col * TILE_SIZE
            tile_y = row * TILE_SIZE
            if tile_x < MAP_WIDTH and tile_y < MAP_HEIGHT:
                draw_x = tile_x - camera_x
                draw_y = tile_y - camera_y
                if grass_img:
                    screen.blit(grass_img, (draw_x, draw_y))
                else:
                    pygame.draw.rect(screen, GRASS_FALLBACK_COLOR, (draw_x, draw_y, TILE_SIZE, TILE_SIZE))
                    pygame.draw.rect(screen, (20, 100, 20), (draw_x, draw_y, TILE_SIZE, TILE_SIZE), 1)


def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("DSA Survival - Tuần 2 (Min-Heap Auto Aim)")
    clock = pygame.time.Clock()

    grass_tile = load_grass_tile()
    player = Player(MAP_WIDTH // 2, MAP_HEIGHT // 2)

    # --- KHỞI TẠO DỮ LIỆU TUẦN 2 ---
    enemies = []
    bullets = []
    target_heap = MinHeap()  # Khởi tạo Min-Heap

    # Timers
    SPAWN_ENEMY_EVENT = pygame.USEREVENT + 1
    pygame.time.set_timer(SPAWN_ENEMY_EVENT, 1000)  # Sinh 1 quái mỗi giây

    SHOOT_EVENT = pygame.USEREVENT + 2
    pygame.time.set_timer(SHOOT_EVENT, 500)  # Bắn 2 viên đạn mỗi giây

    running = True
    while running:
        # 1. XỬ LÝ SỰ KIỆN
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            # Sinh quái vật ngẫu nhiên quanh người chơi
            if event.type == SPAWN_ENEMY_EVENT:
                # Sinh ra ở một điểm cách người chơi khoảng 600 pixel
                angle = random.uniform(0, 2 * math.pi)
                spawn_x = player.x + math.cos(angle) * 600
                spawn_y = player.y + math.sin(angle) * 600
                enemies.append(Enemy(spawn_x, spawn_y))

            # Logic Bắn tự động dùng Min-Heap
            if event.type == SHOOT_EVENT and len(enemies) > 0:
                # Lấy phần tử trên cùng của Heap (đã được tính toán trong vòng lặp Update)
                closest_enemy_data = target_heap.pop()
                if closest_enemy_data:
                    closest_dist, target_enemy = closest_enemy_data
                    # Tạo đạn bay thẳng vào con quái gần nhất
                    bullets.append(Bullet(player.x + player.size // 2, player.y + player.size // 2, target_enemy.x,
                                          target_enemy.y))

        keys = pygame.key.get_pressed()

        # 2. CẬP NHẬT LOGIC
        player.move(keys, MAP_WIDTH, MAP_HEIGHT)

        target_heap.clear()  # Xóa Heap cũ mỗi khung hình

        # Cập nhật Quái vật & Đưa khoảng cách vào Min-Heap
        for enemy in enemies:
            dist = enemy.move_towards(player.x, player.y)
            # Push vào Heap định dạng: (Khoảng_cách, Đối_tượng_quái)
            target_heap.push((dist, enemy))

        # Cập nhật Đạn
        for bullet in bullets:
            bullet.move()

        # Logic Camera
        camera_x = player.x - (WIDTH // 2) + (player.size // 2)
        camera_y = player.y - (HEIGHT // 2) + (player.size // 2)
        camera_x = max(0, min(MAP_WIDTH - WIDTH, camera_x))
        camera_y = max(0, min(MAP_HEIGHT - HEIGHT, camera_y))

        # 3. RENDER LÊN MÀN HÌNH
        screen.fill(BG_COLOR)
        draw_map(screen, camera_x, camera_y, grass_tile)

        for enemy in enemies:
            enemy.draw(screen, camera_x, camera_y)

        for bullet in bullets:
            bullet.draw(screen, camera_x, camera_y)

        player.draw(screen, camera_x, camera_y)

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()