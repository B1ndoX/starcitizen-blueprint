#!/usr/bin/env python3
"""Add photos to the GVY gallery and rebuild the duplicated marquee markup."""

from __future__ import annotations

import argparse
import re
import subprocess
from datetime import datetime
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
GALLERY_DIR = ROOT / "assets" / "gallery"
FLEET_HTML = ROOT / "fleet.html"
SUPPORTED_EXTS = {".jpg", ".jpeg", ".png", ".webp", ".heic", ".tif", ".tiff"}
TRACK_RE = re.compile(
    r"(?P<prefix>          <div class=\"gallery-track\">\n)"
    r"(?P<body>.*?)"
    r"(?P<suffix>          </div>\n        </div>)",
    re.S,
)
TEAM_RE = re.compile(r"^team-(\d+)\.jpg$", re.I)


def image_sort_key(path: Path) -> tuple[float, str]:
    try:
        modified = path.stat().st_mtime
    except OSError:
        modified = 0
    return (modified, path.name.lower())


def collect_images(paths: list[str], newest: int | None = None) -> list[Path]:
    images: list[Path] = []
    for value in paths:
        path = Path(value).expanduser()
        if path.is_dir():
            images.extend(
                item
                for item in path.iterdir()
                if item.is_file() and item.suffix.lower() in SUPPORTED_EXTS
            )
        elif path.is_file() and path.suffix.lower() in SUPPORTED_EXTS:
            images.append(path)

    images = sorted(set(images), key=image_sort_key)
    if newest:
        images = sorted(images, key=image_sort_key, reverse=True)[:newest]
        images = sorted(images, key=image_sort_key)
    return images


def existing_gallery_numbers() -> list[int]:
    numbers: list[int] = []
    for path in GALLERY_DIR.glob("team-*.jpg"):
        match = TEAM_RE.match(path.name)
        if match:
            numbers.append(int(match.group(1)))
    return sorted(numbers)


def convert_photo(source: Path, destination: Path, max_edge: int) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(
        [
            "sips",
            "-s",
            "format",
            "jpeg",
            "-s",
            "formatOptions",
            "82",
            str(source),
            "--out",
            str(destination),
        ],
        check=True,
        stdout=subprocess.DEVNULL,
    )
    subprocess.run(
        ["sips", "-Z", str(max_edge), str(destination)],
        check=True,
        stdout=subprocess.DEVNULL,
    )


def build_gallery_markup(version: str) -> str:
    numbers = existing_gallery_numbers()
    if not numbers:
        raise SystemExit("assets/gallery 里没有 team-XX.jpg，无法重建图册。")

    lines: list[str] = []
    for hidden in (False, True):
        for number in numbers:
            aria = ' aria-hidden="true"' if hidden else ""
            alt = "" if hidden else f"GVY 团建照片 {number:02d}"
            lines.extend(
                [
                    f'            <figure class="gallery-card"{aria}>',
                    f'              <img src="./assets/gallery/team-{number:02d}.jpg?v={version}" alt="{alt}" loading="lazy" decoding="async" />',
                    "            </figure>",
                ]
            )
    return "\n".join(lines) + "\n"


def rebuild_fleet_html(version: str) -> None:
    html = FLEET_HTML.read_text(encoding="utf-8")
    match = TRACK_RE.search(html)
    if not match:
        raise SystemExit("没找到 fleet.html 里的 gallery-track 区块。")

    body = build_gallery_markup(version)
    updated = html[: match.start("body")] + body + html[match.end("body") :]
    FLEET_HTML.write_text(updated, encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Add GVY gallery photos and rebuild fleet.html gallery cards.",
    )
    parser.add_argument(
        "photos",
        nargs="*",
        help="照片文件或文件夹路径。例如：~/Downloads/团建照片",
    )
    parser.add_argument(
        "--newest",
        type=int,
        help="只添加路径里修改时间最新的 N 张照片。",
    )
    parser.add_argument(
        "--max-edge",
        type=int,
        default=1920,
        help="导入照片最长边尺寸，默认 1920。",
    )
    parser.add_argument(
        "--version",
        default=datetime.now().strftime("%Y%m%d-gallery"),
        help="图片缓存版本号，默认今天日期。",
    )
    parser.add_argument(
        "--rebuild-only",
        action="store_true",
        help="不添加照片，只按现有 team-XX.jpg 重建图册 HTML。",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    numbers = existing_gallery_numbers()
    next_number = (max(numbers) + 1) if numbers else 1

    images = [] if args.rebuild_only else collect_images(args.photos, args.newest)
    if not args.rebuild_only and not images:
        raise SystemExit("没有找到要添加的照片。示例：scripts/add_gallery_photos.py ~/Downloads/团建照片 --newest 4")

    for index, source in enumerate(images, start=next_number):
        destination = GALLERY_DIR / f"team-{index:02d}.jpg"
        print(f"add {source} -> {destination.relative_to(ROOT)}")
        convert_photo(source, destination, args.max_edge)

    rebuild_fleet_html(args.version)
    print(f"gallery rebuilt: {len(existing_gallery_numbers())} photos, version={args.version}")


if __name__ == "__main__":
    main()
