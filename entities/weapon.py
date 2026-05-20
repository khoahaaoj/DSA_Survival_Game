"""
Module quản lý hệ thống Vũ khí (Weapons) và Thực thể đạn (Projectiles).
Cung cấp các lớp vũ khí đa dạng (Súng tỉa đơn mục tiêu, Hào quang diện rộng, Sét đánh ngẫu nhiên)
kết hợp với các hiệu ứng thị giác tính toán bằng Toán học (Motion Trail, Alpha Blending)
thay vì sử dụng tài nguyên ảnh tĩnh (Static Assets).
"""
import pygame
import math
import random
from settings import *


# ==========================================
# CLASS BULLET: ĐẠN TIA BĂNG CỰC QUANG
# ==========================================
class Bullet:
    """
    Thực thể đạn vật lý (Projectile) bay theo đường thẳng với hiệu ứng Vết mờ chuyển động (Motion Trail).
    Tích hợp cơ chế Quản lý bộ nhớ (Garbage Collection) thông qua biến vòng đời (Time-To-Live).

    Attributes:
        x (float), y (float): Tọa độ không gian 2D hiện tại.
        dx (float), dy (float): Vector hướng (Direction Vector) đã được chuẩn hóa.
        speed (float): Vận tốc tuyến tính của đạn.
        trail_points (list): Hàng đợi lưu trữ lịch sử tọa độ để kết xuất đuôi đạn.
        life_time (int): Thời gian tồn tại hiện tại (tính bằng số khung hình).
        max_life (int): Ngưỡng vòng đời tối đa (Time-To-Live) để tự hủy, chống rò rỉ bộ nhớ (Memory Leak).
    """

    def __init__(self, x: float, y: float, tx: float, ty: float, damage: float):
        self.x, self.y = x, y
        self.speed = 12.0
        self.damage = damage
        self.head_radius = 5

        # Toán học Vector: Tính toán và chuẩn hóa vector hướng mục tiêu
        dist = math.sqrt((tx - x) ** 2 + (ty - y) ** 2)
        self.dx = (tx - x) / dist if dist != 0 else 1
        self.dy = (ty - y) / dist if dist != 0 else 0

        self.trail_points = []
        self.max_trail_length = 15

        # Cơ chế TTL (Time-To-Live): Đạn tự hủy sau ~1.3 giây nếu không trúng mục tiêu
        self.life_time = 0
        self.max_life = 80

    def move(self):
        """
        Cập nhật động học của viên đạn.
        Đẩy tọa độ hiện tại vào mảng lịch sử trước khi nội suy vị trí mới.
        """
        self.trail_points.insert(0, (self.x, self.y))
        if len(self.trail_points) > self.max_trail_length:
            self.trail_points.pop()

        self.x += self.dx * self.speed
        self.y += self.dy * self.speed

        self.life_time += 1

    def draw(self, screen: pygame.Surface, cx: float, cy: float):
        """
        Kết xuất đồ họa cho viên đạn (Rendering).
        Áp dụng thuật toán Alpha Blending để tạo hiệu ứng mờ dần (Fade-out)
        và nội suy kích thước (Shrink) cho phần đuôi tia sáng.
        """
        draw_x = int(self.x - cx)
        draw_y = int(self.y - cy)

        # Kết xuất đuôi đạn (Trail Rendering)
        if len(self.trail_points) > 1:
            for i in range(len(self.trail_points) - 1):
                # Nội suy tuyến tính (Lerp) cho độ trong suốt và độ dày
                alpha = int(250 * (1 - (i / self.max_trail_length)))
                width = int(6 * (1 - (i / self.max_trail_length))) + 1

                p1 = self.trail_points[i]
                p2 = self.trail_points[i + 1]
                start_p = (int(p1[0] - cx), int(p1[1] - cy))
                end_p = (int(p2[0] - cx), int(p2[1] - cy))

                # Hiệu ứng chuyển màu (Color Gradient): Từ Xanh Cyan sang Trắng
                if i < self.max_trail_length // 2:
                    color = (0, 255, 255, alpha)
                else:
                    color = (255, 255, 255, alpha)

                # Viewport Culling: Chỉ vẽ các đoạn thẳng nằm trong màn hình
                if abs(start_p[0] - end_p[0]) < WIDTH and abs(start_p[1] - end_p[1]) < HEIGHT:
                    pygame.draw.line(screen, color, start_p, end_p, width)

        # Kết xuất lõi năng lượng (Đầu đạn)
        pygame.draw.circle(screen, (255, 255, 255, 250), (draw_x, draw_y), self.head_radius)
        pygame.draw.circle(screen, (0, 255, 255, 150), (draw_x, draw_y), self.head_radius + 2, 2)


# ==========================================
# GIAO DIỆN VŨ KHÍ (WEAPON INTERFACES)
# ==========================================
class Weapon:
    """Lớp Cơ sở Trừu tượng (Abstract Base Class) cho hệ thống vũ khí."""

    def update(self, player, quadtree, target_heap, current_time) -> list:
        """Hàm ảo để cập nhật logic vật lý và trả về danh sách sự kiện sát thương."""
        return []

    def draw(self, screen, cx, cy, player):
        """Hàm ảo để kết xuất hiệu ứng vũ khí lên màn hình."""
        pass


