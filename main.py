"""
File khởi chạy chính (Entry Point) của dự án Game Survival 2D.
Tích hợp trọn vẹn thuật toán của 3 tuần:
- Tuần 1: Camera Culling, Vector Movement.
- Tuần 2: Min-Heap (Hệ thống ngắm bắn tự động).
- Tuần 3: QuadTree (Tối ưu không gian), Boids (Trí tuệ bầy đàn), Cơ chế Sinh tồn (HP, I-frames).
"""
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
from algorithms.quadtree import QuadTree

def load_grass_tile() -> pygame.Surface:
    """
    Tải và xử lý hình ảnh nền (grass) từ thư mục assets.

    Returns:
        pygame.Surface: Bề mặt ảnh nền đã được scale theo TILE_SIZE.
        None: Nếu không tìm thấy file ảnh.
    """
    img_path = os.path.join("assets", "grass.png")
    if os.path.exists(img_path):
        img = pygame.image.load(img_path).convert()
        return pygame.transform.scale(img, (TILE_SIZE, TILE_SIZE))
    return None

def draw_map(screen: pygame.Surface, camera_x: float, camera_y: float, grass_img: pygame.Surface):
    """
    Vẽ lưới bản đồ vô tận.
    Sử dụng kỹ thuật Culling: Chỉ tính toán và render những ô gạch nằm bên trong Camera,
    giúp tiết kiệm tài nguyên GPU.

    Args:
        screen (pygame.Surface): Bề mặt vẽ chính.
        camera_x (float): Tọa độ góc trên cùng bên trái của Camera (Trục X).
        camera_y (float): Tọa độ góc trên cùng bên trái của Camera (Trục Y).
        grass_img (pygame.Surface): Hình ảnh cỏ dùng để lấp đầy ô gạch.
    """
    start_col = int(camera_x // TILE_SIZE)
    start_row = int(camera_y // TILE_SIZE)
    cols = (WIDTH // TILE_SIZE) + 2
    rows = (HEIGHT // TILE_SIZE) + 2

    for row in range(start_row, start_row + rows):
        for col in range(start_col, start_col + cols):
            tile_x = col * TILE_SIZE
            tile_y = row * TILE_SIZE
            # Chỉ vẽ nếu gạch nằm trong giới hạn MAP_WIDTH, MAP_HEIGHT
            if tile_x < MAP_WIDTH and tile_y < MAP_HEIGHT:
                draw_x = tile_x - camera_x
                draw_y = tile_y - camera_y
                if grass_img:
                    screen.blit(grass_img, (draw_x, draw_y))
                else:
                    pygame.draw.rect(screen, GRASS_FALLBACK_COLOR, (draw_x, draw_y, TILE_SIZE, TILE_SIZE))
                    pygame.draw.rect(screen, (20, 100, 20), (draw_x, draw_y, TILE_SIZE, TILE_SIZE), 1)

def main():
    """
    Hàm thực thi vòng lặp Game chính (Game Loop).
    Quản lý khởi tạo Pygame, bắt sự kiện, cập nhật thuật toán và kết xuất đồ họa.
    """
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("DSA Survival - Tuần 3 (Hoàn thiện Thuật toán)")
    clock = pygame.time.Clock()

    # Khởi tạo tài nguyên và thực thể
    grass_tile = load_grass_tile()
    player = Player(MAP_WIDTH // 2, MAP_HEIGHT // 2)

    enemies = []
    bullets = []
    target_heap = MinHeap()

    # Thiết lập bộ đếm thời gian (Timers)
    SPAWN_ENEMY_EVENT = pygame.USEREVENT + 1
    pygame.time.set_timer(SPAWN_ENEMY_EVENT, 300) # Sinh quái mỗi 0.3s

    SHOOT_EVENT = pygame.USEREVENT + 2
    pygame.time.set_timer(SHOOT_EVENT, 500)       # Bắn đạn mỗi 0.5s

    # --- CÁC BIẾN TRẠNG THÁI TRÒ CHƠI ---
    show_quadtree = False    # Cờ Bật/Tắt lưới hiển thị Quadtree
    last_damage_time = 0     # Biến đếm I-frames (khung hình bất tử)
    game_over = False        # Trạng thái kết thúc game
    font = pygame.font.SysFont(None, 80) # Phông chữ hiển thị Game Over

    running = True
    while running:
        # ==========================================
        # 1. XỬ LÝ SỰ KIỆN (EVENTS)
        # ==========================================
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q:
                    show_quadtree = not show_quadtree

            # Chỉ sinh quái và bắn đạn khi nhân vật còn sống
            if not game_over:
                if event.type == SPAWN_ENEMY_EVENT:
                    angle = random.uniform(0, 2 * math.pi)
                    spawn_x = player.x + math.cos(angle) * 600
                    spawn_y = player.y + math.sin(angle) * 600
                    enemies.append(Enemy(spawn_x, spawn_y))

                if event.type == SHOOT_EVENT and len(enemies) > 0:
                    closest_enemy_data = target_heap.pop()
                    if closest_enemy_data:
                        closest_dist, target_enemy = closest_enemy_data
                        bullets.append(Bullet(
                            player.x,
                            player.y,
                            target_enemy.x,
                            target_enemy.y
                        ))

        keys = pygame.key.get_pressed()

        # ==========================================
        # 2. CẬP NHẬT LOGIC & THUẬT TOÁN (UPDATE)
        # ==========================================
        # Bọc toàn bộ thuật toán trong điều kiện "not game_over" để đóng băng game khi chết
        if not game_over:
            player.move(keys, MAP_WIDTH, MAP_HEIGHT)

            # --- KHỞI TẠO QUADTREE ---
            map_boundary = pygame.Rect(0, 0, MAP_WIDTH, MAP_HEIGHT)
            quadtree = QuadTree(map_boundary, 4)
            for enemy in enemies:
                quadtree.insert(enemy)

            # --- CẬP NHẬT TRÍ TUỆ BẦY ĐÀN (BOIDS) ---
            target_heap.clear()
            for enemy in enemies:
                dist = enemy.update_movement(player.x, player.y, quadtree)
                target_heap.push((dist, enemy))

            # --- XỬ LÝ VA CHẠM (COLLISION): ĐẠN TRÚNG QUÁI ---
            enemies_to_remove = []
            bullets_to_remove = []

            for bullet in bullets:
                bullet.move()
                bullet_rect = pygame.Rect(bullet.x - bullet.size, bullet.y - bullet.size, bullet.size*2, bullet.size*2)

                # Truy vấn QuadTree để tối ưu O(log N)
                nearby_enemies = quadtree.query(bullet_rect, [])
                for enemy in nearby_enemies:
                    enemy_rect = pygame.Rect(enemy.x - enemy.size/2, enemy.y - enemy.size/2, enemy.size, enemy.size)
                    if bullet_rect.colliderect(enemy_rect):
                        if enemy not in enemies_to_remove:
                            enemies_to_remove.append(enemy)
                        if bullet not in bullets_to_remove:
                            bullets_to_remove.append(bullet)
                        break

            # --- XỬ LÝ VA CHẠM: QUÁI CẮN PLAYER ---
            current_time = pygame.time.get_ticks()
            player_rect = pygame.Rect(player.x - player.size/4, player.y - player.size/4, player.size/2, player.size/2)

            nearby_enemies_to_player = quadtree.query(player_rect, [])
            for enemy in nearby_enemies_to_player:
                enemy_rect = pygame.Rect(enemy.x - enemy.size/2, enemy.y - enemy.size/2, enemy.size, enemy.size)
                if player_rect.colliderect(enemy_rect):
                    # I-frames (Thời gian bất tử tạm thời): Tránh bị trừ máu liên tục mỗi frame
                    if current_time - last_damage_time > 1000:
                        player.hp -= enemy.damage
                        last_damage_time = current_time

                        # Kích hoạt trạng thái chết
                        if player.hp <= 0:
                            player.hp = 0
                            game_over = True
                    break

            # Dọn dẹp bộ nhớ (Garbage collection)
            for enemy in enemies_to_remove:
                if enemy in enemies: enemies.remove(enemy)
            for bullet in bullets_to_remove:
                if bullet in bullets: bullets.remove(bullet)

            # Tính toán Camera bám theo Player
            camera_x = player.x - (WIDTH // 2)
            camera_y = player.y - (HEIGHT // 2)
            camera_x = max(0, min(MAP_WIDTH - WIDTH, camera_x))
            camera_y = max(0, min(MAP_HEIGHT - HEIGHT, camera_y))

        # ==========================================
        # 3. KẾT XUẤT ĐỒ HỌA (RENDER)
        # ==========================================
        screen.fill(BG_COLOR)
        draw_map(screen, camera_x, camera_y, grass_tile)

        # Chế độ Debug (Phím Q)
        if show_quadtree:
            quadtree.draw(screen, camera_x, camera_y)

        for enemy in enemies:
            enemy.draw(screen, camera_x, camera_y)

        for bullet in bullets:
            bullet.draw(screen, camera_x, camera_y)

        player.draw(screen, camera_x, camera_y)

        # Hiển thị thông báo khi tử trận
        if game_over:
            text_surface = font.render("GAME OVER", True, (255, 0, 0))
            text_rect = text_surface.get_rect(center=(WIDTH // 2, HEIGHT // 2))

            # Khung nền đen mờ
            bg_rect = text_rect.inflate(60, 30)
            pygame.draw.rect(screen, (0, 0, 0), bg_rect)
            pygame.draw.rect(screen, (255, 255, 255), bg_rect, 3) # Viền trắng

            screen.blit(text_surface, text_rect)

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()