from __future__ import annotations

from pathlib import Path

from flet_splash.config import SplashConfig, SplashType
from flet_splash.inject import check_splash_injected, inject_splash
from flet_splash.templates import SPLASH_MARKER

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

SAMPLE_MAIN_DART = """\
import 'dart:async';
import 'dart:io';

import 'package:flet/flet.dart';
import 'package:flutter/foundation.dart';
import 'package:flutter/material.dart';
import 'package:path/path.dart' as path;

const bool isProduction = bool.fromEnvironment('dart.vm.product');
const assetPath = "app/app.zip";
final hideLoadingPage = true;

String pageUrl = "";
String assetsDir = "";

void main() async {
  runApp(FutureBuilder(
      future: prepareApp(),
      builder: (BuildContext context, AsyncSnapshot snapshot) {
        if (snapshot.hasData) {
          return kIsWeb
              ? FletApp(
                  pageUrl: pageUrl,
                  assetsDir: assetsDir,
                  hideLoadingPage: hideLoadingPage,
                )
              : FutureBuilder(
                  future: runPythonApp(),
                  builder:
                      (BuildContext context, AsyncSnapshot<String?> snapshot) {
                    if (snapshot.hasData || snapshot.hasError) {
                      return MaterialApp(
                        home: ErrorScreen(
                            title: "Error running app",
                            text: snapshot.data ?? snapshot.error.toString()),
                      );
                    } else {
                      return FletApp(
                        pageUrl: pageUrl,
                        assetsDir: assetsDir,
                        hideLoadingPage: hideLoadingPage,
                      );
                    }
                  });
        } else if (snapshot.hasError) {
          return MaterialApp(
              home: ErrorScreen(
                  title: "Error starting app",
                  text: snapshot.error.toString()));
        } else {
          return const MaterialApp(home: BlankScreen());
        }
      }));
}

class ErrorScreen extends StatelessWidget {
  final String title;
  final String text;
  const ErrorScreen({super.key, required this.title, required this.text});
  @override
  Widget build(BuildContext context) {
    return Scaffold(body: Text(text));
  }
}

class BlankScreen extends StatelessWidget {
  const BlankScreen({
    super.key,
  });

  @override
  Widget build(BuildContext context) {
    return const Scaffold(
      body: SizedBox.shrink(),
    );
  }
}
"""

SAMPLE_PUBSPEC = """\
name: flet_app
description: A Flet application.

dependencies:
  flutter:
    sdk: flutter
  flet: ^0.82.0

flutter:
  uses-material-design: true
"""


def _make_config(**overrides: object) -> SplashConfig:
    defaults: dict[str, object] = {
        "splash_type": SplashType.COLOR,
        "source": None,
        "background": "#1a1a2e",
        "dark_background": "#0a0a1e",
        "min_duration_ms": 2000,
        "fade_duration_ms": 500,
        "text": None,
        "text_color": "#ffffff",
        "text_size": 14,
    }
    defaults.update(overrides)
    return SplashConfig(**defaults)  # type: ignore[arg-type]


def _create_flutter_project(tmp_path: Path) -> Path:
    flutter_dir = tmp_path / "build" / "flutter"
    (flutter_dir / "lib").mkdir(parents=True)
    (flutter_dir / "lib" / "main.dart").write_text(SAMPLE_MAIN_DART)
    (flutter_dir / "pubspec.yaml").write_text(SAMPLE_PUBSPEC)
    return flutter_dir


# ---------------------------------------------------------------------------
# Tests: check_splash_injected
# ---------------------------------------------------------------------------


class TestCheckSplashInjected:
    def test_false_when_no_flutter_dir(self, tmp_path: Path) -> None:
        assert check_splash_injected(tmp_path / "nonexistent") is False

    def test_false_when_no_marker(self, tmp_path: Path) -> None:
        flutter_dir = _create_flutter_project(tmp_path)
        assert check_splash_injected(flutter_dir) is False

    def test_true_when_marker_present(self, tmp_path: Path) -> None:
        flutter_dir = _create_flutter_project(tmp_path)
        main_dart = flutter_dir / "lib" / "main.dart"
        main_dart.write_text(SPLASH_MARKER + "\n" + main_dart.read_text())
        assert check_splash_injected(flutter_dir) is True


