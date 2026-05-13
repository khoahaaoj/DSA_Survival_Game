"""
Module chứa các cấu trúc dữ liệu tự cài đặt cho dự án.
Cung cấp lớp MinHeap để xử lý các bài toán về Hàng đợi ưu tiên (Priority Queue).
"""


class MinHeap:
    """
    Cấu trúc dữ liệu Min-Heap tự cài đặt bằng mảng (Array).

    Trong đồ án này, Min-Heap được sử dụng để quản lý danh sách kẻ địch,
    giúp hệ thống vũ khí (Auto-aim) luôn tìm được mục tiêu gần nhất
    mà không cần duyệt lại toàn bộ mảng mỗi khung hình.

    Attributes:
        heap (list): Mảng 1 chiều lưu trữ các phần tử. Mỗi phần tử là một
                     tuple có định dạng: (khoảng_cách_đến_người_chơi, đối_tượng_Enemy).
    """

    def __init__(self):
        """Khởi tạo một Min-Heap rỗng."""
        self.heap = []

    def push(self, item: tuple):
        """
        Thêm một phần tử mới vào Heap và duy trì tính chất của Min-Heap.

        Độ phức tạp thời gian: O(log N) với N là số lượng phần tử trong Heap.

        Args:
            item (tuple): Tuple chứa (khoảng_cách, đối_tượng_Enemy).
        """
        self.heap.append(item)
        self._heapify_up(len(self.heap) - 1)

    def pop(self) -> tuple:
        """
        Lấy ra và xóa phần tử có giá trị khoảng cách nhỏ nhất (Gốc của Heap).

        Độ phức tạp thời gian: O(log N).

        Returns:
            tuple: Phần tử có khoảng cách nhỏ nhất (khoảng_cách, đối_tượng_Enemy).
            None: Nếu Heap đang rỗng.
        """
        if len(self.heap) == 0:
            return None
        if len(self.heap) == 1:
            return self.heap.pop()

        # Lưu lại phần tử nhỏ nhất ở đỉnh
        root = self.heap[0]
        # Đưa phần tử cuối cùng lên đỉnh và tái cân bằng từ trên xuống
        self.heap[0] = self.heap.pop()
        self._heapify_down(0)

        return root

    def clear(self):
        """
        Làm sạch toàn bộ dữ liệu trong Heap.
        Được gọi ở mỗi khung hình (frame) mới để cập nhật lại tọa độ.

        Độ phức tạp thời gian: O(1).
        """
        self.heap = []

    def _heapify_up(self, index: int):
        """
        Hàm nội bộ (Internal): Đẩy phần tử có giá trị nhỏ nổi lên trên.
        So sánh phần tử hiện tại với node cha, nếu nhỏ hơn thì hoán đổi (swap).

        Args:
            index (int): Vị trí (index) của phần tử cần kiểm tra.
        """
        parent = (index - 1) // 2
        if index > 0 and self.heap[index][0] < self.heap[parent][0]:
            self.heap[index], self.heap[parent] = self.heap[parent], self.heap[index]
            self._heapify_up(parent)

    def _heapify_down(self, index: int):
        """
        Hàm nội bộ (Internal): Chìm phần tử có giá trị lớn xuống dưới.
        So sánh node hiện tại với 2 node con, hoán đổi với node con nhỏ nhất.

        Args:
            index (int): Vị trí (index) của phần tử cần kiểm tra.
        """
        smallest = index
        left = 2 * index + 1
        right = 2 * index + 2

        if left < len(self.heap) and self.heap[left][0] < self.heap[smallest][0]:
            smallest = left
        if right < len(self.heap) and self.heap[right][0] < self.heap[smallest][0]:
            smallest = right

        if smallest != index:
            self.heap[index], self.heap[smallest] = self.heap[smallest], self.heap[index]
            self._heapify_down(smallest)