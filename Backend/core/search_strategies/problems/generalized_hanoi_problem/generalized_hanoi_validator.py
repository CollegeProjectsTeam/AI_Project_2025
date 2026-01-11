from __future__ import annotations

from Backend.services import Logger

log = Logger("GenHanoiValidator")


class GeneralizedHanoiValidator:
    @staticmethod
    def is_valid(disks: int, pegs: int) -> bool:
        if not isinstance(disks, int) or disks < 1:
            return False
        if not isinstance(pegs, int) or pegs < 3:
            return False
        log.ok("Generalized Hanoi instance valid", ctx={"disks": disks, "pegs": pegs})
        return True