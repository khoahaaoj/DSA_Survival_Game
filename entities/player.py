# entities/player.py
import pygame

class Player:
    """
    Lớp đại diện cho nhân vật chính do người chơi điều khiển.
    Lưu trữ tọa độ thực tế trên bản đồ rộng (World Coordinates).
    """
    def __init__(self, x: float, y: float):
        self.x = x
        self.y = y
        self.speed = 5.0
        self.size = 40
        self.color = (0, 255, 128)

    def move(self, keys, map_w: int, map_h: int):
        """
        Xử lý logic di chuyển dựa trên phím bấm.
        Áp dụng chuẩn hóa vector để tốc độ đi chéo không bị nhanh hơn đi thẳng.
        """
        dx, dy = 0, 0
        if keys[pygame.K_w] or keys[pygame.K_UP]: dy -= 1
        if keys[pygame.K_s] or keys[pygame.K_DOWN]: dy += 1
        if keys[pygame.K_a] or keys[pygame.K_LEFT]: dx -= 1
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]: dx += 1

        # Chuẩn hóa vector đường chéo (Tránh lỗi kinh điển: đi chéo nhanh gấp rưỡi)
        if dx != 0 and dy != 0:
            dx *= 0.7071  # Căn bậc 2 của 2 chia 2
            dy *= 0.7071

        self.x += dx * self.speed
        self.y += dy * self.speed

        # Giữ nhân vật nằm gọn trong phạm vi của bản đồ lớn
        self.x = max(0, min(map_w - self.size, self.x))
        self.y = max(0, min(map_h - self.size, self.y))