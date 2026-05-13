"""
Module Core của hệ thống: Chứa Game Loop chính và các bộ điều khiển trung tâm.
Quản lý việc tích hợp cấu trúc dữ liệu (QuadTree, MinHeap), hệ thống kết xuất đồ họa (Rendering),
xử lý vật lý (Physics/Collision), và phân luồng âm thanh đa kênh (Multi-channel Audio).
"""
import pygame
import sys
import os
import random
import math

from settings import *
from entities.player import Player
from entities.enemy import Enemy
from entities.item import ExpGem
from algorithms.min_heap import MinHeap
from algorithms.quadtree import QuadTree
from entities.enemy import Zombie, Bat, Golem


def load_grass_tiles() -> list:
    """
    Tải bộ nhớ đệm (Cache) và tạo các biến thể không gian (Tile Variations).
    Thực hiện lật ảnh ngang/dọc để tái sử dụng tài nguyên bộ nhớ,
    giúp đa dạng hóa kết xuất bản đồ nền mà không cần thêm file đồ họa mới.

    Returns:
        list: Danh sách chứa các Surface của gạch cỏ (đã tối ưu hóa).
    """
    img_path = os.path.join("assets", "grass.png")
    variations = []
    if os.path.exists(img_path):
        base_img = pygame.image.load(img_path).convert()
        base_img = pygame.transform.scale(base_img, (TILE_SIZE, TILE_SIZE))
        variations.append(base_img)
        variations.append(pygame.transform.flip(base_img, True, False))
        variations.append(pygame.transform.flip(base_img, False, True))
        variations.append(pygame.transform.flip(base_img, True, True))
    return variations


