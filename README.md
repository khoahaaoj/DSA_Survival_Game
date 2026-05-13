# ⚔️ DSA Survival: Top-Down Time Survival Game

Một tựa game sinh tồn 2D nhịp độ cao được phát triển trên nền tảng Python/Pygame. Dự án áp dụng chuyên sâu các **Cấu trúc dữ liệu và Giải thuật (DSA)** nâng cao nhằm giải quyết bài toán tối ưu hóa hiệu năng (Big Data thời gian thực), duy trì 60 FPS khi xử lý hàng ngàn thực thể đồng thời trên màn hình.

---

## 📸 Ảnh minh họa (Screenshots)

### 1. Chiến đấu nhịp độ cao & Trí tuệ bầy đàn (Boids AI)
<img width="1284" height="737" alt="image" src="https://github.com/user-attachments/assets/1400efbb-6b1c-4dd5-af27-efa102aada8b" />

> *Hệ thống tự động phân tán quái vật bao vây người chơi kết hợp với Particle System hiển thị sát thương.*

### 2. Tối ưu không gian bằng Cây tứ phân (QuadTree)
<img width="1284" height="737" alt="image" src="https://github.com/user-attachments/assets/9c4bafa3-79fc-40b7-8f4a-92c4d0275c01" />

> *Giao diện Debug trực quan hóa thuật toán phân bào không gian đệ quy. Khu vực đông quái được chẻ nhỏ để giảm phạm vi tính toán va chạm.*

### 3. Giao diện điều khiển & Phân luồng âm thanh
<img width="1280" height="752" alt="image" src="https://github.com/user-attachments/assets/6ef79cff-bcc9-4968-b376-2992d8734887" />

> *Pause Menu với kỹ thuật Alpha Blending, cho phép can thiệp trực tiếp vào 2 luồng âm thanh BGM và SFX độc lập.*

---

## 🎮 Cách chơi (Gameplay)
- **Di chuyển:** Sử dụng cụm phím `W`, `A`, `S`, `D` để điều hướng nhân vật.
- **Chiến đấu tự động:** Người chơi không cần ngắm bắn. Hệ thống Auto-aim sẽ tự động quét và xả đạn vào các mục tiêu gần nhất.
- **Mục tiêu:** Né tránh vòng vây của kẻ thù, thu thập Ngọc kinh nghiệm (EXP) rớt ra từ quái vật để thăng cấp. Mỗi lần lên cấp, hệ thống sẽ mở khóa hoặc nâng cấp hỏa lực ngẫu nhiên. Sinh tồn càng lâu, thử thách càng khắc nghiệt!
- **Tạm dừng (Pause):** Nhấn phím `P` hoặc `ESC` để mở Menu, tại đây bạn có thể tùy chỉnh Nhạc nền (BGM) và Hiệu ứng âm thanh (SFX).

---

## 🧠 Cấu trúc dữ liệu & Thuật toán cốt lõi
Dự án không lạm dụng sức mạnh phần cứng mà tập trung vào tối ưu thuật toán:
- **Cây tứ phân (QuadTree):** Tối ưu hóa truy vấn không gian, giảm chi phí xét va chạm từ O(N^2) xuống tiệm cận O(N log N).
- **Hàng đợi ưu tiên (Min-Heap):** Quản lý mục tiêu tấn công cho vũ khí, đảm bảo truy vấn kẻ địch gần nhất với độ phức tạp O(log N).
- **Trí tuệ bầy đàn (Boids AI):** Thuật toán Separation kết hợp QuadTree giúp quái vật tự động lách qua nhau và bao vây người chơi hợp logic.
- **Lấy mẫu có trọng số (Weighted Random):** Ứng dụng Binary Search trên Prefix Sum Array để cân bằng tỷ lệ sinh quái vật theo độ hiếm.

---

## ⚙️ Cài đặt và Khởi chạy
Đảm bảo máy tính của bạn đã cài đặt Python 3.x.

1. Clone kho lưu trữ về máy:
    git clone [https://github.com/khoahaaoj/DSA_Survival_Game.git](https://github.com/khoahaaoj/DSA_Survival_Game.git)
    cd DSA_Survival_Game

2. Cài đặt thư viện đồ họa Pygame:
    pip install pygame

3. Khởi chạy trò chơi:
    python main.py

---

## 👨‍💻 Tác giả
- **Hà Nhật Khoa** (MSSV: 25520854)
- Lớp: IT003.Q21.CTTN  - Đại học Công nghệ Thông tin (UIT)
