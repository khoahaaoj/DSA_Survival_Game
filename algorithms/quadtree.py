"""
Module: algorithms/quadtree.py
Cung cấp cấu trúc dữ liệu QuadTree (Cây Tứ Phân) tự cài đặt.

Giải quyết bài toán:
    Với N entity trên màn hình, kiểm tra va chạm brute-force tốn O(N^2) phép tính.
    QuadTree giảm xuống O(N log N) bằng cách phân vùng không gian — chỉ so sánh
    các entity CÙNG nằm trong một vùng nhỏ, loại bỏ những cặp ở xa nhau.

Ứng dụng trong game:
    - Đạn kiểm tra va chạm với kẻ địch.
    - Kẻ địch tìm hàng xóm để tránh chồng lên nhau (Boids AI).
    - Player tìm kẻ địch trong vùng tiếp xúc.
"""
import pygame


class QuadTree:
    """
    Cây phân vùng không gian 2D đệ quy (Recursive 2D Spatial Partitioning Tree).

    Nguyên lý hoạt động:
        Mỗi node quản lý một vùng hình chữ nhật và lưu tối đa `capacity` entity.
        Khi đầy, node tự chia thành 4 ô con (NW, NE, SW, SE) và đẩy entity xuống
        ô con phù hợp. Khi truy vấn, chỉ duyệt các nhánh giao với vùng tìm kiếm.

    Ví dụ với capacity=4 và 10 entity:
        Node gốc (đầy 4) → chia thành 4 con
        Chỉ duyệt con chứa vùng tìm kiếm → bỏ qua 3 con còn lại

    Attributes:
        boundary (pygame.Rect): Vùng không gian mà node này quản lý.
        capacity (int):         Số entity tối đa trước khi tự chia (trong game: 4).
        enemies (list):         Danh sách entity đang lưu tại node này.
        divided (bool):         True nếu node đã chia thành 4 con.
        northwest, northeast,
        southwest, southeast:   4 node con (None nếu chưa chia).
    """

    def __init__(self, boundary: pygame.Rect, capacity: int):
        """
        Khởi tạo một node QuadTree mới (có thể là node gốc hoặc node con).

        Args:
            boundary (pygame.Rect): Vùng không gian node này quản lý.
            capacity (int):         Số entity tối đa trước khi chia nhỏ.
        """
        self.boundary = boundary
        self.capacity = capacity
        self.enemies  = []
        self.divided  = False

        self.northwest = None
        self.northeast = None
        self.southwest = None
        self.southeast = None

    def subdivide(self):
        """
        Chia node hiện tại thành 4 node con bằng nhau (theo 4 góc phần tư).

        Được gọi tự động khi số entity vượt quá `capacity`.
        Mỗi node con nhận 1/4 diện tích của node cha.

        Time Complexity: O(1)
        """
        x, y   = self.boundary.x, self.boundary.y
        w, h   = self.boundary.width, self.boundary.height
        hw, hh = w / 2, h / 2

        self.northwest = QuadTree(pygame.Rect(x,      y,      hw, hh), self.capacity)
        self.northeast = QuadTree(pygame.Rect(x + hw, y,      hw, hh), self.capacity)
        self.southwest = QuadTree(pygame.Rect(x,      y + hh, hw, hh), self.capacity)
        self.southeast = QuadTree(pygame.Rect(x + hw, y + hh, hw, hh), self.capacity)

        self.divided = True

    def insert(self, enemy) -> bool:
        """
        Chèn một entity vào đúng vị trí trong cây.

        Nếu entity nằm ngoài vùng node → từ chối (return False).
        Nếu node còn chỗ → lưu trực tiếp.
        Nếu node đầy → chia nhỏ rồi đẩy entity xuống node con phù hợp.

        Args:
            enemy: Entity cần chèn (phải có thuộc tính x, y, size).

        Returns:
            True  nếu chèn thành công.
            False nếu entity nằm ngoài vùng của node này.

        Time Complexity: O(log N) trung bình, O(N) trường hợp xấu nhất
                         (khi toàn bộ entity chồng lên cùng một điểm).
        """
        enemy_rect = pygame.Rect(enemy.x - enemy.size / 2,
                                 enemy.y - enemy.size / 2,
                                 enemy.size, enemy.size)

        if not self.boundary.colliderect(enemy_rect):
            return False

        if len(self.enemies) < self.capacity:
            self.enemies.append(enemy)
            return True

        if not self.divided:
            self.subdivide()

        # Thử chèn vào từng node con theo thứ tự ưu tiên
        if self.northwest.insert(enemy): return True
        if self.northeast.insert(enemy): return True
        if self.southwest.insert(enemy): return True
        if self.southeast.insert(enemy): return True

        return False

    def query(self, search_rect: pygame.Rect, found: list) -> list:
        """
        Tìm tất cả entity nằm trong vùng hình chữ nhật `search_rect`.

        Cơ chế tối ưu: nếu `search_rect` không giao với vùng của node,
        toàn bộ nhánh con cũng bị bỏ qua ngay lập tức (pruning).

        Ứng dụng trong game:
            - Đạn truy vấn vùng 10×10 quanh nó để tìm kẻ địch trúng đạn.
            - Kẻ địch truy vấn vùng 76×76 quanh nó để chạy thuật toán Boids.
            - HolyAura truy vấn vùng 240×240 để gây sát thương diện rộng.

        Args:
            search_rect (pygame.Rect): Vùng cần tìm entity.
            found (list):              Danh sách kết quả (truyền vào để đệ quy tích lũy).

        Returns:
            list: Danh sách entity nằm trong `search_rect`.

        Time Complexity: O(log N + K), K = số entity tìm được.
        """
        if not self.boundary.colliderect(search_rect):
            return found

        for enemy in self.enemies:
            enemy_rect = pygame.Rect(enemy.x - enemy.size / 2,
                                     enemy.y - enemy.size / 2,
                                     enemy.size, enemy.size)
            if search_rect.colliderect(enemy_rect):
                found.append(enemy)

        if self.divided:
            self.northwest.query(search_rect, found)
            self.northeast.query(search_rect, found)
            self.southwest.query(search_rect, found)
            self.southeast.query(search_rect, found)

        return found

    def draw(self, screen: pygame.Surface, camera_x: float, camera_y: float):
        """
        Vẽ đường kẻ phân vùng của QuadTree lên màn hình (chế độ debug).

        Nhấn phím Q trong game để bật/tắt chế độ này và quan sát
        cách cây tự động phân chia theo sự phân bố của kẻ địch.

        Args:
            screen (pygame.Surface): Bề mặt render của Pygame.
            camera_x (float):        Độ lệch camera theo trục X.
            camera_y (float):        Độ lệch camera theo trục Y.
        """
        draw_rect = pygame.Rect(
            self.boundary.x - camera_x,
            self.boundary.y - camera_y,
            self.boundary.width,
            self.boundary.height
        )
        pygame.draw.rect(screen, (255, 0, 255), draw_rect, 1)
        if self.divided:
            self.northwest.draw(screen, camera_x, camera_y)
            self.northeast.draw(screen, camera_x, camera_y)
            self.southwest.draw(screen, camera_x, camera_y)
            self.southeast.draw(screen, camera_x, camera_y)