"""
Module định nghĩa các thực thể thù địch trong trò chơi.
Được nâng cấp tích hợp Trí tuệ bầy đàn (Boids) ở Tuần 3.
"""
import pygame
import math

class Enemy:
    """
    Lớp đại diện cho quái vật rượt đuổi người chơi.

    Attributes:
        x (float): Tọa độ trục X hiện tại trên bản đồ (World Coordinate).
        y (float): Tọa độ trục Y hiện tại trên bản đồ.
        speed (float): Tốc độ di chuyển cơ bản.
        size (int): Kích thước hitbox của quái vật.
        color (tuple): Màu sắc hiển thị (RGB).
    """

    def __init__(self, x: float, y: float):
        """
        Khởi tạo quái vật mới tại tọa độ xác định.

        Args:
            x (float): Tọa độ X ban đầu.
            y (float): Tọa độ Y ban đầu.
        """
        self.x = x
        self.y = y
        self.speed = 2.5
        self.size = 35
        self.color = (255, 50, 50)  # Màu đỏ cảnh báo

    def update_movement(self, target_x: float, target_y: float, quadtree) -> float:
        """
        Tính toán toán học Vector kết hợp 2 yếu tố:
        1. Lực rượt đuổi (Attraction): Đi thẳng về phía người chơi.
        2. Lực đẩy bầy đàn (Separation - Boids): Né các quái vật khác.

        Truy vấn hàng xóm siêu tốc thông qua QuadTree (O(log N)).

        Args:
            target_x (float): Tọa độ X của Player.
            target_y (float): Tọa độ Y của Player.
            quadtree (QuadTree): Cấu trúc cây tứ phân để tìm hàng xóm.

        Returns:
            float: Khoảng cách tới Player (dùng để đẩy vào Min-Heap).
        """
        # 1. VECTOR RƯỢT ĐUỔI
        dx = target_x - self.x
        dy = target_y - self.y
        dist_to_player = math.sqrt(dx**2 + dy**2)

        dir_x, dir_y = 0, 0
        if dist_to_player != 0:
            dir_x = dx / dist_to_player
            dir_y = dy / dist_to_player

        # 2. VECTOR LỰC ĐẨY BẦY ĐÀN (Boids Separation)
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

        # 3. TỔNG HỢP VECTOR VÀ CHUẨN HÓA
        final_dx = (dir_x * 1.0) + (sep_x * 1.5)
        final_dy = (dir_y * 1.0) + (sep_y * 1.5)

        f_dist = math.sqrt(final_dx**2 + final_dy**2)
        if f_dist != 0:
            self.x += (final_dx / f_dist) * self.speed
            self.y += (final_dy / f_dist) * self.speed

        return dist_to_player

    def draw(self, screen: pygame.Surface, camera_x: float, camera_y: float):
        """
        Vẽ quái vật lên màn hình hiển thị dựa trên tọa độ Camera.

        Args:
            screen (pygame.Surface): Bề mặt (Surface) chính.
            camera_x (float): Tọa độ X của Camera.
            camera_y (float): Tọa độ Y của Camera.
        """
        draw_x = self.x - camera_x
        draw_y = self.y - camera_y
        pygame.draw.rect(screen, self.color, (draw_x, draw_y, self.size, self.size))