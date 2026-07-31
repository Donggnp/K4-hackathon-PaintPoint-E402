"""System prompt cho việc sinh nội dung.

    repo.py     — GIAI ĐOẠN 1: prompt sinh repo code
    tutorial.py — ví dụ vàng cho GIAI ĐOẠN 2 (prompt nằm ở tutorial_builder.py,
                  vì tutorial sinh theo từng phase song song)
"""

from .repo import SYSTEM_PROMPT_REPO
from .tutorial import GOLDEN_PHASE_EXAMPLE

__all__ = ['SYSTEM_PROMPT_REPO', 'GOLDEN_PHASE_EXAMPLE']
