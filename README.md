# SP Panorama

Note: PILOT PHASE

Still figuring out the full workflow (hardware and software).

A long-running photo panorama of São Paulo. A GoPro HERO10 takes one photo every 5 minutes.
The photos are published as a static STAC catalog, with a tiny web viewer and a notebook to browse them.
The data is released under **CC0**.

## Layout

```
data/                    inbox: drop new GoPro JPGs here
stac/catalog.json        STAC root
stac/<collection>/items/<id>/<id>.JPG       original
stac/<collection>/items/<id>/<id>.web.jpg   1600px web copy
stac/<collection>/items/<id>/<id>.json      STAC item
stac/images.json         photo list used by the viewer
```

`<id>` is `YYYY-MM-DD-HH-MM-SP-PANORAMA`, in São Paulo local time (UTC-3), taken from the photo's EXIF.
If two photos fall in the same minute, the second one gets `-2`.

## Adding new photos

```sh
cp /path/to/gopro/DCIM/100GOPRO/*.JPG data/
python3 rename.py            # preview the renames
python3 rename.py --apply    # rename
python3 make_stac.py         # move photos into stac/, make web copies, write the STAC JSON
python3 build_index.py       # update the viewer's photo list
```

Requires Python 3.9+ and Pillow (`pip install pillow`).

## Viewing

**Website:** run `python3 -m http.server` and open <http://localhost:8000>.
Use ◀ ▶ (or the arrow keys) to go through the photos, and ◀◀ day ▶▶ (or Shift + arrows) to jump a day. The date picker jumps to the closest photo.
Gaps longer than 10 minutes are shown next to the buttons, and the URL (`#2026-09-15-17-58`) links to a specific photo.

**Notebook:** run `uvx marimo edit --sandbox browse.py`. It needs [uv](https://docs.astral.sh/uv/) and installs its own dependencies.

## Notes

- The GPS location is hardcoded in `make_stac.py` (23°34'7.49"S, 46°43'41.14"W, 820.9 m), taken from the first collection's EXIF.
  Change `COLLECTION` and the coordinates there for new collections.
- Design docs are in [`wiki/`](wiki/README.md): [capture](wiki/CAPTURE.md), [format](wiki/FORMAT.md) and [hosting](wiki/HOSTING.md).
