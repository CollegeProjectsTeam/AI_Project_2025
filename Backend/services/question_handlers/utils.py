from __future__ import annotations

import inspect
from typing import Any


def clamp_int(v: Any, lo: int, hi: int, default: int) -> int:
    try:
        x = int(v)
    except Exception:
        return default
    if x < lo:
        return lo
    if x > hi:
        return hi
    return x


def call_game_generator(fn, size: int, payoff_min: int, payoff_max: int):
    sig = inspect.signature(fn)
    params = sig.parameters
    kwargs = {}

    if "size" in params:
        kwargs["size"] = size
    if "m" in params:
        kwargs["m"] = size
    if "n" in params:
        kwargs["n"] = size
    if "rows" in params:
        kwargs["rows"] = size
    if "cols" in params:
        kwargs["cols"] = size

    if "payoff_min" in params:
        kwargs["payoff_min"] = payoff_min
    if "payoff_max" in params:
        kwargs["payoff_max"] = payoff_max

    if "min_payoff" in params:
        kwargs["min_payoff"] = payoff_min
    if "max_payoff" in params:
        kwargs["max_payoff"] = payoff_max

    try:
        return fn(**kwargs)
    except TypeError:
        if len(params) == 1:
            return fn(size)
        if len(params) >= 2:
            try:
                return fn(size, size, payoff_min=payoff_min, payoff_max=payoff_max)
            except TypeError:
                return fn(size, size)