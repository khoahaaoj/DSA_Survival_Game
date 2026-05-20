"""
Module cung cấp cấu trúc dữ liệu Queue (Hàng đợi FIFO) tự cài đặt.
Được WaveManager sử dụng để quản lý chuỗi Wave theo thứ tự FIFO.
"""


class Queue:
    """
    Cấu trúc dữ liệu Hàng đợi (Queue) tự cài đặt bằng mảng động.
    Nguyên tắc FIFO (First In – First Out): phần tử vào trước sẽ ra trước.

    Tối ưu bộ nhớ: dùng con trỏ _head thay vì list.pop(0) để tránh
    dịch chuyển O(N) mỗi lần dequeue. Mảng được thu gọn định kỳ
    để ngăn rò rỉ bộ nhớ (Memory Leak).

    Attributes:
        _data (list): Mảng nội bộ lưu trữ phần tử.
        _head (int) : Chỉ số phần tử đầu hàng đợi.

    Time Complexity:
        enqueue : O(1) amortized
        dequeue : O(1) amortized
        peek    : O(1)
        size    : O(1)
    """

    def __init__(self):
        """Khởi tạo một Queue rỗng."""
        self._data: list = []
        self._head: int  = 0

    def enqueue(self, item) -> None:
        """
        Thêm phần tử vào cuối hàng đợi.

        Args:
            item: Phần tử bất kỳ cần thêm vào.

        Time Complexity: O(1) amortized.
        """
        self._data.append(item)

    def dequeue(self):
        """
        Lấy và xóa phần tử ở đầu hàng đợi (FIFO).
        Tiến con trỏ _head thay vì xóa vật lý để đạt O(1).
        Tự động thu gọn mảng khi _head vượt quá nửa độ dài.

        Returns:
            Phần tử đầu hàng đợi, hoặc None nếu rỗng.

        Time Complexity: O(1) amortized.
        """
        if self.is_empty():
            return None
        item = self._data[self._head]
        self._head += 1
        # Thu gọn mảng để tránh Memory Leak khi hàng đợi chạy lâu
        if self._head > len(self._data) // 2:
            self._data = self._data[self._head:]
            self._head = 0
        return item

    def peek(self):
        """
        Xem phần tử đầu mà không xóa.

        Returns:
            Phần tử đầu, hoặc None nếu rỗng.

        Time Complexity: O(1).
        """
        return None if self.is_empty() else self._data[self._head]

    def is_empty(self) -> bool:
        """Kiểm tra Queue có rỗng không. Time Complexity: O(1)."""
        return self._head >= len(self._data)

    def size(self) -> int:
        """Trả về số phần tử còn trong Queue. Time Complexity: O(1)."""
        return len(self._data) - self._head

    def __len__(self)  -> int:  return self.size()
    def __repr__(self) -> str:  return f"Queue({self._data[self._head:]})"
