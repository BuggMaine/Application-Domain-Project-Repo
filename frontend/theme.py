"""Colors, validation, and reusable widgets. Values match design-tokens.css / the Figma style guide."""
import re

import flet as ft

RED = "#D92B20"
NAVY = "#1B3358"
BLUE = "#4A86D8"
YELLOW = "#F7DC3F"
BACKGROUND = "#71A1E4"   # same blue as drnos.com
WHITE = "#FFFFFF"
TEXT = "#1B2A44"
MUTED = "#5B6B85"        # only on white cards
BORDER = "#CBD6E6"
SUCCESS = "#1F8A4C"
ERROR_ON_BLUE = "#8A1008"
SCRIM = "#73000000"
MAX_WIDTH = 480          # keep content phone-sized on big screens

_EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def valid_email(v):
    return bool(_EMAIL_RE.match((v or "").strip()))


def valid_phone(v):
    d = re.sub(r"\D", "", v or "")
    return len(d) == 10 or (len(d) == 11 and d.startswith("1"))


def money(p):
    return "PI" if p["price"] is None else f"${p['price']:.2f}"


def label(text, size=14, color=TEXT, bold=False, align=None):
    return ft.Text(text, size=size, color=color, weight=ft.FontWeight.BOLD if bold else None, text_align=align)


def heading(text, size=18, color=NAVY):
    return ft.Text(text, size=size, weight=ft.FontWeight.BOLD, color=color)


def wordmark(app=None, size=22):
    """Red italic 'Dr. No's' with a yellow outline. Click it to go Home."""
    try:
        base = dict(size=size, weight=ft.FontWeight.BOLD, italic=True)
        outline = ft.Text("Dr. No's", style=ft.TextStyle(foreground=ft.Paint(color=YELLOW, stroke_width=5, style=ft.PaintingStyle.STROKE), **base))
        fill = ft.Text("Dr. No's", style=ft.TextStyle(color=RED, **base))
        logo = ft.Stack(controls=[outline, fill], width=size * 4.2, height=size * 1.5)
    except Exception:
        logo = ft.Text("Dr. No's", size=size, weight=ft.FontWeight.BOLD, color=RED)
    return ft.Container(content=logo, on_click=(lambda e: app.go("home")) if app and app.entered else None)


def button(text, on_click=None, kind="primary"):
    """kind: primary (red) | secondary (white, navy outline) | accent (yellow, navy outline)."""
    bg, fg, border = {"primary": (RED, WHITE, None), "secondary": (WHITE, NAVY, ft.Border.all(2, NAVY)), "accent": (YELLOW, NAVY, ft.Border.all(2, NAVY))}[kind]
    return ft.Container(
        content=ft.Text(text, color=fg, size=16, weight=ft.FontWeight.BOLD, text_align=ft.TextAlign.CENTER),
        alignment=ft.Alignment.CENTER, bgcolor=bg, border=border, border_radius=12,
        padding=ft.Padding.symmetric(horizontal=24, vertical=14), ink=True, on_click=on_click)


def card(content, padding=14, on_click=None):
    return ft.Container(content=content, bgcolor=WHITE, border=ft.Border.all(1, BORDER), border_radius=12,
                        padding=padding, on_click=on_click, ink=bool(on_click))


def chip(text, selected, on_click):
    return ft.Container(
        content=ft.Text(text, size=14, color=WHITE if selected else TEXT),
        bgcolor=NAVY if selected else WHITE, border=ft.Border.all(1, NAVY if selected else BORDER),
        border_radius=20, padding=ft.Padding.symmetric(horizontal=14, vertical=8), ink=True, on_click=on_click)


def text_field(label_text, hint, value="", keyboard_type=None):
    return ft.TextField(label=label_text, hint_text=hint, value=value, keyboard_type=keyboard_type,
                        bgcolor=WHITE, border_color=BORDER, border_radius=10)


