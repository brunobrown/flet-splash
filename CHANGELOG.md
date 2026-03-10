# Changelog

## [0.2.1] - 2026-03-09

### Improved

- **Dual-condition splash fade** — splash now fades only when both `min_duration` has elapsed AND `prepareApp()` has completed. This prevents white screen flashes on cold starts where app initialization takes longer than `min_duration`. Uses a `ValueNotifier<bool>` signal and `_maybeHide()` pattern for reliable coordination.
- **Default `min_duration`** updated from 2.0 to 5.0 seconds to better cover cold start times on mobile devices.

## [0.2.0] - 2026-03-09

### Changed

- **CLI command renamed** from `flet-splash` to `fs-build` for a shorter, more intuitive interface aligned with `flet build` (e.g. `fs-build apk`, `fs-build ipa`).

## [0.1.0] - 2026-03-08

### Added

- **CLI tool** (`fs-build`) that automatically injects custom splash screens into Flet apps during the Flutter build process.
- **Multi-pass build** strategy with 3 smart scenarios: full build (3 steps), inject+rebuild (2 steps), or single pass (already injected).
- **5 splash types:**
  - `color` — solid color background, no external assets needed.
  - `image` — static image (PNG, JPG, GIF, WebP) centered on screen.
  - `lottie` — Lottie JSON animation via `lottie: ^3.2.0`.
  - `svg` — vector graphic via `flutter_svg: ^2.0.17`.
  - `custom` — developer-provided `.dart` file with full Flutter widget control.
- **Configuration via `pyproject.toml`** under `[tool.flet.splash]` with CLI flag overrides.
- **Dark mode support** — automatic brightness detection with separate `dark_background` color.
- **Text overlay** — optional text below the splash body with configurable color and size.
- **`_SplashBootstrap` overlay** — wraps the entire `runApp` content in a `Stack` with `AnimatedOpacity`, covering all loading phases (BlankScreen → LoadingPage → app) with a single smooth splash.
- **`CustomSplash` widget** — replaces the Flet template's `BlankScreen` class using brace-depth counting for robust class replacement.
- **Idempotent injection** — marker-based detection (`// [flet-splash] Custom splash screen`) prevents double-injection.
- **`parse_known_args` passthrough** — all unrecognized CLI flags are forwarded directly to `flet build`.
- **pubspec.yaml patching** — dependencies and asset entries added with correct indentation, preserving existing assets.
- **Asset copy** — source files copied to `build/flutter/splash_assets/` automatically.
- **`--clean` flag** — removes `build/` directory for a fresh start.
- **Rich CLI output** — styled panels, config table, step progress, and success/failure messages using Rich library.
- **Cross-platform support** — works with all 7 Flet build targets: `apk`, `aab`, `ipa`, `web`, `macos`, `linux`, `windows`.
- **5 example apps** — `color_splash`, `image_splash`, `lottie_splash`, `svg_splash`, `custom_splash` using Flet declarative mode.