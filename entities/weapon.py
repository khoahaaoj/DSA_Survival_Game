import pygame
import math


class Bullet:
    """ Lớp đại diện cho viên đạn được bắn ra từ vũ khí tự động. """

    def __init__(self, start_x, start_y, target_x, target_y):
        self.x = start_x
        self.y = start_y
        self.speed = 12.0
        self.size = 8
        self.color = (255, 255, 0)  # Đạn màu vàng

        # Tính toán vector hướng bay của đạn
        dx = target_x - self.x
        dy = target_y - self.y
        distance = math.sqrt(dx ** 2 + dy ** 2)

        if distance != 0:
            self.dx = (dx / distance) * self.speed
            self.dy = (dy / distance) * self.speed
        else:
            self.dx, self.dy = 0, 0

    def move(self):
        self.x += self.dx
        self.y += self.dy

    def draw(self, screen, camera_x, camera_y):
        draw_x = self.x - camera_x
        draw_y = self.y - camera_y
        pygame.draw.circle(screen, self.color, (int(draw_x), int(draw_y)), self.size)