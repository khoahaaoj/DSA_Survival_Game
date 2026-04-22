# algorithms/min_heap.py

class MinHeap:
    """
    Cấu trúc dữ liệu Min-Heap tự cài đặt bằng mảng (Array).
    Dùng để quản lý Priority Queue, giúp tìm kẻ địch gần nhất với O(log N).
    """

    def __init__(self):
        # Mảng lưu trữ các phần tử. Mỗi phần tử là 1 tuple: (khoảng_cách, đối_tượng_quái)
        self.heap = []

    def push(self, item):
        """ Thêm một phần tử vào Heap và tái cấu trúc từ dưới lên. """
        self.heap.append(item)
        self._heapify_up(len(self.heap) - 1)

    def pop(self):
        """ Lấy ra và xóa phần tử nhỏ nhất (gốc của Heap). """
        if len(self.heap) == 0:
            return None
        if len(self.heap) == 1:
            return self.heap.pop()

        # Lưu lại phần tử nhỏ nhất ở đỉnh
        root = self.heap[0]
        # Đưa phần tử cuối cùng lên đỉnh và tái cấu trúc từ trên xuống
        self.heap[0] = self.heap.pop()
        self._heapify_down(0)

        return root

    def clear(self):
        """ Làm sạch Heap cho mỗi khung hình mới. """
        self.heap = []

    def _heapify_up(self, index):
        """ Thuật toán đưa phần tử nhỏ nổi lên trên (O(log N)). """
        parent = (index - 1) // 2
        # Nếu node hiện tại nhỏ hơn node cha, tiến hành hoán đổi (swap)
        if index > 0 and self.heap[index][0] < self.heap[parent][0]:
            self.heap[index], self.heap[parent] = self.heap[parent], self.heap[index]
            self._heapify_up(parent)

    def _heapify_down(self, index):
        """ Thuật toán chìm phần tử lớn xuống dưới (O(log N)). """
        smallest = index
        left = 2 * index + 1
        right = 2 * index + 2

        # Kiểm tra con trái
        if left < len(self.heap) and self.heap[left][0] < self.heap[smallest][0]:
            smallest = left
        # Kiểm tra con phải
        if right < len(self.heap) and self.heap[right][0] < self.heap[smallest][0]:
            smallest = right

        # Nếu node hiện tại không phải nhỏ nhất, hoán đổi với node con nhỏ hơn
        if smallest != index:
            self.heap[index], self.heap[smallest] = self.heap[smallest], self.heap[index]
            self._heapify_down(smallest)