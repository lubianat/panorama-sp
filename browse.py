# /// script
# requires-python = ">=3.10"
# dependencies = ["marimo", "pystac"]
# ///
"""Browse the SP Panorama STAC catalog. Run: uvx marimo edit --sandbox browse.py"""
import marimo

app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo
    import pystac
    from collections import Counter
    return Counter, mo, pystac


@app.cell
def _(pystac):
    CATALOG = "stac/catalog.json"  # or an https:// URL once hosted
    catalog = pystac.Catalog.from_file(CATALOG)
    items = sorted(catalog.get_items(recursive=True), key=lambda it: it.datetime)
    return catalog, items


@app.cell
def _(Counter, catalog, items, mo):
    per_day = Counter(it.datetime.date().isoformat() for it in items)
    mo.md(
        f"# {catalog.description}\n\n**{len(items)} photos** on **{len(per_day)} days**, "
        f"{items[0].datetime:%Y-%m-%d %H:%M} → {items[-1].datetime:%Y-%m-%d %H:%M}\n\n"
        + "\n".join(f"- {d}: {n} photos" for d, n in sorted(per_day.items()))
    )
    return (per_day,)


@app.cell
def _(mo, per_day):
    day = mo.ui.dropdown(sorted(per_day), value=max(per_day), label="Day")
    day
    return (day,)


@app.cell
def _(day, items, mo):
    todays = [it for it in items if it.datetime.date().isoformat() == day.value]
    photo = mo.ui.slider(0, len(todays) - 1, value=0, label="Photo", full_width=True)
    photo
    return photo, todays


@app.cell
def _(mo, photo, todays):
    it = todays[photo.value]
    mo.vstack([
        mo.md(f"## {it.datetime:%Y-%m-%d %H:%M} &nbsp; `{it.id}`"),
        mo.image(it.assets["overview"].get_absolute_href(), width="100%"),
        mo.md(f"[Full resolution]({it.assets['image'].get_absolute_href()}) · [Item JSON]({it.get_self_href()})"),
    ])
    return


@app.cell
def _(items, mo):
    mo.ui.table([{"id": it.id, "datetime": it.datetime.isoformat()} for it in items], selection=None)
    return


if __name__ == "__main__":
    app.run()
