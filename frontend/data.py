"""Sample data + search/filter logic. Replace PRODUCTS with the rows from Buck's catalog CSV later.

CSV columns: item_id, title, base_title, issue_number, author, publisher, price (number or PI),
description, cover_image_url, release_date, featured (Y/N), catalog_month
"""

def _p(pid, title, base, issue, author, publisher, price, desc, featured):
    return {"id": pid, "title": title, "base_title": base, "issue": issue, "author": author,
            "publisher": publisher, "price": price, "description": desc, "cover_url": None,
            "release_date": "", "featured": featured}

PRODUCTS = [
    _p("S1", "Amazing Spider-Man #1", "Amazing Spider-Man", "1", "Stan Lee", "Marvel Comics", 4.99, "Description of the comic goes here.", True),
    _p("S2", "X-Men #12", "X-Men", "12", "Chris Claremont", "Marvel Comics", 3.99, "Description of the comic goes here.", True),
    _p("S3", "Batman: Year One", "Batman: Year One", "", "Frank Miller", "DC Comics", 14.99, "Description of the comic goes here.", True),
    _p("S4", "Saga Vol. 1", "Saga", "1", "Brian K. Vaughan", "Image Comics", 9.99, "Description of the comic goes here.", True),
    _p("S5", "Superman #1", "Superman", "1", "Jerry Siegel", "DC Comics", 3.99, "Description of the comic goes here.", False),
    _p("S6", "Rare Variant Cover", "Rare Variant Cover", "", "Various", "Example Publisher", None, "Price on inquiry (PI).", False),
]
BY_ID = {p["id"]: p for p in PRODUCTS}

CATALOGS = ["November 2026 (Current)", "October 2026", "September 2026", "August 2026", "July 2026"]
CATALOG_URL = "https://www.drnos.com"   # TODO: real link for each catalog

# (order number, date, [(product id, quantity)])  - sample orders so the Order History screen has content
SAMPLE_ORDERS = [
    {"number": "DN-1042", "date": "Oct 7, 2026", "items": [("S1", 1), ("S2", 2), ("S6", 1)]},
    {"number": "DN-0988", "date": "Sep 9, 2026", "items": [("S3", 1)]},
    {"number": "DN-0931", "date": "Aug 5, 2026", "items": [("S4", 2)]},
]

PRICE_BANDS = {"Under $5": (0, 5), "$5 – $15": (5, 15), "$15 – $30": (15, 30), "$30+": (30, 10**9)}
PRICE_CHIPS = list(PRICE_BANDS) + ["PI"]


def filter_products(query="", author="", publisher="", price=None):
    """Search box (title or author) + filters (author, publisher, price incl. PI)."""
    q, a, pub = query.strip().lower(), author.strip().lower(), publisher.strip().lower()
    out = []
    for p in PRODUCTS:
        if q and q not in p["title"].lower() and q not in p["author"].lower():
            continue
        if a and a not in p["author"].lower():
            continue
        if pub and pub not in p["publisher"].lower():
            continue
        if price == "PI" and p["price"] is not None:
            continue
        if price in PRICE_BANDS:
            lo, hi = PRICE_BANDS[price]
            if p["price"] is None or not (lo <= p["price"] < hi):
                continue
        out.append(p)
    return out