# ---------------------------------------------------------------------------
# Tests: inject_splash — main.dart patching
# ---------------------------------------------------------------------------


class TestInjectMainDart:
    def test_replaces_blank_screen_class(self, tmp_path: Path) -> None:
        flutter_dir = _create_flutter_project(tmp_path)
        inject_splash(flutter_dir, _make_config(), tmp_path)

        content = (flutter_dir / "lib" / "main.dart").read_text()
        assert "class BlankScreen" not in content
        assert "class CustomSplash extends StatelessWidget" in content

    def test_replaces_blank_screen_refs(self, tmp_path: Path) -> None:
        flutter_dir = _create_flutter_project(tmp_path)
        inject_splash(flutter_dir, _make_config(), tmp_path)

        content = (flutter_dir / "lib" / "main.dart").read_text()
        assert "BlankScreen()" not in content
        assert "CustomSplash()" in content

    def test_wraps_run_app_with_bootstrap(self, tmp_path: Path) -> None:
        flutter_dir = _create_flutter_project(tmp_path)
        inject_splash(flutter_dir, _make_config(), tmp_path)

        content = (flutter_dir / "lib" / "main.dart").read_text()
        assert "_SplashBootstrap(child: FutureBuilder(" in content
        assert "})));" in content

    def test_appends_bootstrap_class(self, tmp_path: Path) -> None:
        flutter_dir = _create_flutter_project(tmp_path)
        inject_splash(flutter_dir, _make_config(), tmp_path)

        content = (flutter_dir / "lib" / "main.dart").read_text()
        assert "class _SplashBootstrap extends StatefulWidget" in content
        assert "class _SplashBootstrapState extends State<_SplashBootstrap>" in content

    def test_adds_splash_marker(self, tmp_path: Path) -> None:
        flutter_dir = _create_flutter_project(tmp_path)
        inject_splash(flutter_dir, _make_config(), tmp_path)

        content = (flutter_dir / "lib" / "main.dart").read_text()
        assert SPLASH_MARKER in content

    def test_idempotent(self, tmp_path: Path) -> None:
        flutter_dir = _create_flutter_project(tmp_path)
        cfg = _make_config()
        inject_splash(flutter_dir, cfg, tmp_path)
        first_pass = (flutter_dir / "lib" / "main.dart").read_text()

        inject_splash(flutter_dir, cfg, tmp_path)
        second_pass = (flutter_dir / "lib" / "main.dart").read_text()

        assert first_pass == second_pass

    def test_background_colors_injected(self, tmp_path: Path) -> None:
        flutter_dir = _create_flutter_project(tmp_path)
        cfg = _make_config(background="#abcdef", dark_background="#112233")
        inject_splash(flutter_dir, cfg, tmp_path)

        content = (flutter_dir / "lib" / "main.dart").read_text()
        assert "0xFFabcdef" in content
        assert "0xFF112233" in content

    def test_timing_values_injected(self, tmp_path: Path) -> None:
        flutter_dir = _create_flutter_project(tmp_path)
        cfg = _make_config(min_duration_ms=3500, fade_duration_ms=750)
        inject_splash(flutter_dir, cfg, tmp_path)

        content = (flutter_dir / "lib" / "main.dart").read_text()
        assert "milliseconds: 3500" in content
        assert "milliseconds: 750" in content

    def test_preserves_error_screen(self, tmp_path: Path) -> None:
        flutter_dir = _create_flutter_project(tmp_path)
        inject_splash(flutter_dir, _make_config(), tmp_path)

        content = (flutter_dir / "lib" / "main.dart").read_text()
        assert "class ErrorScreen extends StatelessWidget" in content

    def test_adds_app_ready_notifier(self, tmp_path: Path) -> None:
        flutter_dir = _create_flutter_project(tmp_path)
        inject_splash(flutter_dir, _make_config(), tmp_path)

        content = (flutter_dir / "lib" / "main.dart").read_text()
        assert "ValueNotifier<bool> _appReady" in content

    def test_injects_ready_signal_in_future_builder(self, tmp_path: Path) -> None:
        flutter_dir = _create_flutter_project(tmp_path)
        inject_splash(flutter_dir, _make_config(), tmp_path)

        content = (flutter_dir / "lib" / "main.dart").read_text()
        assert "_appReady.value = true;" in content

    def test_bootstrap_listens_to_app_ready(self, tmp_path: Path) -> None:
        flutter_dir = _create_flutter_project(tmp_path)
        inject_splash(flutter_dir, _make_config(), tmp_path)

        content = (flutter_dir / "lib" / "main.dart").read_text()
        assert "_appReady.addListener(_maybeHide)" in content
        assert "_timerDone && _appReady.value" in content

    def test_bootstrap_removes_listener_on_dispose(self, tmp_path: Path) -> None:
        flutter_dir = _create_flutter_project(tmp_path)
        inject_splash(flutter_dir, _make_config(), tmp_path)

        content = (flutter_dir / "lib" / "main.dart").read_text()
        assert "_appReady.removeListener(_maybeHide)" in content


