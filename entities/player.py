"""
Module định nghĩa Player.
Tích hợp thuật toán Auto-Crop thông minh, gọt bỏ nền trong suốt thừa
để nhân vật luôn hiển thị to, rõ ràng và chuẩn kích thước.
"""
import pygame
import math
import os

class Player:
    def __init__(self, x: float, y: float):
        self.x = x
        self.y = y
        self.speed = 4.0
        # KÍCH THƯỚC NHÂN VẬT (BẠN MUỐN TO BAO NHIÊU THÌ SỬA Ở ĐÂY)
        self.size = 64

        # --- THÔNG SỐ SINH TỒN ---
        self.max_hp = 100
        self.hp = 100

        # --- ANIMATION TRẠNG THÁI ---
        self.facing_right = True
        self.is_moving = False
        self.animation_timer = 0
        self.current_frame = 0
        self.frames = []

        # --- THUẬT TOÁN LOAD VÀ AUTO-CROP HÌNH ẢNH ---
        img_path = os.path.join("assets", "Soldier-Idle.png")
        if os.path.exists(img_path):
            sheet = pygame.image.load(img_path).convert_alpha()
            w, h = sheet.get_width(), sheet.get_height()

            # 1. Tự động nhận diện: Nếu ảnh rộng gấp 3 lần chiều cao -> Là bảng 6 khung hình.
            # Nếu ảnh vuông vuông -> Nó chỉ là 1 tấm ảnh!
            frames_count = 6 if w >= h * 3 else 1
            frame_width = w // frames_count

            for i in range(frames_count):
                rect = pygame.Rect(i * frame_width, 0, frame_width, h)
                frame_surface = sheet.subsurface(rect)

                # 2. AUTO-CROP: Lấy hộp giới hạn chứa các điểm ảnh thật (xóa bỏ không gian trong suốt)
                bounding_rect = frame_surface.get_bounding_rect()

                if bounding_rect.width > 0 and bounding_rect.height > 0:
                    # Cắt sát rạt vào body nhân vật
                    cropped = frame_surface.subsurface(bounding_rect)
                    # 3. Ép body nhân vật bành trướng ra đúng self.size (64x64)
                    scaled = pygame.transform.scale(cropped, (self.size, self.size))
                    self.frames.append(scaled)

        # Nếu mảng frames vẫn rỗng (do lỗi ảnh), dùng hình chữ nhật dự phòng
        if len(self.frames) == 0:
            backup_img = pygame.Surface((self.size, self.size))
            backup_img.fill((0, 255, 0)) # Màu xanh lá
            self.frames.append(backup_img)

    def move(self, keys, map_width: float, map_height: float):
        dx, dy = 0, 0
        if keys[pygame.K_w]: dy -= 1
        if keys[pygame.K_s]: dy += 1
        if keys[pygame.K_a]: dx -= 1
        if keys[pygame.K_d]: dx += 1

        if dx > 0:
            self.facing_right = True
        elif dx < 0:
            self.facing_right = False

        if dx != 0 or dy != 0:
            self.is_moving = True
            length = math.sqrt(dx**2 + dy**2)
            dx /= length
            dy /= length
        else:
            self.is_moving = False

        self.x += dx * self.speed
        self.y += dy * self.speed

        self.x = max(0, min(map_width, self.x))
        self.y = max(0, min(map_height, self.y))

    def draw(self, screen: pygame.Surface, camera_x: float, camera_y: float):
        # draw_x, draw_y bây giờ là TÂM của nhân vật
        draw_x = self.x - camera_x
        draw_y = self.y - camera_y

        if self.is_moving and len(self.frames) > 1:
            self.animation_timer += 1
            if self.animation_timer >= 5:
                self.current_frame = (self.current_frame + 1) % len(self.frames)
                self.animation_timer = 0
        else:
            self.current_frame = 0
            self.animation_timer = 0

        img_to_draw = self.frames[self.current_frame]
        img_to_draw = pygame.transform.flip(img_to_draw, not self.facing_right, False)

        # Căn chỉnh TÂM ảnh đúng vào TÂM tọa độ
        img_rect = img_to_draw.get_rect()
        img_rect.center = (draw_x, draw_y)

        # 1. Vẽ nhân vật
        screen.blit(img_to_draw, img_rect.topleft)

        # 2. Vẽ thanh máu (HP Bar) - Đã căn giữa trên đầu
        hp_bar_width = self.size
        hp_bar_height = 6
        hp_ratio = self.hp / self.max_hp

        if self.hp > 0:
            bar_start_x = draw_x - hp_bar_width / 2
            bar_start_y = img_rect.top - 12 # Nổi lên trên đỉnh đầu

            pygame.draw.rect(screen, (255, 0, 0), (bar_start_x, bar_start_y, hp_bar_width, hp_bar_height))
            pygame.draw.rect(screen, (0, 255, 0), (bar_start_x, bar_start_y, hp_bar_width * hp_ratio, hp_bar_height))