"""Write stac/ro-crate-metadata.json: an RO-Crate 1.2 view of the STAC catalog.
STAC is the source of truth; run after make_stac.py."""
import json
from datetime import date
from pathlib import Path

STAC = Path(__file__).parent / "stac"
SPEC = "https://w3id.org/ro/crate/1.2"
STAC_SPEC = "https://github.com/radiantearth/stac-spec/tree/v1.0.0"
CC0 = "https://creativecommons.org/publicdomain/zero/1.0/"
TYPES = {".json": "application/json", ".jpg": "image/jpeg"}
ROLES = {"data": "Original GoPro photo, untouched.", "overview": "Web copy, 1600 px, levelled by camera:roll."}


def file(path, **extra):
    rel = path.relative_to(STAC).as_posix()
    return {"@id": rel, "@type": "File", "name": path.name, "contentSize": str(path.stat().st_size),
            "encodingFormat": TYPES[path.suffix.lower()], **extra}


def stac_file(path, kind):
    return file(path, conformsTo={"@id": STAC_SPEC}, description=f"STAC {kind} (JSON).")


def main():
    catalog = json.loads((STAC / "catalog.json").read_text())
    graph = [
        {"@id": "ro-crate-metadata.json", "@type": "CreativeWork",
         "conformsTo": {"@id": SPEC}, "about": {"@id": "./"}},
        {"@id": CC0, "@type": "CreativeWork", "name": "CC0 1.0 Universal",
         "description": "Public domain dedication: no rights reserved."},
        {"@id": STAC_SPEC, "@type": "CreativeWork", "name": "STAC specification 1.0.0",
         "description": "SpatioTemporal Asset Catalog specification."},
        stac_file(STAC / "catalog.json", "Catalog"),
        file(STAC / "images.json", description="Photo list used by the web viewer."),
    ]
    root = {"@id": "./", "@type": "Dataset", "name": "SP Panorama",
            "description": catalog["description"], "license": {"@id": CC0},
            "datePublished": date.today().isoformat(), "mainEntity": {"@id": "catalog.json"},
            "hasPart": [{"@id": "catalog.json"}, {"@id": "images.json"}]}
    graph.insert(1, root)

    for link in catalog["links"]:
        if link["rel"] != "child":
            continue
        cpath = STAC / link["href"]
        coll = json.loads(cpath.read_text())
        cdir = cpath.parent.relative_to(STAC).as_posix() + "/"
        lon, lat = coll["extent"]["spatial"]["bbox"][0][:2]
        start, end = coll["extent"]["temporal"]["interval"][0]
        place = f"#place-{coll['id']}"
        graph += [
            {"@id": place, "@type": "Place", "name": "Camera site, São Paulo",
             "geo": {"@id": f"#geo-{coll['id']}"}},
            {"@id": f"#geo-{coll['id']}", "@type": "Geometry", "name": f"Camera position ({lat}, {lon})",
             "asWKT": f"POINT({lon} {lat})"},
            stac_file(cpath, "Collection"),
        ]
        items = []
        for ilink in coll["links"]:
            if ilink["rel"] != "item":
                continue
            ipath = cpath.parent / ilink["href"]
            item = json.loads(ipath.read_text())
            idir = ipath.parent.relative_to(STAC).as_posix() + "/"
            assets = [(ipath.parent / a["href"], ROLES[a["roles"][0]]) for a in item["assets"].values()]
            parts = [stac_file(ipath, "Item")] + [file(a, description=d) for a, d in assets if a.exists()]  # originals may live only on the data host
            graph += parts + [{"@id": idir, "@type": "Dataset", "name": item["id"],
                               "dateCreated": item["properties"]["datetime"],
                               "description": f"Panorama photo taken {item['properties']['datetime']}.",
                               "spatialCoverage": {"@id": place},
                               "hasPart": [{"@id": p["@id"]} for p in parts]}]
            items.append({"@id": idir})
        graph.append({"@id": cdir, "@type": "Dataset", "name": coll["title"], "description": coll["description"],
                      "spatialCoverage": {"@id": place},
                      "temporalCoverage": f"{start}/{end}",
                      "hasPart": [{"@id": cpath.relative_to(STAC).as_posix()}] + items})
        root["hasPart"].append({"@id": cdir})

    out = STAC / "ro-crate-metadata.json"
    out.write_text(json.dumps({"@context": f"{SPEC}/context", "@graph": graph}, indent=2, ensure_ascii=False))
    print(f"{len(graph)} entities -> {out}")


if __name__ == "__main__":
    main()
