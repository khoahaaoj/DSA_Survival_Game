"""
Module WaveManager — Quản lý chuỗi Wave bằng Queue (FIFO).

Kiến trúc:
  - Mỗi Wave được mô tả bằng dict (tỉ lệ quái, spawn interval, thời lượng, cap).
  - Tất cả wave cố định được enqueue khi khởi tạo.
  - WaveManager dequeue từng wave: Wave → Nghỉ (4s) → Wave tiếp → ...
  - Sau khi hết wave cố định: chuyển sang Endless Mode, tự sinh wave khó hơn.
"""
import pygame
import math
import random

from algorithms.queue import Queue
from entities.enemy   import Zombie, Bat, Golem
from settings         import MAP_WIDTH, MAP_HEIGHT


# ---------------------------------------------------------------------------
# Hàm tiện ích nội bộ: Roulette Selection (Prefix Sum + Binary Search O(log N))
# ---------------------------------------------------------------------------
def _roulette(options: list, weights: list):
    """Chọn ngẫu nhiên có trọng số. Dùng Prefix Sum + Binary Search — O(log N)."""
    prefix, s = [], 0
    for w in weights:
        s += w
        prefix.append(s)
    roll = random.uniform(0, prefix[-1])
    lo, hi = 0, len(prefix) - 1
    while lo < hi:
        mid = (lo + hi) // 2
        if roll < prefix[mid]: hi = mid
        else:                   lo = mid + 1
    return options[lo]


# ---------------------------------------------------------------------------
class WaveManager:
    """
    Quản lý vòng đời chuỗi Wave trong game.

    Sử dụng Queue (FIFO) để lưu và giải phóng các Wave theo thứ tự.
    Sau mỗi Wave, hệ thống vào trạng thái nghỉ (BREAK) trước khi
    tự động dequeue và kích hoạt Wave tiếp theo.

    DSA áp dụng:
        - Queue (FIFO) — quản lý thứ tự wave: O(1) enqueue/dequeue.
        - Roulette Selection — chọn loại quái theo tỉ lệ: O(log N).

    Attributes:
        wave_queue  (Queue): Hàng đợi chứa các định nghĩa wave.
        wave_number (int)  : Số thứ tự wave hiện tại.
        is_break    (bool) : True khi đang trong khoảng nghỉ giữa 2 wave.
        spawn_event (int)  : pygame.USEREVENT ID để kích hoạt spawn timer.
    """

    BREAK_MS   = 2000   # Thời gian nghỉ giữa các wave — giảm 4000→2000 để giữ momentum
    SPAWN_DIST = 700    # Bán kính spawn quanh player (px)

    # Định nghĩa 5 wave cố định: [Zombie%, Bat%, Golem%], interval_ms, cap, duration_s
    _FIXED_WAVES = [
        {'weights': [100,  0,  0], 'interval': 600, 'cap':  50, 'duration': 40},
        {'weights': [ 70, 30,  0], 'interval': 500, 'cap':  90, 'duration': 55},
        {'weights': [ 60, 30, 10], 'interval': 400, 'cap': 130, 'duration': 65},
        {'weights': [ 50, 35, 15], 'interval': 320, 'cap': 170, 'duration': 75},
        {'weights': [ 45, 35, 20], 'interval': 260, 'cap': 210, 'duration': 85},
    ]

    def __init__(self, spawn_event: int):
        """
        Khởi tạo WaveManager và nạp toàn bộ wave cố định vào Queue.

        Args:
            spawn_event (int): pygame Event ID dùng cho timer spawn.
        """
        self.spawn_event  = spawn_event
        self.wave_queue   = Queue()
        self.wave_number  = 0
        self.is_break     = False
        self._break_start = 0
        self._wave_start  = 0
        self._current     = None

        # Nạp tất cả wave vào Queue theo thứ tự FIFO
        for wd in self._FIXED_WAVES:
            self.wave_queue.enqueue(wd)

        self._advance()   # Kích hoạt Wave 1

    # ------------------------------------------------------------------
    def update(self, current_time: int) -> bool:
        """
        Cập nhật trạng thái wave mỗi frame.

        Returns:
            True nếu wave vừa kết thúc (để HUD hiển thị thông báo).
        """
        if self.is_break:
            if current_time - self._break_start >= self.BREAK_MS:
                self._advance()
            return False

        elapsed_s = (current_time - self._wave_start) / 1000.0
        if elapsed_s >= self._current['duration']:
            self.is_break     = True
            self._break_start = current_time
            pygame.time.set_timer(self.spawn_event, 0)  # Dừng spawn timer
            return True
        return False

    # ------------------------------------------------------------------
    def try_spawn(self, enemies: list, player) -> object:
        """
        Sinh 1 quái vật theo tỉ lệ của wave hiện tại, nếu chưa đạt cap.

        Args:
            enemies (list): Danh sách quái đang tồn tại (để kiểm tra cap).
            player        : Player object (lấy vị trí và level).

        Returns:
            Instance quái vật, hoặc None nếu không thể spawn.
        """
        if self.is_break or len(enemies) >= self._current['cap']:
            return None

        angle   = random.uniform(0, 2 * math.pi)
        spawn_x = max(0, min(MAP_WIDTH,  player.x + math.cos(angle) * self.SPAWN_DIST))
        spawn_y = max(0, min(MAP_HEIGHT, player.y + math.sin(angle) * self.SPAWN_DIST))

        enemy_cls = _roulette([Zombie, Bat, Golem], self._current['weights'])
        return enemy_cls(spawn_x, spawn_y, player.level)

    # ------------------------------------------------------------------
    @property
    def break_fraction(self) -> float:
        """0.0→1.0 tiến độ đếm ngược nghỉ giữa wave."""
        if not self.is_break:
            return 0.0
        elapsed = pygame.time.get_ticks() - self._break_start
        return min(1.0, elapsed / self.BREAK_MS)

    @property
    def seconds_to_next(self) -> int:
        """Số giây còn lại đến wave tiếp theo."""
        if not self.is_break:
            return 0
        remaining = self.BREAK_MS - (pygame.time.get_ticks() - self._break_start)
        return max(0, int(remaining / 1000) + 1)

    # ------------------------------------------------------------------
    def _advance(self):
        """Dequeue wave tiếp theo (hoặc tạo endless wave nếu Queue rỗng)."""
        if not self.wave_queue.is_empty():
            self._current = self.wave_queue.dequeue()
        else:
            self._current = self._endless()

        self.wave_number += 1
        self.is_break     = False
        self._wave_start  = pygame.time.get_ticks()
        pygame.time.set_timer(self.spawn_event, self._current['interval'])

    def _endless(self) -> dict:
        """Tạo wave vô tận với độ khó tăng dần theo số wave."""
        n = self.wave_number
        return {
            'weights':  [40, 35, 25],
            'interval': max(150, 260 - (n - 5) * 12),
            'cap':      min(400, 210 + (n - 5) * 20),
            'duration': min(120, 90  + (n - 5) * 8),
        }
