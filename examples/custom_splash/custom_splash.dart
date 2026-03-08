// [flet-splash] Custom splash screen
class CustomSplash extends StatelessWidget {
  const CustomSplash({super.key});

  @override
  Widget build(BuildContext context) {
    var brightness =
        WidgetsBinding.instance.platformDispatcher.platformBrightness;
    return ColoredBox(
      color: brightness == Brightness.dark
          ? const Color(0xFF0a0a1e)
          : const Color(0xFF1a1a2e),
      child: Center(
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            // Animated rotating logo
            TweenAnimationBuilder<double>(
              tween: Tween(begin: 0, end: 2 * 3.14159),
              duration: const Duration(seconds: 2),
              builder: (context, value, child) {
                return Transform.rotate(
                  angle: value,
                  child: child,
                );
              },
              child: Container(
                width: 80,
                height: 80,
                decoration: BoxDecoration(
                  borderRadius: BorderRadius.circular(20),
                  gradient: const LinearGradient(
                    colors: [Color(0xFF6C63FF), Color(0xFF3F3D99)],
                  ),
                ),
                child: const Center(
                  child: Icon(
                    Icons.rocket_launch,
                    size: 40,
                    color: Colors.white,
                  ),
                ),
              ),
            ),
            const SizedBox(height: 24),
            const Text(
              'Loading...',
              style: TextStyle(
                color: Colors.white70,
                fontSize: 16,
                decoration: TextDecoration.none,
                fontWeight: FontWeight.normal,
              ),
            ),
          ],
        ),
      ),
    );
  }
}