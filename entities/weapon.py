"""
Module cung cấp các thực thể vũ khí (Weapon) và đạn (Bullet) của trò chơi.
Bao gồm súng (Gun), vòng năng lượng (HolyAura) và sét đánh (ThunderStorm).
"""
import pygame
import math
import random
from settings import *


# ==========================================
# CLASS BULLET "TIA BĂNG CỰC QUANG"
# ==========================================
class Bullet:
    """
    Thực thể đạn vật lý bay theo đường thẳng với hiệu ứng vết đuôi (trail).

    Attributes:
        x (float): Tọa độ X hiện tại.
        y (float): Tọa độ Y hiện tại.
        dx (float): Hướng bay theo trục X (Vector chuẩn hóa).
        dy (float): Hướng bay theo trục Y (Vector chuẩn hóa).
        trail_points (list): Danh sách các điểm trước đó để vẽ đuôi tia sáng.
    """

    def __init__(self, x, y, tx, ty, damage):
        self.x, self.y = x, y
        self.speed = 6.0
        self.damage = damage
        self.head_radius = 5

        dist = math.sqrt((tx - x) ** 2 + (ty - y) ** 2)
        self.dx = (tx - x) / dist if dist != 0 else 1
        self.dy = (ty - y) / dist if dist != 0 else 0

        self.trail_points = []
        self.max_trail_length = 15

    def move(self):
        """Cập nhật tọa độ của đạn và ghi nhận điểm ảnh (trail) mới nhất."""
        self.trail_points.insert(0, (self.x, self.y))
        if len(self.trail_points) > self.max_trail_length:
            self.trail_points.pop()

        self.x += self.dx * self.speed
        self.y += self.dy * self.speed

    def draw(self, screen, cx, cy):
        """Vẽ đạn và hiệu ứng vết sáng giảm dần (fading tail) lên màn hình."""
        draw_x = int(self.x - cx)
        draw_y = int(self.y - cy)

        if len(self.trail_points) > 1:
            for i in range(len(self.trail_points) - 1):
                alpha = int(250 * (1 - (i / self.max_trail_length)))
                width = int(6 * (1 - (i / self.max_trail_length))) + 1

                p1 = self.trail_points[i]
                p2 = self.trail_points[i + 1]
                start_p = (int(p1[0] - cx), int(p1[1] - cy))
                end_p = (int(p2[0] - cx), int(p2[1] - cy))

                if i < self.max_trail_length // 2:
                    color = (0, 255, 255, alpha)
                else:
                    color = (255, 255, 255, alpha)

                if abs(start_p[0] - end_p[0]) < WIDTH and abs(start_p[1] - end_p[1]) < HEIGHT:
                    pygame.draw.line(screen, color, start_p, end_p, width)

        pygame.draw.circle(screen, (255, 255, 255, 250), (draw_x, draw_y), self.head_radius)
        pygame.draw.circle(screen, (0, 255, 255, 150), (draw_x, draw_y), self.head_radius + 2, 2)


# ==========================================
# VŨ KHÍ CỦA TRÒ CHƠI
# ==========================================
class Weapon:
    """Lớp Interface cơ sở cho tất cả vũ khí."""

    def update(self, player, quadtree, target_heap, current_time):
        """Cập nhật logic, va chạm và sát thương."""
        return []

    def draw(self, screen, cx, cy, player):
        """Vẽ đồ họa riêng của vũ khí."""
        pass


class Gun(Weapon):
    """
    Súng bắn đạn thẳng đơn mục tiêu, cơ chế 1 viên (Sniper).
    Chỉ khai hỏa khi viên đạn trước đó đã trúng đích hoặc biến mất.
    """

    def __init__(self):
        # Không cần dùng thời gian hồi chiêu (cooldown) nữa
        self.bullets = []
        self.damage = 25

    def update(self, player, quadtree, target_heap, current_time):
        events = []

        # CƠ CHẾ MỚI: Chỉ đẻ thêm đạn khi không còn viên đạn nào đang bay
        if len(self.bullets) == 0:
            target = target_heap.pop()
            if target:
                self.bullets.append(Bullet(player.x, player.y, target[1].x, target[1].y, self.damage))

        for b in self.bullets[:]:
            b.move()

            # CHỐNG KẸT SÚNG: Xóa đạn nếu bay trượt và ra khỏi bản đồ quá 200 pixel
            if b.x < -200 or b.x > MAP_WIDTH + 200 or b.y < -200 or b.y > MAP_HEIGHT + 200:
                if b in self.bullets:
                    self.bullets.remove(b)
                continue

            nearby = quadtree.query(pygame.Rect(b.x - 5, b.y - 5, 10, 10), [])
            for e in nearby:
                if math.sqrt((b.x - e.x) ** 2 + (b.y - e.y) ** 2) < 20:
                    e.hp -= b.damage
                    events.append({'x': e.x, 'y': e.y, 'damage': b.damage})
                    # Đạn nổ sau khi trúng đích, dọn đường cho viên tiếp theo
                    if b in self.bullets:
                        self.bullets.remove(b)
                    break
        return events

    def draw(self, screen, cx, cy, player):
        for b in self.bullets: b.draw(screen, cx, cy)


class HolyAura(Weapon):
    """Vòng năng lượng phát sát thương diện rộng xung quanh người chơi."""

    def __init__(self):
        self.radius, self.damage, self.tick, self.last = 120, 15, 250, 0

    def update(self, player, quadtree, target_heap, current_time):
        events = []
        if current_time - self.last >= self.tick:
            nearby = quadtree.query(pygame.Rect(player.x - 120, player.y - 120, 240, 240), [])
            for e in nearby:
                if math.sqrt((player.x - e.x) ** 2 + (player.y - e.y) ** 2) < self.radius:
                    e.hp -= self.damage
                    events.append({'x': e.x, 'y': e.y, 'damage': self.damage})
            self.last = current_time
        return events

    def draw(self, screen, cx, cy, player):
        pulse = math.sin(pygame.time.get_ticks() / 100.0) * 8
        pygame.draw.circle(screen, (0, 255, 255), (int(player.x - cx), int(player.y - cy)), int(self.radius + pulse), 3)


class ThunderStorm(Weapon):
    """Kỹ năng sấm sét ngẫu nhiên giật xuống bản đồ gây sát thương lớn."""

    def __init__(self):
        self.cooldown, self.last, self.damage, self.strikes = 1500, 0, 100, []

    def update(self, player, quadtree, target_heap, current_time):
        events = []
        self.strikes = [s for s in self.strikes if current_time - s['t'] < 100]
        if current_time - self.last >= self.cooldown:
            nearby = quadtree.query(pygame.Rect(player.x - 500, player.y - 400, 1000, 800), [])
            if nearby:
                for target in random.sample(nearby, min(2, len(nearby))):
                    target.hp -= self.damage
                    self.strikes.append({'x': target.x, 'y': target.y, 't': current_time})
                    events.append({'x': target.x, 'y': target.y, 'damage': self.damage})
            self.last = current_time
        return events

    def draw(self, screen, cx, cy, player):
        for s in self.strikes:
            pygame.draw.line(screen, (255, 255, 100), (s['x'] - cx, s['y'] - cy - 800), (s['x'] - cx, s['y'] - cy), 5)
            pygame.draw.circle(screen, (255, 255, 255), (int(s['x'] - cx), int(s['y'] - cy)), 25, 3)