"""Dr. No's Comics & Games - mobile app (Flet).

Run from the frontend folder with:  flet run
"""
import flet as ft

import screens
import theme as t

SCREENS = {
    "sign_in": screens.sign_in,
    "create_account": screens.create_account,
    "home": screens.home,
}
START_SCREEN = "sign_in"   # Figma flow starts at Sign In ("Continue as guest" goes to Home)


class App:
    """Holds app state (who is signed in, what is in the cart) and handles navigation."""

    def __init__(self, page: ft.Page):
        self.page = page
        self.user = None
        self.cart = {"items": 0, "qty": 0, "total": "$0.00"}   # filled in by the cart task later

        page.title = "Dr. No's Comics & Games"
        page.padding = 0
        page.bgcolor = t.BACKGROUND
        page.theme_mode = ft.ThemeMode.LIGHT
        page.theme = ft.Theme(color_scheme_seed=t.NAVY)
        try:  # phone-sized window when testing on a computer
            page.window.width = 390
            page.window.height = 844
        except Exception:
            pass

        self.root = ft.Container(expand=True, bgcolor=t.BACKGROUND)
        self._build_sidebar()
        page.add(ft.SafeArea(expand=True, content=self.root))
        self.go(START_SCREEN)

    # ---- navigation -------------------------------------------------------
    def go(self, name: str):
        self.close_sidebar()
        self.root.content = SCREENS[name](self)
        self.page.update()

    def toast(self, message: str):
        self.page.show_dialog(ft.SnackBar(ft.Text(message)))

    # ---- side bar (Figma: 10 Store Info) -----------------------------------
    def _build_sidebar(self):
        self.scrim = ft.Container(
            left=0, right=0, top=0, bottom=0, bgcolor=t.SCRIM, visible=False,
            on_click=lambda e: self.close_sidebar(),
        )
        self.panel = ft.Container(
            left=0, top=0, bottom=0, width=300,
            bgcolor=t.WHITE,
            padding=ft.Padding.all(20),
            offset=ft.Offset(-1.05, 0),                       # hidden off-screen to the left
            animate_offset=ft.Animation(250, ft.AnimationCurve.EASE_OUT),
        )
        self.page.overlay.append(self.scrim)
        self.page.overlay.append(self.panel)

    def _sidebar_content(self):
        def section(title, lines):
            return ft.Column(
                spacing=2,
                controls=[t.label(title, 12, t.MUTED)] + [t.label(x, 16) for x in lines],
            )

        deals = ft.Container(
            bgcolor=t.YELLOW, border_radius=10, padding=ft.Padding.symmetric(horizontal=14, vertical=12),
            content=ft.Column(spacing=4, controls=[
                t.label("Online deals", 14, t.NAVY, bold=True),
                t.label("Current mailing and order discounts show here.", 12, t.NAVY),
            ]),
        )
        signed_in = self.user is not None
        auth_button = (
            t.button("Sign Out", on_click=lambda e: self._sign_out(), kind="secondary")
            if signed_in
            else t.button("Sign In", on_click=lambda e: self.go("sign_in"), kind="secondary")
        )
        return ft.Column(
            scroll=ft.ScrollMode.AUTO,
            spacing=14,
            horizontal_alignment=ft.CrossAxisAlignment.STRETCH,
            controls=[
                ft.Row(
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    controls=[
                        ft.Text("Store Info", size=18, weight=ft.FontWeight.BOLD, color=t.NAVY),
                        ft.IconButton(icon=ft.Icons.CLOSE, on_click=lambda e: self.close_sidebar()),
                    ],
                ),
                section("HOURS", ["Mon–Sat: 11am – 8pm", "Sunday: 12pm – 6pm"]),
                t.label("Open 363 days a year. Closed Thanksgiving and Christmas. Curbside pick-up available.", 12, t.MUTED),
                section("CONTACT", ["(770) 422-4642", "(678) 903-3705", "manager@drnos.com"]),
                t.label("3372 Canton Rd #104, Marietta GA 30066", 14, t.MUTED),
                deals,
                t.button("Recurring Orders", on_click=lambda e: self.toast("Recurring Orders comes later"), kind="secondary"),
                t.button("About Devs", on_click=lambda e: self.toast("About Devs comes later"), kind="secondary"),
                auth_button,
            ],
        )

    def open_sidebar(self):
        self.panel.content = self._sidebar_content()   # rebuilt each time so Sign In / Sign Out is current
        self.scrim.visible = True
        self.panel.offset = ft.Offset(0, 0)
        self.page.update()

    def close_sidebar(self):
        self.scrim.visible = False
        self.panel.offset = ft.Offset(-1.05, 0)
        self.page.update()

    def _sign_out(self):
        self.user = None
        self.toast("Signed out")
        self.go("sign_in")


def main(page: ft.Page):
    App(page)


ft.run(main)


import flet as ft

# Colors from the style guide
RED = "#D92B20"
NAVY = "#1B3358"
BLUE = "#4A86D8"
YELLOW = "#F7DC3F"
BACKGROUND = "#EEF4FD"
WHITE = "#FFFFFF"
TEXT = "#1B2A44"
MUTED = "#5B6B85"
BORDER = "#CBD6E6"
SUCCESS = "#1F8A4C"


