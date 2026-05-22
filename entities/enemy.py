"""
Module: entities/enemy.py
Quản lý logic và hiển thị của toàn bộ loại kẻ địch trong game.

Kiến trúc kế thừa:
    Enemy (lớp cơ sở)  ←  Zombie, Bat, Golem (các lớp con)

    Lớp cơ sở xử lý:
        - Di chuyển hướng về player.
        - Boids Separation: tránh chồng lên nhau bằng lực đẩy.
        - Tải và hiển thị sprite animation.

    Lớp con chỉ định nghĩa chỉ số:
        - Zombie:  tốc độ trung bình, máu trung bình.
        - Bat:     tốc độ nhanh, máu giấy.
        - Golem:   tốc độ chậm, máu trâu và sát thương lớn.
"""
import pygame
import math
import os
import random


class Enemy:
    """
    Lớp cơ sở đại diện cho một quái vật trong game.

    Tích hợp thuật toán di chuyển tìm đường cơ bản và AI Steering Behaviors
    (Quy tắc Separation) để quái vật không di chuyển đè lên nhau.

    Attributes:
        x (float): Tọa độ X hiện tại của quái vật.
        y (float): Tọa độ Y hiện tại của quái vật.
        speed (float): Tốc độ di chuyển, tăng dần theo cấp độ người chơi.
        size (int): Kích thước hiển thị của quái vật (mặc định 64x64).
        damage (float): Lượng sát thương gây ra cho người chơi.
        max_hp (float): Lượng máu tối đa.
        hp (float): Lượng máu hiện tại.
        last_attack_time (int): Thời điểm (ms) cuối cùng quái vật tấn công.
        frames (list): Danh sách các khung hình (Surface) để tạo hoạt ảnh.
    """

    def __init__(self, x: float, y: float, player_level: int, img_name: str, base_speed: float, base_hp: float,
                 base_dmg: float, color: tuple):
        self.x = x
        self.y = y
        self.speed = base_speed + (player_level * 0.05)
        self.size = 64
        self.damage = base_dmg + (player_level * 2)
        self.max_hp = base_hp + (player_level * 25)
        self.hp = self.max_hp
        self.last_attack_time = 0

        self.facing_right = True
        self.animation_timer = random.randint(0, 20)
        self.current_frame = 0
        self.frames = []

        img_path = os.path.join("assets", img_name)
        if os.path.exists(img_path):
            sheet = pygame.image.load(img_path).convert_alpha()
            w, h = sheet.get_width(), sheet.get_height()
            frames_count = max(1, w // h) if w > h else 1
            frame_width = w // frames_count
            for i in range(frames_count):
                rect = pygame.Rect(i * frame_width, 0, frame_width, h)
                frame_surface = sheet.subsurface(rect)
                bounding_rect = frame_surface.get_bounding_rect()
                if bounding_rect.width > 0 and bounding_rect.height > 0:
                    cropped = frame_surface.subsurface(bounding_rect)
                    scaled = pygame.transform.scale(cropped, (self.size, self.size))
                    self.frames.append(scaled)

        if len(self.frames) == 0:
            backup_img = pygame.Surface((self.size, self.size))
            backup_img.fill(color)
            self.frames.append(backup_img)

    def update_movement(self, target_x: float, target_y: float, quadtree) -> float:
        """
        Cập nhật vị trí của quái vật dựa trên mục tiêu và không gian xung quanh.

        Args:
            target_x (float): Tọa độ X của người chơi.
            target_y (float): Tọa độ Y của người chơi.
            quadtree (QuadTree): Cấu trúc dữ liệu không gian chứa các quái vật khác.

        Returns:
            float: Khoảng cách từ quái vật đến người chơi.
        """
        dx = target_x - self.x
        dy = target_y - self.y
        dist_to_player = math.sqrt(dx ** 2 + dy ** 2)

        dir_x, dir_y = 0, 0
        if dist_to_player != 0:
            dir_x = dx / dist_to_player
            dir_y = dy / dist_to_player

        if dir_x > 0:
            self.facing_right = True
        elif dir_x < 0:
            self.facing_right = False

        sep_x, sep_y = 0, 0
        search_radius = self.size * 1.2
        search_radius_sq = search_radius * search_radius  # Tránh sqrt trong bước lọc đầu
        search_rect = pygame.Rect(self.x - search_radius, self.y - search_radius, search_radius * 2, search_radius * 2)
        neighbors = quadtree.query(search_rect, [])
        repel_count = 0

        for neighbor in neighbors:
            if neighbor is not self:
                ndx = self.x - neighbor.x
                ndy = self.y - neighbor.y
                ndist_sq = ndx * ndx + ndy * ndy   # So sánh bằng bình phương trước
                if 0 < ndist_sq < search_radius_sq:
                    ndist = math.sqrt(ndist_sq)    # Chỉ gọi sqrt khi đã chắc chắn có lân cận
                    sep_x += (ndx / ndist)
                    sep_y += (ndy / ndist)
                    repel_count += 1

        if repel_count > 0:
            sep_x /= repel_count
            sep_y /= repel_count
            s_dist = math.sqrt(sep_x ** 2 + sep_y ** 2)
            if s_dist != 0:
                sep_x /= s_dist
                sep_y /= s_dist

        final_dx = (dir_x * 1.0) + (sep_x * 1.5)
        final_dy = (dir_y * 1.0) + (sep_y * 1.5)

        f_dist = math.sqrt(final_dx ** 2 + final_dy ** 2)
        if f_dist != 0:
            self.x += (final_dx / f_dist) * self.speed
            self.y += (final_dy / f_dist) * self.speed

        return dist_to_player

    def draw(self, screen: pygame.Surface, camera_x: float, camera_y: float):
        """
        Vẽ kẻ địch lên màn hình cùng thanh máu (chỉ hiện khi bị thương).

        Hoạt ảnh: chuyển frame mỗi 6 frame kẻ địch có nhiều khung hình;
        nếu chỉ có 1 khung hình, giả lập bằng cách nhích nhẹ lên xuống.

        Args:
            screen (pygame.Surface): Bề mặt render của Pygame.
            camera_x (float):        Độ lệch camera trục X (dùng để chuyển World → Screen).
            camera_y (float):        Độ lệch camera trục Y.
        """
        draw_x = self.x - camera_x
        draw_y = self.y - camera_y

        self.animation_timer += 1
        if len(self.frames) > 1:
            if self.animation_timer >= 6:
                self.current_frame = (self.current_frame + 1) % len(self.frames)
                self.animation_timer = 0
        else:
            if (self.animation_timer // 10) % 2 == 0: draw_y -= 4

        img_to_draw = self.frames[self.current_frame]
        img_to_draw = pygame.transform.flip(img_to_draw, not self.facing_right, False)

        img_rect = img_to_draw.get_rect()
        img_rect.center = (draw_x, draw_y)
        screen.blit(img_to_draw, img_rect.topleft)

        hp_bar_width = 30
        hp_bar_height = 4
        hp_ratio = self.hp / self.max_hp
        if 0 < self.hp < self.max_hp:
            bar_start_x = draw_x - hp_bar_width / 2
            bar_start_y = img_rect.top - 5
            pygame.draw.rect(screen, (255, 0, 0), (bar_start_x, bar_start_y, hp_bar_width, hp_bar_height))
            pygame.draw.rect(screen, (0, 255, 0), (bar_start_x, bar_start_y, hp_bar_width * hp_ratio, hp_bar_height))


class Zombie(Enemy):
    """
    Kẻ địch loại Zombie: chỉ số cân bằng, xuất hiện chủ yếu ở Wave 1-3.

    Tốc độ: 1.2 px/frame | Máu: 75 + 25×cấp | Sát thương: 10 + 2×cấp
    """
    def __init__(self, x, y, player_level):
        super().__init__(x, y, player_level, "zombie.png", 1.2, 75, 10, (34, 139, 34))


class Bat(Enemy):
    """
    Kẻ địch loại Dơi: cực nhanh nhưng mỏng manh, xuất hiện từ Wave 2.

    Tốc độ: 2.5 px/frame | Máu: 20 + 25×cấp | Sát thương: 5 + 2×cấp
    Nguy hiểm vì di chuyển khó dự đoán, hay luƳn lách qua đám đông.
    """
    def __init__(self, x, y, player_level):
        super().__init__(x, y, player_level, "bat.png", 2.5, 20, 5, (75, 0, 130))


class Golem(Enemy):
    """
    Kẻ địch loại Golem: rất chậm nhưng độ máu và sát thương cao nhất, xuất hiện từ Wave 3.

    Tốc độ: 0.6 px/frame | Máu: 200 + 25×cấp | Sát thương: 25 + 2×cấp
    Đây là đẫn kẻ địch dạy dạng để học thông điệp “kill nhanh trước khi chúng đến gần”.
    """
    def __init__(self, x, y, player_level):
        super().__init__(x, y, player_level, "golem.png", 0.6, 200, 25, (105, 105, 105))