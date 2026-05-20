"""
Module cung cấp lớp nhân vật người chơi (Player).
Quản lý trạng thái, cấp độ, kinh nghiệm, di chuyển và kho vũ khí của người chơi.
"""
import pygame
import math
import os
from entities.weapon import Gun, HolyAura, ThunderStorm


class Player:
    """
    Đại diện cho nhân vật chính do người chơi điều khiển.

    Quản lý tọa độ toàn cục, điểm kinh nghiệm (EXP), quá trình lên cấp (Level Up),
    và vòng đời vũ khí (Cập nhật và kết xuất đồ họa).

    Attributes:
        x (float): Tọa độ X hiện tại.
        y (float): Tọa độ Y hiện tại.
        level (int): Cấp độ hiện tại của người chơi.
        exp (int): Điểm kinh nghiệm hiện tại.
        weapons (list): Danh sách các vũ khí (class Weapon) đang trang bị.
    """

    def __init__(self, x: float, y: float):
        self.x = x
        self.y = y
        self.speed = 2.0
        self.size = 48
        self.max_hp = 100
        self.hp = 100
        self.damage_flash = 0   # Đếm ngược frame hiệu ứng đỏ khi bị đánh (I-frame visual)

        # --- HỆ THỐNG CẤP ĐỘ (LEVEL) ---
        self.level = 1
        self.exp = 0
        self.max_exp = 100
        self.level_up_pending = False  # Cờ báo hiệu: người chơi vừa lên cấp, chờ chọn phần thưởng

        self.weapons = [Gun()]

        self.facing_right = True
        self.is_moving = False
        self.animation_timer = 0
        self.current_frame = 0
        self.frames = []

        # ==========================================
        # XỬ LÝ ẢNH SPRITESHEET NHÂN VẬT MỚI
        # ==========================================
        img_path = os.path.join("assets", "Soldier-Idle.png")
        if os.path.exists(img_path):
            sheet = pygame.image.load(img_path).convert_alpha()

            # 1. Tự động xóa phông nền trắng (Lấy màu ở pixel 0,0 làm chuẩn)
            colorkey = sheet.get_at((0, 0))
            sheet.set_colorkey(colorkey, pygame.RLEACCEL)

            w, h = sheet.get_width(), sheet.get_height()
            frames_count = 6  # Tấm ảnh của sếp có đúng 6 khung hình
            frame_width = w // frames_count

            # 2. Cắt ảnh ra làm 6 phần và tự động zoom sát nhân vật
            for i in range(frames_count):
                rect = pygame.Rect(i * frame_width, 0, frame_width, h)
                frame_surface = sheet.subsurface(rect).copy()

                # Cắt bỏ các viền thừa xung quanh
                bounding_rect = frame_surface.get_bounding_rect()
                if bounding_rect.width > 0 and bounding_rect.height > 0:
                    cropped = frame_surface.subsurface(bounding_rect)
                    # Phóng to lên đúng bằng kích thước (size 64x64)
                    scaled = pygame.transform.scale(cropped, (self.size, self.size))
                    self.frames.append(scaled)

        # Nếu không tìm thấy ảnh, dùng cục vuông màu xanh làm mồi
        if len(self.frames) == 0:
            backup_img = pygame.Surface((self.size, self.size))
            backup_img.fill((0, 255, 0))
            self.frames.append(backup_img)

    def gain_exp(self, amount: int):
        """
        Nhận điểm kinh nghiệm và xử lý tăng cấp nếu đạt ngưỡng tối đa.

        Args:
            amount (int): Lượng kinh nghiệm nhận được.
        """
        self.exp += amount
        if self.exp >= self.max_exp:
            self.exp -= self.max_exp
            self.level += 1
            self.max_exp = int(self.max_exp * 1.5)
            self.trigger_level_up()

    def trigger_level_up(self):
        """
        Kích hoạt sự kiện thăng cấp.
        Thay vì tự động gán vũ khí, đặt cờ `level_up_pending` để
        Game Loop hiển thị màn hình chọn phần thưởng (Level Up Screen).
        """
        print(f"LÊN CẤP {self.level}!")
        self.level_up_pending = True  # Gửi tín hiệu lên Game Loop để mở UI chọn vật phẩm

    def move(self, keys, map_width: float, map_height: float):
        """
        Cập nhật vị trí người chơi dựa trên phím bấm, giới hạn trong kích thước bản đồ.

        Args:
            keys (sequence): Trạng thái của toàn bộ bàn phím.
            map_width (float): Chiều rộng tối đa của bản đồ.
            map_height (float): Chiều cao tối đa của bản đồ.
        """
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
            length = math.sqrt(dx ** 2 + dy ** 2)
            dx /= length
            dy /= length
        else:
            self.is_moving = False

        self.x += dx * self.speed
        self.y += dy * self.speed

        self.x = max(0, min(map_width, self.x))
        self.y = max(0, min(map_height, self.y))

    def update_weapons(self, quadtree, target_heap, current_time) -> list:
        """
        Kích hoạt cơ chế tấn công của toàn bộ kho vũ khí đang trang bị.

        Args:
            quadtree (QuadTree): Cây không gian để truy vấn va chạm.
            target_heap (MinHeap): Hàng đợi ưu tiên chứa mục tiêu gần nhất.
            current_time (int): Thời gian hệ thống hiện tại.

        Returns:
            list: Danh sách các sự kiện sát thương sinh ra trong frame.
        """
        all_events = []
        for weapon in self.weapons:
            res = weapon.update(self, quadtree, target_heap, current_time)
            if res: all_events.extend(res)
        return all_events

    def draw_weapons(self, screen, camera_x, camera_y):
        """Kết xuất đồ họa cho toàn bộ vũ khí."""
        for weapon in self.weapons:
            weapon.draw(screen, camera_x, camera_y, self)

    def draw(self, screen: pygame.Surface, camera_x: float, camera_y: float):
        """
        Vẽ nhân vật, xử lý hoạt ảnh (animation) và thanh máu.

        Args:
            screen (pygame.Surface): Bề mặt vẽ.
            camera_x (float): Tọa độ X của camera hiện hành.
            camera_y (float): Tọa độ Y của camera hiện hành.
        """
        draw_x = self.x - camera_x
        draw_y = self.y - camera_y

        # Chỉ phát animation chuyển frame khi nhân vật đang di chuyển
        if self.is_moving and len(self.frames) > 1:
            self.animation_timer += 1
            if self.animation_timer >= 5:
                self.current_frame = (self.current_frame + 1) % len(self.frames)
                self.animation_timer = 0
        else:
            self.current_frame = 0
            self.animation_timer = 0

        img_to_draw = self.frames[self.current_frame]
        # Tự động lật mặt nhân vật khi đi sang trái
        img_to_draw = pygame.transform.flip(img_to_draw, not self.facing_right, False)

        img_rect = img_to_draw.get_rect()
        img_rect.center = (draw_x, draw_y)
        screen.blit(img_to_draw, img_rect.topleft)

        # Hiệu ứng đỏ (Damage Flash): Overlay màu đỏ mờ khi bị đánh
        if self.damage_flash > 0:
            flash_surf = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
            alpha = int(200 * self.damage_flash / 12)
            flash_surf.fill((255, 30, 30, alpha))
            screen.blit(flash_surf, img_rect.topleft)
            self.damage_flash -= 1

        # Vẽ thanh máu dưới chân nhân vật (hoặc trên đầu)
        hp_bar_width = self.size
        hp_bar_height = 6
        hp_ratio = self.hp / self.max_hp
        if self.hp > 0:
            bar_start_x = draw_x - hp_bar_width / 2
            bar_start_y = img_rect.top - 12
            pygame.draw.rect(screen, (255, 0, 0), (bar_start_x, bar_start_y, hp_bar_width, hp_bar_height))
            pygame.draw.rect(screen, (0, 255, 0), (bar_start_x, bar_start_y, hp_bar_width * hp_ratio, hp_bar_height))