# ---------------------------------------------------------------------------
# Tests: inject_splash — lottie support
# ---------------------------------------------------------------------------


class TestInjectLottie:
    def test_adds_lottie_import(self, tmp_path: Path) -> None:
        flutter_dir = _create_flutter_project(tmp_path)
        (tmp_path / "splash.json").write_text("{}")
        cfg = _make_config(splash_type=SplashType.LOTTIE, source="splash.json")
        inject_splash(flutter_dir, cfg, tmp_path)

        content = (flutter_dir / "lib" / "main.dart").read_text()
        assert "package:lottie/lottie.dart" in content

    def test_adds_lottie_dependency(self, tmp_path: Path) -> None:
        flutter_dir = _create_flutter_project(tmp_path)
        (tmp_path / "splash.json").write_text("{}")
        cfg = _make_config(splash_type=SplashType.LOTTIE, source="splash.json")
        inject_splash(flutter_dir, cfg, tmp_path)

        pubspec = (flutter_dir / "pubspec.yaml").read_text()
        assert "lottie:" in pubspec

    def test_no_lottie_for_image(self, tmp_path: Path) -> None:
        flutter_dir = _create_flutter_project(tmp_path)
        (tmp_path / "logo.png").write_bytes(b"PNG")
        cfg = _make_config(splash_type=SplashType.IMAGE, source="logo.png")
        inject_splash(flutter_dir, cfg, tmp_path)

        content = (flutter_dir / "lib" / "main.dart").read_text()
        assert "lottie" not in content.lower()

    def test_no_lottie_for_color(self, tmp_path: Path) -> None:
        flutter_dir = _create_flutter_project(tmp_path)
        inject_splash(flutter_dir, _make_config(), tmp_path)

        pubspec = (flutter_dir / "pubspec.yaml").read_text()
        assert "lottie" not in pubspec


# ---------------------------------------------------------------------------
# Tests: inject_splash — pubspec.yaml patching
# ---------------------------------------------------------------------------


