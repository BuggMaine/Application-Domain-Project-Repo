"""All screens, matching the Figma file (phone layout)."""
import inspect

import flet as ft

import data
import theme as t


async def _open_url(app, url):
    try:
        result = app.page.launch_url(url)
        if inspect.isawaitable(result):
            await result
    except Exception:
        app.toast("Couldn't open the link: " + url)


# ---------------------------------------------------------------- Sign in
def sign_in(app):
    """Email only: no password, no code, no phone (per Reese/Buck)."""
    email = t.text_field("Email", "name@example.com", keyboard_type=ft.KeyboardType.EMAIL)

    def submit(e):
        email.error = None if t.valid_email(email.value) else "Enter a valid email address, like name@example.com."
        app.page.update()
        if email.error is None:
            app.sign_in(email.value.strip())

    return t.screen(app, [
        heading_("Sign In"),
        t.label("Enter your email to sign in. No password needed.", 14),
        email,
        t.button("Sign In", on_click=submit),
        t.label("By continuing, you agree Dr. No's may keep your email to sign you in and send receipts.", 12),
        ft.Container(alignment=ft.Alignment.CENTER, padding=8, ink=True, on_click=lambda e: app.enter_as_guest(),
                     content=ft.Text("Continue as guest", size=16, color=t.NAVY, weight=ft.FontWeight.BOLD)),
    ], signed_in=False, strip=False)


def heading_(text):
    return t.heading(text)


# ---------------------------------------------------------------- Home
def home(app):
    rows = [t.item_row(p, on_click=lambda e, p=p: app.show_item(p)) for p in app.featured]
    return t.screen(app, [
        t.search_field(on_submit=lambda e: app.show_shop(e.control.value or "")),
        t.button("View Catalog", on_click=lambda e: app.go("catalogs")),
        heading_("Featured Items"),
        ft.Column(spacing=10, controls=rows),
    ])


# ---------------------------------------------------------------- Shop (All Items) with search + filters
def shop(app, query=""):
    st = {"author": "", "publisher": "", "price": None, "open": False}
    results = ft.Column(spacing=10)
    count = t.label("", 14)
    search = t.search_field(value=query)
    author = t.text_field("Author / creator", "e.g. Stan Lee")
    publisher = t.text_field("Publisher", "e.g. Marvel Comics")
    chips = ft.Row(wrap=True, spacing=8, run_spacing=8)
    panel = ft.Container(visible=False, content=t.card(ft.Column(spacing=12, controls=[
        t.heading("Filters"), author, publisher, t.label("Price", 14, t.MUTED), chips]), padding=16))

    def build_results(found):
        count.value = f"{len(found)} item" + ("" if len(found) == 1 else "s")
        if found:
            return [t.item_row(p, on_click=lambda e, p=p: app.show_item(p)) for p in found]
        return [ft.Container(padding=ft.Padding.symmetric(vertical=32), alignment=ft.Alignment.CENTER, content=ft.Column(
            horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=8, controls=[
                t.heading("No results found"), t.label("Try a different title, author, or publisher, or clear your filters.", 14, align=ft.TextAlign.CENTER),
                ft.Container(width=200, content=t.button("Clear Filters", on_click=clear, kind="secondary"))]))]

    def refresh(e=None):
        st["author"], st["publisher"] = author.value or "", publisher.value or ""
        results.controls = build_results(data.filter_products(search.value or "", st["author"], st["publisher"], st["price"]))
        app.page.update()

    def pick(price):
        st["price"] = None if st["price"] == price else price
        draw_chips(); refresh()

    def draw_chips():
        chips.controls = [t.chip("PI (Please inquire)" if c == "PI" else c, st["price"] == c, lambda e, c=c: pick(c)) for c in data.PRICE_CHIPS]

    def clear(e=None):
        search.value = author.value = publisher.value = ""
        st["price"] = None
        draw_chips(); refresh()

    def toggle(e):
        panel.visible = not panel.visible
        app.page.update()

    search.on_change = refresh; author.on_change = refresh; publisher.on_change = refresh
    draw_chips()
    filters_btn = ft.Container(content=ft.Text("Filters", size=14, color=t.TEXT), bgcolor=t.WHITE, border=ft.Border.all(1, t.BORDER),
                               border_radius=20, padding=ft.Padding.symmetric(horizontal=14, vertical=8), ink=True, on_click=toggle)
    page = t.screen(app, [
        heading_("All Items"), search,
        ft.Row(alignment=ft.MainAxisAlignment.SPACE_BETWEEN, vertical_alignment=ft.CrossAxisAlignment.CENTER, controls=[count, filters_btn]),
        panel, results])
    results.controls = build_results(data.filter_products(query))
    return page


