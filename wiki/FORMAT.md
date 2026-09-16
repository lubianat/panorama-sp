# Data format

## Originals: GoPro JPEG, untouched

- 5568×4176, about 5 MB, with full EXIF.
- These are the archive masters.
- **Never recompress them.** Lossy re-encoding blurs the faint dark-sky detail that the light-pollution use depends on, and it throws away EXIF (the exposure record).
- A lossless shrink (`jpegtran -optimize`) would save only ~5–10%, which isn't worth it for now.
- RAW is deferred; see [CAPTURE](CAPTURE.md).

## Web copy

- 1600 px on the long side, JPEG quality 80, about 130 KB, no EXIF.
- Rotated to cancel `camera:roll` and cropped to remove empty corners. Because of lens distortion, only the centre of the horizon is exactly level.
- For viewing only. It can be regenerated from the original at any time.
- Created by `make_stac.py`.

## Naming

`YYYY-MM-DD-HH-MM-SP-PANORAMA[-n]`

- Time is São Paulo local time (UTC-3), from the EXIF `DateTimeOriginal`.
- `-n` (`-2`, `-3`, …) is added only when two photos fall in the same minute.
- Brazil has had no daylight saving time since 2019. If it comes back, local names would repeat or skip an hour, so switch to UTC names or put the offset in the name.

## Layout

```
stac/
  catalog.json
  images.json                      viewer photo list (paths relative to stac/)
  <collection>/
    collection.json
    items/<id>/<id>.JPG            original
    items/<id>/<id>.web.jpg        web copy
    items/<id>/<id>.json           STAC item
```

- Every href is relative, so the `stac/` folder can be uploaded to any host unchanged.
- **Scale limit:** a year at 5 minutes means ~105k folders under one `items/`, and hosts such as HF advise at most 10k entries per folder.
  When that matters, use `items/YYYY/MM/DD/<id>/` or one collection per month.

## STAC fields

| Field | Value | Why |
|-------|-------|-----|
| `geometry` | Point (lon, lat, altitude) of the camera | where it was taken; fixed per collection |
| `properties.datetime` | ISO 8601 with a `-03:00` offset | unambiguous time |
| `properties.platform` / `instruments` | `GoPro HERO10 Black` / `gopro-hero10` | provenance |
| `properties.license` / collection `license` | `CC0-1.0` | open data |
| `assets.image` | original JPEG, role `data` | the archive master |
| `assets.overview` | web copy, roles `overview`, `visual`, levelled by `camera:roll` | fast viewing |
| `pers:perspective_center` / `pers:crs` | camera lon, lat, altitude / `4979` | [perspective-imagery](https://github.com/stac-extensions/perspective-imagery) extension |
| `gopro:gravity_vector` | `[x, y, z]` from the GoPro `GravityVector` tag (accelerometer) | raw tilt record |
| `camera:roll` / `camera:pitch` | degrees, `atan2(x, y)` / `atan2(z, y)` | tilt, to level images and spot when the camera moved |

Planned fields (not written yet):

- exposure settings copied from EXIF, such as `exposure_time`, `iso` and `white_balance`, so frames can be filtered by them
- `sun_elevation`, to split day, twilight and night without guessing
- per-frame metrics: mean brightness, sky brightness, cloud cover

Why custom `camera:` and `gopro:` fields: `pers:rotation_matrix` needs the full orientation, including heading, and the camera doesn't record heading.
Existing extensions are used wherever they fit.

Future: registering each frame against a reference frame (OpenCV) to catch panning and shifts, which gravity can't detect.

## Collections

- One collection per deployment, meaning a fixed camera position and fixed settings.
- The ID is `sp-panorama-<start-date>`.
- The collection description records the camera settings and anything notable about the site.

## Scale path

For real analysis, pull the per-frame numbers into one table: a Parquet/GeoParquet file with one row per frame (id, datetime, exposure, metrics).
The analysis runs on that table, and the JPEGs serve as the evidence behind the numbers.