def main(page: ft.Page):
    page.title = "Dr. No's Comics & Games"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.bgcolor = BACKGROUND
    page.padding = 0
    page.window.width = 390
    page.window.height = 844
    page.scroll = ft.ScrollMode.AUTO

    cart = {}
    search = ft.TextField(
        hint_text="Search comics, games, toys...",
        prefix_icon=ft.Icons.SEARCH,
        border_radius=25,
        bgcolor=WHITE,
        border_color=BORDER,
        text_size=14,
    )

    products = [
        {"name": "Amazing Spider-Man #1",
         "creator": "Stan Lee", "price": 4.99},
        {"name": "Batman #1",
         "creator": "DC Comics", "price": 5.99},
        {"name": "X-Men #1",
         "creator": "Marvel Comics", "price": 6.99},
        {"name": "Superman #1",
         "creator": "DC Comics", "price": 3.99},
    ]

    content = ft.Column(spacing=12)
    cart_count = ft.Text("Cart (0)", color=WHITE, size=12)

    def header():
        return ft.Container(
            bgcolor=NAVY,
            padding=15,
            content=ft.Row(
                [
                    ft.IconButton(
                        icon=ft.Icons.MENU,
                        icon_color=WHITE,
                        on_click=lambda e: show_home(),
                    ),
                    ft.Text(
                        "Dr. No's",
                        color=WHITE,
                        size=18,
                        weight=ft.FontWeight.BOLD,
                        expand=True,
                        text_align=ft.TextAlign.CENTER,
                    ),
                    ft.TextButton(
                        content=cart_count,
                        on_click=lambda e: show_cart(),
                    ),
                ]
            ),
        )

    def add_to_cart(product):
        name = product["name"]
        if name not in cart:
            cart[name] = {
                "price": product["price"],
                "quantity": 0,
            }
        cart[name]["quantity"] += 1
        update_count()
        page.update()

    def update_count():
        count = sum(item["quantity"] for item in cart.values())
        cart_count.value = f"Cart ({count})"

    def product_card(product):
        return ft.Container(
            bgcolor=WHITE,
            border=ft.border.all(1, BORDER),
            border_radius=10,
            padding=15,
            content=ft.Column(
                [
                    ft.Text(
                        product["name"],
                        size=16,
                        weight=ft.FontWeight.BOLD,
                        color=TEXT,
                    ),
                    ft.Text(
                        product["creator"],
                        size=12,
                        color=MUTED,
                    ),
                    ft.Row(
                        [
                            ft.Text(
                                f'${product["price"]:.2f}',
                                size=20,
                                weight=ft.FontWeight.BOLD,
                                color=RED,
                            ),
                            ft.ElevatedButton(
                                "Add to Cart",
                                bgcolor=RED,
                                color=WHITE,
                                on_click=lambda e, p=product: add_to_cart(p),
                            ),
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    ),
                ],
                spacing=10,
            ),
        )

    def show_home():
        content.controls.clear()
        content.controls.extend(
            [
                ft.Text(
                    "Shop Comics & Games",
                    size=24,
                    weight=ft.FontWeight.BOLD,
                    color=TEXT,
                ),
                search,
                ft.Text(
                    "Featured Comics",
                    size=18,
                    weight=ft.FontWeight.W_600,
                    color=NAVY,
                ),
            ]
        )
        for product in products:
            content.controls.append(product_card(product))
        page.update()

    def change_quantity(name, amount):
        cart[name]["quantity"] += amount
        if cart[name]["quantity"] <= 0:
            del cart[name]
        update_count()
        show_cart()

    def show_cart():
        content.controls.clear()
        content.controls.append(
            ft.Text(
                "Shopping Cart",
                size=24,
                weight=ft.FontWeight.BOLD,
                color=TEXT,
            )
        )

        total = 0
        quantity = 0

        for name, item in cart.items():
            qty = item["quantity"]
            total += item["price"] * qty
            quantity += qty

            content.controls.append(
                ft.Container(
                    bgcolor=WHITE,
                    border_radius=10,
                    padding=12,
                    content=ft.Column(
                        [
                            ft.Text(name, size=16, color=TEXT),
                            ft.Text(
                                f'${item["price"]:.2f}',
                                size=20,
                                weight=ft.FontWeight.BOLD,
                                color=RED,
                            ),
                            ft.Row(
                                [
                                    ft.IconButton(
                                        ft.Icons.REMOVE_CIRCLE_OUTLINE,
                                        on_click=lambda e, n=name:
                                            change_quantity(n, -1),
                                    ),
                                    ft.Text(str(qty), color=TEXT),
                                    ft.IconButton(
                                        ft.Icons.ADD_CIRCLE_OUTLINE,
                                        on_click=lambda e, n=name:
                                            change_quantity(n, 1),
                                    ),
                                ]
                            ),
                        ]
                    ),
                )
            )

        content.controls.append(
            ft.Container(
                bgcolor=WHITE,
                padding=15,
                content=ft.Column(
                    [
                        ft.Text(
                            f"Items: {len(cart)}     Qty: {quantity}",
                            color=TEXT,
                        ),
                        ft.Text(
                            f"Total: ${total:.2f}",
                            size=20,
                            weight=ft.FontWeight.BOLD,
                            color=RED,
                        ),
                        ft.ElevatedButton(
                            "Continue Shopping",
                            bgcolor=WHITE,
                            color=NAVY,
                            on_click=lambda e: show_home(),
                        ),
                    ]
                ),
            )
        )
        page.update()

    page.add(
        header(),
        ft.Container(
            padding=20,
            content=content,
        ),
    )

    show_home()


if __name__ == "__main__":
    ft.run(main)
