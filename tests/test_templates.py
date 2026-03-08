from __future__ import annotations

from flet_splash.config import SplashConfig, SplashType
from flet_splash.templates import (
    SPLASH_MARKER,
    custom_splash_class,
    extra_imports,
    extra_pubspec_deps,
    flutter_asset_path,
    splash_bootstrap_class,
)


def _make_config(**overrides: object) -> SplashConfig:
    defaults: dict[str, object] = {
        "splash_type": SplashType.COLOR,
        "source": None,
        "background": "#000000",
        "dark_background": None,
        "min_duration_ms": 2000,
        "fade_duration_ms": 500,
        "text": None,
        "text_color": "#ffffff",
        "text_size": 14,
    }
    defaults.update(overrides)
    return SplashConfig(**defaults)  # type: ignore[arg-type]


# ---------------------------------------------------------------------------
# extra_imports
# ---------------------------------------------------------------------------


class TestExtraImports:
    def test_lottie(self) -> None:
        cfg = _make_config(splash_type=SplashType.LOTTIE, source="s.json")
        imports = extra_imports(cfg)
        assert any("lottie" in i for i in imports)

    def test_svg(self) -> None:
        cfg = _make_config(splash_type=SplashType.SVG, source="s.svg")
        imports = extra_imports(cfg)
        assert any("flutter_svg" in i for i in imports)

    def test_image_no_import(self) -> None:
        cfg = _make_config(splash_type=SplashType.IMAGE, source="s.png")
        assert extra_imports(cfg) == []

    def test_color_no_import(self) -> None:
        assert extra_imports(_make_config()) == []

    def test_custom_no_import(self) -> None:
        cfg = _make_config(splash_type=SplashType.CUSTOM, source="/tmp/s.dart")
        assert extra_imports(cfg) == []


# ---------------------------------------------------------------------------
# extra_pubspec_deps
# ---------------------------------------------------------------------------


class TestExtraPubspecDeps:
    def test_lottie(self) -> None:
        cfg = _make_config(splash_type=SplashType.LOTTIE, source="s.json")
        deps = extra_pubspec_deps(cfg)
        assert ("lottie", "^3.2.0") in deps

    def test_svg(self) -> None:
        cfg = _make_config(splash_type=SplashType.SVG, source="s.svg")
        deps = extra_pubspec_deps(cfg)
        assert ("flutter_svg", "^2.0.17") in deps

    def test_image_no_deps(self) -> None:
        cfg = _make_config(splash_type=SplashType.IMAGE, source="s.png")
        assert extra_pubspec_deps(cfg) == []

    def test_color_no_deps(self) -> None:
        assert extra_pubspec_deps(_make_config()) == []


# ---------------------------------------------------------------------------
# custom_splash_class
# ---------------------------------------------------------------------------


class TestCustomSplashClass:
    def test_contains_marker(self) -> None:
        result = custom_splash_class(_make_config())
        assert SPLASH_MARKER in result

    def test_contains_class_def(self) -> None:
        result = custom_splash_class(_make_config())
        assert "class CustomSplash extends StatelessWidget" in result

    def test_color_type_no_asset(self) -> None:
        result = custom_splash_class(_make_config())
        assert "SizedBox.shrink()" in result

    def test_lottie_type_uses_lottie_asset(self) -> None:
        cfg = _make_config(splash_type=SplashType.LOTTIE, source="assets/splash.json")
        result = custom_splash_class(cfg)
        assert "Lottie.asset('splash_assets/splash.json')" in result

    def test_image_type_uses_image_asset(self) -> None:
        cfg = _make_config(splash_type=SplashType.IMAGE, source="assets/logo.png")
        result = custom_splash_class(cfg)
        assert "Image.asset('splash_assets/logo.png')" in result

    def test_svg_type_uses_svg_picture(self) -> None:
        cfg = _make_config(splash_type=SplashType.SVG, source="assets/logo.svg")
        result = custom_splash_class(cfg)
        assert "SvgPicture.asset('splash_assets/logo.svg')" in result

    def test_background_color(self) -> None:
        cfg = _make_config(background="#abcdef")
        result = custom_splash_class(cfg)
        assert "0xFFabcdef" in result

    def test_dark_background_fallback(self) -> None:
        cfg = _make_config(background="#aaaaaa", dark_background=None)
        result = custom_splash_class(cfg)
        assert result.count("0xFFaaaaaa") == 2

    def test_dark_background_separate(self) -> None:
        cfg = _make_config(background="#aaaaaa", dark_background="#111111")
        result = custom_splash_class(cfg)
        assert "0xFFaaaaaa" in result
        assert "0xFF111111" in result

    def test_custom_type_reads_dart_file(self, tmp_path) -> None:
        dart_file = tmp_path / "my_splash.dart"
        dart_file.write_text("class CustomSplash extends StatelessWidget {}")
        cfg = _make_config(splash_type=SplashType.CUSTOM, source=str(dart_file))
        result = custom_splash_class(cfg)
        assert "class CustomSplash extends StatelessWidget" in result
        assert SPLASH_MARKER in result


