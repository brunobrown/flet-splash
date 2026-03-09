<p align="center"><img src="" width="500" height="500" alt="Flet Splash"></p>

**CLI tool that automatically injects fully customizable splash screens into Flet apps during the Flutter build process. Configure once in `pyproject.toml`, build with `flet-splash apk`, and your app launches with a beautiful custom splash.**

![Python](https://img.shields.io/badge/python-3.10+-3776AB?logo=python&logoColor=white)
![Flet](https://img.shields.io/badge/flet-0.80.0+-00B4D8?logo=flet)
![License](https://img.shields.io/badge/license-MIT-yellow)

---

> **Solves [flet-dev/flet#5523](https://github.com/flet-dev/flet/issues/5523)** — Unified and fully customizable startup sequence (splash → boot → startup) with support for custom Flutter widgets/animations.
>
> The default Flet startup experience shows a blank white screen → a `CircularProgressIndicator` → then finally the app. This creates a jarring, unprofessional launch experience. **flet-splash** replaces the entire startup sequence with a smooth, customizable splash screen that covers all loading phases and fades out gracefully when the app is ready.

---

## Table of Contents

- [The Problem](#the-problem)
- [The Solution](#the-solution)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [How It Works](#how-it-works)
- [Build Process in Detail](#build-process-in-detail)
  - [1. Configuration Loading](#1-configuration-loading)
  - [2. Build Orchestration](#2-build-orchestration)
  - [3. Injection: main.dart Patching](#3-injection-maindart-patching)
  - [4. Injection: pubspec.yaml Patching](#4-injection-pubspecyaml-patching)
  - [5. Asset Copy](#5-asset-copy)
  - [6. Rebuild](#6-rebuild)
- [Configuration](#configuration)
  - [pyproject.toml](#pyprojecttoml)
  - [CLI Overrides](#cli-overrides)
- [Splash Types](#splash-types)
  - [Color](#color)
  - [Image](#image)
  - [Lottie](#lottie)
  - [SVG](#svg)
  - [Custom Dart Widget](#custom-dart-widget)
- [Text Overlay](#text-overlay)
- [Dark Mode Support](#dark-mode-support)
- [CLI Reference](#cli-reference)
- [Important Notes](#important-notes)
- [Examples](#examples)
- [Supported Platforms](#supported-platforms)
- [Development](#development)
- [Buy Me a Coffee](#buy-me-a-coffee)
- [Learn more](#learn-more)
- [Flet Community](#flet-community)
- [Support](#support)
- [Contributing](#contributing)

---

## Buy Me a Coffee

If you find this project useful, please consider supporting its development:

<a href="https://www.buymeacoffee.com/brunobrown">
<img src="https://www.buymeacoffee.com/assets/img/guidelines/download-assets-sm-1.svg" width="200" alt="Buy Me a Coffee">
</a>

---


## The Problem

When a Flet app starts, users see **three different screens** before the actual app appears:

```
1. BlankScreen (white)  →  2. LoadingPage (spinner)  →  3. Your app
```

This creates a flickering, unprofessional startup experience — especially on mobile where cold starts can take several seconds.

## The Solution

**flet-splash** injects a custom splash overlay that covers **all three phases** with a single, smooth screen:

```
1. CustomSplash (your design)  →  fade out  →  Your app
```

The splash stays visible throughout the entire boot process and fades out gracefully once the app is ready. No flicker, no spinner — just your brand.

---

## Installation

```bash
# Using UV (recommended)
uv add flet-splash

# Using pip
pip install flet-splash

# From GitHub (latest development version)
uv add flet-splash@git+https://github.com/brunobrown/flet-splash.git

# or

pip install git+https://github.com/brunobrown/flet-splash.git
```

**Requirements:** Python 3.10+, Flet 0.80.0+

---

## Quick Start

**1. Configure your splash in `pyproject.toml`:**

```toml
[tool.flet.splash]
type = "color"
background = "#1a1a2e"
min_duration = 2.0
```

**2. Build your app:**

```bash
flet-splash apk
```

That's it. The splash screen is automatically injected into the Flutter build.

---

## How It Works

flet-splash uses a **multi-pass build** strategy:

```
Step 1/3  First pass — flet build generates the Flutter project
Step 2/3  Inject — patches main.dart, pubspec.yaml, and copies assets
Step 3/3  Rebuild — flet build recompiles with the splash injected
```

The injection is:

- **Automatic** — no manual Flutter/Dart editing required
- **Idempotent** — running twice won't double-inject (marker-based detection)
- **Non-destructive** — only modifies `BlankScreen`, `runApp`, and `pubspec.yaml`
- **Smart** — if the Flutter project already exists, skips the first pass

### What gets patched

| File | Change |
|------|--------|
| `lib/main.dart` | `BlankScreen` class → `CustomSplash` (your design) |
| `lib/main.dart` | `runApp(FutureBuilder(...))` → `runApp(_SplashBootstrap(child: FutureBuilder(...)))` |
| `lib/main.dart` | `_SplashBootstrap` overlay with `AnimatedOpacity` appended |
| `pubspec.yaml` | Dependencies added (`lottie`, `flutter_svg`) if needed |
| `pubspec.yaml` | Asset entries added to `flutter.assets` |
| `splash_assets/` | Source file copied (image, lottie, svg) |

---

## Build Process in Detail

This section explains exactly what happens when you run `flet-splash apk` — from reading your config to delivering the final APK.

### 1. Configuration Loading

flet-splash reads your `pyproject.toml` and merges it with any CLI flags:

```
pyproject.toml [tool.flet.splash]  ←  defaults
         ↓
    CLI flags override             ←  --type, --source, --background, etc.
         ↓
    SplashConfig (final)           ←  validated, ready to use
```

Validations at this stage:
- Types `lottie`, `image`, `svg`, and `custom` require a `source` file
- Type `custom` requires a `.dart` extension
- The source file must exist on disk

### 2. Build Orchestration

flet-splash detects the current state and chooses the optimal build path:

```
                          ┌─────────────────────────────┐
                          │  Does build/flutter/ exist? │
                          └──────────────┬──────────────┘
                                         │
                          ┌──── NO ──────┼────── YES ───┐
                          │              │              │
                          ▼              │              ▼
                   ┌─────────────┐       │    ┌────────────────────┐
                   │  FULL BUILD │       │    │  Splash injected?  │
                   │  (3 steps)  │       │    └─────────┬──────────┘
                   └─────────────┘       │         YES  │  NO
                                         │          │   │
                                         │          ▼   ▼
                                         │    ┌──────┐ ┌──────────────┐
                                         │    │SINGLE│ │INJECT+REBUILD│
                                         │    │ PASS │ │  (2 steps)   │
                                         │    └──────┘ └──────────────┘
```

**Scenario A — Full Build (first time):**

```
Step 1/3  flet build apk         →  generates build/flutter/ (the Flutter project)
Step 2/3  inject_splash()        →  patches main.dart, pubspec.yaml, copies assets
Step 3/3  flet build apk         →  recompiles with splash injected
```

**Scenario B — Inject + Rebuild (Flutter project exists but no splash):**

```
Step 1/2  inject_splash()        →  patches existing Flutter project
Step 2/2  flet build apk         →  compiles with splash
```

**Scenario C — Single Pass (splash already injected):**

```
Step 1/1  flet build apk         →  builds directly (nothing to inject)
```

### 3. Injection: main.dart Patching

The injection modifies `build/flutter/lib/main.dart` in **5 sequential patches**:

#### Patch 1 — Add Imports

If the splash type requires external packages, the corresponding imports are added after the last existing `import` statement:

```dart
// BEFORE (original Flet template)
import 'package:flet/flet.dart';
import 'package:flutter/material.dart';

// AFTER (lottie type)
import 'package:flet/flet.dart';
import 'package:flutter/material.dart';
import 'package:lottie/lottie.dart';        // ← added

// AFTER (svg type)
import 'package:flet/flet.dart';
import 'package:flutter/material.dart';
import 'package:flutter_svg/flutter_svg.dart'; // ← added
```

Types `color`, `image`, and `custom` don't add any imports.

#### Patch 2 — Replace BlankScreen Class

The original `BlankScreen` class (a blank `Scaffold`) is **entirely replaced** by `CustomSplash` — your splash widget. The replacement uses **brace-depth counting** to accurately find the class boundaries, regardless of inner classes or nested braces:

```dart
// BEFORE (original Flet template)
class BlankScreen extends StatelessWidget {
  const BlankScreen({super.key});
  @override
  Widget build(BuildContext context) {
    return const Scaffold(body: SizedBox.shrink());
  }
}

// AFTER (replaced by flet-splash — example with image type)
// [flet-splash] Custom splash screen
class CustomSplash extends StatelessWidget {
  const CustomSplash({super.key});
  @override
  Widget build(BuildContext context) {
    var brightness = WidgetsBinding.instance.platformDispatcher.platformBrightness;
    return ColoredBox(
      color: brightness == Brightness.dark
          ? const Color(0xFF0a0a1e)
          : const Color(0xFF1a1a2e),
      child: Center(
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Image.asset('splash_assets/custom_splash.png'),
          ],
        ),
      ),
    );
  }
}
```

For `type = "custom"`, the entire content of your `.dart` file replaces the class.

#### Patch 3 — Replace BlankScreen References

All `BlankScreen()` constructor calls in the code are replaced with `CustomSplash()`:

```dart
// BEFORE
return const MaterialApp(home: BlankScreen());

// AFTER
return const MaterialApp(home: CustomSplash());
```

#### Patch 4 — Wrap runApp with _SplashBootstrap

The `runApp` call is wrapped to add the splash overlay on top of the entire widget tree:

```dart
// BEFORE
runApp(FutureBuilder(
    future: prepareApp(),
    builder: (BuildContext context, AsyncSnapshot snapshot) {
        // ... app content ...
    }));

// AFTER
runApp(_SplashBootstrap(child: FutureBuilder(
    future: prepareApp(),
    builder: (BuildContext context, AsyncSnapshot snapshot) {
        // ... app content ...
    })));
```

This ensures the splash overlay sits **above everything** — `BlankScreen`, `LoadingPage`, and the app itself.

#### Patch 5 — Append _SplashBootstrap Class

The `_SplashBootstrap` widget is appended at the end of `main.dart`. This is the core mechanism that creates the overlay effect:

```dart
class _SplashBootstrap extends StatefulWidget {
  final Widget child;
  const _SplashBootstrap({required this.child});

  @override
  State<_SplashBootstrap> createState() => _SplashBootstrapState();
}

class _SplashBootstrapState extends State<_SplashBootstrap> {
  bool _showSplash = true;

  @override
  void initState() {
    super.initState();
    // After min_duration, start hiding the splash
    Future.delayed(const Duration(milliseconds: 2000), () {
      if (mounted) setState(() => _showSplash = false);
    });
  }

  @override
  Widget build(BuildContext context) {
    return Directionality(
      textDirection: TextDirection.ltr,
      child: Stack(
        children: [
          widget.child,                    // ← the actual app (behind)
          IgnorePointer(
            ignoring: !_showSplash,        // ← lets taps pass through during fade
            child: AnimatedOpacity(
              opacity: _showSplash ? 1.0 : 0.0,
              duration: const Duration(milliseconds: 500),  // ← fade_duration
              child: const CustomSplash(), // ← your splash (on top)
            ),
          ),
        ],
      ),
    );
  }
}
```

**How it works at runtime:**

1. App starts → `_SplashBootstrap` renders a `Stack` with the app **behind** and `CustomSplash` **on top** (opacity 1.0)
2. The app boots normally underneath (invisible to the user)
3. After `min_duration` ms → `_showSplash` becomes `false`
4. `AnimatedOpacity` fades from 1.0 to 0.0 over `fade_duration` ms
5. `IgnorePointer` allows touch events to pass through during the fade
6. The splash becomes fully transparent → the app is revealed

### 4. Injection: pubspec.yaml Patching

Dependencies and assets are added to `build/flutter/pubspec.yaml`:

```yaml
# Dependencies added (only when needed):
dependencies:
  lottie: ^3.2.0             # ← added for type "lottie"
  flutter_svg: ^2.0.17       # ← added for type "svg"

# Asset entry appended to existing list:
flutter:
  assets:
    - app/app.zip             # ← existing Flet asset (preserved)
    - app/app.zip.hash        # ← existing Flet asset (preserved)
    - splash_assets/custom_splash.json  # ← added by flet-splash
```

The asset is appended **at the end** of the existing `assets:` list, preserving the original indentation.

### 5. Asset Copy

The source file is copied from your project into the Flutter build directory:

```
your_project/assets/custom_splash.json  →  build/flutter/splash_assets/custom_splash.json
your_project/assets/custom_splash.png   →  build/flutter/splash_assets/custom_splash.png
your_project/assets/custom_splash.svg   →  build/flutter/splash_assets/custom_splash.svg
```

For `type = "color"`, no asset is copied. For `type = "custom"`, the `.dart` content is injected directly into `main.dart` (no asset copy needed).

### 6. Rebuild

Finally, `flet build` runs again. This time the Flutter project already contains:
- The `CustomSplash` widget (replacing `BlankScreen`)
- The `_SplashBootstrap` overlay wrapping `runApp`
- Any required dependencies (`lottie`, `flutter_svg`)
- The splash asset file in `splash_assets/`

Flutter compiles everything into the final binary (APK, IPA, etc.) with the custom splash built-in.

### Summary: File Flow

```
your_project/
├── pyproject.toml                     ← [1] config read from here
├── assets/
│   └── custom_splash.json             ← [5] copied to build/flutter/splash_assets/
└── build/
    └── flutter/                       ← generated by flet build (Step 1)
        ├── lib/
        │   └── main.dart              ← [3] patched (5 sequential modifications)
        ├── pubspec.yaml               ← [4] patched (deps + assets)
        └── splash_assets/
            └── custom_splash.json     ← [5] asset copied here
```

---

## Configuration

### pyproject.toml

All configuration goes under `[tool.flet.splash]`:

```toml
[tool.flet.splash]
type = "lottie"                      # lottie | image | svg | color | custom
source = "assets/custom_splash.json" # path to asset file (relative to project root)
background = "#1a1a2e"               # background color (hex)
dark_background = "#0a0a1e"          # dark mode background (optional, falls back to background)
min_duration = 2.0                   # minimum splash duration in seconds
fade_duration = 0.5                  # fade-out animation duration in seconds
text = "Loading..."                  # optional text below the splash
text_color = "#ffffff"               # text color (hex)
text_size = 14                       # text font size in pixels
```

### CLI Overrides

Any config option can be overridden via CLI flags:

```bash
flet-splash apk --type lottie --source assets/custom_splash.json --background "#1a1a2e"
flet-splash apk --min-duration 3.0 --fade-duration 0.8
flet-splash apk --text "Loading..." --text-color "#cccccc" --text-size 16
```

**Priority:** CLI flags > `pyproject.toml` > defaults

All extra flags are passed directly to `flet build`:

```bash
# These flags go straight to flet build
flet-splash apk -v --org com.example --build-version 1.0.0 --split-per-abi
```

---

## Splash Types

### Color

A solid color background. Simplest option — no external assets needed.

```toml
[tool.flet.splash]
type = "color"
background = "#1a1a2e"
dark_background = "#0d0d1a"
```

### Image

A static image (PNG, JPG, GIF, WebP) centered on the splash screen.

```toml
[tool.flet.splash]
type = "image"
source = "assets/custom_splash.png"
background = "#0d47a1"
```

### Lottie

A [Lottie](https://lottiefiles.com) animation (JSON) that plays during startup. Great for animated logos and branded loading screens.

```toml
[tool.flet.splash]
type = "lottie"
source = "assets/custom_splash.json"
background = "#1b0536"
min_duration = 3.0
```

> **Tip:** Download free Lottie animations from [LottieFiles](https://lottiefiles.com).

### SVG

A vector graphic (SVG) rendered via `flutter_svg`. Ideal for logos that need to be crisp at any resolution.

```toml
[tool.flet.splash]
type = "svg"
source = "assets/custom_splash.svg"
background = "#1b1b2f"
```

> **Important:** Do not name your SVG file `splash.svg` inside the `assets/` folder. Flet automatically detects `assets/splash.*` files and passes them to `flutter_native_splash`, which does not support SVG format. Use a different name like `custom_splash.svg`.

### Custom Dart Widget

For full control, provide your own `.dart` file with a `CustomSplash` widget. You can use any Flutter widget, animation, or layout.

```toml
[tool.flet.splash]
type = "custom"
source = "custom_splash.dart"
min_duration = 3.0
```

The `.dart` file must define a `CustomSplash` class that extends `StatelessWidget` or `StatefulWidget`:

```dart
class CustomSplash extends StatelessWidget {
  const CustomSplash({super.key});

  @override
  Widget build(BuildContext context) {
    return ColoredBox(
      color: const Color(0xFF1a1a2e),
      child: Center(
        child: TweenAnimationBuilder<double>(
          tween: Tween(begin: 0, end: 2 * 3.14159),
          duration: const Duration(seconds: 2),
          builder: (context, value, child) {
            return Transform.rotate(angle: value, child: child);
          },
          child: const Icon(Icons.rocket_launch, size: 64, color: Colors.white),
        ),
      ),
    );
  }
}
```

> **Note:** When using `type = "custom"`, the `background` and `dark_background` settings are ignored — your widget controls everything.

---

## Text Overlay

Add optional text below the splash content (available for all types except `custom`):

```toml
[tool.flet.splash]
type = "image"
source = "assets/custom_splash.png"
background = "#1a1a2e"
text = "Loading..."
text_color = "#cccccc"
text_size = 16
```

The text is rendered as a Flutter `Text` widget positioned below the splash body.

---

## Dark Mode Support

flet-splash automatically detects the device's brightness setting and applies the appropriate background:

```toml
[tool.flet.splash]
background = "#1a1a2e"           # light mode
dark_background = "#0a0a1e"      # dark mode (optional)
```

If `dark_background` is not set, the `background` color is used for both modes.

---

## CLI Reference

```
Usage: flet-splash [-h] [--type {lottie,image,svg,color,custom}]
                   [--source SOURCE] [--background BACKGROUND]
                   [--dark-background DARK_BACKGROUND]
                   [--min-duration MIN_DURATION]
                   [--fade-duration FADE_DURATION]
                   [--text TEXT] [--text-color TEXT_COLOR]
                   [--text-size TEXT_SIZE] [--clean]
                   {apk,aab,ipa,web,macos,linux,windows}
```

| Option | Type | Description |
|--------|------|-------------|
| `platform` | positional | Target platform: `apk`, `aab`, `ipa`, `web`, `macos`, `linux`, `windows` |
| `--type` | TEXT | Splash type: `lottie`, `image`, `svg`, `color`, `custom` |
| `--source` | PATH | Path to splash asset file |
| `--background` | TEXT | Background color (hex, e.g. `"#1a1a2e"`) |
| `--dark-background` | TEXT | Dark mode background color (hex) |
| `--min-duration` | FLOAT | Minimum splash duration in seconds |
| `--fade-duration` | FLOAT | Fade-out animation duration in seconds |
| `--text` | TEXT | Optional text below the splash |
| `--text-color` | TEXT | Text color (hex) |
| `--text-size` | INT | Text font size in pixels |
| `--clean` | FLAG | Clean build directory before building |

All unrecognized flags are forwarded to `flet build`:

```bash
flet-splash apk -v --org com.example --build-version 2.0.0
#                   ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#                   these go directly to flet build
```

---

## Important Notes

### Asset naming

Flet automatically detects files named `assets/splash.*` and uses them as the native splash screen (via `flutter_native_splash`). To avoid conflicts:

- **Do not** name your splash asset `splash.png`, `splash.svg`, `splash.json`, etc.
- **Use** a different name like `custom_splash.png`, `brand_logo.svg`, `loading.json`, etc.

### Build directory

flet-splash modifies files inside `build/flutter/`. If you encounter issues, use `--clean` to start fresh:

```bash
flet-splash apk --clean
```

### Idempotency

The injection is idempotent. If flet-splash detects its marker (`// [flet-splash] Custom splash screen`) in `main.dart`, it skips the injection step and proceeds directly to the build.

---

## Examples

The `examples/` directory contains ready-to-build sample apps for each splash type:

| Example | Type | Description |
|---------|------|-------------|
| [`color_splash`](examples/color_splash) | `color` | Solid color background — simplest configuration |
| [`image_splash`](examples/image_splash) | `image` | Static PNG image centered on splash |
| [`lottie_splash`](examples/lottie_splash) | `lottie` | Lottie JSON animation during startup |
| [`svg_splash`](examples/svg_splash) | `svg` | SVG vector graphic via flutter_svg |
| [`custom_splash`](examples/custom_splash) | `custom` | Custom Dart widget with rotation animation |

To test an example:

```bash
cd examples/color_splash
flet-splash apk
```

---

## Supported Platforms

flet-splash works with all platforms supported by Flet:

| Platform | Command | Notes |
|----------|---------|-------|
| Android (APK) | `flet-splash apk` | Debug APK |
| Android (AAB) | `flet-splash aab` | Play Store bundle |
| iOS | `flet-splash ipa` | Requires macOS + Xcode |
| Web | `flet-splash web` | Static web app |
| macOS | `flet-splash macos` | Desktop app |
| Linux | `flet-splash linux` | Desktop app |
| Windows | `flet-splash windows` | Desktop app |

---

## Development

```bash
# Clone and install
git clone https://github.com/brunobrown/flet-splash.git
cd flet-splash
uv sync

# Run tests
uv run pytest tests/ -v

# Lint and format
uv tool run ruff format
uv tool run ruff check
uv tool run ty check

# Run the CLI locally
uv run flet-splash apk
```

---

## Learn more
* [Documentation](https://brunobrown.github.io/flet-splash)

## Flet Community

Join the community to contribute or get help:

* [Discussions](https://github.com/flet-dev/flet/discussions)
* [Discord](https://discord.gg/dzWXP8SHG8)
* [X (Twitter)](https://twitter.com/fletdev)
* [Bluesky](https://bsky.app/profile/fletdev.bsky.social)
* [Email us](mailto:hello@flet.dev)

## Support

If you like this project, please give it a [GitHub star](https://github.com/brunobrown/flet-splash) ⭐

---

## Contributing

Contributions and feedback are welcome!

1. Fork the repository
2. Create a feature branch
3. Submit a pull request with detailed explanation

For feedback, [open an issue](https://github.com/brunobrown/flet-splash/issues) with your suggestions.

---
## Give your Flet app a professional first impression with flet-splash!

<p align="center"><img src="https://github.com/user-attachments/assets/431aa05f-5fbc-4daa-9689-b9723583e25a" width="50%"></p>
<p align="center"><a href="https://www.bible.com/bible/116/PRO.16.NLT"> Commit your work to the LORD, and your plans will succeed. Proverbs 16:3</a></p>