class TestInjectPubspec:
    def test_adds_asset_to_existing_flutter_section(self, tmp_path: Path) -> None:
        flutter_dir = _create_flutter_project(tmp_path)
        (tmp_path / "splash.json").write_text("{}")
        cfg = _make_config(splash_type=SplashType.LOTTIE, source="splash.json")
        inject_splash(flutter_dir, cfg, tmp_path)

        pubspec = (flutter_dir / "pubspec.yaml").read_text()
        assert "splash_assets/splash.json" in pubspec

    def test_no_asset_for_color(self, tmp_path: Path) -> None:
        flutter_dir = _create_flutter_project(tmp_path)
        inject_splash(flutter_dir, _make_config(), tmp_path)

        pubspec = (flutter_dir / "pubspec.yaml").read_text()
        assert "splash_assets" not in pubspec

    def test_adds_assets_section_if_missing(self, tmp_path: Path) -> None:
        flutter_dir = _create_flutter_project(tmp_path)
        # pubspec without assets section
        pubspec_content = """\
name: test_app
dependencies:
  flutter:
    sdk: flutter

flutter:
  uses-material-design: true
"""
        (flutter_dir / "pubspec.yaml").write_text(pubspec_content)
        (tmp_path / "logo.png").write_bytes(b"PNG")
        cfg = _make_config(splash_type=SplashType.IMAGE, source="logo.png")
        inject_splash(flutter_dir, cfg, tmp_path)

        pubspec = (flutter_dir / "pubspec.yaml").read_text()
        assert "assets:" in pubspec
        assert "splash_assets/logo.png" in pubspec

    def test_preserves_existing_assets(self, tmp_path: Path) -> None:
        """Splash asset must be appended after existing assets, not break indentation."""
        flutter_dir = _create_flutter_project(tmp_path)
        pubspec_content = """\
name: test_app
dependencies:
  flet: 0.82.0
  flutter:
    sdk: flutter
flutter:
  uses-material-design: true
  assets:
    - app/app.zip
    - app/app.zip.hash
"""
        (flutter_dir / "pubspec.yaml").write_text(pubspec_content)
        (tmp_path / "logo.svg").write_text("<svg/>")
        cfg = _make_config(splash_type=SplashType.SVG, source="logo.svg")
        inject_splash(flutter_dir, cfg, tmp_path)

        pubspec = (flutter_dir / "pubspec.yaml").read_text()
        assert "    - app/app.zip\n" in pubspec
        assert "    - app/app.zip.hash\n" in pubspec
        assert "    - splash_assets/logo.svg\n" in pubspec
        # Verify the YAML is valid by checking no line starts at wrong indent
        import yaml

        parsed = yaml.safe_load(pubspec)
        assert "splash_assets/logo.svg" in parsed["flutter"]["assets"]
        assert "app/app.zip" in parsed["flutter"]["assets"]


# ---------------------------------------------------------------------------
# Tests: inject_splash — asset copy
# ---------------------------------------------------------------------------


class TestInjectAssets:
    def test_copies_asset_file(self, tmp_path: Path) -> None:
        flutter_dir = _create_flutter_project(tmp_path)
        (tmp_path / "splash.json").write_text('{"animation": true}')
        cfg = _make_config(splash_type=SplashType.LOTTIE, source="splash.json")
        inject_splash(flutter_dir, cfg, tmp_path)

        copied = flutter_dir / "splash_assets" / "splash.json"
        assert copied.exists()
        assert copied.read_text() == '{"animation": true}'

    def test_no_copy_for_color(self, tmp_path: Path) -> None:
        flutter_dir = _create_flutter_project(tmp_path)
        inject_splash(flutter_dir, _make_config(), tmp_path)

        assert not (flutter_dir / "splash_assets").exists()

    def test_creates_splash_assets_dir(self, tmp_path: Path) -> None:
        flutter_dir = _create_flutter_project(tmp_path)
        (tmp_path / "logo.png").write_bytes(b"PNG")
        cfg = _make_config(splash_type=SplashType.IMAGE, source="logo.png")
        inject_splash(flutter_dir, cfg, tmp_path)

        assert (flutter_dir / "splash_assets").is_dir()


# ---------------------------------------------------------------------------
# Tests: inject_splash — SVG support
# ---------------------------------------------------------------------------


class TestInjectSvg:
    def test_adds_svg_import(self, tmp_path: Path) -> None:
        flutter_dir = _create_flutter_project(tmp_path)
        (tmp_path / "logo.svg").write_text("<svg/>")
        cfg = _make_config(splash_type=SplashType.SVG, source="logo.svg")
        inject_splash(flutter_dir, cfg, tmp_path)

        content = (flutter_dir / "lib" / "main.dart").read_text()
        assert "package:flutter_svg/flutter_svg.dart" in content

    def test_adds_flutter_svg_dependency(self, tmp_path: Path) -> None:
        flutter_dir = _create_flutter_project(tmp_path)
        (tmp_path / "logo.svg").write_text("<svg/>")
        cfg = _make_config(splash_type=SplashType.SVG, source="logo.svg")
        inject_splash(flutter_dir, cfg, tmp_path)

        pubspec = (flutter_dir / "pubspec.yaml").read_text()
        assert "flutter_svg:" in pubspec

    def test_svg_asset_copied(self, tmp_path: Path) -> None:
        flutter_dir = _create_flutter_project(tmp_path)
        (tmp_path / "logo.svg").write_text("<svg/>")
        cfg = _make_config(splash_type=SplashType.SVG, source="logo.svg")
        inject_splash(flutter_dir, cfg, tmp_path)

        assert (flutter_dir / "splash_assets" / "logo.svg").exists()

    def test_svg_picture_asset_in_dart(self, tmp_path: Path) -> None:
        flutter_dir = _create_flutter_project(tmp_path)
        (tmp_path / "logo.svg").write_text("<svg/>")
        cfg = _make_config(splash_type=SplashType.SVG, source="logo.svg")
        inject_splash(flutter_dir, cfg, tmp_path)

        content = (flutter_dir / "lib" / "main.dart").read_text()
        assert "SvgPicture.asset('splash_assets/logo.svg')" in content