# ---------------------------------------------------------------------------
# Text support
# ---------------------------------------------------------------------------


class TestTextSection:
    def test_no_text_by_default(self) -> None:
        result = custom_splash_class(_make_config())
        assert "Text(" not in result

    def test_text_rendered(self) -> None:
        cfg = _make_config(text="Loading...")
        result = custom_splash_class(cfg)
        assert "'Loading...'" in result

    def test_text_color(self) -> None:
        cfg = _make_config(text="Wait", text_color="#ff0000")
        result = custom_splash_class(cfg)
        assert "0xFFff0000" in result

    def test_text_size(self) -> None:
        cfg = _make_config(text="Wait", text_size=20)
        result = custom_splash_class(cfg)
        assert "fontSize: 20.0" in result

    def test_text_with_lottie(self) -> None:
        cfg = _make_config(
            splash_type=SplashType.LOTTIE,
            source="assets/s.json",
            text="Starting...",
        )
        result = custom_splash_class(cfg)
        assert "Lottie.asset" in result
        assert "'Starting...'" in result


# ---------------------------------------------------------------------------
# splash_bootstrap_class
# ---------------------------------------------------------------------------


class TestSplashBootstrapClass:
    def test_contains_class_def(self) -> None:
        result = splash_bootstrap_class(_make_config())
        assert "class _SplashBootstrap extends StatefulWidget" in result

    def test_min_duration_injected(self) -> None:
        cfg = _make_config(min_duration_ms=3000)
        result = splash_bootstrap_class(cfg)
        assert "milliseconds: 3000" in result

    def test_fade_duration_injected(self) -> None:
        cfg = _make_config(fade_duration_ms=800)
        result = splash_bootstrap_class(cfg)
        assert "milliseconds: 800" in result

    def test_contains_animated_opacity(self) -> None:
        result = splash_bootstrap_class(_make_config())
        assert "AnimatedOpacity" in result

    def test_contains_ignore_pointer(self) -> None:
        result = splash_bootstrap_class(_make_config())
        assert "IgnorePointer" in result


# ---------------------------------------------------------------------------
# flutter_asset_path
# ---------------------------------------------------------------------------


class TestFlutterAssetPath:
    def test_none_for_color(self) -> None:
        assert flutter_asset_path(_make_config()) is None

    def test_none_for_custom(self) -> None:
        cfg = _make_config(splash_type=SplashType.CUSTOM, source="/tmp/s.dart")
        assert flutter_asset_path(cfg) is None

    def test_extracts_filename(self) -> None:
        cfg = _make_config(source="assets/deep/splash.json")
        assert flutter_asset_path(cfg) == "splash_assets/splash.json"

    def test_simple_source(self) -> None:
        cfg = _make_config(source="logo.png")
        assert flutter_asset_path(cfg) == "splash_assets/logo.png"

    def test_svg_asset(self) -> None:
        cfg = _make_config(splash_type=SplashType.SVG, source="assets/logo.svg")
        assert flutter_asset_path(cfg) == "splash_assets/logo.svg"
