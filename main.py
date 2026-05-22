"""
DSA Survival Game — Vòng lặp chính (Game Engine Pipeline).

Kiến trúc phân lớp sau tái cấu trúc:
  algorithms/
    quadtree.py     — Spatial Partitioning O(log N)
    min_heap.py     — Priority Queue O(log N) cho Auto-Aim
    queue.py        — FIFO Queue O(1) cho Wave System  ← MỚI
  entities/
    player.py / enemy.py / weapon.py / item.py
  managers/
    wave_manager.py    — WaveManager: chuỗi wave qua Queue
    upgrade_manager.py — Build pool, apply upgrade, draw cards
    renderer.py        — HUD, Pause, Game Over, Wave Banner
  main.py (file này) — Chỉ chứa init + game loop core (~250 dòng)
"""
import os
import sys
import math
import random
import asyncio   # Pygbag yêu cầu để chạy game trên trình duyệt (WebAssembly)

import pygame

from settings         import WIDTH, HEIGHT, FPS, MAP_WIDTH, MAP_HEIGHT, TILE_SIZE, GRASS_FALLBACK_COLOR
from algorithms.quadtree  import QuadTree
from algorithms.min_heap  import MinHeap
from entities.player  import Player
from entities.item    import ExpGem

from managers.wave_manager    import WaveManager
from managers.upgrade_manager import build_upgrade_pool, apply_upgrade, draw_level_up_screen
from managers.renderer        import Renderer


# ---------------------------------------------------------------------------
# Bộ nạp tài nguyên Map (Asset Loader + Tile Variation Cache)
# ---------------------------------------------------------------------------
def load_grass_tiles() -> list:
    """
    Load grass texture, tạo 4 biến thể bằng flip matrix để đa dạng bản đồ.
    Tái sử dụng 1 texture gốc — tránh tốn bộ nhớ VRAM.
    """
    img_path = os.path.join("assets", "grass.png")
    if not os.path.exists(img_path):
        return []
    base = pygame.image.load(img_path).convert()
    base = pygame.transform.scale(base, (TILE_SIZE, TILE_SIZE))
    return [
        base,
        pygame.transform.flip(base, True,  False),
        pygame.transform.flip(base, False, True),
        pygame.transform.flip(base, True,  True),
    ]


