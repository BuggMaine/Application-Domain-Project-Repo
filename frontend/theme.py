"""Shared colors, sample data, and reusable widgets.

Everything here comes from the Figma style guide, so every screen looks the same.
Change a color here and it changes everywhere.
"""
import re

import flet as ft

# ---- Colors (Figma style guide) -------------------------------------------
RED = "#D92B20"          # Brand/Red (logo red)
NAVY = "#1B3358"         # Brand/Navy (top bar)
BLUE = "#4A86D8"         # Brand/Blue (links)
YELLOW = "#F7DC3F"       # Brand/Yellow (accent, like the Discord buttons)
BACKGROUND = "#71A1E4"   # Surface/Background Blue (same blue as drnos.com)
WHITE = "#FFFFFF"
TEXT = "#1B2A44"         # Text/Primary
MUTED = "#5B6B85"        # Text/Muted
BORDER = "#CBD6E6"       # Border/Default
ERROR = "#B3261E"        # Status/Error
SCRIM = "#73000000"      # 45% black behind the side bar

# ---- Sample data (replaced by the back end later) ---------------------------
FEATURED_ITEMS = [
    ("Amazing Spider-Man #1", "Stan Lee", "$4.99"),
    ("X-Men #12", "Chris Claremont", "$3.99"),
    ("Batman: Year One", "Frank Miller", "$14.99"),
]

# ---- Validation -----------------------------------------------------------
_EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def valid_email(value: str) -> bool:
    return bool(_EMAIL_RE.match(value.strip()))


def valid_phone(value: str) -> bool:
    digits = re.sub(r"\D", "", value)
    return len(digits) == 10 or (len(digits) == 11 and digits.startswith("1"))


# ---- Small helpers --------------------------------------------------------
def label(text, size=14, color=TEXT, bold=False):
    return ft.Text(text, size=size, color=color, weight=ft.FontWeight.BOLD if bold else None)


def wordmark(size=22):
    """The 'Dr. No's' text: red letters with a yellow outline, like the store logo."""
    try:
        style = dict(size=size, weight=ft.FontWeight.BOLD, italic=True)
        outline = ft.Text(
            "Dr. No's",
            style=ft.TextStyle(
                foreground=ft.Paint(color=YELLOW, stroke_width=5, style=ft.PaintingStyle.STROKE),
                **style,
            ),
        )
        fill = ft.Text("Dr. No's", style=ft.TextStyle(color=RED, **style))
        return ft.Stack(controls=[outline, fill], width=size * 4.2, height=size * 1.5)
    except Exception:  # if this Flet version rejects outlined text, fall back to plain red text
        return ft.Text("Dr. No's", size=size, weight=ft.FontWeight.BOLD, color=RED)


def button(text, on_click=None, kind="primary"):
    """kind: 'primary' (red), 'secondary' (white + navy outline), 'accent' (yellow)."""
    styles = {
        "primary": (RED, WHITE, None),
        "secondary": (WHITE, NAVY, ft.Border.all(2, NAVY)),
        "accent": (YELLOW, NAVY, ft.Border.all(2, NAVY)),
    }
    bg, fg, border = styles[kind]
    return ft.Container(
        content=ft.Text(text, color=fg, size=16, weight=ft.FontWeight.BOLD, text_align=ft.TextAlign.CENTER),
        alignment=ft.Alignment.CENTER,
        bgcolor=bg,
        border=border,
        border_radius=12,
        padding=ft.Padding.symmetric(horizontal=24, vertical=14),
        ink=True,
        on_click=on_click,
    )


def text_field(label_text, hint, keyboard_type=None):
    return ft.TextField(
        label=label_text,
        hint_text=hint,
        keyboard_type=keyboard_type,
        bgcolor=WHITE,
        border_color=BORDER,
        border_radius=10,
    )


def search_field(on_submit=None):
    return ft.TextField(
        hint_text="Search comics by title, author…",
        prefix_icon=ft.Icons.SEARCH,
        bgcolor=WHITE,
        border_color=BORDER,
        border_radius=24,
        on_submit=on_submit,
    )


def item_row(title, author, price, on_click=None):
    """The long rectangle Buck asked for: name, author, price."""
    return ft.Container(
        bgcolor=WHITE,
        border=ft.Border.all(1, BORDER),
        border_radius=12,
        padding=ft.Padding.symmetric(horizontal=16, vertical=14),
        ink=True,
        on_click=on_click,
        content=ft.Row(
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                ft.Column(spacing=2, expand=True, controls=[label(title, 16), label(author, 14, MUTED)]),
                ft.Text(price, size=20, weight=ft.FontWeight.BOLD, color=RED),
            ],
        ),
    )


def top_bar(app):
    """Navy bar: menu button (opens the side bar), wordmark, cart count."""
    return ft.Container(
        bgcolor=NAVY,
        padding=ft.Padding.symmetric(horizontal=8, vertical=6),
        content=ft.Row(
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                ft.IconButton(icon=ft.Icons.MENU, icon_color=WHITE, on_click=lambda e: app.open_sidebar()),
                wordmark(),
                ft.Container(
                    padding=ft.Padding.only(right=8),
                    content=ft.Text(f"Cart ({app.cart['items']})", color=WHITE, size=14),
                ),
            ],
        ),
    )


def order_strip(app):
    """Top line Buck asked for: items, quantity, running total."""
    c = app.cart
    return ft.Container(
        bgcolor=WHITE,
        padding=ft.Padding.symmetric(horizontal=16, vertical=8),
        content=ft.Row(
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            controls=[
                label(f"Items: {c['items']}"),
                label(f"Qty: {c['qty']}"),
                label(f"Total: {c['total']}", color=NAVY),
            ],
        ),
    )
