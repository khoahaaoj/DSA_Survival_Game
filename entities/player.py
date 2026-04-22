# entities/player.py
import pygame
import math
from settings import *


class Player:
    """
    Lớp đại diện cho nhân vật chính do người chơi điều khiển.

    Attributes:
        x (float): Tọa độ trục X thực tế trên bản đồ.
        y (float): Tọa độ trục Y thực tế trên bản đồ.
        speed (float): Tốc độ di chuyển cơ bản của nhân vật.
        size (int): Kích thước hitbox (cạnh hình vuông).
        color (tuple): Màu sắc hiển thị.
    """

    def __init__(self, x: float, y: float):
        self.x = x
        self.y = y
        self.speed = 5.0
        self.size = 40
        self.color = PLAYER_FALLBACK_COLOR  # Lấy màu từ settings.py (xanh neon)

    def move(self, keys, map_w: int, map_h: int):
        """
        Xử lý di chuyển dựa trên phím bấm.
        Áp dụng toán Vector để vận tốc đi chéo không bị sai lệch.
        """
        dx, dy = 0, 0
        if keys[pygame.K_w] or keys[pygame.K_UP]: dy -= 1
        if keys[pygame.K_s] or keys[pygame.K_DOWN]: dy += 1
        if keys[pygame.K_a] or keys[pygame.K_LEFT]: dx -= 1
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]: dx += 1

        # Tránh lỗi chia cho 0 nếu không bấm phím nào
        if dx != 0 or dy != 0:
            # Chuẩn hóa Vector (Tính độ dài vector và chia đều cho X, Y)
            length = math.sqrt(dx ** 2 + dy ** 2)
            dx /= length
            dy /= length

        # Cập nhật tọa độ
        self.x += dx * self.speed
        self.y += dy * self.speed

        # Giữ nhân vật không chạy lọt ra ngoài bản đồ
        self.x = max(0, min(map_w - self.size, self.x))
        self.y = max(0, min(map_h - self.size, self.y))

    def draw(self, screen, camera_x, camera_y):
        """
        Vẽ nhân vật lên màn hình dựa theo tọa độ Camera.
        Sử dụng vẽ hình học cơ bản của Pygame thay vì hình ảnh.
        """
        draw_x = self.x - camera_x
        draw_y = self.y - camera_y

        # Vẽ một hình vuông đại diện cho nhân vật
        pygame.draw.rect(screen, self.color, (draw_x, draw_y, self.size, self.size))

        # Tùy chọn: Vẽ một đường viền trắng cho đẹp mắt
        pygame.draw.rect(screen, (255, 255, 255), (draw_x, draw_y, self.size, self.size), 2)