from __future__ import annotations

import argparse
from pathlib import Path

import pytest

from flet_splash.config import SplashConfig, SplashType, hex_to_dart_color, load_config


class TestHexToDartColor:
    def test_six_digit_hex(self) -> None:
        assert hex_to_dart_color("#1a1a2e") == "0xFF1a1a2e"

    def test_six_digit_no_hash(self) -> None:
        assert hex_to_dart_color("ff00cc") == "0xFFff00cc"

    def test_eight_digit_hex(self) -> None:
        assert hex_to_dart_color("#80ffffff") == "0x80ffffff"

    def test_eight_digit_no_hash(self) -> None:
        assert hex_to_dart_color("CC1a1a2e") == "0xCC1a1a2e"


class TestSplashType:
    def test_lottie(self) -> None:
        assert SplashType("lottie") is SplashType.LOTTIE

    def test_image(self) -> None:
        assert SplashType("image") is SplashType.IMAGE

    def test_color(self) -> None:
        assert SplashType("color") is SplashType.COLOR

    def test_svg(self) -> None:
        assert SplashType("svg") is SplashType.SVG

    def test_custom(self) -> None:
        assert SplashType("custom") is SplashType.CUSTOM

    def test_invalid_raises(self) -> None:
        with pytest.raises(ValueError):
            SplashType("unknown")


class TestSplashConfig:
    def test_frozen(self) -> None:
        cfg = SplashConfig(
            splash_type=SplashType.COLOR,
            source=None,
            background="#000000",
            dark_background=None,
            min_duration_ms=2000,
            fade_duration_ms=500,
            text=None,
            text_color="#ffffff",
            text_size=14,
        )
        with pytest.raises(AttributeError):
            cfg.background = "#ffffff"  # type: ignore[misc]


