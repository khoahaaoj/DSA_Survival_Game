# 📚 Giải Thích Chi Tiết Thuật Toán — DSA Survival Game

> Tài liệu này giải thích từng thuật toán được sử dụng trong game,
> bằng ngôn ngữ đơn giản, có ví dụ minh họa và code thực tế.

---

## Mục lục

1. [QuadTree — Chia Vùng Không Gian](#1-quadtree)
2. [MinHeap — Hàng Đợi Ưu Tiên (Auto-Aim)](#2-minheap)
3. [Queue FIFO — Hàng Đợi Quản Lý Wave](#3-queue-fifo)
4. [Roulette Selection — Chọn Ngẫu Nhiên Có Trọng Số](#4-roulette-selection)
5. [Boids Separation — AI Tránh Chồng Lên Nhau](#5-boids-separation)
6. [Viewport Culling — Chỉ Vẽ Những Gì Nhìn Thấy](#6-viewport-culling)
7. [Floating Text O(N) — Xóa Hiệu Quả Khỏi Danh Sách](#7-floating-text-on)

---

## 1. QuadTree

**File:** `algorithms/quadtree.py`  
**Dùng để:** Tìm kẻ địch gần nhau, kiểm tra va chạm

### Vấn đề cần giải quyết

Trong game có tới 400 kẻ địch. Nếu muốn kiểm tra xem viên đạn của bạn có trúng kẻ địch nào không, cách đơn giản nhất là duyệt qua **toàn bộ 400 kẻ địch** để so sánh.

Giả sử có 50 viên đạn và 400 kẻ địch:
```
50 đạn × 400 kẻ địch = 20,000 phép tính mỗi frame
60 FPS → 1,200,000 phép tính mỗi giây ❌ QUÁ CHẬM
```

### Ý tưởng của QuadTree

Chia màn hình thành các ô nhỏ hơn. Chỉ kiểm tra va chạm giữa các vật thể **trong cùng một ô**.

```
Màn hình ban đầu (1 ô lớn):
┌─────────────────────────┐
│  👾  👾                 │
│          👾  👾  👾     │
│  👾              👾     │
│      👾  👾  👾         │
└─────────────────────────┘

Sau khi chia (QuadTree với capacity=4):
┌────────────┬────────────┐
│  👾  👾   │            │
│           │ 👾  👾  👾 │
├────────────┼────────────┤
│  👾        │     👾     │
│      👾   │  👾  👾    │
└────────────┴────────────┘

Ô phải dưới có 3 kẻ địch → tự chia tiếp:
┌────────────┬──────┬─────┐
│  👾  👾   │      │     │
│           │👾 👾 │ 👾  │
├────────────┼──────┴─────┤
│  👾        │     👾     │
│      👾   │  👾  👾    │
└────────────┴────────────┘
```

### Quy tắc hoạt động

1. Mỗi ô chứa tối đa **4 phần tử** (capacity = 4)
2. Khi ô đầy → **tự động chia thành 4 ô con** (gọi là subdivide)
3. Khi cần tìm vật thể gần một điểm → chỉ duyệt ô chứa điểm đó

### Ví dụ thực tế trong game

Viên đạn ở vị trí (300, 200). Thay vì check 400 kẻ địch:
```python
# Truy vấn QuadTree: chỉ lấy kẻ địch trong vùng 10x10 quanh đạn
nearby = quadtree.query(Rect(295, 195, 10, 10), [])
# Kết quả: chỉ 3-5 kẻ địch thay vì 400 → nhanh hơn rất nhiều
```

### Độ phức tạp

| Thao tác | Độ phức tạp | Ý nghĩa |
|---|---|---|
| Thêm 1 kẻ địch vào cây | O(log N) | N = số kẻ địch |
| Tìm kẻ địch trong vùng | O(log N + K) | K = số kẻ tìm được |
| Xây lại toàn bộ cây | O(N log N) | Làm mỗi frame |

> **Tại sao xây lại mỗi frame?**
> Vì kẻ địch di chuyển liên tục. QuadTree cũ sẽ sai vị trí → phải xây lại.

### Code thực tế (từ game)

```python
# Xây QuadTree mỗi frame
quadtree = QuadTree(pygame.Rect(0, 0, MAP_WIDTH, MAP_HEIGHT), capacity=4)
for enemy in enemies:
    quadtree.insert(enemy)  # O(log N) mỗi enemy

# Tìm kẻ địch gần viên đạn
nearby = quadtree.query(pygame.Rect(b.x - 5, b.y - 5, 10, 10), [])
```

---

## 2. MinHeap

**File:** `algorithms/min_heap.py`  
**Dùng để:** Vũ khí tự động tìm kẻ địch gần nhất để nhắm

### Vấn đề cần giải quyết

Vũ khí trong game tự động bắn vào kẻ địch **gần nhất**. Làm sao tìm kẻ địch gần nhất trong số 400 kẻ?

**Cách đơn giản (sai):**
```python
# Sắp xếp toàn bộ 400 kẻ theo khoảng cách rồi lấy phần tử đầu
sorted_enemies = sorted(enemies, key=lambda e: distance(player, e))
closest = sorted_enemies[0]
# Độ phức tạp: O(N log N) và phải làm lại mỗi frame → CHẬM
```

### Ý tưởng của MinHeap

Heap là cây nhị phân đặc biệt: **cha luôn nhỏ hơn hoặc bằng con**.

```
Minh họa MinHeap với khoảng cách kẻ địch đến player:

        50 ← kẻ địch gần nhất luôn ở đỉnh
       /   \
     120    80
    /   \  /  \
  200  150 100  300

- Lấy kẻ gần nhất (50): O(1) chỉ cần xem đỉnh
- Thêm 1 kẻ địch mới: O(log N) để sắp xếp lại
- Không cần sort toàn bộ!
```

### Cách hoạt động trong game

```
Mỗi frame:
1. Tính khoảng cách từng kẻ địch đến player
2. Push vào MinHeap: heap.push((khoảng_cách, enemy))
3. Khi vũ khí cần bắn: heap.pop() → lấy kẻ gần nhất ngay lập tức
```

### Code thực tế

```python
# Xây MinHeap mỗi frame
target_heap.clear()
for enemy in enemies:
    dist = distance(player, enemy)
    target_heap.push((dist, enemy))  # O(log N)

# Vũ khí lấy mục tiêu
target = target_heap.pop()  # O(log N) — lấy kẻ gần nhất
if target:
    bullet = Bullet(player.x, player.y, target.x, target.y)
```

### Tại sao không dùng sort?

```
sort() toàn bộ 400 kẻ mỗi frame:
  → O(N log N) = 400 × 8.6 ≈ 3,440 phép tính

MinHeap push 400 kẻ + pop 1:
  → 400 × O(log N) push + O(log N) pop
  → Tương đương, NHƯNG MinHeap có thể tái sử dụng giữa các vũ khí
  → Vũ khí 1 pop() → lấy kẻ gần nhất
  → Vũ khí 2 pop() → lấy kẻ gần nhất thứ 2
  → Không cần sort lại!
```

---

## 3. Queue FIFO

**File:** `algorithms/queue.py`  
**Dùng để:** Quản lý thứ tự các đợt Wave quái vật

### FIFO là gì?

**First In — First Out**: Cái nào vào trước thì ra trước.

Giống như hàng đợi mua vé:
```
Vào:  [Wave1] → [Wave2] → [Wave3] → [Wave4] → [Wave5]
Ra:    Wave1 → Wave2 → Wave3 → Wave4 → Wave5
```

### Vấn đề với cách đơn giản

```python
# Cách SAI — dùng list thông thường
waves = [wave1, wave2, wave3, wave4, wave5]
waves.pop(0)  # Lấy wave đầu tiên

# pop(0) phải DỊCH CHUYỂN toàn bộ mảng về trái:
# [wave2, wave3, wave4, wave5]
#  ↑ wave này phải dịch sang trái
# Độ phức tạp: O(N) — chậm khi có nhiều wave
```

### Giải pháp: Con trỏ Head

```python
# Cách ĐÚNG — dùng con trỏ
_data = [wave1, wave2, wave3, wave4, wave5]
_head = 0  # Con trỏ trỏ vào phần tử đầu tiên

# Lấy wave đầu:
item = _data[_head]  # Lấy phần tử tại vị trí head
_head += 1           # Dịch con trỏ sang phải (không cần dịch cả mảng!)

# Sau khi lấy wave1:
_data = [wave1, wave2, wave3, wave4, wave5]
_head =        1 ← con trỏ

# Sau khi lấy wave2:
_data = [wave1, wave2, wave3, wave4, wave5]
_head =               2 ← con trỏ

# Khi _head > len/2 → xóa phần đã dùng để giải phóng bộ nhớ
_data = [wave3, wave4, wave5]
_head = 0
```

### Độ phức tạp

| Thao tác | List.pop(0) ❌ | Queue với _head ✅ |
|---|---|---|
| Thêm wave vào cuối | O(1) | O(1) |
| Lấy wave đầu tiên | **O(N)** | **O(1)** |

### Code thực tế trong game

```python
# Khởi tạo: nạp 5 wave vào Queue
wave_queue = Queue()
wave_queue.enqueue(wave1_config)  # O(1)
wave_queue.enqueue(wave2_config)  # O(1)
wave_queue.enqueue(wave3_config)  # O(1)
...

# Trong game: khi wave cũ kết thúc, lấy wave tiếp theo
next_wave = wave_queue.dequeue()  # O(1) nhờ con trỏ
if next_wave:
    activate_wave(next_wave)
else:
    # Queue rỗng → chuyển sang Endless Mode
    activate_endless_wave()
```

---

## 4. Roulette Selection

**File:** `managers/wave_manager.py` (hàm `_roulette`)  
**Dùng để:** Quyết định loại quái nào xuất hiện theo xác suất

### Vấn đề cần giải quyết

Mỗi khi quái xuất hiện, cần chọn loại quái theo tỉ lệ:
- **Zombie:** 60% 
- **Bat:** 30%
- **Golem:** 10%

**Cách đơn giản (không tối ưu):**
```python
# Tạo danh sách 100 phần tử: 60 Zombie, 30 Bat, 10 Golem
pool = ['Zombie'] * 60 + ['Bat'] * 30 + ['Golem'] * 10
chosen = random.choice(pool)  # O(1) nhưng tốn bộ nhớ 100 phần tử
```

**Vấn đề:** Nếu tỉ lệ là 60.5%, 30.3%, 9.2% → không dùng số nguyên được. Tỉ lệ nhiều loại quái → danh sách rất dài.

### Giải pháp: Prefix Sum + Binary Search

**Bước 1:** Tính tổng tiền tố (Prefix Sum)

```
weights = [60, 30, 10]
             ↓
prefix = [60, 90, 100]
          ↑   ↑   ↑
         60  60+30  60+30+10
```

**Bước 2:** Tung số ngẫu nhiên từ 0 đến 100

```
roll = random.uniform(0, 100)
Giả sử roll = 75
```

**Bước 3:** Tìm xem roll rơi vào đoạn nào (Binary Search)

```
prefix = [60, 90, 100]
                ↑
roll=75 < 90 → Bat (index 1)

roll=45 < 60 → Zombie (index 0)

roll=95 < 100 → Golem (index 2)
```

**Tại sao Binary Search?**

```
Nếu có 100 loại quái:
- Duyệt tuyến tính: O(N) = 100 bước
- Binary Search:    O(log N) = 7 bước  ← nhanh hơn 14 lần!
```

### Minh họa Binary Search

```
Tìm roll=75 trong [60, 90, 100]:

lo=0, hi=2
mid = (0+2)//2 = 1
prefix[1] = 90

75 < 90 → hi = 1

lo=0, hi=1
mid = (0+1)//2 = 0
prefix[0] = 60

75 > 60 → lo = 1

lo == hi == 1 → Chọn options[1] = Bat ✓
```

### Code thực tế

```python
def _roulette(options, weights):
    # Bước 1: Xây Prefix Sum
    prefix, s = [], 0
    for w in weights:
        s += w
        prefix.append(s)
    # prefix = [60, 90, 100]

    # Bước 2: Tung số ngẫu nhiên
    roll = random.uniform(0, prefix[-1])  # 0.0 đến 100.0

    # Bước 3: Binary Search
    lo, hi = 0, len(prefix) - 1
    while lo < hi:
        mid = (lo + hi) // 2
        if roll < prefix[mid]:
            hi = mid
        else:
            lo = mid + 1

    return options[lo]  # Trả về loại quái được chọn
```

---

## 5. Boids Separation

**File:** `entities/enemy.py`  
**Dùng để:** Kẻ địch tránh chồng lên nhau khi di chuyển

### Vấn đề

Nếu không có gì ngăn cản, tất cả kẻ địch sẽ chồng chất lên nhau thành 1 đống → trông rất giả tạo:

```
Không có Boids:         Có Boids:
     👾                   👾 👾
   👾👾👾               👾    👾
     👾                   👾 👾
(đống lộn xộn)         (dàn đều xung quanh)
```

### Ý tưởng

Mỗi kẻ địch nhìn quanh trong bán kính nhỏ. Nếu có kẻ địch khác gần quá → đẩy ra xa.

```
Kẻ địch A nhìn quanh:
        ← Đẩy ra hướng này
  B ●──●── A
  C ●──●── A
        ← Đẩy ra hướng này

A cộng tất cả lực đẩy → di chuyển ra xa B và C
```

### Tối ưu: Squared Distance

Để so sánh khoảng cách, bình thường phải tính:
```python
dist = sqrt(dx² + dy²)  # sqrt() rất tốn CPU
if dist < radius:        # mới dùng dist
    ...
```

**Vấn đề:** `sqrt()` là phép tính nặng, gọi hàng nghìn lần mỗi frame.

**Tối ưu hóa:**
```python
# Không cần sqrt để so sánh!
dist_sq = dx * dx + dy * dy          # Tính bình phương khoảng cách
if dist_sq < radius * radius:        # So sánh bình phương
    dist = sqrt(dist_sq)             # Chỉ tính sqrt KHI CẦN
    # (khi cần normalize vector để tính hướng đẩy)
```

**Lợi ích:**
```
400 kẻ địch × 15 lân cận mỗi kẻ = 6,000 lần so sánh/frame
Nếu chỉ 5/15 thực sự trong range:
  Trước tối ưu: 6,000 sqrt() calls
  Sau tối ưu:   2,000 sqrt() calls  ← giảm 67%!
```

### Code thực tế

```python
for neighbor in nearby_enemies:
    ndx = self.x - neighbor.x
    ndy = self.y - neighbor.y

    # Dùng bình phương để tránh sqrt() trong vòng lặp
    ndist_sq = ndx * ndx + ndy * ndy

    if 0 < ndist_sq < separation_radius_sq:
        # Chỉ tính sqrt khi chắc chắn neighbor trong range
        ndist = math.sqrt(ndist_sq)
        # Tính lực đẩy tỉ lệ nghịch với khoảng cách
        separation_x += (ndx / ndist) / ndist
        separation_y += (ndy / ndist) / ndist
```

---

## 6. Viewport Culling

**File:** `main.py` (hàm `draw_map`)  
**Dùng để:** Chỉ vẽ những ô map đang hiện trên màn hình

### Vấn đề

Bản đồ game rất lớn (ví dụ: 5000×5000 pixel), nhưng màn hình chỉ hiện 1060×680 pixel. Nếu vẽ toàn bộ bản đồ mỗi frame → cực kỳ lãng phí:

```
Bản đồ thực:          Màn hình thấy:
┌──────────────────┐  ┌──────┐
│                  │  │      │
│  ┌──────┐        │  │ đây  │
│  │ thấy │        │  │      │
│  └──────┘        │  └──────┘
│                  │
└──────────────────┘
Vẽ toàn bộ = lãng phí!
```

### Giải pháp: Chỉ vẽ tile trong viewport

```python
def draw_map(screen, camera_x, camera_y, grass_tiles):
    # Tính tile đầu tiên cần vẽ (góc trái trên màn hình)
    start_col = int(camera_x // TILE_SIZE)
    start_row = int(camera_y // TILE_SIZE)

    # Tính số tile cần vẽ (vừa đủ lấp đầy màn hình + 2 tile dự phòng)
    cols = WIDTH  // TILE_SIZE + 2  # ≈ 22 cột
    rows = HEIGHT // TILE_SIZE + 2  # ≈ 14 hàng

    # Chỉ vẽ 22 × 14 = 308 tile thay vì toàn bộ bản đồ!
    for row in range(start_row, start_row + rows):
        for col in range(start_col, start_col + cols):
            draw_x = col * TILE_SIZE - camera_x
            draw_y = row * TILE_SIZE - camera_y
            screen.blit(grass_tiles[...], (draw_x, draw_y))
```

### Trick: Tile biến thể không lặp lại

Chỉ có 1 ảnh cỏ nhưng muốn bản đồ trông đa dạng:

```python
# Dùng phép hash đơn giản
tile_index = (col * 31 + row * 17) % len(grass_tiles)
```

- Nhân với số nguyên tố (31, 17) → tạo ra phân phối đều
- Cùng tọa độ (col, row) → luôn ra cùng tile → bản đồ không thay đổi mỗi frame

---

## 7. Floating Text O(N)

**File:** `main.py`  
**Dùng để:** Xóa hiệu quả các con số sát thương bay lên sau khi hết thời gian

### Vấn đề

Khi kẻ địch bị đánh hoặc player bị đánh → xuất hiện con số bay lên ("+25", "-10",...). Sau vài giây cần xóa đi.

**Cách sai:**
```python
for ft in floating_texts:
    ft['life'] -= 1
    if ft['life'] <= 0:
        floating_texts.remove(ft)  # ← remove() phải tìm kiếm + dịch mảng!
```

`remove()` trong Python list:
1. Duyệt từ đầu đến khi tìm được phần tử → O(N)
2. Dịch tất cả phần tử phía sau về trái → O(N)
3. Gọi trong vòng for → **O(N²) tổng thể!**

Với 100 floating texts → 100 × 100 = **10,000 thao tác** mỗi frame!

**Cách đúng — List Rebuild:**
```python
next_texts = []  # Tạo list mới, rỗng
for ft in floating_texts:
    ft['life'] -= 1
    if ft['life'] > 0:
        next_texts.append(ft)  # Chỉ giữ lại những cái còn sống
floating_texts = next_texts  # Thay thế list cũ
```

Duyệt 1 lần duy nhất → **O(N)** — nhanh hơn 100× so với cách dùng `remove()`!

---

## Tổng Kết Độ Phức Tạp

| Thuật toán | Dùng để | Độ phức tạp |
|---|---|---|
| QuadTree | Va chạm | O(N log N) build, O(log N + K) query |
| MinHeap | Auto-aim | O(N log N) build, O(log N) query |
| Queue FIFO | Wave system | O(1) enqueue, O(1) dequeue |
| Roulette | Spawn loại quái | O(N) build, O(log N) query |
| Boids Separation | AI kẻ địch | O(N × K), K ≈ 5-10 |
| Viewport Culling | Vẽ bản đồ | O(W × H / tile²) — không phụ thuộc map size |
| List Rebuild | Floating text | O(N) |

**Tổng mỗi frame:** Dominated bởi O(N log N) từ QuadTree và MinHeap.

Với N = 400 kẻ địch:
```
O(N log N) = 400 × log₂(400) ≈ 400 × 8.6 ≈ 3,440 phép tính

So với O(N²) brute-force:
O(N²) = 400 × 400 = 160,000 phép tính

→ Tối ưu được 160,000 / 3,440 ≈ 46 lần nhanh hơn! 🚀
```
