from __future__ import annotations

import argparse
import sys
from dataclasses import dataclass
from enum import Enum
from pathlib import Path

if sys.version_info >= (3, 11):
    import tomllib
else:
    import tomli as tomllib  # type: ignore[no-redefine]


class SplashType(Enum):
    LOTTIE = "lottie"
    IMAGE = "image"
    SVG = "svg"
    COLOR = "color"
    CUSTOM = "custom"


@dataclass(frozen=True)
class SplashConfig:
    splash_type: SplashType
    source: str | None
    background: str
    dark_background: str | None
    min_duration_ms: int
    fade_duration_ms: int
    text: str | None
    text_color: str
    text_size: int


_DEFAULTS: dict[str, object] = {
    "type": "image",
    "source": None,
    "background": "#000000",
    "dark_background": None,
    "min_duration": 5.0,
    "fade_duration": 0.5,
    "text": None,
    "text_color": "#ffffff",
    "text_size": 14,
}

_TYPES_REQUIRING_SOURCE = {SplashType.LOTTIE, SplashType.IMAGE, SplashType.SVG, SplashType.CUSTOM}


def load_config(cli_args: argparse.Namespace, project_root: Path) -> SplashConfig:
    """Build SplashConfig by merging pyproject.toml defaults with CLI overrides."""
    file_cfg = _read_pyproject(project_root)

    def _resolve(key: str) -> object:
        cli_val = getattr(cli_args, key, None)
        if cli_val is not None:
            return cli_val
        return file_cfg.get(key, _DEFAULTS[key])

    splash_type = SplashType(str(_resolve("type")))
    source = _resolve("source")
    source_str = str(source) if source is not None else None

    if splash_type in _TYPES_REQUIRING_SOURCE and source_str is None:
        print(
            f"ERROR: splash type '{splash_type.value}' requires 'source' "
            f"(set in [tool.flet.splash] or via --source).",
            file=sys.stderr,
        )
        sys.exit(1)

    if source_str and not (project_root / source_str).exists():
        print(
            f"ERROR: source file not found: {project_root / source_str}",
            file=sys.stderr,
        )
        sys.exit(1)

    if splash_type == SplashType.CUSTOM and source_str and not source_str.endswith(".dart"):
        print(
            "ERROR: custom splash type requires a .dart file as source.",
            file=sys.stderr,
        )
        sys.exit(1)

    min_dur = float(_resolve("min_duration"))  # type: ignore[arg-type]
    fade_dur = float(_resolve("fade_duration"))  # type: ignore[arg-type]

    bg = str(_resolve("background"))
    dark_bg_raw = _resolve("dark_background")
    dark_bg = str(dark_bg_raw) if dark_bg_raw is not None else None

    text_raw = _resolve("text")
    text = str(text_raw) if text_raw is not None else None
    text_color = str(_resolve("text_color"))
    text_size = int(_resolve("text_size"))  # type: ignore[arg-type]

    return SplashConfig(
        splash_type=splash_type,
        source=source_str,
        background=bg,
        dark_background=dark_bg,
        min_duration_ms=int(min_dur * 1000),
        fade_duration_ms=int(fade_dur * 1000),
        text=text,
        text_color=text_color,
        text_size=text_size,
    )


def hex_to_dart_color(hex_str: str) -> str:
    """Convert '#1a1a2e' or '#FF1a1a2e' to Dart Color literal '0xFF1a1a2e'."""
    h = hex_str.lstrip("#")
    if len(h) == 6:
        return f"0xFF{h}"
    if len(h) == 8:
        return f"0x{h}"
    return f"0xFF{h}"


def _read_pyproject(project_root: Path) -> dict[str, object]:
    pyproject_path = project_root / "pyproject.toml"
    if not pyproject_path.exists():
        return {}

    with open(pyproject_path, "rb") as f:
        data = tomllib.load(f)

    return data.get("tool", {}).get("flet", {}).get("splash", {})
