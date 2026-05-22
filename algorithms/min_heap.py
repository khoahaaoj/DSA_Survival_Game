"""
Module: algorithms/min_heap.py
Cung cấp cấu trúc dữ liệu Min-Heap (Đống nhỏ) tự cài đặt từ đầu bằng mảng.

Giải quyết bài toán:
    Hệ thống vũ khí cần auto-aim — tìm kẻ địch GẦN NHẤT để nhắm bắn.
    Nếu sort() toàn bộ danh sách mỗi frame: O(N log N) nhưng lãng phí vì
    chỉ cần lấy 1-2 phần tử nhỏ nhất.
    MinHeap cho phép lấy min trong O(1), thêm phần tử trong O(log N).

Ứng dụng trong game:
    Mỗi frame, khoảng cách từng kẻ địch đến player được push vào heap.
    Mỗi vũ khí pop() một lần → lấy kẻ địch gần nhất, không cần quét lại.
    Nhiều vũ khí → pop() nhiều lần → tự động lấy mục tiêu khác nhau.
"""


class MinHeap:
    """
    Min-Heap (Đống nhỏ) tự cài đặt bằng mảng 1 chiều.

    Tính chất bất biến (Heap Property):
        Phần tử tại node cha LUÔN nhỏ hơn hoặc bằng cả 2 node con.
        → Phần tử nhỏ nhất luôn ở vị trí heap[0] (đỉnh cây).

    Biểu diễn bằng mảng:
        Với node tại index i:
            - Node cha:    (i - 1) // 2
            - Node con trái: 2*i + 1
            - Node con phải: 2*i + 2

    Ví dụ heap chứa (khoảng_cách, enemy):
        heap[0] = (45.2, Zombie_A)   ← kẻ địch gần nhất, luôn ở đỉnh
        heap[1] = (120.5, Bat_B)
        heap[2] = (88.0, Zombie_C)
        heap[3] = (200.1, Golem_D)

    Attributes:
        heap (list): Mảng nội bộ lưu các tuple (khoảng_cách, enemy).
    """

    def __init__(self):
        """Khởi tạo Min-Heap rỗng."""
        self.heap: list = []

    def push(self, item: tuple):
        """
        Thêm một phần tử mới vào heap và duy trì tính chất Min-Heap.

        Cách hoạt động:
            1. Thêm phần tử vào cuối mảng.
            2. "Bơi lên" (heapify_up): so sánh với cha, hoán đổi nếu nhỏ hơn.
            3. Lặp lại đến khi đúng vị trí hoặc đến đỉnh.

        Args:
            item (tuple): (khoảng_cách: float, enemy: Enemy)
                          Khoảng cách dùng làm khóa so sánh.

        Time Complexity: O(log N)
        """
        self.heap.append(item)
        self._heapify_up(len(self.heap) - 1)

    def pop(self) -> tuple | None:
        """
        Lấy ra và xóa phần tử có khoảng cách NHỎ NHẤT (kẻ địch gần nhất).

        Cách hoạt động:
            1. Lấy phần tử đỉnh (heap[0]) — đây là min.
            2. Đưa phần tử cuối lên đỉnh.
            3. "Chìm xuống" (heapify_down): so sánh với 2 con, hoán đổi với con nhỏ hơn.
            4. Lặp lại đến khi đúng vị trí hoặc đến lá.

        Returns:
            tuple: (khoảng_cách, enemy) của kẻ địch gần nhất.
            None:  Nếu heap rỗng (không còn kẻ địch).

        Time Complexity: O(log N)
        """
        if not self.heap:
            return None
        if len(self.heap) == 1:
            return self.heap.pop()

        root = self.heap[0]
        self.heap[0] = self.heap.pop()   # Đưa phần tử cuối lên đỉnh
        self._heapify_down(0)            # Sắp xếp lại từ đỉnh xuống
        return root

    def clear(self):
        """
        Xóa toàn bộ heap, chuẩn bị cho frame tiếp theo.

        Được gọi ở đầu mỗi frame vì vị trí kẻ địch đã thay đổi —
        heap cũ chứa khoảng cách sai, phải xây lại hoàn toàn.

        Time Complexity: O(1)
        """
        self.heap = []

    def _heapify_up(self, index: int):
        """
        (Nội bộ) Đẩy phần tử tại `index` lên trên cho đến khi đúng chỗ.

        So sánh với node cha: nếu nhỏ hơn thì hoán đổi và tiếp tục lên.
        Dừng khi đã là đỉnh (index == 0) hoặc lớn hơn/bằng cha.

        Args:
            index (int): Vị trí cần kiểm tra trong mảng heap.
        """
        parent = (index - 1) // 2
        if index > 0 and self.heap[index][0] < self.heap[parent][0]:
            self.heap[index], self.heap[parent] = self.heap[parent], self.heap[index]
            self._heapify_up(parent)

    def _heapify_down(self, index: int):
        """
        (Nội bộ) Đẩy phần tử tại `index` xuống dưới cho đến khi đúng chỗ.

        So sánh với 2 node con: hoán đổi với con NHỎ HƠN nếu cha lớn hơn con.
        Dừng khi cả 2 con đều lớn hơn/bằng cha, hoặc đã là node lá.

        Args:
            index (int): Vị trí cần kiểm tra trong mảng heap.
        """
        smallest = index
        left  = 2 * index + 1
        right = 2 * index + 2

        if left  < len(self.heap) and self.heap[left][0]  < self.heap[smallest][0]:
            smallest = left
        if right < len(self.heap) and self.heap[right][0] < self.heap[smallest][0]:
            smallest = right

        if smallest != index:
            self.heap[index], self.heap[smallest] = self.heap[smallest], self.heap[index]
            self._heapify_down(smallest)

    def __len__(self) -> int:
        """Trả về số phần tử hiện có trong heap."""
        return len(self.heap)

    def __repr__(self) -> str:
        return f"MinHeap({len(self.heap)} items, min={self.heap[0][0]:.1f} if self.heap else 'empty')"