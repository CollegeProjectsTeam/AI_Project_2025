from __future__ import annotations

from Backend.services import Logger

log = Logger("KnightsTourValidator")


class KnightsTourValidator:
    @staticmethod
    def is_valid(board_size: int, start: tuple[int, int]) -> bool:
        if not isinstance(board_size, int) or board_size < 1:
            return False
        r, c = start
        if not isinstance(r, int) or not isinstance(c, int):
            return False
        if r < 0 or c < 0 or r >= board_size or c >= board_size:
            return False
        log.ok("Knights Tour instance valid", ctx={"board_size": board_size, "start": [r, c]})
        return True