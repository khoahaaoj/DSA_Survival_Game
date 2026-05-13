# settings.py

# ==========================================
# THÔNG SỐ MÀN HÌNH & HIỆU NĂNG
# ==========================================
WIDTH = 1280       # Chiều rộng cửa sổ game
HEIGHT = 720       # Chiều cao cửa sổ game
FPS = 60           # Tốc độ khung hình (Frames Per Second)

# ==========================================
# THÔNG SỐ BẢN ĐỒ (WORLD SPACE)
# ==========================================
MAP_WIDTH = 10000   # Chiều rộng bản đồ thực tế
MAP_HEIGHT = 10000  # Chiều cao bản đồ thực tế
TILE_SIZE = 64     # Kích thước của 1 ô gạch (Tile cỏ)

# ==========================================
# BẢNG MÀU (RGB) - Dùng khi chưa có hình ảnh
# ==========================================
BG_COLOR = (30, 30, 30)         # Xám đen (Nền ngoài map)
GRASS_FALLBACK_COLOR = (34, 139, 34) # Màu xanh lá (Nếu không có hình cỏ)
PLAYER_FALLBACK_COLOR = (0, 255, 128) # Màu xanh neon (Nếu không có hình NV)