"""Định nghĩa hợp đồng chung cho các tool của Research Agent.

Mọi tool kế thừa :class:`BaseTool` và trả về :class:`ToolResult`. Nhờ đó,
vòng lặp ReAct có thể xử lý các tool theo cùng một cách mà không phụ thuộc
vào cách từng tool tìm kiếm hoặc tính toán dữ liệu.
"""

from dataclasses import dataclass


@dataclass
class ToolResult:
    """Kết quả chuẩn hóa được trả về từ một tool."""

    ok: bool
    content: str
    source: str

    def as_observation(self) -> str:
        """Chuyển kết quả thành một dòng Observation trong log ReAct."""
        status = "OK" if self.ok else "EMPTY"
        return f"[{self.source}/{status}] {self.content}"


class BaseTool:
    """Lớp cơ sở mà mọi tool cụ thể phải kế thừa."""

    name: str = "base"
    description: str = "Tool cơ sở, không dùng trực tiếp."

    def run(self, query: str) -> ToolResult:
        """Thực thi tool; lớp con phải cài đặt phương thức này."""
        raise NotImplementedError(
            f"Tool '{self.name}' chưa cài đặt phương thức run()."
        )

    def ok(self, content: str) -> ToolResult:
        """Tạo kết quả thành công và tự gắn tên tool làm nguồn."""
        return ToolResult(ok=True, content=content, source=self.name)

    def empty(self, content: str) -> ToolResult:
        """Tạo kết quả hợp lệ khi tool không tìm thấy dữ liệu."""
        return ToolResult(ok=False, content=content, source=self.name)
