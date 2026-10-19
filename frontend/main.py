import flet as ft


def main(page: ft.Page):
    page.title = "Application Domain Project"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.padding = 30

    page.add(
        ft.Text(
            "Application Domain Project",
            size=28,
            weight=ft.FontWeight.BOLD,
        ),
        ft.Text("Welcome! Your Flet frontend is working."),
    )


if __name__ == "__main__":
    ft.run(main)