class TestLoadConfig:
    def _make_args(self, **overrides: object) -> argparse.Namespace:
        defaults: dict[str, object] = {
            "type": None,
            "source": None,
            "background": None,
            "dark_background": None,
            "min_duration": None,
            "fade_duration": None,
            "text": None,
            "text_color": None,
            "text_size": None,
        }
        defaults.update(overrides)
        return argparse.Namespace(**defaults)

    def test_defaults_color_type(self, tmp_path: Path) -> None:
        (tmp_path / "pyproject.toml").write_text("[project]\nname = 'test'\n")
        cfg = load_config(self._make_args(type="color"), tmp_path)

        assert cfg.splash_type is SplashType.COLOR
        assert cfg.source is None
        assert cfg.background == "#000000"
        assert cfg.dark_background is None
        assert cfg.min_duration_ms == 5000
        assert cfg.fade_duration_ms == 500

    def test_reads_pyproject(self, tmp_path: Path) -> None:
        toml = """\
[tool.flet.splash]
type = "color"
background = "#abcdef"
min_duration = 3.0
fade_duration = 1.0
"""
        (tmp_path / "pyproject.toml").write_text(toml)
        cfg = load_config(self._make_args(), tmp_path)

        assert cfg.splash_type is SplashType.COLOR
        assert cfg.background == "#abcdef"
        assert cfg.min_duration_ms == 3000
        assert cfg.fade_duration_ms == 1000

    def test_cli_overrides_pyproject(self, tmp_path: Path) -> None:
        toml = """\
[tool.flet.splash]
type = "color"
background = "#111111"
"""
        (tmp_path / "pyproject.toml").write_text(toml)
        cfg = load_config(self._make_args(background="#222222"), tmp_path)

        assert cfg.background == "#222222"

    def test_image_requires_source(self, tmp_path: Path) -> None:
        (tmp_path / "pyproject.toml").write_text("[project]\nname = 'test'\n")
        with pytest.raises(SystemExit):
            load_config(self._make_args(type="image"), tmp_path)

    def test_lottie_requires_source(self, tmp_path: Path) -> None:
        (tmp_path / "pyproject.toml").write_text("[project]\nname = 'test'\n")
        with pytest.raises(SystemExit):
            load_config(self._make_args(type="lottie"), tmp_path)

    def test_missing_source_file_exits(self, tmp_path: Path) -> None:
        (tmp_path / "pyproject.toml").write_text("[project]\nname = 'test'\n")
        with pytest.raises(SystemExit):
            load_config(self._make_args(type="image", source="no_such.png"), tmp_path)

    def test_image_with_valid_source(self, tmp_path: Path) -> None:
        (tmp_path / "pyproject.toml").write_text("[project]\nname = 'test'\n")
        (tmp_path / "splash.png").write_bytes(b"PNG")
        cfg = load_config(self._make_args(type="image", source="splash.png"), tmp_path)

        assert cfg.splash_type is SplashType.IMAGE
        assert cfg.source == "splash.png"

    def test_no_pyproject_uses_defaults(self, tmp_path: Path) -> None:
        cfg = load_config(self._make_args(type="color"), tmp_path)

        assert cfg.splash_type is SplashType.COLOR
        assert cfg.background == "#000000"

    def test_dark_background(self, tmp_path: Path) -> None:
        toml = """\
[tool.flet.splash]
type = "color"
background = "#111111"
dark_background = "#222222"
"""
        (tmp_path / "pyproject.toml").write_text(toml)
        cfg = load_config(self._make_args(), tmp_path)

        assert cfg.dark_background == "#222222"

    def test_svg_requires_source(self, tmp_path: Path) -> None:
        (tmp_path / "pyproject.toml").write_text("[project]\nname = 'test'\n")
        with pytest.raises(SystemExit):
            load_config(self._make_args(type="svg"), tmp_path)

    def test_custom_requires_source(self, tmp_path: Path) -> None:
        (tmp_path / "pyproject.toml").write_text("[project]\nname = 'test'\n")
        with pytest.raises(SystemExit):
            load_config(self._make_args(type="custom"), tmp_path)

    def test_custom_requires_dart_extension(self, tmp_path: Path) -> None:
        (tmp_path / "pyproject.toml").write_text("[project]\nname = 'test'\n")
        (tmp_path / "splash.txt").write_text("not dart")
        with pytest.raises(SystemExit):
            load_config(self._make_args(type="custom", source="splash.txt"), tmp_path)

    def test_custom_with_dart_file(self, tmp_path: Path) -> None:
        (tmp_path / "pyproject.toml").write_text("[project]\nname = 'test'\n")
        (tmp_path / "splash.dart").write_text("class CustomSplash {}")
        cfg = load_config(self._make_args(type="custom", source="splash.dart"), tmp_path)
        assert cfg.splash_type is SplashType.CUSTOM
        assert cfg.source == "splash.dart"

    def test_text_defaults(self, tmp_path: Path) -> None:
        (tmp_path / "pyproject.toml").write_text("[project]\nname = 'test'\n")
        cfg = load_config(self._make_args(type="color"), tmp_path)
        assert cfg.text is None
        assert cfg.text_color == "#ffffff"
        assert cfg.text_size == 14

    def test_text_from_pyproject(self, tmp_path: Path) -> None:
        toml = """\
[tool.flet.splash]
type = "color"
text = "Loading..."
text_color = "#aabbcc"
text_size = 18
"""
        (tmp_path / "pyproject.toml").write_text(toml)
        cfg = load_config(self._make_args(), tmp_path)
        assert cfg.text == "Loading..."
        assert cfg.text_color == "#aabbcc"
        assert cfg.text_size == 18

    def test_text_cli_override(self, tmp_path: Path) -> None:
        (tmp_path / "pyproject.toml").write_text("[project]\nname = 'test'\n")
        cfg = load_config(self._make_args(type="color", text="Please wait"), tmp_path)
        assert cfg.text == "Please wait"
