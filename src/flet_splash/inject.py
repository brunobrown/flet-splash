from __future__ import annotations

import re
import shutil
from pathlib import Path

from flet_splash import ui
from flet_splash.config import SplashConfig, SplashType
from flet_splash.templates import (
    SPLASH_MARKER,
    custom_splash_class,
    extra_imports,
    extra_pubspec_deps,
    flutter_asset_path,
    splash_bootstrap_class,
)


def check_splash_injected(flutter_dir: Path) -> bool:
    """Return True if the splash has already been injected into main.dart."""
    main_dart = flutter_dir / "lib" / "main.dart"
    if not main_dart.exists():
        return False
    return SPLASH_MARKER in main_dart.read_text()


def inject_splash(flutter_dir: Path, config: SplashConfig, project_root: Path) -> bool:
    """Inject custom splash into the Flutter project.

    Returns True if any modifications were made.
    """
    resolved_config = _resolve_custom_source(config, project_root)
    modified = False

    main_dart = flutter_dir / "lib" / "main.dart"
    if main_dart.exists():
        modified |= _patch_main_dart(main_dart, resolved_config)

    pubspec = flutter_dir / "pubspec.yaml"
    if pubspec.exists():
        modified |= _patch_pubspec(pubspec, resolved_config)

    modified |= _copy_assets(flutter_dir, resolved_config, project_root)

    return modified


def _resolve_custom_source(config: SplashConfig, project_root: Path) -> SplashConfig:
    """For custom type, resolve relative source to absolute path for _read_custom_dart."""
    if config.splash_type != SplashType.CUSTOM or config.source is None:
        return config
    abs_path = (project_root / config.source).resolve()
    return SplashConfig(
        splash_type=config.splash_type,
        source=str(abs_path),
        background=config.background,
        dark_background=config.dark_background,
        min_duration_ms=config.min_duration_ms,
        fade_duration_ms=config.fade_duration_ms,
        text=config.text,
        text_color=config.text_color,
        text_size=config.text_size,
    )


def _patch_main_dart(path: Path, config: SplashConfig) -> bool:
    """Apply all splash patches to main.dart."""
    content = path.read_text()

    if SPLASH_MARKER in content:
        ui.info("Splash", "already injected — skipping main.dart")
        return False

    original = content

    content = _add_imports(content, config)
    content = _replace_blank_screen_class(content, config)
    content = _replace_blank_screen_refs(content)
    content = _wrap_run_app(content)
    content = _append_bootstrap_class(content, config)

    if content == original:
        return False

    path.write_text(content)
    ui.modified("Patched: lib/main.dart")
    return True


def _add_imports(content: str, config: SplashConfig) -> str:
    lines_to_add = [line for line in extra_imports(config) if line not in content]
    if not lines_to_add:
        return content

    last_import = _find_last_import_position(content)
    insert = "\n".join(lines_to_add) + "\n"

    if last_import == -1:
        return insert + content

    return content[:last_import] + insert + content[last_import:]


def _find_last_import_position(content: str) -> int:
    """Find the position right after the last import statement."""
    pos = -1
    for m in re.finditer(r"^import\s+.+;$", content, re.MULTILINE):
        pos = m.end() + 1  # +1 for the newline
    return pos


def _replace_blank_screen_class(content: str, config: SplashConfig) -> str:
    """Replace the BlankScreen class definition with CustomSplash."""
    return _replace_class(content, "BlankScreen", custom_splash_class(config))


def _replace_blank_screen_refs(content: str) -> str:
    """Replace all BlankScreen() references with CustomSplash()."""
    return content.replace("BlankScreen()", "CustomSplash()")


def _wrap_run_app(content: str) -> str:
    """Wrap the runApp(FutureBuilder(...)) with _SplashBootstrap."""
    marker = "runApp(FutureBuilder("
    if marker not in content:
        return content

    content = content.replace(marker, "runApp(_SplashBootstrap(child: FutureBuilder(", 1)

    # Add closing paren for _SplashBootstrap — find the last "}));" in the file
    last_close = content.rfind("}));")
    if last_close != -1:
        content = content[:last_close] + "})));" + content[last_close + 4 :]

    return content


def _append_bootstrap_class(content: str, config: SplashConfig) -> str:
    return content + "\n" + splash_bootstrap_class(config)


def _replace_class(content: str, class_name: str, replacement: str) -> str:
    """Replace an entire class definition using brace-depth counting."""
    marker = f"class {class_name} "
    start = content.find(marker)
    if start == -1:
        return content

    brace_start = content.find("{", start)
    if brace_start == -1:
        return content

    depth = 1
    pos = brace_start + 1
    while pos < len(content) and depth > 0:
        if content[pos] == "{":
            depth += 1
        elif content[pos] == "}":
            depth -= 1
        pos += 1

    return content[:start] + replacement + "\n" + content[pos:]


def _patch_pubspec(path: Path, config: SplashConfig) -> bool:
    """Add dependencies and splash asset to pubspec.yaml."""
    content = path.read_text()
    original = content

    for pkg_name, pkg_version in extra_pubspec_deps(config):
        if f"{pkg_name}:" not in content:
            content = content.replace(
                "dependencies:\n", f"dependencies:\n  {pkg_name}: {pkg_version}\n", 1
            )
            ui.modified(f"Injected: {pkg_name} dependency into pubspec.yaml")

    asset_path = flutter_asset_path(config)
    if asset_path and asset_path not in content:
        content = _add_flutter_asset(content, asset_path)
        ui.modified(f"Injected: {asset_path} into pubspec.yaml assets")

    if content == original:
        return False

    path.write_text(content)
    return True


def _add_flutter_asset(content: str, asset_path: str) -> str:
    """Add an asset entry to the flutter.assets section, preserving existing indentation."""
    # Find existing assets section and detect indentation
    match = re.search(r"^( +)assets:\s*\n(( +)- .+\n)*", content, re.MULTILINE)
    if match:
        # Detect indent from existing entries, or use parent indent + 2
        item_indent = match.group(3) if match.group(3) else match.group(1) + "  "
        asset_entry = f"{item_indent}- {asset_path}\n"
        # Insert at the end of the assets list
        insert_pos = match.end()
        return content[:insert_pos] + asset_entry + content[insert_pos:]

    if "flutter:" in content:
        return content.replace("flutter:\n", f"flutter:\n  assets:\n    - {asset_path}\n", 1)

    return content + f"\nflutter:\n  assets:\n    - {asset_path}\n"


def _copy_assets(flutter_dir: Path, config: SplashConfig, project_root: Path) -> bool:
    """Copy splash asset into the Flutter project."""
    if config.source is None:
        return False

    asset_path = flutter_asset_path(config)
    if asset_path is None:
        return False

    src_file = project_root / config.source
    dst_file = flutter_dir / asset_path

    if not src_file.exists():
        ui.warning(f"Source file not found: {src_file}")
        return False

    dst_file.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src_file, dst_file)
    ui.modified(f"Copied: {config.source} -> {asset_path}")
    return True
