"""CLI entry point for flet-splash."""

from __future__ import annotations

import argparse
from pathlib import Path

from flet_splash import ui
from flet_splash.build import ALL_PLATFORMS, build
from flet_splash.config import load_config


def app() -> None:
    parser = argparse.ArgumentParser(
        prog="flet-splash",
        description="Build Flet apps with a custom splash screen",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=_EPILOG,
    )
    parser.add_argument(
        "platform",
        choices=ALL_PLATFORMS,
        help="Target platform (apk, aab, ipa, web, macos, linux, windows)",
    )
    parser.add_argument(
        "--type", dest="type", choices=["lottie", "image", "svg", "color", "custom"]
    )
    parser.add_argument("--source", dest="source")
    parser.add_argument("--background", dest="background")
    parser.add_argument("--dark-background", dest="dark_background")
    parser.add_argument("--min-duration", dest="min_duration", type=float)
    parser.add_argument("--fade-duration", dest="fade_duration", type=float)
    parser.add_argument("--text", dest="text")
    parser.add_argument("--text-color", dest="text_color")
    parser.add_argument("--text-size", dest="text_size", type=int)
    parser.add_argument("--clean", action="store_true", help="Clean build directory first")

    args, extra = parser.parse_known_args()

    ui.header_panel("Custom startup screen builder")

    project_root = _find_project_root()
    config = load_config(args, project_root)

    rows = [
        ("Project root", str(project_root)),
        ("Platform", args.platform.upper()),
        ("Splash type", config.splash_type.value),
        ("Source", config.source or "-"),
        ("Background", config.background),
        ("Dark background", config.dark_background or "(same)"),
        ("Min duration", f"{config.min_duration_ms}ms"),
        ("Fade duration", f"{config.fade_duration_ms}ms"),
    ]
    if config.text:
        rows.append(("Text", config.text))
        rows.append(("Text color", config.text_color))
        rows.append(("Text size", f"{config.text_size}px"))

    ui.config_table(rows)

    build(config, args.platform, extra, project_root, clean=args.clean)


def _find_project_root() -> Path:
    """Walk up from cwd to find the directory containing pyproject.toml."""
    current = Path.cwd()

    while current != current.parent:
        if (current / "pyproject.toml").exists():
            return current
        current = current.parent

    return Path.cwd()


_EPILOG = """\
Examples:
    flet-splash apk
    flet-splash aab --split-per-abi
    flet-splash ipa
    flet-splash web
    flet-splash apk --type lottie --source assets/splash.json
    flet-splash apk --background "#1a1a2e" --min-duration 3.0

    All extra options are passed directly to flet build:
    flet-splash apk -v --org com.example --build-version 1.0.0

Configuration via pyproject.toml:
    [tool.flet.splash]
    type = "lottie"              # lottie | image | svg | color | custom
    source = "assets/splash.json"
    background = "#1a1a2e"
    dark_background = "#0a0a1e"
    min_duration = 2.0
    fade_duration = 0.5
    text = "Loading..."          # optional text below the splash
    text_color = "#ffffff"
    text_size = 14
"""