def draw_map(screen: pygame.Surface, camera_x: float, camera_y: float, grass_tiles: list):
    """
    Kết xuất đồ họa bản đồ theo thuật toán Viewport Culling.
    Chỉ vẽ các phần của bản đồ nằm trong vùng nhìn thấy của Camera (Frustum Culling 2D),
    nhằm tiết kiệm tối đa chu kỳ xử lý của CPU.

    Args:
        screen (pygame.Surface): Bề mặt vẽ chính của trò chơi.
        camera_x (float): Hệ tọa độ toàn cục X của Camera.
        camera_y (float): Hệ tọa độ toàn cục Y của Camera.
        grass_tiles (list): Cache bộ nhớ chứa các biến thể ảnh cỏ.
    """
    start_col = int(camera_x // TILE_SIZE)
    start_row = int(camera_y // TILE_SIZE)
    cols = (WIDTH // TILE_SIZE) + 2
    rows = (HEIGHT // TILE_SIZE) + 2

    for row in range(start_row, start_row + rows):
        for col in range(start_col, start_col + cols):
            tile_x = col * TILE_SIZE
            tile_y = row * TILE_SIZE
            if tile_x < MAP_WIDTH and tile_y < MAP_HEIGHT:
                draw_x = tile_x - camera_x
                draw_y = tile_y - camera_y
                if grass_tiles:
                    tile_index = (col * 31 + row * 17) % len(grass_tiles)
                    screen.blit(grass_tiles[tile_index], (draw_x, draw_y))
                else:
                    pygame.draw.rect(screen, GRASS_FALLBACK_COLOR, (draw_x, draw_y, TILE_SIZE, TILE_SIZE))


def main():
    """
    Hàm thực thi vòng lặp chính của hệ thống (Main Game Engine Loop).

    Quy trình xử lý (Pipeline) của mỗi Frame (khung hình):
    1. Input Handling: Bắt sự kiện người dùng (Phím, Chuột, Menu).
    2. Physics & DSA Updates:
       - Cập nhật và chèn thực thể vào cây không gian QuadTree.
       - Tính toán khoảng cách và đẩy vào MinHeap để tối ưu ngắm bắn.
       - Giải quyết va chạm (Collision Resolution).
    3. Rendering: Xóa màn hình, tính toán Culling và vẽ lại toàn bộ State mới.
    """
    # =========================================================================
    # PHẦN 1: KHỞI TẠO HỆ THỐNG ENGINE (SETUP)
    # =========================================================================

    # Khởi tạo Mixer âm thanh trước tiên để tránh bị trễ tiếng (delay)
    pygame.mixer.pre_init(44100, -16, 2, 512)
    pygame.init()
    pygame.mixer.init()

    # Tạo cửa sổ game với kích thước định sẵn trong settings.py
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("DSA Survival - Đồ án lớp Tài năng")

    # Khởi tạo đồng hồ để kiểm soát FPS (Số khung hình trên giây)
    clock = pygame.time.Clock()

    # --- TẢI ÂM THANH & PHÂN LUỒNG ---
    # Luồng 1: Nhạc Nền (BGM - Chạy liên tục)
    bgm_path = os.path.join("assets", "bgm.mp3")
    has_music = os.path.exists(bgm_path)
    music_on = True  # Cờ trạng thái bật/tắt nhạc
    if has_music:
        pygame.mixer.music.load(bgm_path)
        pygame.mixer.music.set_volume(0.1)  # Để nhạc nhỏ thôi cho đỡ nhức đầu
        pygame.mixer.music.play(-1)  # -1 nghĩa là lặp lại vô tận

    # Luồng 2: Hiệu ứng âm thanh vật lý (SFX - Phát khi có sự kiện)
    sfx_on = True  # Cờ trạng thái bật/tắt hiệu ứng âm thanh
    sfx_hit = pygame.mixer.Sound("assets/hit.wav") if os.path.exists("assets/hit.wav") else None
    sfx_gem = pygame.mixer.Sound("assets/gem.wav") if os.path.exists("assets/gem.wav") else None
    if sfx_hit: sfx_hit.set_volume(0.2)
    if sfx_gem: sfx_gem.set_volume(0.4)

    # =========================================================================
    # PHẦN 2: KHỞI TẠO TRẠNG THÁI GAME (GAME STATE)
    # =========================================================================

    # Tải hình ảnh bản đồ cỏ
    grass_tiles = load_grass_tiles()

    # Đặt nhân vật (Player) xuất hiện ở chính giữa bản đồ lớn (MAP_WIDTH, MAP_HEIGHT)
    player = Player(MAP_WIDTH // 2, MAP_HEIGHT // 2)

    # Khởi tạo các mảng chứa thực thể trong game
    enemies = []  # Chứa quái vật
    gems = []  # Chứa ngọc kinh nghiệm rớt ra
    floating_texts = []  # Chứa các con số sát thương nảy lên

    # Khởi tạo Cấu trúc dữ liệu Min-Heap dùng để ưu tiên ngắm bắn mục tiêu gần nhất
    target_heap = MinHeap()

    # Cài đặt một bộ đếm giờ (Timer) để tự động sinh quái vật mỗi 350ms
    SPAWN_ENEMY_EVENT = pygame.USEREVENT + 1
    pygame.time.set_timer(SPAWN_ENEMY_EVENT, 350)

    # Các biến cờ (Flags) điều khiển luồng game
    show_quadtree = False  # Nhấn Q để hiện lưới QuadTree (Debug)
    is_paused = False  # Trạng thái tạm dừng
    game_over = False  # Trạng thái thua game

    # Các biến phục vụ tính toán thời gian và điểm số
    kill_count = 0
    start_ticks = pygame.time.get_ticks()  # Lưu thời điểm game bắt đầu
    paused_duration = 0  # Tổng thời gian game bị tạm dừng
    last_pause_start = 0  # Mốc thời gian bắt đầu nhấn Pause
    timer_text = "00:00"

    # =========================================================================
    # PHẦN 3: GIAO DIỆN NGƯỜI DÙNG (UI/HUD)
    # =========================================================================

    # Tải các font chữ với kích thước khác nhau
    font_large = pygame.font.SysFont(None, 80)
    font_medium = pygame.font.SysFont(None, 48)
    font_small = pygame.font.SysFont("Arial", 28, bold=True)
    font_dmg = pygame.font.SysFont(None, 24)

    # Khởi tạo các hộp tương tác (Rect) cho nút bấm Menu
    pause_btn_rect = pygame.Rect(WIDTH - 50, 45, 35, 35)  # Nút góc phải trên
    menu_rect = pygame.Rect(WIDTH // 2 - 150, HEIGHT // 2 - 150, 300, 300)  # Khung Menu Pause
    resume_btn_rect = pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2 - 60, 200, 50)
    toggle_music_btn_rect = pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2 + 10, 200, 50)
    toggle_sfx_btn_rect = pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2 + 80, 200, 50)

    # =========================================================================
    # PHẦN 4: VÒNG LẶP HỆ THỐNG CHÍNH (MAIN GAME LOOP)
    # Chạy liên tục 60 lần/giây (FPS = 60) cho đến khi người dùng tắt game
    # =========================================================================
    running = True
    while running:
        current_time = pygame.time.get_ticks()  # Lấy thời gian hiện tại của hệ thống

        # Tính toán thời gian sinh tồn (Giây) hiển thị lên màn hình
        # Lưu ý: Phải trừ đi khoảng thời gian game bị Pause để đồng hồ không chạy láo
        if not is_paused and not game_over:
            total_seconds = (current_time - start_ticks - paused_duration) // 1000
            minutes = total_seconds // 60
            seconds = total_seconds % 60
            timer_text = f"{minutes:02d}:{seconds:02d}"

        # ---------------------------------------------------------------------
        # BƯỚC 4.1: XỬ LÝ SỰ KIỆN (INPUT HANDLING)
        # Bắt các thao tác phím, chuột của người chơi
        # ---------------------------------------------------------------------
        for event in pygame.event.get():
            if event.type == pygame.QUIT: running = False  # Tắt cửa sổ

            # Xử lý khi nhấn phím trên bàn phím
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q:
                    show_quadtree = not show_quadtree  # Bật/tắt xem QuadTree
                if event.key == pygame.K_ESCAPE or event.key == pygame.K_p:
                    if not game_over:
                        is_paused = not is_paused  # Bật/tắt Pause
                        if is_paused:
                            last_pause_start = pygame.time.get_ticks()  # Bắt đầu đếm giờ Pause
                        else:
                            paused_duration += pygame.time.get_ticks() - last_pause_start  # Cộng dồn thời gian đã Pause

            # Xử lý khi click chuột vào các nút UI
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mouse_pos = event.pos
                if not game_over:
                    if not is_paused:  # Nếu đang chơi -> Bấm nút Pause nhỏ ở góc
                        if pause_btn_rect.collidepoint(mouse_pos):
                            is_paused = True
                            last_pause_start = pygame.time.get_ticks()
                    else:  # Nếu đang Pause -> Bấm các nút trong Menu
                        if resume_btn_rect.collidepoint(mouse_pos):
                            is_paused = False
                            paused_duration += pygame.time.get_ticks() - last_pause_start
                        elif toggle_music_btn_rect.collidepoint(mouse_pos) and has_music:
                            music_on = not music_on
                            if music_on:
                                pygame.mixer.music.unpause()
                            else:
                                pygame.mixer.music.pause()
                        elif toggle_sfx_btn_rect.collidepoint(mouse_pos):
                            sfx_on = not sfx_on

            # Sinh sản quái vật (Được kích hoạt mỗi 350ms bởi SPAWN_ENEMY_EVENT)
            if not game_over and not is_paused:
                if event.type == SPAWN_ENEMY_EVENT:
                    # Toán học lượng giác: Đẻ quái vật ở một điểm ngẫu nhiên cách người chơi 700 pixel (ngoài rìa màn hình)
                    angle = random.uniform(0, 2 * math.pi)
                    spawn_x = player.x + math.cos(angle) * 700
                    spawn_y = player.y + math.sin(angle) * 700

                    # Ràng buộc không cho đẻ quái ngoài giới hạn bản đồ
                    spawn_x = max(0, min(MAP_WIDTH, spawn_x))
                    spawn_y = max(0, min(MAP_HEIGHT, spawn_y))

                    # THUẬT TOÁN: Phân phối xác suất ngẫu nhiên (Weighted Random)
                    # Quái xịn (Golem) tỷ lệ xuất hiện thấp, quái cùi (Zombie) tỷ lệ cao
                    enemy_classes = [Zombie, Bat, Golem]
                    chosen_enemy_class = random.choices(enemy_classes, weights=[60, 30, 10], k=1)[0]
                    enemies.append(chosen_enemy_class(spawn_x, spawn_y, player.level))

        # ---------------------------------------------------------------------
        # BƯỚC 4.2: CẬP NHẬT TRẠNG THÁI VÀ THUẬT TOÁN (PHYSICS & DSA UPDATES)
        # Cập nhật vị trí, va chạm, sát thương (Chỉ chạy khi game không bị Pause)
        # ---------------------------------------------------------------------
        if not game_over and not is_paused:
            # 1. Nhận input di chuyển của người chơi (W A S D)
            player.move(pygame.key.get_pressed(), MAP_WIDTH, MAP_HEIGHT)

            # 2. XÂY DỰNG QUADTREE (O(N log N))
            # Mỗi khung hình, xóa QuadTree cũ và xây lại cái mới chứa vị trí hiện tại của quái
            map_boundary = pygame.Rect(0, 0, MAP_WIDTH, MAP_HEIGHT)
            quadtree = QuadTree(map_boundary, 4)
            for enemy in enemies:
                quadtree.insert(enemy)

            # 3. AI DI CHUYỂN VÀ XÂY DỰNG MIN-HEAP (O(N log N))
            target_heap.clear()
            for enemy in enemies:
                # Quái vật gọi QuadTree để thực hiện Separation (tránh dẫm lên nhau) và tiến về phía người chơi
                dist = enemy.update_movement(player.x, player.y, quadtree)
                # Đẩy khoảng cách vào Min-Heap để súng có thể pop() ra mục tiêu gần nhất
                target_heap.push((dist, enemy))

            # 4. VŨ KHÍ TẤN CÔNG (Collision Detection)
            # Truyền QuadTree vào vũ khí để tính toán va chạm cực nhanh
            dmg_events = player.update_weapons(quadtree, target_heap, current_time)
            if dmg_events:
                if sfx_hit and sfx_on: sfx_hit.play()  # Phát âm thanh xẹt xẹt
                for ev in dmg_events:
                    # Tạo hiệu ứng số sát thương nảy lên (Floating Text)
                    floating_texts.append({'x': ev['x'], 'y': ev['y'] - 20, 'text': str(ev['damage']), 'life': 30,
                                           'color': (255, 255, 255)})

            # 5. DỌN DẸP XÁC QUÁI VẬT VÀ ĐẺ NGỌC
            new_enemies = []
            for e in enemies:
                if e.hp > 0:
                    new_enemies.append(e)  # Quái còn sống thì giữ lại
                else:
                    gems.append(ExpGem(e.x, e.y))  # Quái chết rớt ngọc
                    kill_count += 1
            enemies = new_enemies  # Cập nhật mảng quái vật mới

            # 6. THU THẬP NGỌC KINH NGHIỆM
            new_gems = []
            for g in gems:
                # Dùng định lý Pythagoras tính khoảng cách từ người chơi tới viên ngọc
                if math.sqrt((player.x - g.x) ** 2 + (player.y - g.y) ** 2) < 50:
                    player.gain_exp(g.value)  # Nhận EXP, có thể dẫn đến Level Up
                    if sfx_gem and sfx_on: sfx_gem.play()
                    floating_texts.append(
                        {'x': player.x, 'y': player.y - 40, 'text': f"+{g.value}", 'life': 40, 'color': (0, 255, 255)})
                else:
                    new_gems.append(g)
            gems = new_gems

            # 7. QUÁI VẬT CẮN NGƯỜI CHƠI
            player_rect = pygame.Rect(player.x - 16, player.y - 16, 32, 32)
            # Lại dùng QuadTree để tìm nhanh xem có con quái nào đang đứng quanh nhân vật không
            nearby = quadtree.query(player_rect, [])
            for e in nearby:
                if player_rect.colliderect(pygame.Rect(e.x - 16, e.y - 16, 32, 32)):
                    # Cooldown đánh của quái: 0.5s (500ms) mới cắn được 1 phát tiếp theo
                    if current_time - e.last_attack_time > 500:
                        player.hp -= e.damage
                        e.last_attack_time = current_time

                        # Văng số máu bị trừ màu đỏ
                        offset_x = random.randint(-15, 15)
                        offset_y = random.randint(-15, 15)
                        floating_texts.append(
                            {'x': player.x + offset_x, 'y': player.y - 30 + offset_y, 'text': f"-{e.damage}",
                             'life': 45, 'color': (255, 50, 50)})

                        if sfx_hit and sfx_on: sfx_hit.play()
                        if player.hp <= 0: game_over = True  # Hết máu thì Game Over

            # 8. CẬP NHẬT TỌA ĐỘ CAMERA
            # Giữ người chơi luôn ở giữa màn hình, và không cho Camera trượt ra khỏi biên bản đồ
            camera_x = max(0, min(MAP_WIDTH - WIDTH, player.x - WIDTH // 2))
            camera_y = max(0, min(MAP_HEIGHT - HEIGHT, player.y - HEIGHT // 2))

        # ---------------------------------------------------------------------
        # BƯỚC 4.3: KẾT XUẤT ĐỒ HỌA (RENDERING PASS)
        # Vẽ tất cả mọi thứ lên màn hình (Theo thứ tự từ dưới lên trên)
        # ---------------------------------------------------------------------

        # Xóa màn hình cũ
        screen.fill((15, 15, 15))

        # Layer 1: Vẽ bản đồ nền
        draw_map(screen, camera_x, camera_y, grass_tiles)

        # Layer 2: Vẽ ngọc kinh nghiệm rơi trên đất
        for g in gems: g.draw(screen, camera_x, camera_y)

        # Layer 3 (Tùy chọn): Vẽ lưới QuadTree để báo cáo Demo
        if show_quadtree: quadtree.draw(screen, camera_x, camera_y)

        # Layer 4: Vẽ hiệu ứng vũ khí (Đạn, Sét, Vòng hào quang)
        player.draw_weapons(screen, camera_x, camera_y)

        # Layer 5: Vẽ quái vật
        for e in enemies: e.draw(screen, camera_x, camera_y)

        # Layer 6: Vẽ nhân vật người chơi đè lên trên cùng
        player.draw(screen, camera_x, camera_y)

        # Layer 7: Vẽ các hiệu ứng số sát thương nổi lên
        for ft in floating_texts[:]:
            ft['life'] -= 1  # Giảm vòng đời của số
            ft['y'] -= 1.5  # Cho chữ bay lên từ từ
            if ft['life'] <= 0:
                floating_texts.remove(ft)
            else:
                txt = font_dmg.render(ft['text'], True, ft['color'])
                outline = font_dmg.render(ft['text'], True, (0, 0, 0))  # Vẽ viền đen cho dễ đọc
                screen.blit(outline, (ft['x'] - camera_x + 1, ft['y'] - camera_y + 1))
                screen.blit(txt, (ft['x'] - camera_x, ft['y'] - camera_y))

        # Layer 8: HUD (Heads-Up Display) - Vẽ thanh EXP và đồng hồ cố định trên màn hình
        pygame.draw.rect(screen, (20, 20, 20), (5, 5, WIDTH - 10, 25))  # Nền thanh EXP
        exp_w = (WIDTH - 10) * (player.exp / player.max_exp)  # Tính độ dài % EXP
        pygame.draw.rect(screen, (0, 120, 255), (5, 5, exp_w, 25))  # Thanh EXP màu xanh
        pygame.draw.rect(screen, (200, 180, 50), (5, 5, WIDTH - 10, 25), 2)  # Viền vàng

        lvl_txt = font_small.render(f"LV {player.level}", True, (255, 255, 255))
        screen.blit(lvl_txt, (WIDTH - 85, 5))

        time_surf = font_medium.render(timer_text, True, (255, 255, 255))
        time_outline = font_medium.render(timer_text, True, (0, 0, 0))
        screen.blit(time_outline, (WIDTH // 2 - time_surf.get_width() // 2 + 2, 42))
        screen.blit(time_surf, (WIDTH // 2 - time_surf.get_width() // 2, 40))

        kill_txt = font_small.render(f"{kill_count} 💀", True, (255, 255, 255))
        screen.blit(kill_txt, (WIDTH - 120, 45))

        # Layer 9: Nút Pause nhỏ góc phải trên
        if not game_over:
            btn_color = (180, 180, 180) if pause_btn_rect.collidepoint(pygame.mouse.get_pos()) else (100, 100, 100)
            pygame.draw.rect(screen, btn_color, pause_btn_rect, border_radius=5)
            # Vẽ 2 vạch trắng đại diện cho icon Pause
            pygame.draw.rect(screen, (255, 255, 255), (pause_btn_rect.x + 10, pause_btn_rect.y + 8, 5, 18))
            pygame.draw.rect(screen, (255, 255, 255), (pause_btn_rect.x + 20, pause_btn_rect.y + 8, 5, 18))

        # Layer 10: Vẽ Overlay Menu khi bị Pause
        if is_paused and not game_over:
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 180))  # Phủ lớp đen mờ lên toàn game
            screen.blit(overlay, (0, 0))

            pygame.draw.rect(screen, (40, 40, 40), menu_rect, border_radius=10)
            pygame.draw.rect(screen, (200, 200, 200), menu_rect, 2, border_radius=10)

            title_text = font_medium.render("PAUSED", True, (255, 255, 255))
            screen.blit(title_text, (WIDTH // 2 - title_text.get_width() // 2, menu_rect.y + 20))

            mouse_pos = pygame.mouse.get_pos()

            # Nút Resume
            res_color = (100, 200, 100) if resume_btn_rect.collidepoint(mouse_pos) else (50, 150, 50)
            pygame.draw.rect(screen, res_color, resume_btn_rect, border_radius=5)
            res_txt = font_small.render("Resume", True, (255, 255, 255))
            screen.blit(res_txt, (resume_btn_rect.x + resume_btn_rect.width // 2 - res_txt.get_width() // 2,
                                  resume_btn_rect.y + 10))

            # Nút Music
            mus_color = (100, 100, 200) if toggle_music_btn_rect.collidepoint(mouse_pos) else (50, 50, 150)
            pygame.draw.rect(screen, mus_color, toggle_music_btn_rect, border_radius=5)
            mus_str = "Music: ON" if music_on else "Music: OFF"
            if not has_music: mus_str = "No bgm.mp3"
            mus_txt = font_small.render(mus_str, True, (255, 255, 255))
            screen.blit(mus_txt, (toggle_music_btn_rect.x + toggle_music_btn_rect.width // 2 - mus_txt.get_width() // 2,
                                  toggle_music_btn_rect.y + 10))

            # Nút SFX
            sfx_color = (200, 150, 50) if toggle_sfx_btn_rect.collidepoint(mouse_pos) else (150, 100, 30)
            pygame.draw.rect(screen, sfx_color, toggle_sfx_btn_rect, border_radius=5)
            sfx_str = "Sound: ON" if sfx_on else "Sound: OFF"
            sfx_txt = font_small.render(sfx_str, True, (255, 255, 255))
            screen.blit(sfx_txt, (toggle_sfx_btn_rect.x + toggle_sfx_btn_rect.width // 2 - sfx_txt.get_width() // 2,
                                  toggle_sfx_btn_rect.y + 10))

        # Layer 11: Màn hình Game Over
        if game_over:
            txt = font_large.render("GAME OVER", True, (255, 0, 0))
            screen.blit(txt, (WIDTH // 2 - txt.get_width() // 2, HEIGHT // 2 - 40))

        # Cập nhật toàn bộ màn hình và chốt khung hình (60 FPS)
        pygame.display.flip()
        clock.tick(FPS)

    # Thoát game an toàn
    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()