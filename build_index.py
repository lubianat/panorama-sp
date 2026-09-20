"""Write stac/images.json for index.html: [path relative to stac/ without extension, camera roll in degrees]."""
import json
from pathlib import Path

STAC = Path(__file__).parent / "stac"


def roll(jpg):
    """Roll of the original; the web copy is already levelled, so the viewer only needs this in high-res mode."""
    item = jpg.with_suffix(".json")
    return json.loads(item.read_text())["properties"].get("camera:roll", 0) if item.exists() else 0


jpgs = sorted(STAC.glob("*/*/items/*/*-SP-PANORAMA*.JPG"), key=lambda p: p.name)  # by timestamp across collections
images = [[str(p.relative_to(STAC).with_suffix("")), roll(p)] for p in jpgs]
(STAC / "images.json").write_text(json.dumps(images, indent=0))
print(f"{len(images)} images")