# ---------------------------------------------------------------- Item detail
def item_detail(app, p):
    qty = {"n": 1}
    stepper_row, qty_text = t.stepper(1, lambda e: bump(-1), lambda e: bump(1))

    def bump(d):
        qty["n"] = max(1, qty["n"] + d)
        qty_text.value = str(qty["n"])
        app.page.update()

    if p.get("cover_url"):
        cover = ft.Image(src=p["cover_url"], width=140, height=190, fit="contain")
    else:
        cover = ft.Container(width=140, height=190, bgcolor=t.WHITE, border=ft.Border.all(1, t.BORDER), border_radius=8,
                             alignment=ft.Alignment.CENTER, content=t.label("Cover image", 12, t.MUTED))
    details = [("Publisher", p["publisher"] or "—"), ("Issue", f"#{p['issue']}" if p["issue"] else "—"),
               ("Release date", p["release_date"] or "—"), ("Base title", p["base_title"] or "—")]
    detail_rows = [ft.Row(alignment=ft.MainAxisAlignment.SPACE_BETWEEN, controls=[t.label(k, 14, t.MUTED), t.label(v, 14)]) for k, v in details]
    controls = [
        ft.Row(alignment=ft.MainAxisAlignment.CENTER, controls=[cover]),
        t.label("Cover images load from Dr. No's website or the publisher.", 12, align=ft.TextAlign.CENTER),
        ft.Text(p["title"], size=24, weight=ft.FontWeight.BOLD, color=t.TEXT),
        ft.Row(alignment=ft.MainAxisAlignment.SPACE_BETWEEN, vertical_alignment=ft.CrossAxisAlignment.CENTER, controls=[
            t.label("by " + p["author"], 16), ft.Text(t.money(p), size=20, weight=ft.FontWeight.BOLD, color=t.RED)]),
    ]
    if p["price"] is None:
        controls.append(t.label("Price on inquiry (PI). Add it to your order with a quantity and the store will confirm the price.", 12))
    controls += [
        t.label("About this comic", 14, t.TEXT, bold=True), t.label(p["description"], 16),
        t.card(ft.Column(spacing=8, controls=detail_rows)),
        ft.Row(alignment=ft.MainAxisAlignment.SPACE_BETWEEN, vertical_alignment=ft.CrossAxisAlignment.CENTER, controls=[t.label("Quantity", 16), stepper_row]),
        t.button("Add to Cart", on_click=lambda e: app.add_to_cart(p, qty["n"])),
    ]
    return t.screen(app, controls)


# ---------------------------------------------------------------- Cart
def cart(app):
    s = app.cart_summary()
    controls = [heading_("Your Cart")]
    if not app.cart:
        controls += [ft.Container(padding=ft.Padding.symmetric(vertical=40), alignment=ft.Alignment.CENTER, content=ft.Column(
            horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=8, controls=[
                t.heading("Your cart is empty"), t.label("Add a comic from the shop to get started.", 14),
                ft.Container(width=240, content=t.button("Browse Items", on_click=lambda e: app.show_shop("")))]))]
        return t.screen(app, controls)
    for pid, line in app.cart.items():
        p = line["product"]
        row, _ = t.stepper(line["qty"], lambda e, pid=pid: app.change_qty(pid, -1), lambda e, pid=pid: app.change_qty(pid, 1))
        price = t.money(p) if p["price"] is None else f"${p['price'] * line['qty']:.2f}"
        controls.append(t.card(ft.Column(spacing=8, controls=[
            ft.Row(alignment=ft.MainAxisAlignment.SPACE_BETWEEN, controls=[t.label(p["title"], 16), ft.Text(price, size=20, weight=ft.FontWeight.BOLD, color=t.RED)]),
            t.label(p["author"], 14, t.MUTED),
            ft.Row(alignment=ft.MainAxisAlignment.SPACE_BETWEEN, vertical_alignment=ft.CrossAxisAlignment.CENTER, controls=[
                row, ft.Container(content=t.label("Remove", 14, t.BLUE), ink=True, on_click=lambda e, pid=pid: app.remove_from_cart(pid))])])))
    controls.append(summary_card(app))
    controls += [t.button("Complete Order", on_click=lambda e: app.go("complete_order")),
                 t.button("Continue Shopping", on_click=lambda e: app.show_shop(""), kind="secondary")]
    return t.screen(app, controls)


