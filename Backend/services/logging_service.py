from __future__ import annotations

import os
import sys
import json
import time
import threading
from dataclasses import dataclass
from typing import Any, Dict, Optional


@dataclass(frozen=True)
class LogConfig:
    level: str = os.getenv("LOG_LEVEL", "INFO").upper()
    use_colors: bool = os.getenv("NO_COLOR", "").strip() == ""


class Logger:
    _lock = threading.Lock()

    _RESET = "\x1b[0m"
    _BLUE = "\x1b[34m"
    _YELLOW = "\x1b[33m"
    _RED = "\x1b[31m"
    _DIM = "\x1b[2m"

    _LEVEL_ORDER = {
        "INFO": 10,
        "WARNING": 20,
        "ERROR": 30,
        "OFF": 1000,
    }

    def __init__(self, name: str, config: Optional[LogConfig] = None):
        self.name = (name or "App").strip()
        self.config = config or LogConfig()

    def info(self, msg: str, ctx: Optional[Dict[str, Any]] = None) -> None:
        self._log("INFO", msg, ctx=ctx)

    def ok(self, msg: str, ctx: Optional[Dict[str, Any]] = None) -> None:
        self._log("INFO", msg, ctx=ctx)

    def warn(self, msg: str, ctx: Optional[Dict[str, Any]] = None) -> None:
        self._log("WARNING", msg, ctx=ctx)

    def error(
        self,
        msg: str,
        ctx: Optional[Dict[str, Any]] = None,
        exc: Optional[BaseException] = None,
    ) -> None:
        if exc is not None:
            ctx = {} if ctx is None else dict(ctx)
            ctx["exc_type"] = type(exc).__name__
            ctx["exc"] = str(exc)
        self._log("ERROR", msg, ctx=ctx)

    def _enabled_for(self, level: str) -> bool:
        min_level = self._LEVEL_ORDER.get(self.config.level, 10)
        this_level = self._LEVEL_ORDER.get(level, 10)
        return this_level >= min_level

    def _color_for(self, level: str) -> str:
        if level == "ERROR":
            return self._RED
        if level == "WARNING":
            return self._YELLOW
        return self._BLUE

    def _safe_json(self, obj: Any) -> str:
        try:
            return json.dumps(obj, ensure_ascii=False, default=str)
        except Exception:
            return str(obj)

    def _timestamp(self) -> str:
        return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())

    def _log(self, level: str, msg: str, ctx: Optional[Dict[str, Any]] = None) -> None:
        level = (level or "INFO").upper()
        if not self._enabled_for(level):
            return

        ts = self._timestamp()

        if self.config.use_colors and sys.stdout.isatty():
            color = self._color_for(level)
            if ctx:
                line = (
                    f"{self._DIM}{ts}{self._RESET} {color}[{level}] {self.name}:{self._RESET} "
                    f"{msg} {self._DIM}{self._safe_json(ctx)}{self._RESET}"
                )
            else:
                line = f"{self._DIM}{ts}{self._RESET} {color}[{level}] {self.name}:{self._RESET} {msg}"
        else:
            line = f"{ts} [{level}] {self.name}: {msg}"
            if ctx:
                line += " " + self._safe_json(ctx)

        with Logger._lock:
            print(line, file=sys.stdout, flush=True)
