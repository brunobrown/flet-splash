"""Example: Custom Dart splash screen.

Build with:
    fs-build apk

The splash uses a developer-provided .dart file containing a
CustomSplash widget with full Flutter animation support.
This gives you complete control over the splash screen.
"""

import flet as ft


@ft.component
def AppView() -> list[ft.Control]:
    count, set_count = ft.use_state(int(0))

    return [
        ft.Container(
            expand=True,
            alignment=ft.Alignment.CENTER,
            content=ft.Column(
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    ft.Icon(icon=ft.Icons.CODE, size=64, color=ft.Colors.PINK),
                    ft.Text(value="Custom Splash Example", size=24, weight=ft.FontWeight.BOLD),
                    ft.Text(
                        value="The app started with a fully custom Dart splash screen.",
                        size=14,
                        color=ft.Colors.GREY,
                    ),
                    ft.Text(
                        value="Edit custom_splash.dart to create any Flutter widget!",
                        size=12,
                        italic=True,
                        color=ft.Colors.GREY_400,
                    ),
                    ft.Divider(height=32),
                    ft.Text(value=f"Counter: {count}", size=32),
                    ft.Row(
                        alignment=ft.MainAxisAlignment.CENTER,
                        controls=[
                            ft.FilledButton(
                                content=ft.Text(value="- 1"),
                                on_click=lambda _: set_count(count - 1),
                            ),
                            ft.FilledButton(
                                content=ft.Text(value="+ 1"),
                                on_click=lambda _: set_count(count + 1),
                            ),
                        ],
                    ),
                ],
            ),
        ),
    ]


def main(page: ft.Page) -> None:
    page.title = "Custom Splash Example"
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.render(AppView)


ft.run(main)
