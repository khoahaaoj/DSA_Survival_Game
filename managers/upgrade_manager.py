"""
Module UpgradeManager — Hệ thống Level-Up kiểu Vampire Survivors.
Tách biệt toàn bộ logic nâng cấp và UI thẻ khỏi game loop chính.
"""
import math
import pygame

from settings         import WIDTH, HEIGHT
from entities.weapon  import Gun, HolyAura, ThunderStorm


# ---------------------------------------------------------------------------
# Font cache Unicode (hỗ trợ tiếng Việt)
# ---------------------------------------------------------------------------
_VN_CACHE: dict = {}

def _vn(size: int) -> pygame.font.Font:
    """Lazy-load font DejaVuSans hỗ trợ tiếng Việt, cache theo size."""
    if size not in _VN_CACHE:
        path = None
        for name in ["dejavusans", "liberationsans", "ubuntu", "notosans"]:
            path = pygame.font.match_font(name)
            if path:
                break
        try:
            _VN_CACHE[size] = pygame.font.Font(path, size) if path else pygame.font.SysFont(None, size)
        except Exception:
            _VN_CACHE[size] = pygame.font.SysFont(None, size)
    return _VN_CACHE[size]


# ---------------------------------------------------------------------------
def build_upgrade_pool(player) -> list:
    """
    Xây dựng pool nâng cấp hợp lệ dựa trên trạng thái hiện tại của người chơi.
    Chỉ hiện vũ khí chưa có, vũ khí chưa max level, và tăng chỉ số.
    """
    pool = []
    gun     = next((w for w in player.weapons if isinstance(w, Gun)),        None)
    aura    = next((w for w in player.weapons if isinstance(w, HolyAura)),   None)
    thunder = next((w for w in player.weapons if isinstance(w, ThunderStorm)), None)

    # Vũ khí mới (chưa sở hữu)
    if gun is None:
        pool.append({'id': 'new_gun',     'name': 'Súng Tỉa',   'type': 'weapon', 'level': 1,
                     'icon': 'gun',     'color': (0, 180, 255),
                     'desc': 'Bắn đạn homing tự dò\nmục tiêu gần nhất'})
    if aura is None:
        pool.append({'id': 'new_aura',    'name': 'Thánh Quang', 'type': 'weapon', 'level': 1,
                     'icon': 'aura',    'color': (0, 230, 180),
                     'desc': 'Vòng sáng liên tục\ngây sát thương xung quanh'})
    if thunder is None:
        pool.append({'id': 'new_thunder', 'name': 'Bão Sét',     'type': 'weapon', 'level': 1,
                     'icon': 'thunder', 'color': (255, 220, 0),
                     'desc': 'Sét đánh ngẫu nhiên\nvào các kẻ thù gần đó'})

    # Nâng cấp vũ khí đang có (chưa Lv.3)
    if gun and gun.level < 3:
        lv = gun.level + 1
        descs = {2: 'Bắn 2 đạn cùng lúc\n+15 sát thương', 3: 'Tốc độ đạn x2\n+20 sát thương'}
        pool.append({'id': 'upgrade_gun', 'name': f'Súng Tỉa Lv.{lv}', 'type': 'upgrade', 'level': lv,
                     'icon': 'gun',     'color': (0, 180, 255), 'desc': descs[lv]})
    if aura and aura.level < 3:
        lv = aura.level + 1
        descs = {2: '+60 bán kính\n+20 sát thương', 3: 'Tần suất x2\n+30 sát thương'}
        pool.append({'id': 'upgrade_aura', 'name': f'Thánh Quang Lv.{lv}', 'type': 'upgrade', 'level': lv,
                     'icon': 'aura',    'color': (0, 230, 180), 'desc': descs[lv]})
    if thunder and thunder.level < 3:
        lv = thunder.level + 1
        descs = {2: 'Đánh 3 mục tiêu\n+40 sát thương', 3: 'Cooldown giảm 50%\n+50 sát thương'}
        pool.append({'id': 'upgrade_thunder', 'name': f'Bão Sét Lv.{lv}', 'type': 'upgrade', 'level': lv,
                     'icon': 'thunder', 'color': (255, 220, 0), 'desc': descs[lv]})

    # Tăng chỉ số (luôn có sẵn)
    pool.append({'id': 'stat_hp',     'name': 'Hồi Máu',  'type': 'stat', 'level': 1,
                 'icon': 'heart',  'color': (255, 80, 100),
                 'desc': 'Hồi phục 40% HP tối đa\nngay lập tức'})
    pool.append({'id': 'stat_max_hp', 'name': 'Sinh Lực', 'type': 'stat', 'level': 1,
                 'icon': 'shield', 'color': (220, 100, 130),
                 'desc': '+50 HP tối đa\nHồi 20 HP'})
    pool.append({'id': 'stat_speed',  'name': 'Tốc Độ',   'type': 'stat', 'level': 1,
                 'icon': 'boot',   'color': (80, 255, 140),
                 'desc': '+0.7 tốc độ di chuyển\nLinh hoạt hơn'})
    pool.append({'id': 'stat_damage', 'name': 'Sức Mạnh', 'type': 'stat', 'level': 1,
                 'icon': 'sword',  'color': (255, 140, 40),
                 'desc': '+12 sát thương\ncho tất cả vũ khí'})
    return pool


