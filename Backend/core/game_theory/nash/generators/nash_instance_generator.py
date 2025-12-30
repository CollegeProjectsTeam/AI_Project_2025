from __future__ import annotations

from typing import Any, Dict

from Backend.services.logging_service import Logger
from Backend.core.game_theory.nash.generators.base_generator import NashBaseGenerator
from Backend.core.game_theory.nash.generators.pure_game_generator import NashPureGameGenerator
from Backend.core.game_theory.nash.generators.mixed_game_generator import NashMixedGameGenerator
from Backend.core.game_theory.nash.generators.combined_game_generator import NashCombinedGameGenerator

log = Logger("NashInstanceGenerator")


class NashInstanceGenerator:
    generate_pure_game = staticmethod(NashPureGameGenerator.generate)
    generate_mixed_game = staticmethod(NashMixedGameGenerator.generate)
    generate_combined_game = staticmethod(NashCombinedGameGenerator.generate)

    instance_to_text = staticmethod(NashBaseGenerator.instance_to_text)

    @staticmethod
    def generate(kind: str, **kwargs) -> Dict[str, Any]:
        k = (kind or "").strip().lower()
        if k in ("pure", "p"):
            return NashPureGameGenerator.generate(**kwargs)
        if k in ("mixed", "m"):
            return NashMixedGameGenerator.generate(**kwargs)
        if k in ("combined", "c", "both"):
            return NashCombinedGameGenerator.generate(**kwargs)

        log.error("Unknown generator kind", {"kind": kind, "kwargs": kwargs})
        raise ValueError(f"Unknown kind '{kind}'. Use pure/mixed/combined.")
