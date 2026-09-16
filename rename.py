"""Rename GoPro JPGs in data/ to YYYY-MM-DD-HH-MM-SP-PANORAMA.JPG (dry run unless --apply)."""
import re, sys
from datetime import datetime
from pathlib import Path
from PIL import Image

DATA = Path(__file__).parent / "data"
DONE = re.compile(r"^\d{4}-\d{2}-\d{2}-\d{2}-\d{2}-SP-PANORAMA(-\d+)?\.JPG$")
FMT = "%Y-%m-%d-%H-%M-SP-PANORAMA"


def taken(path):
    exif = Image.open(path).getexif().get_ifd(0x8769)  # Exif sub-IFD
    return datetime.strptime(exif[36867], "%Y:%m:%d %H:%M:%S")  # DateTimeOriginal, local time


def target(dt, n=1):
    return dt.strftime(FMT) + (f"-{n}" if n > 1 else "") + ".JPG"


def main(apply):
    for f in sorted(DATA.glob("*.[jJ][pP][gG]")):
        if DONE.match(f.name):
            continue
        dt, n = taken(f), 1
        while (DATA / target(dt, n)).exists():  # never overwrite: same minute -> -2, -3...
            n += 1
        print(f"{f.name} -> {target(dt, n)}")
        if apply:
            f.rename(DATA / target(dt, n))
    if not apply:
        print("(dry run, use --apply)")


assert DONE.match(target(datetime(2026, 9, 15, 17, 58))) and DONE.match(target(datetime(2026, 9, 15, 17, 58), 2))

if __name__ == "__main__":
    main("--apply" in sys.argv)
