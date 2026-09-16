"""Write stac/images.json: sorted item paths (relative to stac/, no extension) for index.html."""
import json
from pathlib import Path

STAC = Path(__file__).parent / "stac"
paths = sorted((str(p.relative_to(STAC).with_suffix("")) for p in STAC.glob("*/items/*/*-SP-PANORAMA*.JPG")),
               key=lambda s: s.rsplit("/", 1)[1])  # sort by timestamp across collections
(STAC / "images.json").write_text(json.dumps(paths, indent=0))
print(f"{len(paths)} images")
