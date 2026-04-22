import pygame
import math


class Enemy:
    """ Lớp đại diện cho quái vật rượt đuổi người chơi. """

    def __init__(self, x: float, y: float):
        self.x = x
        self.y = y
        self.speed = 2.5
        self.size = 35
        self.color = (255, 50, 50)  # Màu đỏ

    def move_towards(self, target_x: float, target_y: float):
        """ Tính toán vector và di chuyển thẳng về phía mục tiêu. """
        dx = target_x - self.x
        dy = target_y - self.y
        distance = math.sqrt(dx ** 2 + dy ** 2)

        if distance != 0:
            self.x += (dx / distance) * self.speed
            self.y += (dy / distance) * self.speed

        return distance  # Trả về khoảng cách để đẩy vào Min-Heap

    def draw(self, screen, camera_x, camera_y):
        draw_x = self.x - camera_x
        draw_y = self.y - camera_y
        pygame.draw.rect(screen, self.color, (draw_x, draw_y, self.size, self.size))