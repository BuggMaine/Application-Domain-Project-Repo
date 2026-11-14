"""Dr. No's Comics & Games web app (Flet).

Run from this folder:   flet run            (desktop window)
                        flet run --web      (in a browser; resize it to test phone sizes)
"""
import random
from datetime import date

import flet as ft

import data
import screens
import theme as t

SCREENS = {
    "sign_in": screens.sign_in, "home": screens.home, "catalogs": screens.catalogs, "cart": screens.cart,
    "complete_order": screens.complete_order, "confirmation": screens.confirmation,
    "order_history": screens.order_history, "about_devs": screens.about_devs,
}


class App:
    """App state + navigation."""

    def __init__(self, page: ft.Page):
        self.page = page
        self.user = None            # {"email": ...} once signed in
        self.entered = False        # True after sign in OR "Continue as guest" (the side bar stays locked until then)
        self.cart = {}              # product id -> {"product": p, "qty": n}   (reset on sign out)
        self.orders = list(data.SAMPLE_ORDERS)   # in memory only; TODO back end
        self.last_order = None
        self.featured = []
        self._order_no = 1043

        page.title = "Dr. No's Comics & Games"
        page.padding = 0
        page.bgcolor = t.BACKGROUND
        page.theme_mode = ft.ThemeMode.LIGHT
        page.theme = ft.Theme(color_scheme_seed=t.NAVY)
        try:
            page.window.width = 390
            page.window.height = 844
        except Exception:
            pass

        self.frame = ft.Container(expand=True, width=t.MAX_WIDTH)
        self.root = ft.Container(expand=True, bgcolor=t.BACKGROUND, alignment=ft.Alignment.TOP_CENTER, content=self.frame)
        self._build_overlays()
        page.add(ft.SafeArea(expand=True, content=self.root))
        try:
            page.on_resize = lambda e: self._fit()
        except Exception:
            pass
        self._fit()
        self.go("sign_in")

    def _fit(self):
        w = getattr(self.page, "width", None) or t.MAX_WIDTH
        self.frame.width = min(w, t.MAX_WIDTH)
        try:
            self.page.update()
        except Exception:
            pass

    # ---- navigation -------------------------------------------------------
    def go(self, name, **kw):
        self.close_overlays()
        self.frame.content = SCREENS[name](self, **kw)
        self.page.update()

    def show_item(self, p):
        self.close_overlays()
        self.frame.content = screens.item_detail(self, p)
        self.page.update()

    def show_shop(self, query=""):
        self.close_overlays()
        self.frame.content = screens.shop(self, query)
        self.page.update()

    def toast(self, message):
        self.page.show_dialog(ft.SnackBar(ft.Text(message)))

    # ---- sign in / out ------------------------------------------------------
    def _enter(self):
        self.entered = True
        pool = [p for p in data.PRODUCTS if p["featured"]]
        self.featured = random.sample(pool, min(4, len(pool)))   # new random set every time someone enters
        self.go("home")

    def sign_in(self, email):
        self.user = {"email": email}
        self._enter()

    def enter_as_guest(self):
        self.user = None
        self._enter()

    def sign_out(self):
        self.user, self.entered, self.cart, self.last_order = None, False, {}, None   # cart resets on log out
        self.go("sign_in")

    # ---- cart -----------------------------------------------------------------
    def cart_summary(self):
        subtotal = sum(l["product"]["price"] * l["qty"] for l in self.cart.values() if l["product"]["price"] is not None)
        pi = sum(1 for l in self.cart.values() if l["product"]["price"] is None)
        return {"items": len(self.cart), "qty": sum(l["qty"] for l in self.cart.values()), "subtotal": subtotal, "pi": pi,
                "total": f"${subtotal:.2f}" + (" + PI" if pi else "")}

    def add_to_cart(self, p, qty=1):
        line = self.cart.setdefault(p["id"], {"product": p, "qty": 0})
        line["qty"] += qty
        self._show_added(p, qty)

    def change_qty(self, pid, delta):
        self.cart[pid]["qty"] += delta
        if self.cart[pid]["qty"] <= 0:
            del self.cart[pid]
        self.go("cart")

    def remove_from_cart(self, pid):
        self.cart.pop(pid, None)
        self.go("cart")

    def reorder(self, order):
        for pid, q in order["items"]:
            line = self.cart.setdefault(pid, {"product": data.BY_ID[pid], "qty": 0})
            line["qty"] += q
        self.go("cart")

    def place_order(self, email, phone):
        s = self.cart_summary()
        self.last_order = {"number": f"DN-{self._order_no}", "date": f"{date.today():%b} {date.today().day}, {date.today().year}",
                           "items": [(pid, l["qty"]) for pid, l in self.cart.items()], "total": s["total"], "email": email, "phone": phone}
        self._order_no += 1
        self.orders.insert(0, self.last_order)
        # TODO (back end): auto-create the order email to Dr. No's (their format) and send the customer a receipt.
        self.cart = {}
        self.go("confirmation")

    # ---- overlays: side bar + "added to cart" sheet ----------------------------
    def _build_overlays(self):
        self.scrim = ft.Container(left=0, right=0, top=0, bottom=0, bgcolor=t.SCRIM, visible=False, on_click=lambda e: self.close_overlays())
        self.panel = ft.Container(left=0, top=0, bottom=0, width=300, bgcolor=t.WHITE, padding=ft.Padding.all(20),
                                  offset=ft.Offset(-1.05, 0), animate_offset=ft.Animation(250, ft.AnimationCurve.EASE_OUT))
        self.sheet = ft.Container(left=0, right=0, bottom=0, bgcolor=t.WHITE, visible=False, padding=ft.Padding.all(24),
                                  border_radius=ft.BorderRadius.only(top_left=20, top_right=20))
        for c in (self.scrim, self.panel, self.sheet):
            self.page.overlay.append(c)

    def close_overlays(self):
        self.scrim.visible = False
        self.panel.offset = ft.Offset(-1.05, 0)
        self.sheet.visible = False
        self.page.update()

    def open_sidebar(self):
        if not self.entered:          # locked until signed in or guest
            return
        self.panel.content = self._sidebar_content()
        self.scrim.visible = True
        self.panel.offset = ft.Offset(0, 0)
        self.page.update()

    def _show_added(self, p, qty):
        check = ft.Container(width=56, height=56, bgcolor=t.SUCCESS, border_radius=28, alignment=ft.Alignment.CENTER, content=ft.Icon(ft.Icons.CHECK, color=t.WHITE))
        self.sheet.content = ft.Column(spacing=14, horizontal_alignment=ft.CrossAxisAlignment.STRETCH, controls=[
            ft.Row(alignment=ft.MainAxisAlignment.CENTER, controls=[check]),
            ft.Text("Added to cart", size=18, weight=ft.FontWeight.BOLD, color=t.NAVY, text_align=ft.TextAlign.CENTER),
            t.label(f"{p['title']} × {qty}", 16, t.MUTED, align=ft.TextAlign.CENTER),
            t.button("View Cart", on_click=lambda e: self.go("cart")),
            t.button("Continue Shopping", on_click=lambda e: self.show_shop(""), kind="secondary")])
        self.scrim.visible = True
        self.sheet.visible = True
        self.page.update()

    def _sidebar_content(self):
        def block(title, lines):
            return ft.Column(spacing=2, controls=[t.label(title, 12, t.MUTED)] + [t.label(x, 16) for x in lines])
        deals = ft.Container(bgcolor=t.YELLOW, border_radius=10, padding=ft.Padding.symmetric(horizontal=14, vertical=12), content=ft.Column(spacing=4, controls=[
            t.label("Online deals", 14, t.NAVY, bold=True), t.label("Current mailing and order discounts show here.", 12, t.NAVY)]))
        auth = (t.button("Sign Out", on_click=lambda e: self.sign_out(), kind="secondary") if self.user
                else t.button("Sign In", on_click=lambda e: self._to_sign_in(), kind="secondary"))
        return ft.Column(scroll=ft.ScrollMode.AUTO, spacing=14, horizontal_alignment=ft.CrossAxisAlignment.STRETCH, controls=[
            ft.Row(alignment=ft.MainAxisAlignment.SPACE_BETWEEN, vertical_alignment=ft.CrossAxisAlignment.CENTER, controls=[
                t.heading("Store Info"), ft.IconButton(icon=ft.Icons.CLOSE, on_click=lambda e: self.close_overlays())]),
            block("HOURS", ["Mon–Sat: 11am – 8pm", "Sunday: 12pm – 6pm"]),
            t.label("Open 363 days a year. Closed Thanksgiving and Christmas. Curbside pick-up available.", 12, t.MUTED),
            block("CONTACT", ["(770) 422-4642", "(678) 903-3705", "manager@drnos.com"]),
            t.label("3372 Canton Rd #104, Marietta GA 30066", 14, t.MUTED), deals,
            t.button("Order History", on_click=lambda e: self.go("order_history"), kind="secondary"),
            t.button("About Devs", on_click=lambda e: self.go("about_devs"), kind="secondary"), auth])

    def _to_sign_in(self):
        self.entered = False
        self.go("sign_in")


def main(page: ft.Page):
    App(page)


ft.run(main)
