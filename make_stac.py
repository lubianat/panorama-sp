"""Build a self-contained static STAC in stac/: moves renamed photos from data/ into item folders,
makes web-sized overviews, and (re)writes all the JSON. Safe to rerun."""
import json, math, re, subprocess
from datetime import datetime, timedelta, timezone
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).parent
DATA, STAC = ROOT / "data", ROOT / "stac"
COLLECTION = "sp-panorama-2026-09-15"
COLL = STAC / COLLECTION
# ponytail: hardcoded for collection 1 (from EXIF: 23°34'7.49"S 46°43'41.14"W, 820.9 m); per-collection later
LON, LAT, ALT = -46.728094, -23.568747, 820.9
TZ = timezone(timedelta(hours=-3))  # camera clock = São Paulo local time
V = "1.0.0"
CC0 = "https://creativecommons.org/publicdomain/zero/1.0/"
JSON_T, GEO_T = "application/json", "application/geo+json"
PERS = "https://stac-extensions.github.io/perspective-imagery/v1.0.0/schema.json"
ROLL_SIGN = -1  # PIL angle sign that cancels camera:roll (checked visually); flip if levelled overviews come out tilted the other way


def parse(name):
    m = re.match(r"(\d{4}-\d{2}-\d{2}-\d{2}-\d{2})-SP-PANORAMA", name)
    return datetime.strptime(m[1], "%Y-%m-%d-%H-%M").replace(tzinfo=TZ)


def write(path, obj):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, ensure_ascii=False))


def ingest():
    """Move renamed originals from data/ into stac/<collection>/items/<id>/ (never overwrites)."""
    for f in sorted(DATA.glob("*-SP-PANORAMA*.JPG")):
        dest = COLL / f.stem[:10] / "items" / f.stem / f.name  # one sub-catalog per day
        if dest.exists():
            print(f"skip, already in catalog: {f.name}")
            continue
        dest.parent.mkdir(parents=True, exist_ok=True)
        f.rename(dest)


def gravity(jpgs):
    """GoPro GravityVector (x, y, z) per photo; cached in the item JSON so exiftool only sees new photos."""
    out, todo = {}, []
    for j in jpgs:
        cached = j.with_suffix(".json")
        g = json.loads(cached.read_text())["properties"].get("gopro:gravity_vector") if cached.exists() else None
        if g:
            out[j] = g
        else:
            todo.append(j)
    if todo:
        res = subprocess.run(["exiftool", "-j", "-b", "-GravityVector", *map(str, todo)],
                             capture_output=True, text=True, check=True)
        for r in json.loads(res.stdout):
            if "GravityVector" in r:
                out[Path(r["SourceFile"])] = [float(v) for v in r["GravityVector"].split()]
    return out


def tilt(g):
    """(roll, pitch) in degrees from the gravity vector; y points down the image."""
    x, y, z = g
    return round(math.degrees(math.atan2(x, y)), 2), round(math.degrees(math.atan2(z, y)), 2)


def level(im, roll):
    """Rotate to cancel the camera roll and crop to the largest same-aspect rectangle without empty corners."""
    a = math.radians(abs(roll))
    W, H = im.size
    s = min(W / (W * math.cos(a) + H * math.sin(a)), H / (W * math.sin(a) + H * math.cos(a)))
    im = im.rotate(ROLL_SIGN * roll, resample=Image.BICUBIC)  # PIL rotates counter-clockwise
    w, h = W * s, H * s
    return im.crop((round((W - w) / 2), round((H - h) / 2), round((W + w) / 2), round((H + h) / 2)))


def overview(jpg, roll):
    web = jpg.with_name(jpg.stem + ".web.jpg")
    if not web.exists():
        im = Image.open(jpg)
        im.thumbnail((2000, 2000))  # shrink first; rotating 23 MP is slow
        if roll:
            im = level(im, roll)
        im.thumbnail((1600, 1600))
        im.save(web, quality=80)  # no exif= passed, so metadata is dropped
    return web


def item(jpg, g):
    iid = jpg.stem
    tilt_props = {}
    if g:
        roll, pitch = tilt(g)
        tilt_props = {"gopro:gravity_vector": g, "camera:roll": roll, "camera:pitch": pitch}
    return {
        "type": "Feature", "stac_version": V, "stac_extensions": [PERS],
        "id": iid, "collection": COLLECTION,
        "geometry": {"type": "Point", "coordinates": [LON, LAT, ALT]},
        "bbox": [LON, LAT, LON, LAT],
        "properties": {"datetime": parse(iid).isoformat(), "platform": "GoPro HERO10 Black",
                       "instruments": ["gopro-hero10"], "license": "CC0-1.0",
                       "pers:perspective_center": [LON, LAT, ALT], "pers:crs": 4979, **tilt_props},
        "assets": {
            "image": {"href": jpg.name, "type": "image/jpeg", "title": "Original photo", "roles": ["data"]},
            "overview": {"href": overview(jpg, tilt_props.get("camera:roll")).name, "type": "image/jpeg",
                         "title": "Web copy (1600px, levelled by camera:roll)",
                         "roles": ["overview", "visual"]},
        },
        "links": [{"rel": "collection", "href": "../../../collection.json", "type": JSON_T},
                  {"rel": "parent", "href": "../../catalog.json", "type": JSON_T},
                  {"rel": "root", "href": "../../../../catalog.json", "type": JSON_T},
                  {"rel": "license", "href": CC0}],
    }


def main():
    ingest()
    jpgs = sorted(COLL.glob("*/items/*/*-SP-PANORAMA*.JPG"))
    grav = gravity(jpgs)
    for j in jpgs:
        write(j.with_suffix(".json"), item(j, grav.get(j)))
    times = [parse(j.stem) for j in jpgs]
    days = {}
    for j in jpgs:
        days.setdefault(j.stem[:10], []).append(j)
    for day, djpgs in days.items():
        write(COLL / day / "catalog.json", {
            "type": "Catalog", "stac_version": V, "id": f"{COLLECTION}-{day}",
            "description": f"Photos taken on {day}.",
            "links": [{"rel": "root", "href": "../../catalog.json", "type": JSON_T},
                      {"rel": "parent", "href": "../collection.json", "type": JSON_T},
                      {"rel": "collection", "href": "../collection.json", "type": JSON_T}]
                     + [{"rel": "item", "href": f"items/{j.stem}/{j.stem}.json", "type": GEO_T} for j in djpgs],
        })
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
                 + [{"rel": "child", "href": f"{day}/catalog.json", "type": JSON_T} for day in days],
    })
    write(STAC / "catalog.json", {
        "type": "Catalog", "stac_version": V, "id": "sp-panorama",
        "description": "Long-running photo panorama of São Paulo. CC0.",
        "links": [{"rel": "root", "href": "catalog.json", "type": JSON_T},
                  {"rel": "child", "href": f"{COLLECTION}/collection.json", "type": JSON_T}],
    })
    print(f"{len(jpgs)} items in {len(days)} day catalogs -> {STAC}")


assert tilt([0, 1, 0]) == (0, 0) and tilt([-0.0849, 0.9953, -0.0435])[0] == -4.88
assert parse("2026-09-15-17-58-SP-PANORAMA-2").isoformat() == "2026-09-15T17:58:00-03:00"

if __name__ == "__main__":
    main()
