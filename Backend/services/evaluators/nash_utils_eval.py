from __future__ import annotations

import re
from typing import List


def parse_floats(s: str) -> List[float]:
    return [float(x) for x in re.findall(r"[-+]?\d*\.?\d+", s or "")]


def norm_prob_vec(v: List[float]) -> List[float] | None:
    if not v:
        return None
    s = sum(v)
    if s <= 0:
        return None
    return [x / s for x in v]


def vec_close(a: List[float] | None, b: List[float] | None, tol: float) -> bool:
    if a is None or b is None or len(a) != len(b):
        return False
    return all(abs(a[i] - b[i]) <= tol for i in range(len(a)))