def draw_map(screen: pygame.Surface, camera_x: float, camera_y: float,
             grass_tiles: list):
    """
    Kết xuất bản đồ với Viewport Culling — chỉ vẽ tiles nằm trong màn hình.
    Hash (col*31 + row*17) % N để gán tile biến thể cố định mỗi vị trí.
    """
    sc = int(camera_x // TILE_SIZE)
    sr = int(camera_y // TILE_SIZE)
    for row in range(sr, sr + HEIGHT // TILE_SIZE + 2):
        for col in range(sc, sc + WIDTH // TILE_SIZE + 2):
            tx, ty = col * TILE_SIZE, row * TILE_SIZE
            if tx < MAP_WIDTH and ty < MAP_HEIGHT:
                dx, dy = tx - camera_x, ty - camera_y
                if grass_tiles:
                    screen.blit(grass_tiles[(col * 31 + row * 17) % len(grass_tiles)], (dx, dy))
                else:
                    pygame.draw.rect(screen, GRASS_FALLBACK_COLOR,
                                     (dx, dy, TILE_SIZE, TILE_SIZE))


# ---------------------------------------------------------------------------
async def main():
    """
    Vòng đời chính của Game Engine.

    Thứ tự xử lý mỗi frame:
        1. Input Phase    — thu thập sự kiện, xử lý Menu/Pause/LevelUp
        2. Update Phase   — WaveManager, Physics, QuadTree, MinHeap, Collision
        3. Rendering Pass — World → Entities → HUD → Overlays (thứ tự Layer)
    """
    # ===== KHỞI TẠO ENGINE =====
    pygame.mixer.pre_init(44100, -16, 2, 512)
    pygame.init()
    pygame.mixer.init()

    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("DSA Survival - UIT")
    clock  = pygame.time.Clock()

    # --- Audio ---
    bgm_path  = os.path.join("assets", "bgm.mp3")
    has_music = os.path.exists(bgm_path)
    music_on  = True
    if has_music:
        pygame.mixer.music.load(bgm_path)
        pygame.mixer.music.set_volume(0.1)
        pygame.mixer.music.play(-1)

    sfx_on  = True
    sfx_hit = pygame.mixer.Sound("assets/hit.wav") if os.path.exists("assets/hit.wav") else None
    sfx_gem = pygame.mixer.Sound("assets/gem.wav") if os.path.exists("assets/gem.wav") else None
    if sfx_hit: sfx_hit.set_volume(0.2)
    if sfx_gem: sfx_gem.set_volume(0.4)

    # --- Fonts ---
    font_large  = pygame.font.SysFont(None, 80)
    font_medium = pygame.font.SysFont(None, 48)
    font_small  = pygame.font.SysFont("Arial", 28, bold=True)
    font_dmg    = pygame.font.SysFont(None, 24)
    fonts_tuple = (font_large, font_medium, font_small, font_dmg)

    # --- Managers ---
    renderer = Renderer(fonts_tuple)

    # --- Assets ---
    grass_tiles = load_grass_tiles()

    # --- pygame Event ID cho Spawn ---
    SPAWN_EVENT = pygame.USEREVENT + 1

    # ===== HÀM RESET (Khởi tạo / Chơi lại) =====
    def make_state():
        """Tạo dict trạng thái game mới (dùng cho lần đầu và restart)."""
        wm = WaveManager(SPAWN_EVENT)   # Nạp Queue wave, bắt đầu Wave 1
        return {
            'player'          : Player(MAP_WIDTH // 2, MAP_HEIGHT // 2),
            'enemies'         : [],
            'gems'            : [],
            'floating_texts'  : [],
            'particles'       : [],   # Death particles
            'target_heap'     : MinHeap(),
            'wave_manager'    : wm,
            'kill_count'      : 0,
            'start_ticks'     : pygame.time.get_ticks(),
            'paused_duration' : 0,
            'last_pause_start': 0,
            'timer_text'      : "00:00",
            'camera_x'        : 0.0,
            'camera_y'        : 0.0,
            # Visual FX
            'screen_shake'     : 0,   # Frame countdown cho screen shake
            'wave_banner_timer': 0,   # Frame countdown cho wave announcement
            # UI state
            'is_paused'        : False,
            'game_over'        : False,
            'show_quadtree'    : False,
            'showing_level_up' : False,
            'level_up_choices' : [],
            'level_up_rects'   : [],
        }

    s = make_state()   # s = game state dict

    # ===== VÒNG LẶP CHÍNH =====
    running = True
    while running:
        current_time = pygame.time.get_ticks()

        # Cập nhật timer (không chạy khi pause/game_over/level_up)
        if not s['is_paused'] and not s['game_over'] and not s['showing_level_up']:
            total_s = (current_time - s['start_ticks'] - s['paused_duration']) // 1000
            s['timer_text'] = f"{total_s // 60:02d}:{total_s % 60:02d}"

        # =================================================================
        # BƯỚC 1: INPUT PHASE
        # =================================================================
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            # --- Keyboard ---
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q:
                    s['show_quadtree'] = not s['show_quadtree']

                if event.key in (pygame.K_ESCAPE, pygame.K_p):
                    if not s['game_over'] and not s['showing_level_up']:
                        s['is_paused'] = not s['is_paused']
                        if s['is_paused']:
                            s['last_pause_start'] = current_time
                        else:
                            s['paused_duration'] += current_time - s['last_pause_start']

                if event.key == pygame.K_r and s['game_over']:
                    s = make_state()   # Restart: tạo state mới hoàn toàn

            # --- Mouse ---
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mp = event.pos

                # Level-Up screen (ưu tiên cao nhất)
                if s['showing_level_up'] and s['level_up_rects']:
                    for idx, rect in enumerate(s['level_up_rects']):
                        if rect.collidepoint(mp) and idx < len(s['level_up_choices']):
                            apply_upgrade(s['level_up_choices'][idx]['id'], s['player'])
                            s['player'].level_up_pending = False
                            s['showing_level_up']  = False
                            s['level_up_choices']  = []
                            s['level_up_rects']    = []
                            s['paused_duration']  += current_time - s['last_pause_start']
                            break

                elif not s['game_over']:
                    if not s['is_paused']:
                        if renderer.pause_btn_rect.collidepoint(mp):
                            s['is_paused']         = True
                            s['last_pause_start']  = current_time
                    else:
                        if renderer.resume_btn_rect.collidepoint(mp):
                            s['is_paused']          = False
                            s['paused_duration']   += current_time - s['last_pause_start']
                        elif renderer.toggle_music_btn_rect.collidepoint(mp) and has_music:
                            music_on = not music_on
                            pygame.mixer.music.unpause() if music_on else pygame.mixer.music.pause()
                        elif renderer.toggle_sfx_btn_rect.collidepoint(mp):
                            sfx_on = not sfx_on

                elif s['game_over']:
                    if renderer.restart_btn_rect.collidepoint(mp):
                        s = make_state()

            # --- Wave Spawn Event ---
            if (event.type == SPAWN_EVENT and not s['game_over']
                    and not s['is_paused'] and not s['showing_level_up']):
                new_enemy = s['wave_manager'].try_spawn(s['enemies'], s['player'])
                if new_enemy:
                    s['enemies'].append(new_enemy)

        # =================================================================
        # BƯỚC 2: UPDATE PHASE (Physics + DSA)
        # =================================================================
        if not s['game_over'] and not s['is_paused'] and not s['showing_level_up']:
            p   = s['player']
            wm  = s['wave_manager']

            # 2.0 WaveManager update — theo dõi chuyển tiếp wave để hiện banner
            _prev_wave = wm.wave_number
            _was_break = wm.is_break
            wm.update(current_time)
            if _was_break and not wm.is_break:   # Vừa kết thúc nghỉ → wave mới bắt đầu
                s['wave_banner_timer'] = 150      # 2.5 giây ở 60FPS

            # 2.1 Player movement
            p.move(pygame.key.get_pressed(), MAP_WIDTH, MAP_HEIGHT)

            # 2.2 Xây dựng QuadTree (Spatial Partitioning)
            quadtree = QuadTree(pygame.Rect(0, 0, MAP_WIDTH, MAP_HEIGHT), 4)
            for e in s['enemies']:
                quadtree.insert(e)

            # 2.3 Xây dựng MinHeap (Priority Queue cho Auto-Aim)
            s['target_heap'].clear()
            for e in s['enemies']:
                dist = e.update_movement(p.x, p.y, quadtree)
                s['target_heap'].push((dist, e))

            # 2.4 Cập nhật vũ khí + va chạm đạn
            dmg_events = p.update_weapons(quadtree, s['target_heap'], current_time)
            if dmg_events:
                if sfx_hit and sfx_on: sfx_hit.play()
                for ev in dmg_events:
                    s['floating_texts'].append({
                        'x': ev['x'], 'y': ev['y'] - 20,
                        'text': str(ev['damage']), 'life': 30, 'color': (255, 255, 255)
                    })

            # 2.5 Dọn quái chết → rớt EXP gem + spawn death particles
            new_enemies = []
            for e in s['enemies']:
                if e.hp > 0:
                    new_enemies.append(e)
                else:
                    s['gems'].append(ExpGem(e.x, e.y))
                    s['kill_count'] += 1
                    # Spawn 6 death particles mang màu của quái
                    ec = getattr(e, 'color', (220, 80, 40))
                    for _ in range(6):
                        s['particles'].append({
                            'x': e.x, 'y': e.y,
                            'vx': random.uniform(-3.5, 3.5),
                            'vy': random.uniform(-5.0, -1.0),
                            'life': random.randint(18, 30),
                            'max_life': 30,
                            'color': ec,
                            'size': random.randint(3, 7),
                        })
            s['enemies'] = new_enemies

            # 2.6 Nhặt EXP gem
            new_gems = []
            for g in s['gems']:
                if math.sqrt((p.x - g.x)**2 + (p.y - g.y)**2) < 50:
                    p.gain_exp(g.value)
                    if sfx_gem and sfx_on: sfx_gem.play()
                    s['floating_texts'].append({
                        'x': p.x, 'y': p.y - 40,
                        'text': f"+{g.value}", 'life': 40, 'color': (0, 255, 255)
                    })
                else:
                    new_gems.append(g)
            s['gems'] = new_gems

            # 2.6b Kích hoạt Level-Up screen
            if p.level_up_pending and not s['showing_level_up']:
                pool = build_upgrade_pool(p)
                s['level_up_choices']  = random.sample(pool, min(3, len(pool)))
                s['showing_level_up']  = True
                s['last_pause_start']  = current_time

            # 2.7 Va chạm player với quái
            p_rect = pygame.Rect(p.x - 16, p.y - 16, 32, 32)
            for e in quadtree.query(p_rect, []):
                if p_rect.colliderect(pygame.Rect(e.x - 16, e.y - 16, 32, 32)):
                    if current_time - e.last_attack_time > 500:
                        p.hp -= e.damage
                        p.damage_flash     = 12
                        s['screen_shake']  = 8   # Screen shake 8 frame
                        e.last_attack_time = current_time
                        s['floating_texts'].append({
                            'x': p.x + random.randint(-15, 15),
                            'y': p.y - 30 + random.randint(-15, 15),
                            'text': f"-{e.damage}", 'life': 45, 'color': (255, 50, 50)
                        })
                        if sfx_hit and sfx_on: sfx_hit.play()
                        if p.hp <= 0: s['game_over'] = True

            # 2.8 Camera (clamp trong bản đồ)
            s['camera_x'] = max(0, min(MAP_WIDTH  - WIDTH,  p.x - WIDTH  // 2))
            s['camera_y'] = max(0, min(MAP_HEIGHT - HEIGHT, p.y - HEIGHT // 2))

        # =================================================================
        # BƯỚC 3: RENDERING PASS
        # =================================================================
        # Screen shake: lệch camera ngẫu nhiên khi bị đánh
        _shk = s['screen_shake']
        shake_x = random.randint(-5, 5) if _shk > 0 else 0
        shake_y = random.randint(-3, 3) if _shk > 0 else 0
        if _shk > 0: s['screen_shake'] -= 1
        cx = s['camera_x'] + shake_x
        cy = s['camera_y'] + shake_y
        screen.fill((15, 15, 15))

        # L0 – Map + gems
        draw_map(screen, cx, cy, grass_tiles)
        for g in s['gems']:
            g.draw(screen, cx, cy)

        # L1 – QuadTree debug
        if s['show_quadtree'] and not s['game_over']:
            quadtree.draw(screen, cx, cy)

        # L2–4 – Weapons / Enemies / Player
        s['player'].draw_weapons(screen, cx, cy)
        for e in s['enemies']:
            e.draw(screen, cx, cy)
        s['player'].draw(screen, cx, cy)

        # L5 – Death particles (O(N) rebuild, trước floating text để text đè lên)
        next_particles = []
        for pt in s['particles']:
            pt['life'] -= 1
            pt['x']    += pt['vx']
            pt['y']    += pt['vy']
            pt['vy']   += 0.25   # Trọng lực nhẹ
            if pt['life'] > 0:
                ratio = pt['life'] / pt['max_life']
                size  = max(1, int(pt['size'] * ratio))
                pygame.draw.circle(screen, pt['color'],
                                   (int(pt['x'] - cx), int(pt['y'] - cy)), size)
                next_particles.append(pt)
        s['particles'] = next_particles

        # L5.5 – Floating texts (O(N) rebuild)
        next_texts = []
        for ft in s['floating_texts']:
            ft['life'] -= 1
            ft['y']    -= 1.5
            if ft['life'] > 0:
                txt = font_dmg.render(ft['text'], True, ft['color'])
                out = font_dmg.render(ft['text'], True, (0, 0, 0))
                screen.blit(out, (ft['x'] - cx + 1, ft['y'] - cy + 1))
                screen.blit(txt, (ft['x'] - cx,     ft['y'] - cy))
                next_texts.append(ft)
        s['floating_texts'] = next_texts

        # L6 – HUD
        renderer.draw_hud(screen, s['player'], s['timer_text'],
                          s['kill_count'], s['wave_manager'])

        # L6.5 – Wave countdown banner (nghỉ giữa wave)
        renderer.draw_wave_banner(screen, s['wave_manager'])

        # L6.6 – Wave announcement ("WAVE X BẮT ĐẦU!" flash khi wave mới)
        if s['wave_banner_timer'] > 0:
            renderer.draw_wave_announcement(screen, s['wave_manager'].wave_number,
                                            s['wave_banner_timer'])
            s['wave_banner_timer'] -= 1

        # L7 – Pause button + Pause menu
        if not s['game_over']:
            renderer.draw_pause_btn(screen, pygame.mouse.get_pos())
        if s['is_paused'] and not s['game_over']:
            renderer.draw_pause(screen, pygame.mouse.get_pos(),
                                music_on, has_music, sfx_on)

        # L8 – Game Over screen
        if s['game_over']:
            renderer.draw_game_over(screen, s['player'],
                                    s['timer_text'], s['kill_count'],
                                    pygame.mouse.get_pos())

        # L9 – Level-Up screen (ưu tiên cao nhất)
        if s['showing_level_up'] and s['level_up_choices']:
            s['level_up_rects'] = draw_level_up_screen(
                screen, s['level_up_choices'], fonts_tuple,
                pygame.mouse.get_pos(), current_time
            )

        pygame.display.flip()
        clock.tick(FPS)
        await asyncio.sleep(0)   # Trả quyền kiểm soát cho trình duyệt mỗi frame

    pygame.quit()
    # sys.exit() không dùng trên web — dùng return thay thế
    return


asyncio.run(main())