"""
Module cung cấp cấu trúc dữ liệu QuadTree (Cây tứ phân).
Ứng dụng thuật toán Phân hoạch không gian (Spatial Partitioning) để tối ưu hóa
các bài toán truy vấn phạm vi (Range Query) và phát hiện va chạm (Collision Detection) trong thời gian thực.
"""
import pygame

class QuadTree:
    """
    Cấu trúc dữ liệu Cây tứ phân (QuadTree) phân chia không gian đệ quy.

    Giúp giảm thiểu số lượng phép toán kiểm tra va chạm từ O(N^2) của thuật toán
    vết cạn (Brute Force) xuống mức tiệm cận O(N log N) bằng cách chỉ xét va chạm
    giữa các thực thể nằm trong cùng một khu vực cục bộ.

    Attributes:
        boundary (pygame.Rect): Khung giới hạn không gian (Bounding Box) mà Node này quản lý.
        capacity (int): Ngưỡng sức chứa tối đa. Nếu vượt quá, Node sẽ tự động phân bào.
        enemies (list): Danh sách các thực thể (Enemy) đang lưu trữ tại Node hiện tại.
        divided (bool): Cờ trạng thái xác định Node đã được phân chia hay chưa.
        northwest, northeast, southwest, southeast (QuadTree): 4 Node con tương ứng với 4 góc phần tư.
    """

    def __init__(self, boundary: pygame.Rect, capacity: int):
        """
        Khởi tạo một Node QuadTree mới.

        Args:
            boundary (pygame.Rect): Khung không gian biên của hệ tọa độ.
            capacity (int): Sức chứa tối đa của Node trước khi phân chia.
        """
        self.boundary = boundary
        self.capacity = capacity
        self.enemies = []
        self.divided = False

        self.northwest = None
        self.northeast = None
        self.southwest = None
        self.southeast = None

    def subdivide(self):
        """
        Thuật toán phân bào (Subdivision).
        Đệ quy chia không gian của Node hiện tại thành 4 phần tư bằng nhau (Góc phần tư 1, 2, 3, 4).
        Được gọi tự động khi số lượng phần tử vượt quá `capacity`.

        Time Complexity: O(1)
        """
        x, y = self.boundary.x, self.boundary.y
        w, h = self.boundary.width, self.boundary.height
        hw, hh = w / 2, h / 2

        self.northwest = QuadTree(pygame.Rect(x, y, hw, hh), self.capacity)
        self.northeast = QuadTree(pygame.Rect(x + hw, y, hw, hh), self.capacity)
        self.southwest = QuadTree(pygame.Rect(x, y + hh, hw, hh), self.capacity)
        self.southeast = QuadTree(pygame.Rect(x + hw, y + hh, hw, hh), self.capacity)

        self.divided = True

    def insert(self, enemy) -> bool:
        """
        Thêm một thực thể (quái vật) vào cây QuadTree.
        Nếu Node đầy, hệ thống tự động phân chia và đẩy thực thể xuống các Node con phù hợp.

        Args:
            enemy (Enemy): Đối tượng quái vật cần chèn vào cây không gian.

        Returns:
            bool: True nếu chèn thành công, False nếu đối tượng nằm ngoài khung giới hạn của Node.

        Time Complexity: Average O(log N), Worst O(N)
        """
        enemy_rect = pygame.Rect(enemy.x - enemy.size/2, enemy.y - enemy.size/2, enemy.size, enemy.size)

        if not self.boundary.colliderect(enemy_rect):
            return False

        if len(self.enemies) < self.capacity:
            self.enemies.append(enemy)
            return True

        if not self.divided:
            self.subdivide()

        if self.northwest.insert(enemy): return True
        if self.northeast.insert(enemy): return True
        if self.southwest.insert(enemy): return True
        if self.southeast.insert(enemy): return True

        return False

    def query(self, search_rect: pygame.Rect, found_enemies: list) -> list:
        """
        Truy vấn không gian (Range Query): Tìm tất cả các thực thể nằm bên trong một khu vực nhất định.
        Ứng dụng cho hệ thống sát thương diện rộng (AoE), xử lý đạn trúng đích hoặc tính toán
        lân cận cho thuật toán bầy đàn (Boids AI).

        Args:
            search_rect (pygame.Rect): Khung hình chữ nhật xác định vùng không gian cần truy vấn.
            found_enemies (list): Mảng tham chiếu dùng để gom nhóm và lưu trữ kết quả đệ quy.

        Returns:
            list: Danh sách chứa các thực thể nằm trong vùng `search_rect`.

        Time Complexity: Average O(log N + K) với K là số lượng thực thể tìm thấy.
        """
        if not self.boundary.colliderect(search_rect):
            return found_enemies

        for enemy in self.enemies:
            enemy_rect = pygame.Rect(enemy.x - enemy.size/2, enemy.y - enemy.size/2, enemy.size, enemy.size)
            if search_rect.colliderect(enemy_rect):
                found_enemies.append(enemy)

        if self.divided:
            self.northwest.query(search_rect, found_enemies)
            self.northeast.query(search_rect, found_enemies)
            self.southwest.query(search_rect, found_enemies)
            self.southeast.query(search_rect, found_enemies)

        return found_enemies

    def draw(self, screen: pygame.Surface, camera_x: float, camera_y: float):
        """
        Kết xuất trực quan (Visualization) cấu trúc lưới QuadTree lên màn hình.
        Hỗ trợ quá trình gỡ lỗi (Debug Mode) để biểu diễn cách thuật toán phân chia không gian.

        Args:
            screen (pygame.Surface): Bề mặt vẽ của Engine Pygame.
            camera_x (float): Tọa độ góc nhìn Camera trục X.
            camera_y (float): Tọa độ góc nhìn Camera trục Y.
        """
        draw_rect = pygame.Rect(
            self.boundary.x - camera_x,
            self.boundary.y - camera_y,
            self.boundary.width,
            self.boundary.height
        )
        pygame.draw.rect(screen, (255, 0, 255), draw_rect, 2)
        if self.divided:
            self.northwest.draw(screen, camera_x, camera_y)
            self.northeast.draw(screen, camera_x, camera_y)
            self.southwest.draw(screen, camera_x, camera_y)
            self.southeast.draw(screen, camera_x, camera_y)