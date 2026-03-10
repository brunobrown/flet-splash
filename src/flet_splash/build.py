from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

from flet_splash import ui
from flet_splash.config import SplashConfig
from flet_splash.inject import check_splash_injected, inject_splash

ALL_PLATFORMS = ("apk", "aab", "ipa", "web", "macos", "linux", "windows")

# ---------------------------------------------------------------------------
# Web app archive helpers
#
# When ``flet build web`` runs against an *existing* ``build/flutter``
# directory it re-packages ``app.zip`` but silently drops the
# ``__pypackages__`` folder that contains the Python dependencies
# (e.g. ``flet``).  The archive produced by the *first* build is
# correct, so we save it and restore it after every subsequent rebuild.
# ---------------------------------------------------------------------------


def _save_web_archive(flutter_dir: Path) -> bytes | None:
    """Read ``app.zip`` into memory so it can be restored later."""
    app_zip = flutter_dir / "app" / "app.zip"
    if app_zip.exists():
        return app_zip.read_bytes()
    return None


def _restore_web_archive(
    data: bytes | None,
    flutter_dir: Path,
    project_root: Path,
) -> None:
    """Write the saved archive back to both build locations."""
    if data is None:
        return
    for target in (
        flutter_dir / "app" / "app.zip",
        project_root / "build" / "web" / "assets" / "app" / "app.zip",
    ):
        if target.parent.exists():
            target.write_bytes(data)


NEXT_STEPS: dict[str, list[str]] = {
    "apk": ["Install on device: adb install <path-to-apk>"],
    "aab": ["Upload to Google Play Console"],
    "ipa": ["Upload to App Store Connect via Xcode or Transporter"],
    "web": ["Deploy the build/web directory to your hosting provider"],
    "macos": ["Run the app from build/macos"],
    "linux": ["Run the app from build/linux"],
    "windows": ["Run the app from build/windows"],
}

FAILURE_TIPS = [
    "Try running with --clean to start fresh",
    "Use -v or -vv for more verbose output",
    "Run: flet build --show-platform-matrix",
]


def build(
    config: SplashConfig,
    platform: str,
    extra_args: list[str],
    project_root: Path,
    clean: bool = False,
) -> None:
    """Orchestrate the multi-pass build with splash injection."""
    if clean:
        build_dir = project_root / "build"
        if build_dir.exists():
            ui.info("Cleaning", str(build_dir))
            shutil.rmtree(build_dir)

    cmd = ["flet", "build", platform, *extra_args]
    flutter_dir = project_root / "build" / "flutter"

    if flutter_dir.exists() and check_splash_injected(flutter_dir):
        _build_single_pass(cmd, platform, project_root)
        return

    if flutter_dir.exists():
        _build_inject_and_rebuild(cmd, config, flutter_dir, platform, project_root)
        return

    _build_full(cmd, config, flutter_dir, platform, project_root)


def _build_single_pass(cmd: list[str], platform: str, project_root: Path) -> None:
    ui.build_info(f"Building {platform.upper()} (splash already configured)")

    flutter_dir = project_root / "build" / "flutter"
    saved = _save_web_archive(flutter_dir) if platform == "web" else None

    result = subprocess.run(cmd, cwd=project_root)

    if saved is not None:
        _restore_web_archive(saved, flutter_dir, project_root)

    _finish(result.returncode, platform, project_root)


def _build_inject_and_rebuild(
    cmd: list[str],
    config: SplashConfig,
    flutter_dir: Path,
    platform: str,
    project_root: Path,
) -> None:
    ui.build_info(f"Building {platform.upper()} with custom splash")

    saved = _save_web_archive(flutter_dir) if platform == "web" else None

    ui.step(1, 2, "Injecting custom splash")
    inject_splash(flutter_dir, config, project_root)

    ui.step(2, 2, "Compiling")
    result = subprocess.run(cmd, cwd=project_root)

    if saved is not None:
        _restore_web_archive(saved, flutter_dir, project_root)

    _finish(result.returncode, platform, project_root)


def _build_full(
    cmd: list[str],
    config: SplashConfig,
    flutter_dir: Path,
    platform: str,
    project_root: Path,
) -> None:
    ui.build_info(f"Building {platform.upper()} with custom splash")

    ui.step(1, 3, "Creating Flutter project")
    result = subprocess.run(cmd, cwd=project_root)

    if not flutter_dir.exists():
        ui.error_panel(
            "Flutter project not created",
            "  The Flutter project was not created.\n  Check the error messages above for details.",
        )
        sys.exit(1)

    # Save correct app archive before rebuild (web loses __pypackages__)
    saved = _save_web_archive(flutter_dir) if platform == "web" else None

    ui.step(2, 3, "Injecting custom splash")
    inject_splash(flutter_dir, config, project_root)

    ui.step(3, 3, "Rebuilding with custom splash")
    result = subprocess.run(cmd, cwd=project_root)

    if saved is not None:
        _restore_web_archive(saved, flutter_dir, project_root)

    _finish(result.returncode, platform, project_root)


def _finish(returncode: int, platform: str, project_root: Path) -> None:
    if returncode == 0:
        output_dir = project_root / "build" / platform
        ui.success_panel(
            platform,
            str(output_dir) if output_dir.exists() else None,
            NEXT_STEPS.get(platform, []),
        )
    else:
        ui.failure_panel(FAILURE_TIPS)

    sys.exit(returncode)
