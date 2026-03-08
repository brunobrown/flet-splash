"""Example: Image splash screen.

Build with:
    flet-splash apk

The splash shows a static image (PNG/JPG/GIF/WebP) during startup,
then fades out to reveal the app.
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
                    ft.Icon(ft.Icons.IMAGE, size=64, color=ft.Colors.TEAL),
                    ft.Text("Image Splash Example", size=24, weight=ft.FontWeight.BOLD),
                    ft.Text(
                        "The app started with a custom image splash screen.",
                        size=14,
                        color=ft.Colors.GREY,
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
    page.title = "Image Splash Example"
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.render(AppView)


ft.run(main)
