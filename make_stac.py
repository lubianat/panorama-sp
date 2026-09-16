"""Build a self-contained static STAC in stac/: moves renamed photos from data/ into item folders,
makes web-sized overviews, and (re)writes all the JSON. Safe to rerun."""
import json, re
from datetime import datetime, timedelta, timezone
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).parent
DATA, STAC = ROOT / "data", ROOT / "stac"
COLLECTION = "sp-panorama-2026-09-15"
ITEMS = STAC / COLLECTION / "items"
# ponytail: hardcoded for collection 1 (from EXIF: 23°34'7.49"S 46°43'41.14"W, 820.9 m); per-collection later
LON, LAT, ALT = -46.728094, -23.568747, 820.9
TZ = timezone(timedelta(hours=-3))  # camera clock = São Paulo local time
V = "1.0.0"
CC0 = "https://creativecommons.org/publicdomain/zero/1.0/"
JSON_T, GEO_T = "application/json", "application/geo+json"


def parse(name):
    m = re.match(r"(\d{4}-\d{2}-\d{2}-\d{2}-\d{2})-SP-PANORAMA", name)
    return datetime.strptime(m[1], "%Y-%m-%d-%H-%M").replace(tzinfo=TZ)


def write(path, obj):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, ensure_ascii=False))


def ingest():
    """Move renamed originals from data/ into stac/<collection>/items/<id>/ (never overwrites)."""
    for f in sorted(DATA.glob("*-SP-PANORAMA*.JPG")):
        dest = ITEMS / f.stem / f.name
        if dest.exists():
            print(f"skip, already in catalog: {f.name}")
            continue
        dest.parent.mkdir(parents=True, exist_ok=True)
        f.rename(dest)


def overview(jpg):
    web = jpg.with_name(jpg.stem + ".web.jpg")
    if not web.exists():
        im = Image.open(jpg)
        im.thumbnail((1600, 1600))
        im.save(web, quality=80)  # no exif= passed, so metadata is dropped
    return web


def item(jpg):
    iid = jpg.stem
    return {
        "type": "Feature", "stac_version": V, "id": iid, "collection": COLLECTION,
        "geometry": {"type": "Point", "coordinates": [LON, LAT, ALT]},
        "bbox": [LON, LAT, LON, LAT],
        "properties": {"datetime": parse(iid).isoformat(), "platform": "GoPro HERO10 Black",
                       "instruments": ["gopro-hero10"], "license": "CC0-1.0"},
        "assets": {
            "image": {"href": jpg.name, "type": "image/jpeg", "title": "Original photo", "roles": ["data"]},
            "overview": {"href": overview(jpg).name, "type": "image/jpeg", "title": "Web copy (1600px)",
                         "roles": ["overview", "visual"]},
        },
        "links": [{"rel": "collection", "href": "../../collection.json", "type": JSON_T},
                  {"rel": "parent", "href": "../../collection.json", "type": JSON_T},
                  {"rel": "root", "href": "../../../catalog.json", "type": JSON_T},
                  {"rel": "license", "href": CC0}],
    }


def main():
    ingest()
    jpgs = sorted(ITEMS.glob("*/*-SP-PANORAMA*.JPG"))
    for j in jpgs:
        write(j.with_suffix(".json"), item(j))
    times = [parse(j.stem) for j in jpgs]
    write(STAC / COLLECTION / "collection.json", {
        "type": "Collection", "stac_version": V, "id": COLLECTION,
        "title": "São Paulo panorama, first collection",
        "description": "GoPro HERO10 timelapse photos of the São Paulo skyline, one every 5 minutes.",
        "license": "CC0-1.0",
        "extent": {"spatial": {"bbox": [[LON, LAT, LON, LAT]]},
                   "temporal": {"interval": [[min(times).isoformat(), max(times).isoformat()]]}},
        "links": [{"rel": "root", "href": "../catalog.json", "type": JSON_T},
                  {"rel": "parent", "href": "../catalog.json", "type": JSON_T},
                  {"rel": "license", "href": CC0}]
                 + [{"rel": "item", "href": f"items/{j.stem}/{j.stem}.json", "type": GEO_T} for j in jpgs],
    })
    write(STAC / "catalog.json", {
        "type": "Catalog", "stac_version": V, "id": "sp-panorama",
        "description": "Long-running photo panorama of São Paulo. CC0.",
        "links": [{"rel": "root", "href": "catalog.json", "type": JSON_T},
                  {"rel": "child", "href": f"{COLLECTION}/collection.json", "type": JSON_T}],
    })
    print(f"{len(jpgs)} items -> {STAC}")


assert parse("2026-09-15-17-58-SP-PANORAMA-2").isoformat() == "2026-09-15T17:58:00-03:00"

if __name__ == "__main__":
    main()
