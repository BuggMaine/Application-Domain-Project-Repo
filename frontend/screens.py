"""Screens: Main Menu (home), Sign In, Create Account. Layout matches the Figma file."""
import flet as ft

import theme as t


def home(app):
    """Main Menu (Figma: 01 Home)."""
    items = [
        t.item_row(title, author, price, on_click=lambda e: app.toast("Item page comes with the next task"))
        for title, author, price in t.FEATURED_ITEMS
    ]
    content = ft.Column(
        scroll=ft.ScrollMode.AUTO,
        expand=True,
        horizontal_alignment=ft.CrossAxisAlignment.STRETCH,
        controls=[
            ft.Container(
                padding=16,
                content=ft.Column(
                    spacing=16,
                    horizontal_alignment=ft.CrossAxisAlignment.STRETCH,
                    controls=[
                        t.search_field(on_submit=lambda e: app.toast("Search comes with the next task")),
                        t.button("View Catalog", on_click=lambda e: app.toast("Catalog comes with the next task")),
                        ft.Text("Featured Items", size=18, weight=ft.FontWeight.BOLD, color=t.NAVY),
                        ft.Column(spacing=10, controls=items),
                    ],
                ),
            )
        ],
    )
    return ft.Column(spacing=0, expand=True, controls=[t.top_bar(app), t.order_strip(app), content])


def sign_in(app):
    """Sign In (Figma: S1 Sign In, plus S1b error text)."""
    email = t.text_field("Email", "name@example.com", ft.KeyboardType.EMAIL)
    phone = t.text_field("Phone number", "(555) 555-5555", ft.KeyboardType.PHONE)

    def submit(e):
        ok = True
        email.error = None if t.valid_email(email.value or "") else "Enter a valid email address, like name@example.com."
        phone.error = None if t.valid_phone(phone.value or "") else "Enter a valid 10-digit phone number."
        ok = email.error is None and phone.error is None
        app.page.update()
        if ok:
            # TODO (back end): check the account exists. For now any valid email + phone signs in.
            app.user = {"email": email.value.strip(), "phone": phone.value.strip()}
            app.toast("Signed in")
            app.go("home")

    body = ft.Container(
        padding=20,
        content=ft.Column(
            spacing=14,
            horizontal_alignment=ft.CrossAxisAlignment.STRETCH,
            controls=[
                ft.Text("Sign In", size=18, weight=ft.FontWeight.BOLD, color=t.NAVY),
                t.label("Sign in with your email and phone number to see your past orders.", 14, t.TEXT),
                email,
                phone,
                t.button("Sign In", on_click=submit),
                t.button("Create Account", on_click=lambda e: app.go("create_account"), kind="secondary"),
                ft.Container(
                    alignment=ft.Alignment.CENTER,
                    padding=8,
                    ink=True,
                    on_click=lambda e: app.go("home"),
                    content=ft.Text("Continue as guest", size=16, color=t.NAVY, weight=ft.FontWeight.BOLD),
                ),
            ],
        ),
    )
    return ft.Column(spacing=0, expand=True, controls=[t.top_bar(app), body])


def create_account(app):
    """Create Account (Figma: S2). Needs explicit consent before saving contact info."""
    email = t.text_field("Email", "name@example.com", ft.KeyboardType.EMAIL)
    phone = t.text_field("Phone number", "(555) 555-5555", ft.KeyboardType.PHONE)
    address = t.text_field("Address (optional)", "Street, city, state, ZIP")
    consent = ft.Checkbox(label="I agree that Dr. No's may keep my email and phone number to process my orders.", value=False)

    def submit(e):
        email.error = None if t.valid_email(email.value or "") else "Enter a valid email address, like name@example.com."
        phone.error = None if t.valid_phone(phone.value or "") else "Enter a valid 10-digit phone number."
        app.page.update()
        if email.error or phone.error:
            return
        if not consent.value:
            app.toast("Please agree to the terms to create an account")
            return
        # TODO (back end): save the account. For now it only lives in memory.
        app.user = {"email": email.value.strip(), "phone": phone.value.strip(), "address": (address.value or "").strip()}
        app.toast("Account created")
        app.go("home")

    body = ft.Column(
        scroll=ft.ScrollMode.AUTO,
        expand=True,
        horizontal_alignment=ft.CrossAxisAlignment.STRETCH,
        controls=[
            ft.Container(
                padding=20,
                content=ft.Column(
                    spacing=14,
                    horizontal_alignment=ft.CrossAxisAlignment.STRETCH,
                    controls=[
                        ft.Text("Create Account", size=18, weight=ft.FontWeight.BOLD, color=t.NAVY),
                        email,
                        phone,
                        address,
                        consent,
                        t.button("Create Account", on_click=submit),
                        t.button("Back to Sign In", on_click=lambda e: app.go("sign_in"), kind="secondary"),
                    ],
                ),
            )
        ],
    )
    return ft.Column(spacing=0, expand=True, controls=[t.top_bar(app), body])
