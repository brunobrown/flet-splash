from __future__ import annotations

from pathlib import Path

from flet_splash.config import SplashConfig, SplashType, hex_to_dart_color

SPLASH_MARKER = "// [flet-splash] Custom splash screen"

_LOTTIE_IMPORT = "import 'package:lottie/lottie.dart';"
_SVG_IMPORT = "import 'package:flutter_svg/flutter_svg.dart';"

APP_READY_NOTIFIER = "final ValueNotifier<bool> _appReady = ValueNotifier(false);"

_CUSTOM_SPLASH_TEMPLATE = """\
// [flet-splash] Custom splash screen
class CustomSplash extends StatelessWidget {
  const CustomSplash({super.key});

  @override
  Widget build(BuildContext context) {
    var brightness = WidgetsBinding.instance.platformDispatcher.platformBrightness;
    return ColoredBox(
      color: brightness == Brightness.dark
          ? const Color(__DARK_BG__)
          : const Color(__BG__),
      child: Center(
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            __BODY__,
__TEXT_SECTION__
          ],
        ),
      ),
    );
  }
}
"""

_TEXT_WIDGET_TEMPLATE = """\
            const SizedBox(height: 16),
            Text(
              '__TEXT__',
              style: TextStyle(
                color: Color(__TEXT_COLOR__),
                fontSize: __TEXT_SIZE__,
                decoration: TextDecoration.none,
                fontWeight: FontWeight.normal,
              ),
            ),"""

_SPLASH_BOOTSTRAP_TEMPLATE = """\
class _SplashBootstrap extends StatefulWidget {
  final Widget child;
  const _SplashBootstrap({required this.child});

  @override
  State<_SplashBootstrap> createState() => _SplashBootstrapState();
}

class _SplashBootstrapState extends State<_SplashBootstrap> {
  bool _showSplash = true;
  bool _timerDone = false;

  @override
  void initState() {
    super.initState();
    Future.delayed(const Duration(milliseconds: __MIN_DURATION__), () {
      _timerDone = true;
      _maybeHide();
    });
    _appReady.addListener(_maybeHide);
  }

  void _maybeHide() {
    if (_timerDone && _appReady.value && mounted) {
      setState(() => _showSplash = false);
    }
  }

  @override
  void dispose() {
    _appReady.removeListener(_maybeHide);
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Directionality(
      textDirection: TextDirection.ltr,
      child: Stack(
        children: [
          widget.child,
          IgnorePointer(
            ignoring: !_showSplash,
            child: AnimatedOpacity(
              opacity: _showSplash ? 1.0 : 0.0,
              duration: const Duration(milliseconds: __FADE_DURATION__),
              child: const CustomSplash(),
            ),
          ),
        ],
      ),
    );
  }
}
"""


def extra_imports(config: SplashConfig) -> list[str]:
    """Return the list of Dart import lines needed for the splash type."""
    imports: list[str] = []
    if config.splash_type == SplashType.LOTTIE:
        imports.append(_LOTTIE_IMPORT)
    elif config.splash_type == SplashType.SVG:
        imports.append(_SVG_IMPORT)
    return imports


def extra_pubspec_deps(config: SplashConfig) -> list[tuple[str, str]]:
    """Return (package_name, version) pairs to add to pubspec.yaml."""
    if config.splash_type == SplashType.LOTTIE:
        return [("lottie", "^3.2.0")]
    if config.splash_type == SplashType.SVG:
        return [("flutter_svg", "^2.0.17")]
    return []


def custom_splash_class(config: SplashConfig) -> str:
    """Generate the CustomSplash widget Dart code."""
    if config.splash_type == SplashType.CUSTOM:
        return _read_custom_dart(config)

    bg = hex_to_dart_color(config.background)
    dark_bg = hex_to_dart_color(config.dark_background) if config.dark_background else bg

    body = _splash_body(config)
    text_section = _text_section(config)

    return (
        _CUSTOM_SPLASH_TEMPLATE.replace("__BG__", bg)
        .replace("__DARK_BG__", dark_bg)
        .replace("__BODY__", body)
        .replace("__TEXT_SECTION__", text_section)
    )


def splash_bootstrap_class(config: SplashConfig) -> str:
    return _SPLASH_BOOTSTRAP_TEMPLATE.replace(
        "__MIN_DURATION__", str(config.min_duration_ms)
    ).replace("__FADE_DURATION__", str(config.fade_duration_ms))


def flutter_asset_path(config: SplashConfig) -> str | None:
    """Return the Flutter-relative asset path, or None when no asset is needed."""
    if config.source is None:
        return None
    if config.splash_type == SplashType.CUSTOM:
        return None
    return _flutter_asset_path(config.source)


def _flutter_asset_path(source: str) -> str:
    filename = Path(source).name
    return f"splash_assets/{filename}"


def _splash_body(config: SplashConfig) -> str:
    if config.source is None:
        return "const SizedBox.shrink()"

    asset_path = _flutter_asset_path(config.source)

    if config.splash_type == SplashType.LOTTIE:
        return f"Lottie.asset('{asset_path}')"
    if config.splash_type == SplashType.IMAGE:
        return f"Image.asset('{asset_path}')"
    if config.splash_type == SplashType.SVG:
        return f"SvgPicture.asset('{asset_path}')"
    return "const SizedBox.shrink()"


def _text_section(config: SplashConfig) -> str:
    if config.text is None:
        return ""

    text_color = hex_to_dart_color(config.text_color)

    return (
        _TEXT_WIDGET_TEMPLATE.replace("__TEXT__", config.text)
        .replace("__TEXT_COLOR__", text_color)
        .replace("__TEXT_SIZE__", f"{config.text_size}.0")
    )


def _read_custom_dart(config: SplashConfig) -> str:
    """Read a developer-provided .dart file containing a CustomSplash class."""
    if config.source is None:
        return ""

    source_path = Path(config.source)
    if not source_path.is_absolute():
        return ""

    content = source_path.read_text()

    if SPLASH_MARKER not in content:
        content = f"{SPLASH_MARKER}\n{content}"

    return content
