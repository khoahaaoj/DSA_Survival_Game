# ⚔️ DSA Survival: Top-Down Time Survival Game

<p align="center">
  <a href="https://github.com/khoahaaoj/DSA_Survival_Game/actions/workflows/build.yml">
    <img src="https://img.shields.io/github/actions/workflow/status/khoahaaoj/DSA_Survival_Game/build.yml?branch=main&label=Build%20EXE&logo=github&style=for-the-badge" alt="Build Status" />
  </a>
  <a href="https://github.com/khoahaaoj/DSA_Survival_Game/releases">
    <img src="https://img.shields.io/github/v/release/khoahaaoj/DSA_Survival_Game?color=brightgreen&label=Release&logo=github&style=for-the-badge" alt="Latest Version" />
  </a>
  <a href="https://github.com/khoahaaoj/DSA_Survival_Game/releases">
    <img src="https://img.shields.io/github/downloads/khoahaaoj/DSA_Survival_Game/total?color=0078D6&label=Downloads&logo=windows&style=for-the-badge" alt="Downloads" />
  </a>
</p>
<p align="center">
  <img src="https://img.shields.io/badge/Python-3.12-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python" />
  <img src="https://img.shields.io/badge/Pygame-2.6-FFD43B?style=for-the-badge&logo=python&logoColor=black" alt="Pygame" />
  <img src="https://img.shields.io/badge/University-UIT%20VNU--HCM-E53935?style=for-the-badge&logo=googleclassroom&logoColor=white" alt="UIT" />
  <img src="https://img.shields.io/badge/Platform-Windows%20%7C%20Linux%20%7C%20Web-4CAF50?style=for-the-badge" alt="Platform" />
  <img src="https://img.shields.io/badge/License-MIT-9C27B0?style=for-the-badge" alt="License" />
</p>


Một tựa game sinh tồn 2D nhịp độ cao (phong cách *Vampire Survivors*) được phát triển trên nền tảng **Python / Pygame**. Dự án áp dụng chuyên sâu các **Cấu trúc dữ liệu và Giải thuật (DSA)** tự cài đặt từ đầu nhằm giải quyết bài toán tối ưu hóa hiệu năng thời gian thực, duy trì ổn định **60 FPS** khi kết xuất và tính toán va chạm cho hàng trăm quái vật trên màn hình.

---

## 📸 Ảnh minh họa (Screenshots)

### 1. Chiến đấu nhịp độ cao & Trí tuệ bầy đàn (Boids AI)
<img width="1284" height="737" alt="Gameplay combat" src="https://github.com/user-attachments/assets/1400efbb-6b1c-4dd5-af27-efa102aada8b" />

> *Hệ thống tự động phân tán quái vật bao vây người chơi kết hợp với Particle System hiển thị sát thương.*

### 2. Tối ưu không gian bằng Cây tứ phân (QuadTree)
<img width="1284" height="737" alt="Quadtree debug" src="https://github.com/user-attachments/assets/9c4bafa3-79fc-40b7-8f4a-92c4d0275c01" />

> *Chế độ Debug trực quan hóa thuật toán phân bào không gian đệ quy (nhấn phím `Q`). Khu vực tập trung đông quái được chẻ nhỏ để giảm không gian tìm kiếm va chạm.*

### 3. Giao diện điều khiển & Phân luồng âm thanh
<img width="1280" height="752" alt="Pause menu" src="https://github.com/user-attachments/assets/6ef79cff-bcc9-4968-b376-2992d8734887" />

> *Pause Menu với kỹ thuật Alpha Blending, cho phép can thiệp trực tiếp vào 2 luồng âm thanh BGM và SFX độc lập.*

---

## 🎮 Cách chơi & Bảng phím điều khiển (Controls)

| Phím bấm | Hành động | Chi tiết |
| :--- | :--- | :--- |
| `W`, `A`, `S`, `D` hoặc `↑`, `↓`, `←`, `→` | **Di chuyển** | Điều hướng nhân vật né tránh quái vật trong bản đồ 10,000 × 10,000 px |
| *(Tự động)* | **Tấn công** | Hệ thống Auto-aim tự ngắm và bắn quái vật gần nhất thông qua Min-Heap |
| `Q` | **Bật/Tắt Debug QuadTree** | Hiển thị các ô phân vùng không gian của QuadTree theo thời gian thực |
| `ESC` hoặc `P` | **Tạm dừng (Pause)** | Mở Pause Menu, tùy chỉnh âm lượng Nhạc nền (BGM) và Âm thanh hiệu ứng (SFX) |
| `R` | **Chơi lại (Restart)** | Tái khởi động ván chơi mới khi bị Game Over |
| `Chuột trái (LMB)` | **Tương tác UI** | Chọn thẻ nâng cấp khi thăng cấp (Level Up) hoặc bấm các nút Menu |

