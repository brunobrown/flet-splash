"""Example: SVG splash screen.

Build with:
    flet-splash apk

The splash shows an SVG image during startup,
then fades out to reveal the app.
SVG is ideal for crisp vector logos at any resolution.
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
                    ft.Icon(ft.Icons.DRAW, size=64, color=ft.Colors.INDIGO),
                    ft.Text("SVG Splash Example", size=24, weight=ft.FontWeight.BOLD),
                    ft.Text(
                        "The app started with an SVG vector splash screen.",
                        size=14,
                        color=ft.Colors.GREY,
                    ),
                    ft.Text(
                        "Replace assets/custom_splash.svg with your own vector graphic!",
                        size=12,
                        italic=True,
                        color=ft.Colors.GREY_400,
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
    page.title = "SVG Splash Example"
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.render(AppView)


ft.run(main)