# ---------------------------------------------------------------------------
def apply_upgrade(choice_id: str, player):
    """
    Áp dụng nâng cấp được chọn vào player/vũ khí.
    Biến đổi trực tiếp attribute — không có side-effect khác.
    """
    gun     = next((w for w in player.weapons if isinstance(w, Gun)),          None)
    aura    = next((w for w in player.weapons if isinstance(w, HolyAura)),     None)
    thunder = next((w for w in player.weapons if isinstance(w, ThunderStorm)), None)

    if   choice_id == 'new_gun':       player.weapons.append(Gun())
    elif choice_id == 'new_aura':      player.weapons.append(HolyAura())
    elif choice_id == 'new_thunder':   player.weapons.append(ThunderStorm())

    elif choice_id == 'upgrade_gun' and gun:
        gun.level += 1
        if gun.level == 2: gun.damage += 15;  gun.multi_shot  = 2
        else:              gun.damage += 20;  gun.bullet_speed = 11.0  # Lv.3: 11px/frame (vẫn nhanh hơn base rõ rệt)

    elif choice_id == 'upgrade_aura' and aura:
        aura.level += 1
        if aura.level == 2: aura.radius += 60; aura.damage += 20
        else:               aura.tick = max(100, aura.tick // 2); aura.damage += 30

    elif choice_id == 'upgrade_thunder' and thunder:
        thunder.level += 1
        if thunder.level == 2: thunder.max_strikes = 3; thunder.damage += 40
        else:                  thunder.cooldown = thunder.cooldown // 2; thunder.damage += 50

    elif choice_id == 'stat_hp':
        player.hp = min(player.max_hp, player.hp + int(player.max_hp * 0.4))
    elif choice_id == 'stat_max_hp':
        player.max_hp += 50;  player.hp = min(player.max_hp, player.hp + 20)
    elif choice_id == 'stat_speed':
        player.speed += 0.7
    elif choice_id == 'stat_damage':
        for w in player.weapons:
            w.damage += 12


# ---------------------------------------------------------------------------
def draw_upgrade_icon(screen: pygame.Surface, icon: str, cx: int, cy: int,
                      color: tuple, t: int):
    """Vẽ icon toán học (không cần ảnh). t = tick để tạo hiệu ứng pulsing."""
    pulse = int(math.sin(t / 200.0) * 4)
    r, g, b_c = color
    glow = (min(255, r + 80), min(255, g + 80), min(255, b_c + 80))

    if icon == 'gun':
        pygame.draw.rect(screen, color, (cx - 22, cy - 6,  38, 12), border_radius=3)
        pygame.draw.rect(screen, glow,  (cx + 14, cy - 4,  16,  8), border_radius=2)
        pygame.draw.rect(screen, color, (cx - 10, cy +  6, 10, 14), border_radius=2)
        pygame.draw.circle(screen, (0, 255, 255), (cx + 30 + pulse, cy), 5)
    elif icon == 'aura':
        for i in range(3):
            r2 = 28 - i * 8 + pulse
            s  = pygame.Surface((r2 * 2 + 4, r2 * 2 + 4), pygame.SRCALPHA)
            pygame.draw.circle(s, (*color, 60 + i * 40), (r2 + 2, r2 + 2), r2, 3)
            screen.blit(s, (cx - r2 - 2, cy - r2 - 2))
        pygame.draw.circle(screen, glow, (cx, cy), 8)
    elif icon == 'thunder':
        pts = [(cx-8, cy-26), (cx+6, cy-4), (cx-2, cy-4),
               (cx+12, cy+24), (cx-4, cy+2), (cx+6, cy+2)]
        pygame.draw.polygon(screen, color, pts)
        pygame.draw.polygon(screen, glow, pts, 2)
        pygame.draw.circle(screen, glow, (cx + 12, cy + 24), 4 + pulse)
    elif icon == 'heart':
        pygame.draw.circle(screen, color, (cx - 9, cy - 8), 11)
        pygame.draw.circle(screen, color, (cx + 9, cy - 8), 11)
        pygame.draw.polygon(screen, color, [(cx-20, cy-2), (cx+20, cy-2), (cx, cy+22)])
        pygame.draw.circle(screen, glow, (cx - 9, cy - 8), 11, 2)
        pygame.draw.circle(screen, glow, (cx + 9, cy - 8), 11, 2)
    elif icon == 'shield':
        pts = [(cx, cy-26-pulse), (cx+20, cy-10), (cx+20, cy+8),
               (cx, cy+26+pulse), (cx-20, cy+8), (cx-20, cy-10)]
        pygame.draw.polygon(screen, color, pts)
        pygame.draw.polygon(screen, glow,  pts, 2)
        pygame.draw.line(screen, glow, (cx, cy-14-pulse), (cx, cy+14+pulse), 2)
    elif icon == 'boot':
        pygame.draw.rect(screen, color, (cx-14, cy-20, 10, 32), border_radius=3)
        pygame.draw.rect(screen, color, (cx-14, cy+8,  28, 12), border_radius=4)
        pygame.draw.rect(screen, glow,  (cx-14, cy-20, 10, 32), 2, border_radius=3)
        for i in range(3):
            x_off = cx + 10 + i * 7 + pulse
            pygame.draw.line(screen, (*color, 180 - i*50),
                             (x_off, cy-10+i*6), (x_off+12, cy-10+i*6), 2)
    elif icon == 'sword':
        pygame.draw.line(screen, color, (cx-4, cy+26), (cx+10, cy-26-pulse), 6)
        pygame.draw.line(screen, glow,  (cx-4, cy+26), (cx+10, cy-26-pulse), 2)
        pygame.draw.line(screen, glow, (cx-16, cy+10), (cx+14, cy-4), 4)
        pygame.draw.circle(screen, glow, (cx-4, cy+24), 5)


# ---------------------------------------------------------------------------
def draw_level_up_screen(screen: pygame.Surface, choices: list, fonts: tuple,
                         mouse_pos: tuple, t: int) -> list:
    """
    Kết xuất màn hình chọn phần thưởng Level-Up (3 thẻ).

    Returns:
        list[pygame.Rect]: Rect của từng thẻ để game loop xử lý click.
    """
    font_large = fonts[0]

    # Overlay mờ
    ov = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    ov.fill((0, 0, 0, 200))
    screen.blit(ov, (0, 0))

    # Tiêu đề LEVEL UP! (pulsing)
    gv    = int(180 + math.sin(t / 120.0) * 75)
    title = font_large.render("LEVEL UP!", True, (255, gv, 0))
    tout  = font_large.render("LEVEL UP!", True, (80, 40, 0))
    tx    = WIDTH // 2 - title.get_width() // 2
    screen.blit(tout, (tx + 3, 93));  screen.blit(title, (tx, 90))

    sub = _vn(26).render("Chọn 1 phần thưởng", True, (200, 200, 200))
    screen.blit(sub, (WIDTH // 2 - sub.get_width() // 2, 155))

    CARD_W, CARD_H = 230, 310
    total_w = len(choices) * CARD_W + (len(choices) - 1) * 30
    start_x = WIDTH // 2 - total_w // 2
    card_y  = HEIGHT // 2 - CARD_H // 2 + 20
    BREAK_MS = 2000
    rects   = []

    for i, card in enumerate(choices):
        cx   = start_x + i * (CARD_W + 30)
        rect = pygame.Rect(cx, card_y, CARD_W, CARD_H)
        rects.append(rect)
        hov  = rect.collidepoint(mouse_pos)

        bc   = card['color']
        r2, g2, b2 = bc
        bright = (min(255, r2+60), min(255, g2+60), min(255, b2+60))

        if hov:
            gs = pygame.Surface((CARD_W+20, CARD_H+20), pygame.SRCALPHA)
            pygame.draw.rect(gs, (*bc, 60), (0, 0, CARD_W+20, CARD_H+20), border_radius=16)
            screen.blit(gs, (cx-10, card_y-10))

        pygame.draw.rect(screen, (60, 60, 75) if hov else (45, 45, 55), rect, border_radius=12)
        pygame.draw.rect(screen, bright if hov else bc, rect, 4 if hov else 3, border_radius=12)

        # Badge
        badge_map = {'weapon': 'VŨ KHÍ', 'upgrade': 'NÂNG CẤP', 'stat': 'CHỈ SỐ'}
        bt = _vn(18).render(badge_map.get(card['type'], ''), True, bright)
        screen.blit(bt, (cx + CARD_W//2 - bt.get_width()//2, card_y + 12))

        # Icon
        draw_upgrade_icon(screen, card['icon'], cx + CARD_W//2, card_y + 100, bc, t)

        # Sao cấp độ
        for si in range(3):
            sc = bc if si < card['level'] else (60, 60, 60)
            sx = cx + CARD_W//2 - 24 + si * 24
            pts = []
            for j in range(5):
                a  = math.pi/2 + j * 2*math.pi/5
                pts.append((sx + 9*math.cos(a), card_y+162 + 9*math.sin(a)))
                a2 = a + math.pi/5
                pts.append((sx + 4*math.cos(a2), card_y+162 + 4*math.sin(a2)))
            pygame.draw.polygon(screen, sc, pts)

        # Tên & mô tả
        ns = _vn(24).render(card['name'], True, bright if hov else (240, 240, 240))
        screen.blit(ns, (cx + CARD_W//2 - ns.get_width()//2, card_y + 185))
        for di, line in enumerate(card['desc'].split('\n')):
            ds = _vn(19).render(line, True, (180, 180, 180))
            screen.blit(ds, (cx + CARD_W//2 - ds.get_width()//2, card_y + 228 + di*22))

        if hov:
            ps = _vn(19).render("► Click để chọn", True, bright)
            screen.blit(ps, (cx + CARD_W//2 - ps.get_width()//2, card_y + CARD_H - 28))

    return rects
