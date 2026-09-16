# Hosting options

Not decided yet. This page lists the options.

## The idea

`stac/` is a **self-contained static STAC catalog**: the JSON, the original JPGs and the web copies sit side by side, and every link is relative.
Upload the whole folder to any public static host and it works as-is:

- **The data**: `https://<host>/stac/catalog.json`, which anyone can open in [STAC Browser](https://radiantearth.github.io/stac-browser/), `pystac` or `browse.py`.
- **The website**: GitHub Pages serves only `index.html`. Point `BASE` in `index.html` at the host's `stac/` URL.

Licence: CC0-1.0.

## Size

About 5 MB per original plus ~0.15 MB per web copy, one photo every 5 minutes:

| Period | Photos (24 h) | Size |
|--------|---------------|-----------|
| day    | 288           | ~1.5 GB   |
| month  | ~8,600        | ~45 GB    |
| year   | ~105,000      | ~550 GB   |

Daylight-only shooting would halve these numbers. Either way it is far too big for GitHub (1 GB soft limit per repo).

## Path A: Source.coop

[source.coop](https://source.coop) is Radiant Earth's free open-data host, made for geospatial data and STAC.

- **Pros:** built for this, and the geo community looks for data there. It is S3-compatible (`aws s3 sync`) with public HTTPS. It is free for open data.
- **Cons:** you need an account and approval for the repository. The audience is geospatial rather than ML.
- **Upload:** `aws s3 sync stac/ s3://<account>/sp-panorama/ --endpoint-url <source.coop endpoint>`, using the credentials from the Source.coop UI.

## Path B: Hugging Face bucket

- **Pros:** probably the most scalable. There are no commits and no file-count limits, uploads are just a sync, and it has CORS (it already works for OME-Zarr).
  It fits a feed that grows every day.
- **Cons:** there is no version history, and it is less discoverable than a dataset page.
- **Upload:**
  ```sh
  hf buckets create <user>/sp-panorama --exist-ok
  hf sync stac/ hf://buckets/<user>/sp-panorama
  ```
  Then set `BASE` in `index.html` to the bucket's public URL (check the exact format with one file first).

## Path C: Hugging Face dataset repo

- **Pros:** versioned, with a dataset card, search and likes, and a DOI can be requested.
- **Cons:** HF advises staying under ~100k files per repo (about one year here) and under 10k per folder, and every upload is a commit.
  It needs a new repo per year, or packing photos into tar/parquet, which breaks the plain-static-STAC idea.
- **Upload:** `hf upload <user>/sp-panorama stac/ . --type dataset`

## Add-on: yearly Zenodo snapshot

At the end of each year, freeze that year's collection on [Zenodo](https://zenodo.org) (50 GB per record, or split it by month) to get a citable DOI.
The live catalog stays on A or B.

## What has to change when moving

- `index.html`: the `BASE` constant (one line).
- `browse.py`: `CATALOG` points at the remote `catalog.json`.
- `make_stac.py`: nothing, because the hrefs are relative. Optionally add a `self` link with the absolute URL.
