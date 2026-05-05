"""
Module chứa cấu trúc dữ liệu Quadtree (Cây tứ phân).
Hỗ trợ chia nhỏ không gian 2D để tối ưu hóa việc truy vấn vị trí và xử lý va chạm.
"""
import pygame

class QuadTree:
    """
    Cấu trúc dữ liệu Cây tứ phân (Quadtree) phân chia không gian đệ quy.
    Giúp giảm thiểu số lượng phép toán từ O(N^2) xuống mức tiệm cận O(N log N)
    bằng cách chỉ xét va chạm giữa các thực thể nằm trong cùng một khu vực nhỏ.

    Attributes:
        boundary (pygame.Rect): Vùng không gian hình chữ nhật mà Node này quản lý.
        capacity (int): Sức chứa tối đa (số lượng thực thể) trước khi Node bị chia nhỏ.
        enemies (list): Danh sách các quái vật hiện đang nằm trong Node này.
        divided (bool): Cờ đánh dấu Node này đã bị chia làm 4 hay chưa.
        northwest, northeast, southwest, southeast (QuadTree): 4 Node con.
    """

    def __init__(self, boundary: pygame.Rect, capacity: int):
        """
        Khởi tạo một Node QuadTree mới.

        Args:
            boundary (pygame.Rect): Khung không gian biên của Node.
            capacity (int): Sức chứa tối đa của Node.
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
        Thuật toán phân bào: Đệ quy chia Node hiện tại thành 4 Node con
        (4 góc phần tư bằng nhau) khi số lượng thực thể vượt quá capacity.
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
        Thêm một quái vật vào cây. Nếu Node đầy, tự động gọi subdivide()
        và đẩy quái vật xuống các Node con.

        Args:
            enemy (Enemy): Đối tượng quái vật cần thêm vào không gian.

        Returns:
            bool: True nếu chèn thành công, False nếu quái vật nằm ngoài boundary.
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
        Truy vấn nhanh tất cả quái vật nằm bên trong một khu vực nhất định.
        Dùng để xử lý đạn trúng quái vật hoặc tìm hàng xóm (Boids Algorithm).

        Args:
            search_rect (pygame.Rect): Khung hình chữ nhật cần tìm kiếm.
            found_enemies (list): Danh sách lưu trữ kết quả đệ quy.

        Returns:
            list: Danh sách các quái vật nằm trong vùng search_rect.
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
        Trực quan hóa cấu trúc QuadTree lên màn hình (Debug Mode).

        Args:
            screen (pygame.Surface): Bề mặt vẽ của Pygame.
            camera_x (float): Tọa độ Camera X.
            camera_y (float): Tọa độ Camera Y.
        """
        draw_rect = pygame.Rect(
            self.boundary.x - camera_x,
            self.boundary.y - camera_y,
            self.boundary.width,
            self.boundary.height
        )
        # Vẽ viền màu Hồng Neon (255, 0, 255) dày 2px để dễ nhìn
        pygame.draw.rect(screen, (255, 0, 255), draw_rect, 2)
        if self.divided:
            self.northwest.draw(screen, camera_x, camera_y)
            self.northeast.draw(screen, camera_x, camera_y)
            self.southwest.draw(screen, camera_x, camera_y)
            self.southeast.draw(screen, camera_x, camera_y)