def search_field(value="", on_submit=None, on_change=None):
    return ft.TextField(hint_text="Search comics by title, author…", value=value, prefix_icon=ft.Icons.SEARCH,
                        bgcolor=WHITE, border_color=BORDER, border_radius=24, on_submit=on_submit, on_change=on_change)


def item_row(p, on_click):
    """Long rectangle: name + author on the left, red price on the right."""
    return card(ft.Row(
        alignment=ft.MainAxisAlignment.SPACE_BETWEEN, vertical_alignment=ft.CrossAxisAlignment.CENTER,
        controls=[ft.Column(spacing=2, expand=True, controls=[label(p["title"], 16), label(p["author"], 14, MUTED)]),
                  ft.Text(money(p), size=20, weight=ft.FontWeight.BOLD, color=RED)]),
        padding=ft.Padding.symmetric(horizontal=16, vertical=14), on_click=on_click)


def _round_btn(symbol, on_click):
    return ft.Container(content=ft.Text(symbol, size=18, weight=ft.FontWeight.BOLD, color=NAVY), width=36, height=36,
                        alignment=ft.Alignment.CENTER, bgcolor=WHITE, border=ft.Border.all(1.5, NAVY), border_radius=18,
                        ink=True, on_click=on_click)


def stepper(qty, on_minus, on_plus):
    """Returns (row, qty_text) so the caller can update the number."""
    qty_text = ft.Text(str(qty), size=18, weight=ft.FontWeight.BOLD, color=TEXT)
    return ft.Row(spacing=14, vertical_alignment=ft.CrossAxisAlignment.CENTER,
                  controls=[_round_btn("−", on_minus), qty_text, _round_btn("+", on_plus)]), qty_text


def top_bar(app, signed_in=True):
    """Navy bar. Logo is centered (equal 44px slots). Signed-out bar has no menu or cart."""
    slot = 44
    left = ft.Container(width=slot, height=40)
    right = ft.Container(width=slot, height=40)
    if signed_in:
        n = app.cart_summary()["items"]
        left = ft.Container(width=slot, height=40, content=ft.IconButton(icon=ft.Icons.MENU, icon_color=WHITE, on_click=lambda e: app.open_sidebar()))
        badge = ft.Container(visible=n > 0, width=17, height=17, bgcolor=RED, border=ft.Border.all(1.5, YELLOW), border_radius=9,
                             alignment=ft.Alignment.CENTER, right=0, top=0,
                             content=ft.Text(str(n), size=10, color=WHITE, weight=ft.FontWeight.BOLD))
        right = ft.Container(width=slot, height=40, content=ft.Stack(controls=[
            ft.IconButton(icon=ft.Icons.SHOPPING_CART, icon_color=WHITE, on_click=lambda e: app.go("cart")), badge]))
    return ft.Container(bgcolor=NAVY, padding=ft.Padding.symmetric(horizontal=8, vertical=8), content=ft.Row(
        alignment=ft.MainAxisAlignment.SPACE_BETWEEN, vertical_alignment=ft.CrossAxisAlignment.CENTER,
        controls=[left, wordmark(app), right]))


def order_strip(app):
    s = app.cart_summary()
    return ft.Container(bgcolor=WHITE, padding=ft.Padding.symmetric(horizontal=16, vertical=8), content=ft.Row(
        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        controls=[label(f"Items: {s['items']}"), label(f"Qty: {s['qty']}"), label(f"Total: {s['total']}", color=NAVY)]))


def screen(app, controls, signed_in=True, strip=True):
    """Standard page: top bar, optional order strip, then scrolling content padded 16px."""
    body = ft.Column(scroll=ft.ScrollMode.AUTO, expand=True, horizontal_alignment=ft.CrossAxisAlignment.STRETCH, controls=[
        ft.Container(padding=16, content=ft.Column(spacing=16, horizontal_alignment=ft.CrossAxisAlignment.STRETCH, controls=controls))])
    parts = [top_bar(app, signed_in)] + ([order_strip(app)] if strip and signed_in else []) + [body]
    return ft.Column(spacing=0, expand=True, controls=parts)
