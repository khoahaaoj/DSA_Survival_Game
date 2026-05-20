"""
Module định nghĩa các vật phẩm rơi ra trên bản đồ (EXP, Máu...)
"""
import pygame
import math


class ExpGem:
    def __init__(self, x: float, y: float):
        self.x = x
        self.y = y
        self.value = 18  # Cần ~6 viên để lên Level 2 — t\u1ea1o tension t\u1ed1t h\u01a1n \u1edf \u0111\u1ea7u game
        self.size = 8

    def draw(self, screen: pygame.Surface, camera_x: float, camera_y: float):
        draw_x = self.x - camera_x
        draw_y = self.y - camera_y

        # Vẽ viên EXP hình kim cương (Diamond) màu xanh dương
        points = [
            (draw_x, draw_y - self.size),  # Đỉnh trên
            (draw_x + self.size - 2, draw_y),  # Góc phải
            (draw_x, draw_y + self.size),  # Đỉnh dưới
            (draw_x - self.size + 2, draw_y)  # Góc trái
        ]
        pygame.draw.polygon(screen, (0, 150, 255), points)
        pygame.draw.polygon(screen, (255, 255, 255), points, 1)  # Viền trắng cho lấp lánh