class Gun(Weapon):
    """
    Súng bắn tỉa (Sniper) tích hợp cơ chế Auto-aim thông qua Min-Heap.
    Chỉ nạp và khai hỏa viên đạn tiếp theo khi viên đạn trước đó đã bị thu gom (Garbage Collected).
    """

    def __init__(self):
        self.bullets = []
        self.damage = 25
        self.level = 1          # Cấp độ hiện tại của súng
        self.multi_shot = 1     # Số đạn bắn mỗi loạt (tăng khi lên Lv.2)
        self.bullet_speed = 7.0   # Tốc độ đạn (tăng khi lên Lv.3) — 7px/frame = nhìn thấy trajectory

    def update(self, player, quadtree, target_heap, current_time) -> list:
        events = []

        # Cơ chế Sniper: Khai thác đỉnh của Min-Heap O(1) để tìm mục tiêu gần nhất
        # Lv.2+: bắn multi_shot viên đạn nhắm vào các mục tiêu khác nhau
        if len(self.bullets) == 0:
            for _ in range(self.multi_shot):
                target = target_heap.pop()
                if target:
                    b = Bullet(player.x, player.y, target[1].x, target[1].y, self.damage)
                    b.speed = self.bullet_speed  # Lv.3: tốc độ đạn tăng gấp đôi
                    self.bullets.append(b)

        for b in self.bullets[:]:
            b.move()

            # Garbage Collection (GC): Thu gom đạn rác nếu vượt quá vòng đời (TTL) hoặc văng ra khỏi Map
            if b.life_time >= b.max_life or b.x < -200 or b.x > MAP_WIDTH + 200 or b.y < -200 or b.y > MAP_HEIGHT + 200:
                if b in self.bullets:
                    self.bullets.remove(b)
                continue

            # Truy vấn không gian cục bộ thông qua QuadTree (Spatial Query) O(log N)
            nearby = quadtree.query(pygame.Rect(b.x - 5, b.y - 5, 10, 10), [])
            for e in nearby:
                # Kiểm tra va chạm vật lý chính xác bằng Khoảng cách Euclidean
                if math.sqrt((b.x - e.x) ** 2 + (b.y - e.y) ** 2) < 20:
                    e.hp -= b.damage
                    events.append({'x': e.x, 'y': e.y, 'damage': b.damage})

                    # Hủy đạn ngay sau khi va chạm thành công
                    if b in self.bullets:
                        self.bullets.remove(b)
                    break
        return events

    def draw(self, screen, cx, cy, player):
        for b in self.bullets: b.draw(screen, cx, cy)


class HolyAura(Weapon):
    """
    Kỹ năng Sát thương diện rộng (AoE - Area of Effect) xung quanh người chơi.
    Sử dụng QuadTree để áp dụng sát thương hàng loạt cực kỳ hiệu quả.
    """

    def __init__(self):
        self.radius = 120
        self.damage = 15
        self.tick = 250
        self.last = 0
        self.level = 1  # Cấp độ Thánh Quang

    def update(self, player, quadtree, target_heap, current_time) -> list:
        events = []
        if current_time - self.last >= self.tick:
            # Truy vấn vùng hình chữ nhật bao quanh bán kính Aura
            nearby = quadtree.query(pygame.Rect(player.x - 120, player.y - 120, 240, 240), [])
            for e in nearby:
                if math.sqrt((player.x - e.x) ** 2 + (player.y - e.y) ** 2) < self.radius:
                    e.hp -= self.damage
                    events.append({'x': e.x, 'y': e.y, 'damage': self.damage})
            self.last = current_time
        return events

    def draw(self, screen, cx, cy, player):
        # Hiệu ứng nhịp đập (Pulsing) tính bằng hàm Sin theo thời gian
        pulse = math.sin(pygame.time.get_ticks() / 100.0) * 8
        pygame.draw.circle(screen, (0, 255, 255), (int(player.x - cx), int(player.y - cy)), int(self.radius + pulse), 3)


class ThunderStorm(Weapon):
    """
    Kỹ năng Sét đánh ngẫu nhiên toàn bản đồ.
    Sử dụng hàm random.sample để lựa chọn mục tiêu từ tập hợp các thực thể trả về bởi QuadTree.
    """

    def __init__(self):
        self.cooldown = 1500
        self.last = 0
        self.damage = 65          # Nerf: 100 → 65 (tránh bá đạo từ Level 3)
        self.strikes = []
        self.level = 1
        self.max_strikes = 2

    def update(self, player, quadtree, target_heap, current_time) -> list:
        events = []
        # Xóa các tia sét cũ đã tồn tại quá 100ms
        self.strikes = [s for s in self.strikes if current_time - s['t'] < 100]

        if current_time - self.last >= self.cooldown:
            # Quét một vùng rộng (Viewport) để tìm mục tiêu
            nearby = quadtree.query(pygame.Rect(player.x - 500, player.y - 400, 1000, 800), [])
            if nearby:
                # Trừng phạt ngẫu nhiên tối đa max_strikes mục tiêu (tăng theo cấp)
                for target in random.sample(nearby, min(self.max_strikes, len(nearby))):
                    target.hp -= self.damage
                    self.strikes.append({'x': target.x, 'y': target.y, 't': current_time})
                    events.append({'x': target.x, 'y': target.y, 'damage': self.damage})
            self.last = current_time
        return events

    def draw(self, screen, cx, cy, player):
        # Kết xuất tia sét thẳng đứng giáng từ trên trời xuống
        for s in self.strikes:
            pygame.draw.line(screen, (255, 255, 100), (s['x'] - cx, s['y'] - cy - 800), (s['x'] - cx, s['y'] - cy), 5)
            pygame.draw.circle(screen, (255, 255, 255), (int(s['x'] - cx), int(s['y'] - cy)), 25, 3)