def summary_card(app):
    s = app.cart_summary()
    rows = [("Subtotal (priced items)", f"${s['subtotal']:.2f}")]
    if s["pi"]:
        rows.append(("PI items (price to be confirmed)", f"{s['pi']} item" + ("" if s["pi"] == 1 else "s")))
    lines = [ft.Row(alignment=ft.MainAxisAlignment.SPACE_BETWEEN, controls=[t.label(k, 14, t.MUTED), t.label(v, 14)]) for k, v in rows]
    lines.append(ft.Row(alignment=ft.MainAxisAlignment.SPACE_BETWEEN, controls=[t.label("Total so far", 16), ft.Text(f"${s['subtotal']:.2f}", size=20, weight=ft.FontWeight.BOLD, color=t.RED)]))
    return t.card(ft.Column(spacing=8, controls=lines))


# ---------------------------------------------------------------- Complete order + confirmation (no shipping/payment)
def complete_order(app):
    email = t.text_field("Email", "name@example.com", value=(app.user or {}).get("email", ""), keyboard_type=ft.KeyboardType.EMAIL)
    phone = t.text_field("Phone number", "(555) 555-5555", keyboard_type=ft.KeyboardType.PHONE)

    def submit(e):
        email.error = None if t.valid_email(email.value) else "Enter a valid email address, like name@example.com."
        phone.error = None if t.valid_phone(phone.value) else "Enter a valid 10-digit phone number."
        app.page.update()
        if not email.error and not phone.error:
            app.place_order(email.value.strip(), phone.value.strip())

    if not app.cart:
        return cart(app)
    return t.screen(app, [heading_("Complete Order"), email, phone, summary_card(app),
                          t.label("A receipt will be emailed to you.", 12), t.button("Complete Order", on_click=submit)])


def confirmation(app):
    o = app.last_order
    lines = [ft.Row(alignment=ft.MainAxisAlignment.SPACE_BETWEEN, controls=[t.label(f"{data.BY_ID[pid]['title']} × {q}", 14), t.label(t.money(data.BY_ID[pid]), 14)]) for pid, q in o["items"]]
    lines.append(ft.Row(alignment=ft.MainAxisAlignment.SPACE_BETWEEN, controls=[t.label("Total so far", 16), ft.Text(o["total"], size=20, weight=ft.FontWeight.BOLD, color=t.RED)]))
    check = ft.Container(width=56, height=56, bgcolor=t.SUCCESS, border_radius=28, alignment=ft.Alignment.CENTER, content=ft.Icon(ft.Icons.CHECK, color=t.WHITE))
    return t.screen(app, [
        ft.Row(alignment=ft.MainAxisAlignment.CENTER, controls=[check]),
        ft.Text("Order complete!", size=24, weight=ft.FontWeight.BOLD, color=t.NAVY, text_align=ft.TextAlign.CENTER),
        t.label(f"Order #{o['number']}", 16, t.TEXT, align=ft.TextAlign.CENTER),
        t.label(f"A receipt has been emailed to {o['email']}", 16, align=ft.TextAlign.CENTER),
        t.card(ft.Column(spacing=8, controls=lines)),
        t.button("Back to Home", on_click=lambda e: app.go("home")),
        t.button("Order History", on_click=lambda e: app.go("order_history"), kind="secondary")])


