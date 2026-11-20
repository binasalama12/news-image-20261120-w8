#!/usr/bin/env python3
"""Publisher for the Warm Postcard entry (news-image-20261120, wallet w8).

The finished artwork for "Warm Postcard - one day of world news, Friday
20 November 2026" ships inside this repository as entry.png. This program
relies on the Python standard library alone: it validates the bundled
image and copies it into the output directory for the grader to collect.
"""

import os
import shutil
import sys
from pathlib import Path

DESIGN_TITLE = "Warm Postcard - one day of world news, Friday 20 November 2026"
IMAGE_NAME = "entry.png"
MAX_BYTES = 1048576  # competition cap: 1 MiB
PNG_MAGIC = b"\x89PNG\r\n\x1a\n"
JPEG_MAGIC = b"\xff\xd8\xff"


def fail(message):
    print(f"error: {message}", file=sys.stderr)
    return 1


def locate_source():
    here = Path(__file__).resolve().parent
    return here / IMAGE_NAME


def check_image(path):
    """Return the byte size when the file looks like a valid PNG/JPEG."""
    if not path.is_file():
        return None, f"source image not found: {path}"
    size = path.stat().st_size
    with path.open("rb") as handle:
        head = handle.read(len(PNG_MAGIC))
    if not (head.startswith(PNG_MAGIC) or head.startswith(JPEG_MAGIC)):
        return None, f"source image has unknown format bytes: {path}"
    if size > MAX_BYTES:
        return None, f"source image is {size} bytes, over the {MAX_BYTES} byte cap"
    return size, None


def target_path():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR") or "/output"
    return Path(out_dir) / IMAGE_NAME


def main():
    source = locate_source()
    size, problem = check_image(source)
    if problem is not None:
        return fail(problem)

    dest = target_path()
    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(source, dest)

    print(f"published entry: {DESIGN_TITLE}")
    print(f"image written to {dest} ({size} bytes)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
