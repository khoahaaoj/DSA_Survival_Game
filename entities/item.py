"""
Module: entities/item.py
Định nghĩa các vật phẩm rơi ra khi kẻ địch chết.

Hiện tại: ExpGem (Tinh thể Kinh nghiệm) — khi người chơi đi qua sẽ
nhận EXP để tăng cấp và mở khóa vũ khí mới.
"""
import pygame
import math


class ExpGem:
    """
    Tinh thể Kinh nghiệm (EXP Gem) rơi ra khi kẻ địch chết.

    Người chơi cần di chuyển đến gần (trong vòng 50px) để tự động nhặt.
    Mỗi tinh thể cộng `value` EXP; khi thanh EXP đầy → lên cấp.

    Attributes:
        x, y (float):  Vị trí rơi xuống (trùng với vị trí kẻ địch khi chết).
        value (int):   Lượng EXP nhận được khi nhặt (mặc định: 18).
        size (int):    Bán kính hình kim cương khi vẽ (đơn vị: pixel).
    """

    def __init__(self, x: float, y: float):
        """
        Tạo tinh thể EXP tại vị trí kẻ địch vừa chết.

        Args:
            x (float): Tọa độ X của tinh thể.
            y (float): Tọa độ Y của tinh thể.
        """
        self.x     = x
        self.y     = y
        self.value = 18   # ~6 viên để lên Lv.2 — tạo áp lực vừa phải ở đầu game
        self.size  = 8

    def draw(self, screen: pygame.Surface, camera_x: float, camera_y: float):
        """
        Vẽ tinh thể EXP dưới dạng hình kim cương màu xanh dương.

        Args:
            screen (pygame.Surface): Bề mặt render của Pygame.
            camera_x (float):        Độ lệch camera theo trục X.
            camera_y (float):        Độ lệch camera theo trục Y.
        """
        draw_x = self.x - camera_x
        draw_y = self.y - camera_y

        # 4 đỉnh tạo thành hình thoi (kim cương)
        points = [
            (draw_x,              draw_y - self.size),  # Đỉnh trên
            (draw_x + self.size - 2, draw_y),            # Góc phải
            (draw_x,              draw_y + self.size),  # Đỉnh dưới
            (draw_x - self.size + 2, draw_y),            # Góc trái
        ]
        pygame.draw.polygon(screen, (0, 150, 255), points)        # Màu xanh dương
        pygame.draw.polygon(screen, (255, 255, 255), points, 1)   # Viền trắng — tạo hiệu ứng lấp lánh