### Mục tiêu trò chơi
1. **Né tránh vòng vây:** Kẻ địch ngày càng đông theo từng đợt (Wave) và có AI luồn lách thông minh.
2. **Thu thập tinh thể (EXP Gem):** Tiêu diệt quái vật để nhặt đá kinh nghiệm màu xanh.
3. **Thăng cấp & Nâng cấp:** Mỗi khi lên cấp, chọn 1 trong 3 thẻ bài nâng cấp vũ khí (Súng tỉa, Thánh quang, Bão sét) hoặc tăng chỉ số (Hồi máu, Tăng tốc, Tăng dame).
4. **Sinh tồn:** Vượt qua 5 Wave thử thách để tiến vào **Endless Mode** với độ khó tăng vô hạn!

---

## 🧠 Cấu trúc Dữ liệu & Giải thuật Cốt lõi (DSA Highlights)

Dự án tự cài đặt các cấu trúc dữ liệu kinh điển từ đầu (không dùng thư viện ngoài) để giải quyết trực tiếp bài toán hiệu năng:

| Cấu trúc dữ liệu / Giải thuật | File nguồn | Độ phức tạp | Vai trò thực tiễn trong Game |
| :--- | :--- | :---: | :--- |
| **Cây tứ phân (QuadTree)** | [`algorithms/quadtree.py`](file:///home/khoaha/PyCharmMiscProject/DSA_Survival_Game/algorithms/quadtree.py) | $O(N \log N)$ | Phân vùng không gian 2D, giảm chi phí kiểm tra va chạm đạn và thực thể từ $O(N^2)$ xuống $O(N \log N)$. |
| **Đống nhỏ (Min-Heap)** | [`algorithms/min_heap.py`](file:///home/khoaha/PyCharmMiscProject/DSA_Survival_Game/algorithms/min_heap.py) | $O(\log N)$ push<br>$O(1)$ peek min | Hàng đợi ưu tiên quản lý khoảng cách mục tiêu, giúp vũ khí ngắm bắn mục tiêu gần nhất tức thì. |
| **Hàng đợi (Queue FIFO)** | [`algorithms/queue.py`](file:///home/khoaha/PyCharmMiscProject/DSA_Survival_Game/algorithms/queue.py) | $O(1)$ amortized | Quản lý vòng đời chuỗi Wave (đợt tấn công & thời gian nghỉ giữa các wave) theo thứ tự First-In-First-Out. |
| **Lấy mẫu có trọng số (Roulette Selection)** | [`managers/wave_manager.py`](file:///home/khoaha/PyCharmMiscProject/DSA_Survival_Game/managers/wave_manager.py) | $O(\log K)$ | Ứng dụng **Mảng cộng dồn (Prefix Sum)** + **Tìm kiếm nhị phân (Binary Search)** để chọn ngẫu nhiên loại quái sinh ra theo tỉ lệ trọng số. |
| **Hành vi Bầy đàn (Boids Separation)** | [`entities/enemy.py`](file:///home/khoaha/PyCharmMiscProject/DSA_Survival_Game/entities/enemy.py) | $O(\log N)$ / quái | Kết hợp QuadTree để phát hiện các quái vật lân cận và tạo vector lực đẩy ngược chiều, tránh quái chồng đè lên nhau. |
| **Loại bỏ ngoài tầm nhìn (Viewport Culling)** | [`main.py`](file:///home/khoaha/PyCharmMiscProject/DSA_Survival_Game/main.py) | $O(1)$ / tile | Chỉ nạp và render các tile bản đồ nằm trong khung nhìn camera, tiết kiệm tài nguyên bộ nhớ và GPU/VRAM. |

> 📖 **Xem giải thích chi tiết có sơ đồ và mã nguồn tại:** [`ALGORITHMS.md`](file:///home/khoaha/PyCharmMiscProject/DSA_Survival_Game/ALGORITHMS.md)

---

## ⚙️ Hướng dẫn Cài đặt & Chạy Game

Bạn có thể chơi game theo 1 trong các cách dưới đây:

### Cách 1: Tải bản đóng gói sẵn cho Windows (Không cần cài Python)
1. Vào mục [Releases](https://github.com/khoahaaoj/DSA_Survival_Game/releases) của repository.
2. Tải file nén `DSA-Survival-Game-Windows.zip`.
3. Giải nén thư mục và mở file `DSA_Survival_Game.exe` để chơi ngay!

---

### Cách 2: Khởi động 1-Click bằng Script (Khuyên dùng khi clone mã nguồn)
Dự án đã tích hợp sẵn script tự động phát hiện Python, khởi tạo môi trường ảo (Virtual Environment), tự động cài đặt thư viện thiếu và khởi động game:

- **Trên Windows:** Click đúp vào file `run.bat`
- **Trên Linux / macOS:** Chạy file shell:
  ```bash
  chmod +x run.sh
  ./run.sh
  ```

---

### Cách 3: Chạy thủ công từ dòng lệnh (Manual Setup)

**Yêu cầu hệ thống:** Máy tính đã cài đặt Python 3.10 trở lên.

1. **Clone repository về máy:**
   ```bash
   git clone https://github.com/khoahaaoj/DSA_Survival_Game.git
   cd DSA_Survival_Game
   ```

2. **Khởi tạo và kích hoạt môi trường ảo (Khuyên dùng):**
   - **Windows:**
     ```cmd
     python -m venv venv
     venv\Scripts\activate
     ```
   - **Linux / macOS:**
     ```bash
     python3 -m venv venv
     source venv/bin/activate
     ```

3. **Cài đặt thư viện phụ thuộc:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Khởi chạy trò chơi:**
   ```bash
   python main.py
   ```

---

## 📦 Hướng dẫn Đóng gói Game (Build Executable)

### 1. Đóng gói thành file `.exe` cho Windows (PyInstaller)
Bạn có thể tự đóng gói game thành ứng dụng Windows độc lập:

- **Cách nhanh (Windows):** Click đúp vào file `build_exe.bat`.
- **Cách thủ công bằng lệnh:**
  ```bash
  pip install -r requirements-dev.txt
  python -m PyInstaller --noconfirm --onedir --windowed \
      --name "DSA_Survival_Game" \
      --add-data "assets:assets" \
      --add-data "settings.py:." \
      --hidden-import pygame \
      --collect-all pygame \
      main.py
  ```
  *(Trên Windows Command Prompt, thay dấu `\` thành `^` và dấu `:` thành `;`)*

Thư mục game thành phẩm sẽ xuất hiện tại `dist/DSA_Survival_Game/`.

### 2. Trải nghiệm trên Trình duyệt Web (Pygbag / WebAssembly)
Dự án hỗ trợ chạy trên nền Web thông qua Pygbag:
```bash
pip install pygbag
pygbag main-pygbag.py
```
Sau đó truy cập địa chỉ `http://localhost:8000` trên trình duyệt web để chơi trực tiếp.

---

## 📂 Cấu trúc Thư mục Dự án

```text
DSA_Survival_Game/
├── algorithms/                 # Các Cấu trúc dữ liệu và Giải thuật tự cài đặt
│   ├── quadtree.py             # Cây tứ phân phân vùng không gian 2D
│   ├── min_heap.py             # Min-Heap tự cân bằng cho Auto-aim
│   └── queue.py                # Hàng đợi FIFO tối ưu bộ nhớ cho Wave
├── assets/                     # Tài nguyên hình ảnh, âm thanh, spritesheet
│   ├── Soldier-Idle.png        # Spritesheet nhân vật chính
│   ├── zombie.png, bat.png...  # Spritesheet các loại quái vật
│   ├── bgm.mp3, hit.wav...     # Âm thanh và nhạc nền
│   └── grass.png               # Texture gạch cỏ bản đồ
├── entities/                   # Các thực thể trong game
│   ├── player.py               # Người chơi (di chuyển, cấp độ, trang bị)
│   ├── enemy.py                # Quái vật & AI Boids Separation
│   ├── weapon.py               # Vũ khí (Gun, HolyAura, ThunderStorm)
│   └── item.py                 # Tinh thể kinh nghiệm (ExpGem)
├── managers/                   # Các hệ thống điều phối
│   ├── wave_manager.py         # Quản lý chuỗi Wave & Roulette Selection
│   ├── upgrade_manager.py      # Hệ thống thẻ bài nâng cấp Level-Up
│   └── renderer.py             # Kết xuất HUD, Pause Menu, Game Over
├── .github/workflows/          # CI/CD tự động build Windows EXE trên GitHub Actions
│   └── build.yml
├── settings.py                 # Cấu hình hằng số & hàm resource_path an toàn
├── main.py                     # Entry point & Vòng lặp chính của Game
├── run.bat / run.sh            # Script 1-click chạy game cho Windows & Linux
├── build_exe.bat               # Script 1-click đóng gói Windows EXE
├── requirements.txt            # Danh sách thư viện cần thiết
├── requirements-dev.txt        # Thư viện phục vụ đóng gói và phát triển
├── ALGORITHMS.md               # Tài liệu học thuật phân tích chi tiết giải thuật
└── README.md                   # Hướng dẫn dự án
```

---

## 👨‍💻 Tác giả & Đồ án

- **Tác giả:** Hà Nhật Khoa (MSSV: 25520854)
- **Lớp:** ATTN2025 (Chương trình An toàn Thông tin Tài năng - Khóa K20)
- **Trường:** Đại học Công nghệ Thông tin (UIT) — ĐHQG TP.HCM.
- **Học phần:** IT003 — Cấu trúc dữ liệu và Giải thuật (DSA).

---

<p align="center">
  <i>Được phát triển với niềm đam mê dành cho Game Development, Toán học giải thuật và An toàn thông tin.</i>
</p>

