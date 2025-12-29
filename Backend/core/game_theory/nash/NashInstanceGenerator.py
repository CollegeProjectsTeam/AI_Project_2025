from __future__ import annotations

from typing import Any, Dict

from Backend.services.logging_service import Logger
from Backend.core.game_theory.nash.generators.nash_instance_generator import (
    NashInstanceGenerator as _NashInstanceGenerator,
)

log = Logger("NashInstanceGenerator")


class NashInstanceGenerator:
    generate_pure_game = staticmethod(_NashInstanceGenerator.generate_pure_game)
    generate_mixed_game = staticmethod(_NashInstanceGenerator.generate_mixed_game)
    generate_combined_game = staticmethod(_NashInstanceGenerator.generate_combined_game)
    instance_to_text = staticmethod(_NashInstanceGenerator.instance_to_text)

    @staticmethod
    def generate(kind: str, **kwargs) -> Dict[str, Any]:
        return _NashInstanceGenerator.generate(kind, **kwargs)