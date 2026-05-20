"""
Module Renderer — Kết xuất HUD, Pause Menu, Game Over và Wave Banner.
Tách biệt toàn bộ logic vẽ ra khỏi Game Loop chính để giảm coupling.
"""
import pygame
import math

from settings import WIDTH, HEIGHT


class Renderer:
    """
    Lớp kết xuất đồ họa cho các thành phần UI cố định.
    Nhận screen + fonts từ main, không giữ state game.

    Methods:
        draw_hud()        : EXP bar, HP bar, timer, kill count, wave info.
        draw_pause()      : Overlay + menu dừng game.
        draw_game_over()  : Overlay + stats + nút Restart.
        draw_wave_banner(): Banner thông báo wave mới / đếm ngược.
        draw_pause_btn()  : Nút ||.
    """

    def __init__(self, fonts: tuple):
        """
        Args:
            fonts (tuple): (font_large, font_medium, font_small, font_dmg)
        """
        self.font_large, self.font_medium, self.font_small, self.font_dmg = fonts

        # Bounding boxes cho các nút UI
        self.pause_btn_rect        = pygame.Rect(WIDTH - 50, 45, 35, 35)
        self.menu_rect             = pygame.Rect(WIDTH // 2 - 150, HEIGHT // 2 - 150, 300, 300)
        self.resume_btn_rect       = pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2 - 60,  200, 50)
        self.toggle_music_btn_rect = pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2 + 10,  200, 50)
        self.toggle_sfx_btn_rect   = pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2 + 80,  200, 50)
        self.restart_btn_rect      = pygame.Rect(0, 0, 360, 46)  # vị trí tính động

        self._vn_cache: dict = {}   # Cache font Unicode

    # ------------------------------------------------------------------
    # Font hỗ trợ tiếng Việt (lazy-load)
    # ------------------------------------------------------------------
    def _vn_font(self, size: int) -> pygame.font.Font:
        """Lazy-load font DejaVuSans hỗ trợ Unicode/tiếng Việt."""
        if size not in self._vn_cache:
            path = None
            for name in ["dejavusans", "liberationsans", "ubuntu", "notosans"]:
                path = pygame.font.match_font(name)
                if path:
                    break
            try:
                self._vn_cache[size] = pygame.font.Font(path, size) if path else pygame.font.SysFont(None, size)
            except Exception:
                self._vn_cache[size] = pygame.font.SysFont(None, size)
        return self._vn_cache[size]

    # ------------------------------------------------------------------
    def draw_hud(self, screen: pygame.Surface, player, timer_text: str,
                 kill_count: int, wave_manager=None):
        """
        Vẽ toàn bộ HUD: EXP bar, HP bar, timer, kill count, wave info.
        """
        # EXP bar
        pygame.draw.rect(screen, (20, 20, 20), (5, 5, WIDTH - 10, 25))
        exp_w = (WIDTH - 10) * (player.exp / max(1, player.max_exp))
        pygame.draw.rect(screen, (0, 120, 255), (5, 5, exp_w, 25))
        pygame.draw.rect(screen, (200, 180, 50), (5, 5, WIDTH - 10, 25), 2)

        # HP bar
        hp_ratio  = max(0.0, player.hp / max(1, player.max_hp))
        hp_color  = (50, 220, 60) if hp_ratio > 0.5 else (255, 200, 0) if hp_ratio > 0.25 else (255, 50, 50)
        pygame.draw.rect(screen, (60, 10, 10),   (10, 38, 220, 18), border_radius=4)
        pygame.draw.rect(screen, hp_color,        (10, 38, int(220 * hp_ratio), 18), border_radius=4)
        pygame.draw.rect(screen, (200, 200, 200), (10, 38, 220, 18), 1, border_radius=4)
        hp_label = self.font_dmg.render(f"♥ {max(0, player.hp)}/{player.max_hp}", True, (255, 255, 255))
        screen.blit(hp_label, (14, 41))

        # Level
        lvl_txt = self.font_small.render(f"LV {player.level}", True, (255, 255, 255))
        screen.blit(lvl_txt, (WIDTH - 85, 5))

        # Timer
        t_surf    = self.font_medium.render(timer_text, True, (255, 255, 255))
        t_outline = self.font_medium.render(timer_text, True, (0, 0, 0))
        tx = WIDTH // 2 - t_surf.get_width() // 2
        screen.blit(t_outline, (tx + 2, 42))
        screen.blit(t_surf,    (tx,     40))

        # Kill count
        k_txt = self.font_small.render(f"{kill_count} 💀", True, (255, 255, 255))
        screen.blit(k_txt, (WIDTH - 120, 45))

        # Wave info
        if wave_manager is not None:
            w_label = self._vn_font(20).render(
                f"Wave {wave_manager.wave_number}", True, (255, 220, 80))
            screen.blit(w_label, (WIDTH - w_label.get_width() - 10, 70))

    # ------------------------------------------------------------------
    def draw_pause_btn(self, screen: pygame.Surface, mouse_pos: tuple):
        """Vẽ nút || (pause) góc phải màn hình."""
        col = (180, 180, 180) if self.pause_btn_rect.collidepoint(mouse_pos) else (100, 100, 100)
        pygame.draw.rect(screen, col, self.pause_btn_rect, border_radius=5)
        pygame.draw.rect(screen, (255, 255, 255),
                         (self.pause_btn_rect.x + 10, self.pause_btn_rect.y + 8, 5, 18))
        pygame.draw.rect(screen, (255, 255, 255),
                         (self.pause_btn_rect.x + 20, self.pause_btn_rect.y + 8, 5, 18))

    # ------------------------------------------------------------------
    def draw_pause(self, screen: pygame.Surface, mouse_pos: tuple,
                   music_on: bool, has_music: bool, sfx_on: bool):
        """Vẽ Pause Overlay + Menu."""
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        screen.blit(overlay, (0, 0))

        pygame.draw.rect(screen, (40, 40, 40), self.menu_rect, border_radius=10)
        pygame.draw.rect(screen, (200, 200, 200), self.menu_rect, 2, border_radius=10)

        title = self.font_medium.render("PAUSED", True, (255, 255, 255))
        screen.blit(title, (WIDTH // 2 - title.get_width() // 2, self.menu_rect.y + 20))

        # Resume
        rc = (100, 200, 100) if self.resume_btn_rect.collidepoint(mouse_pos) else (50, 150, 50)
        pygame.draw.rect(screen, rc, self.resume_btn_rect, border_radius=5)
        rt = self.font_small.render("Resume", True, (255, 255, 255))
        screen.blit(rt, (self.resume_btn_rect.centerx - rt.get_width() // 2,
                         self.resume_btn_rect.y + 10))

        # Music toggle
        mc = (100, 100, 200) if self.toggle_music_btn_rect.collidepoint(mouse_pos) else (50, 50, 150)
        pygame.draw.rect(screen, mc, self.toggle_music_btn_rect, border_radius=5)
        ms = "Music: ON" if music_on else "Music: OFF"
        if not has_music: ms = "No bgm.mp3"
        mt = self.font_small.render(ms, True, (255, 255, 255))
        screen.blit(mt, (self.toggle_music_btn_rect.centerx - mt.get_width() // 2,
                         self.toggle_music_btn_rect.y + 10))

        # SFX toggle
        sc = (200, 150, 50) if self.toggle_sfx_btn_rect.collidepoint(mouse_pos) else (150, 100, 30)
        pygame.draw.rect(screen, sc, self.toggle_sfx_btn_rect, border_radius=5)
        st = self.font_small.render("Sound: ON" if sfx_on else "Sound: OFF", True, (255, 255, 255))
        screen.blit(st, (self.toggle_sfx_btn_rect.centerx - st.get_width() // 2,
                         self.toggle_sfx_btn_rect.y + 10))

    # ------------------------------------------------------------------
    def draw_game_over(self, screen: pygame.Surface, player, timer_text: str,
                       kill_count: int, mouse_pos: tuple):
        """Vẽ màn hình Game Over với panel stats và nút Restart."""
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 200))
        screen.blit(overlay, (0, 0))

        pw, ph = 420, 320
        px = WIDTH  // 2 - pw // 2
        py = HEIGHT // 2 - ph // 2
        pygame.draw.rect(screen, (25, 25, 35),  (px, py, pw, ph), border_radius=14)
        pygame.draw.rect(screen, (180, 30, 30), (px, py, pw, ph), 2, border_radius=14)

        # Tiêu đề
        go     = self.font_large.render("GAME OVER", True, (255, 60, 60))
        go_out = self.font_large.render("GAME OVER", True, (100, 0, 0))
        gx = WIDTH // 2 - go.get_width() // 2
        screen.blit(go_out, (gx + 3, py + 20 + 3))
        screen.blit(go,     (gx,     py + 20))

        pygame.draw.line(screen, (100, 30, 30), (px + 20, py + 90), (px + pw - 20, py + 90), 1)

        # Stats
        stats = [
            f"⏱  Thời gian sống: {timer_text}",
            f"☠  Kẻ thù đã giết: {kill_count}",
            f"★  Cấp độ đạt được: {player.level}",
            f"⚔  Số vũ khí trang bị: {len(player.weapons)}",
        ]
        for i, line in enumerate(stats):
            s = self._vn_font(26).render(line, True, (210, 210, 210))
            screen.blit(s, (WIDTH // 2 - s.get_width() // 2, py + 105 + i * 34))

        pygame.draw.line(screen, (100, 30, 30),
                         (px + 20, py + ph - 72), (px + pw - 20, py + ph - 72), 1)

        # Nút Restart
        btn = pygame.Rect(px + 30, py + ph - 62, pw - 60, 46)
        self.restart_btn_rect.update(btn)
        hov = btn.collidepoint(mouse_pos)
        pygame.draw.rect(screen, (50, 180, 50) if hov else (25, 110, 25), btn, border_radius=8)
        pygame.draw.rect(screen, (120, 255, 120), btn, 2, border_radius=8)
        rl = self._vn_font(24).render("► Chơi Lại  [R]", True, (255, 255, 255))
        screen.blit(rl, (btn.centerx - rl.get_width() // 2,
                         btn.centery - rl.get_height() // 2))

    # ------------------------------------------------------------------
    def draw_wave_banner(self, screen: pygame.Surface, wave_manager):
        """Vẽ banner đếm ngược nghỉ giữa các wave."""
        if not wave_manager.is_break:
            return

        frac = wave_manager.break_fraction
        sec  = wave_manager.seconds_to_next

        # Thanh đếm ngược
        bar_w = 400
        bx    = WIDTH // 2 - bar_w // 2
        pygame.draw.rect(screen, (40, 40, 40),   (bx, 68, bar_w, 12), border_radius=4)
        pygame.draw.rect(screen, (255, 160, 0),  (bx, 68, int(bar_w * frac), 12), border_radius=4)
        pygame.draw.rect(screen, (200, 200, 200),(bx, 68, bar_w, 12), 1, border_radius=4)

        msg = self._vn_font(22).render(
            f"Wave {wave_manager.wave_number + 1} bắt đầu sau {sec}s...", True, (255, 220, 100))
        screen.blit(msg, (WIDTH // 2 - msg.get_width() // 2, 84))

    # ------------------------------------------------------------------
    def draw_wave_announcement(self, screen: pygame.Surface, wave_num: int, timer: int):
        """
        Vẽ banner 'WAVE X BẮT ĐẦU!' ở giữa màn hình với hiệu ứng fade in/out.

        Args:
            wave_num (int): Số thứ tự wave hiện tại.
            timer    (int): Frame countdown (150 → 0).
        """
        MAX  = 150
        FADE = 30   # Số frame để fade in / fade out

        # Tính alpha theo giai đoạn
        if timer > MAX - FADE:              # Fade in
            alpha = int(255 * (MAX - timer) / FADE)
        elif timer < FADE:                  # Fade out
            alpha = int(255 * timer / FADE)
        else:                               # Hold
            alpha = 255
        alpha = max(0, min(255, alpha))

        # Panel nền
        pw, ph = 380, 105
        px     = WIDTH  // 2 - pw // 2
        py     = HEIGHT // 2 - 90

        panel = pygame.Surface((pw, ph), pygame.SRCALPHA)
        panel.fill((0, 0, 0, int(alpha * 0.65)))
        pygame.draw.rect(panel, (*( 255, 200, 50), alpha), (0, 0, pw, ph), 2, border_radius=12)
        screen.blit(panel, (px, py))

        # Text "WAVE N"
        t1 = self._vn_font(54).render(f"WAVE  {wave_num}", True, (255, 200, 50))
        s1 = pygame.Surface(t1.get_size(), pygame.SRCALPHA)
        s1.blit(t1, (0, 0))
        s1.set_alpha(alpha)
        screen.blit(s1, (WIDTH // 2 - t1.get_width() // 2, py + 8))

        # Sub-text "BẮT ĐẦU!"
        t2 = self._vn_font(26).render("BẮT ĐẦU!", True, (255, 240, 180))
        s2 = pygame.Surface(t2.get_size(), pygame.SRCALPHA)
        s2.blit(t2, (0, 0))
        s2.set_alpha(alpha)
        screen.blit(s2, (WIDTH // 2 - t2.get_width() // 2, py + 68))