# ---------------------------------------------------------------------------
# Tests: inject_splash — custom .dart support
# ---------------------------------------------------------------------------


class TestInjectCustom:
    def test_custom_dart_injected(self, tmp_path: Path) -> None:
        flutter_dir = _create_flutter_project(tmp_path)
        dart_file = tmp_path / "my_splash.dart"
        dart_file.write_text("class CustomSplash extends StatelessWidget {}")
        cfg = _make_config(splash_type=SplashType.CUSTOM, source="my_splash.dart")
        inject_splash(flutter_dir, cfg, tmp_path)

        content = (flutter_dir / "lib" / "main.dart").read_text()
        assert "class CustomSplash extends StatelessWidget" in content
        assert SPLASH_MARKER in content

    def test_custom_no_asset_copy(self, tmp_path: Path) -> None:
        flutter_dir = _create_flutter_project(tmp_path)
        dart_file = tmp_path / "my_splash.dart"
        dart_file.write_text("class CustomSplash extends StatelessWidget {}")
        cfg = _make_config(splash_type=SplashType.CUSTOM, source="my_splash.dart")
        inject_splash(flutter_dir, cfg, tmp_path)

        assert not (flutter_dir / "splash_assets").exists()

    def test_custom_no_extra_deps(self, tmp_path: Path) -> None:
        flutter_dir = _create_flutter_project(tmp_path)
        dart_file = tmp_path / "my_splash.dart"
        dart_file.write_text("class CustomSplash extends StatelessWidget {}")
        cfg = _make_config(splash_type=SplashType.CUSTOM, source="my_splash.dart")
        inject_splash(flutter_dir, cfg, tmp_path)

        pubspec = (flutter_dir / "pubspec.yaml").read_text()
        assert "lottie:" not in pubspec
        assert "flutter_svg:" not in pubspec


# ---------------------------------------------------------------------------
# Tests: inject_splash — text support
# ---------------------------------------------------------------------------


class TestInjectText:
    def test_text_rendered_in_dart(self, tmp_path: Path) -> None:
        flutter_dir = _create_flutter_project(tmp_path)
        cfg = _make_config(text="Loading...")
        inject_splash(flutter_dir, cfg, tmp_path)

        content = (flutter_dir / "lib" / "main.dart").read_text()
        assert "'Loading...'" in content

    def test_text_color_injected(self, tmp_path: Path) -> None:
        flutter_dir = _create_flutter_project(tmp_path)
        cfg = _make_config(text="Wait", text_color="#ff0000")
        inject_splash(flutter_dir, cfg, tmp_path)

        content = (flutter_dir / "lib" / "main.dart").read_text()
        assert "0xFFff0000" in content

    def test_text_size_injected(self, tmp_path: Path) -> None:
        flutter_dir = _create_flutter_project(tmp_path)
        cfg = _make_config(text="Wait", text_size=20)
        inject_splash(flutter_dir, cfg, tmp_path)

        content = (flutter_dir / "lib" / "main.dart").read_text()
        assert "fontSize: 20.0" in content

    def test_no_text_widget_in_splash_by_default(self, tmp_path: Path) -> None:
        flutter_dir = _create_flutter_project(tmp_path)
        inject_splash(flutter_dir, _make_config(), tmp_path)

        content = (flutter_dir / "lib" / "main.dart").read_text()
        # Extract only the CustomSplash class to check for Text widget
        marker = "class CustomSplash extends StatelessWidget"
        splash_start = content.find(marker)
        splash_end = content.find("class _SplashBootstrap")
        splash_section = content[splash_start:splash_end]
        assert "Text(" not in splash_section