# ---------------------------------------------------------------- Catalogs: dropdown of current + older catalogs
def catalogs(app):
    st = {"i": 0, "open": False}
    value = ft.Text(data.CATALOGS[0], size=16, color=t.TEXT)
    menu = ft.Container(visible=False)

    def draw():
        value.value = data.CATALOGS[st["i"]]
        menu.visible = st["open"]
        menu.content = ft.Container(bgcolor=t.WHITE, border=ft.Border.all(1, t.BORDER), border_radius=10, content=ft.Column(spacing=0, controls=[
            ft.Container(padding=ft.Padding.symmetric(horizontal=16, vertical=12), bgcolor=t.BACKGROUND if i == st["i"] else None, ink=True,
                         on_click=lambda e, i=i: choose(i), content=t.label(name, 16)) for i, name in enumerate(data.CATALOGS)]))
        app.page.update()

    def choose(i):
        st["i"], st["open"] = i, False
        draw()

    def toggle(e):
        st["open"] = not st["open"]
        draw()

    async def open_catalog(e):
        await _open_url(app, data.CATALOG_URL)   # TODO: one link per catalog

    field = ft.Container(content=ft.Row(alignment=ft.MainAxisAlignment.SPACE_BETWEEN, vertical_alignment=ft.CrossAxisAlignment.CENTER, controls=[
        value, ft.Icon(ft.Icons.ARROW_DROP_DOWN, color=t.NAVY)]), bgcolor=t.WHITE, border=ft.Border.all(1, t.BORDER), border_radius=10,
        padding=ft.Padding.symmetric(horizontal=16, vertical=14), ink=True, on_click=toggle)
    draw_ready = t.screen(app, [heading_("Catalogs"), t.label("Choose a catalog from the list to read or download it. It opens on Dr. No's website.", 14),
                                t.label("Choose a catalog", 14), field, menu, t.button("Open Catalog", on_click=open_catalog)])
    return draw_ready


# ---------------------------------------------------------------- Order history with quantities
def order_history(app):
    controls = [heading_("Order History"), t.label("Your past orders and how many of each item you ordered.", 14)]
    for o in app.orders:
        lines = [ft.Row(alignment=ft.MainAxisAlignment.SPACE_BETWEEN, controls=[t.label("Item", 12, t.MUTED), t.label("Qty", 12, t.MUTED)])]
        lines += [ft.Row(alignment=ft.MainAxisAlignment.SPACE_BETWEEN, controls=[t.label(data.BY_ID[pid]["title"], 14), t.label(f"× {q}", 14)]) for pid, q in o["items"]]
        controls.append(t.card(ft.Column(spacing=8, controls=[
            ft.Row(alignment=ft.MainAxisAlignment.SPACE_BETWEEN, controls=[t.label(f"Order #{o['number']}", 16), ft.Text(o.get("total") or data.order_total(o["items"]), size=20, weight=ft.FontWeight.BOLD, color=t.RED)]),
            t.label(o["date"], 12, t.MUTED), ft.Column(spacing=4, controls=lines),
            t.button("Reorder", on_click=lambda e, o=o: app.reorder(o), kind="accent")]), padding=16))
    return t.screen(app, controls)


# ---------------------------------------------------------------- About devs
def about_devs(app):
    team = [("Reese Mothershed", "Team member"), ("Steven Thai", "Team member"), ("Amber Turner", "UI/UX designer"),
            ("Kartik Negi", "Prototype review"), ("Isaiah Johnson", "Front-end developer"), ("Yaho Noudou Frank", "Back-end developer")]
    rows = [t.card(ft.Row(spacing=12, vertical_alignment=ft.CrossAxisAlignment.CENTER, controls=[
        ft.Container(width=40, height=40, border_radius=20, bgcolor=t.BACKGROUND, alignment=ft.Alignment.CENTER, content=t.label("Photo", 10, t.TEXT)),
        ft.Column(spacing=0, controls=[t.label(n, 16), t.label(r, 12, t.MUTED)])]), padding=ft.Padding.symmetric(horizontal=12, vertical=8)) for n, r in team]
    return t.screen(app, [heading_("About the Devs"),
                          ft.Container(height=150, bgcolor=t.WHITE, border=ft.Border.all(1, t.BORDER), border_radius=12, alignment=ft.Alignment.CENTER, content=t.label("Team photo", 16, t.MUTED)),
                          t.label("We're a Kennesaw State student team who designed and built this app for Dr. No's Comics & Games.", 14),
                          ft.Column(spacing=8, controls=rows)])
