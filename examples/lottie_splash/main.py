"""Example: Lottie animation splash screen.

Build with:
    fs-build apk

The splash shows a Lottie animation during startup,
then fades out to reveal the app.

Tip: Download free Lottie animations from https://lottiefiles.com
and replace assets/custom_splash.json with your own animation.
"""

import flet as ft


@ft.component
def AppView() -> list[ft.Control]:
    count, set_count = ft.use_state(0)

    return [
        ft.Container(
            expand=True,
            alignment=ft.Alignment.CENTER,
            content=ft.Column(
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    ft.Icon(ft.Icons.ANIMATION, size=64, color=ft.Colors.ORANGE),
                    ft.Text("Lottie Splash Example", size=24, weight=ft.FontWeight.BOLD),
                    ft.Text(
                        "The app started with a Lottie animation splash screen.",
                        size=14,
                        color=ft.Colors.GREY,
                    ),
                    ft.Text(
                        "Replace assets/custom_splash.json with your own animation!",
                        size=12,
                        italic=True,
                        color=ft.Colors.GREY_500,
                    ),
                    ft.Divider(height=32),
                    ft.Text(f"Counter: {count}", size=32),
                    ft.Row(
                        alignment=ft.MainAxisAlignment.CENTER,
                        controls=[
                            ft.FilledButton("- 1", on_click=lambda _: set_count(count - 1)),
                            ft.FilledButton("+ 1", on_click=lambda _: set_count(count + 1)),
                        ],
                    ),
                ],
            ),
        ),
    ]


def main(page: ft.Page) -> None:
    page.title = "Lottie Splash Example"
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.render(AppView)


ft.run(main)
