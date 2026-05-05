"""
Module định nghĩa các thực thể thù địch trong trò chơi.
Đã tích hợp Auto-Crop để hình ảnh quái to rõ, sát thương, và Trí tuệ bầy đàn (Boids).
"""
import pygame
import math
import os
import random

class Enemy:
    def __init__(self, x: float, y: float):
        self.x = x
        self.y = y
        self.speed = 2.0     # Quái chạy chậm hơn Player một chút
        self.size = 64       # Ép kích thước to bằng Player (64x64)
        self.damage = 10     # Sát thương mỗi lần cắn trúng

        # --- ANIMATION TRẠNG THÁI ---
        self.facing_right = True
        # Random nhịp độ ban đầu để quái vật không nhảy đều tăm tắp như tập thể dục
        self.animation_timer = random.randint(0, 20)
        self.current_frame = 0
        self.frames = []

        # --- THUẬT TOÁN LOAD VÀ AUTO-CROP ---
        img_path = os.path.join("assets", "enemy.png")
        if os.path.exists(img_path):
            sheet = pygame.image.load(img_path).convert_alpha()
            w, h = sheet.get_width(), sheet.get_height()

            # Tự động ước lượng số khung hình (Nếu ảnh dài ngoằng thì chia cắt)
            frames_count = max(1, w // h) if w > h else 1
            frame_width = w // frames_count

            for i in range(frames_count):
                rect = pygame.Rect(i * frame_width, 0, frame_width, h)
                frame_surface = sheet.subsurface(rect)

                # Gọt bỏ viền trong suốt (padding)
                bounding_rect = frame_surface.get_bounding_rect()
                if bounding_rect.width > 0 and bounding_rect.height > 0:
                    cropped = frame_surface.subsurface(bounding_rect)
                    scaled = pygame.transform.scale(cropped, (self.size, self.size))
                    self.frames.append(scaled)

        # Backup nếu lỗi ảnh
        if len(self.frames) == 0:
            backup_img = pygame.Surface((self.size, self.size))
            backup_img.fill((255, 50, 50))
            self.frames.append(backup_img)

    def update_movement(self, target_x: float, target_y: float, quadtree) -> float:
        # 1. VECTOR RƯỢT ĐUỔI
        dx = target_x - self.x
        dy = target_y - self.y
        dist_to_player = math.sqrt(dx**2 + dy**2)

        dir_x, dir_y = 0, 0
        if dist_to_player != 0:
            dir_x = dx / dist_to_player
            dir_y = dy / dist_to_player

        # Lật mặt dựa trên hướng di chuyển
        if dir_x > 0:
            self.facing_right = True
        elif dir_x < 0:
            self.facing_right = False

        # 2. VECTOR LỰC ĐẨY BẦY ĐÀN (Boids)
        sep_x, sep_y = 0, 0
        search_radius = self.size * 1.2
        search_rect = pygame.Rect(
            self.x - search_radius, self.y - search_radius,
            search_radius * 2, search_radius * 2
        )

        neighbors = quadtree.query(search_rect, [])
        repel_count = 0

        for neighbor in neighbors:
            if neighbor is not self:
                ndx = self.x - neighbor.x
                ndy = self.y - neighbor.y
                ndist = math.sqrt(ndx**2 + ndy**2)

                if 0 < ndist < search_radius:
                    sep_x += (ndx / ndist)
                    sep_y += (ndy / ndist)
                    repel_count += 1

        if repel_count > 0:
            sep_x /= repel_count
            sep_y /= repel_count
            s_dist = math.sqrt(sep_x**2 + sep_y**2)
            if s_dist != 0:
                sep_x /= s_dist
                sep_y /= s_dist

        # 3. TỔNG HỢP VÀ DI CHUYỂN
        final_dx = (dir_x * 1.0) + (sep_x * 1.5)
        final_dy = (dir_y * 1.0) + (sep_y * 1.5)

        f_dist = math.sqrt(final_dx**2 + final_dy**2)
        if f_dist != 0:
            self.x += (final_dx / f_dist) * self.speed
            self.y += (final_dy / f_dist) * self.speed

        return dist_to_player

    def draw(self, screen: pygame.Surface, camera_x: float, camera_y: float):
        draw_x = self.x - camera_x
        draw_y = self.y - camera_y

        # Chạy Animation nếu có nhiều khung hình, không thì chỉ nhún nhảy
        self.animation_timer += 1
        if len(self.frames) > 1:
            if self.animation_timer >= 6:
                self.current_frame = (self.current_frame + 1) % len(self.frames)
                self.animation_timer = 0
        else:
            # Hiệu ứng bobbing (nhún) cho ảnh tĩnh
            if (self.animation_timer // 10) % 2 == 0:
                draw_y -= 4

        img_to_draw = self.frames[self.current_frame]
        img_to_draw = pygame.transform.flip(img_to_draw, not self.facing_right, False)

        # Căn giữa ảnh vào tọa độ
        img_rect = img_to_draw.get_rect()
        img_rect.center = (draw_x, draw_y)

        screen.blit(img_to_draw, img_rect.topleft)