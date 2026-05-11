#!/usr/bin/env python3
from __future__ import annotations

import math
from pathlib import Path

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageOps


RUN_DIR = Path("/Users/xueyuan/Downloads/potato/potato-hatch-run")
SOURCE = Path("/Users/xueyuan/Downloads/potato/potato2.JPG")
OUT_RAW = RUN_DIR / "raw"
OUT_FINAL = RUN_DIR / "final"
OUT_QA = RUN_DIR / "qa"

CELL_W = 192
CELL_H = 208
COLUMNS = 8
ROWS = 9

ROWS_DEF = [
    ("idle", 6),
    ("running-right", 8),
    ("running-left", 8),
    ("waving", 4),
    ("jumping", 5),
    ("failed", 8),
    ("waiting", 6),
    ("running", 6),
    ("review", 6),
]


def ensure_dirs() -> None:
    for path in (OUT_RAW, OUT_FINAL, OUT_QA, RUN_DIR / "frames"):
        path.mkdir(parents=True, exist_ok=True)


def largest_components(mask: np.ndarray, keep: int = 2) -> np.ndarray:
    labels_count, labels, stats, _ = cv2.connectedComponentsWithStats(mask, 8)
    if labels_count <= 1:
        return mask
    areas = [(stats[i, cv2.CC_STAT_AREA], i) for i in range(1, labels_count)]
    areas.sort(reverse=True)
    out = np.zeros(mask.shape, dtype=np.uint8)
    for _, label in areas[:keep]:
        out[labels == label] = 255
    return out


def extract_pet() -> Image.Image:
    bgr = cv2.imread(str(SOURCE), cv2.IMREAD_COLOR)
    if bgr is None:
        raise RuntimeError(f"could not read {SOURCE}")
    h, w = bgr.shape[:2]

    # The main reference photo is a centered full-body portrait.
    rect = (
        int(w * 0.24),
        int(h * 0.02),
        int(w * 0.52),
        int(h * 0.92),
    )
    mask = np.zeros((h, w), np.uint8)
    bgd = np.zeros((1, 65), np.float64)
    fgd = np.zeros((1, 65), np.float64)
    cv2.grabCut(bgr, mask, rect, bgd, fgd, 7, cv2.GC_INIT_WITH_RECT)
    mask = np.where((mask == cv2.GC_FGD) | (mask == cv2.GC_PR_FGD), 255, 0).astype("uint8")

    kernel = np.ones((7, 7), np.uint8)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel, iterations=2)
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel, iterations=1)
    mask = largest_components(mask, keep=2)

    # Remove most of the grey leash on the left/bottom while preserving the white chest.
    yy, xx = np.mgrid[0:h, 0:w]
    leash_zone = (xx < int(w * 0.34)) & (yy > int(h * 0.58))
    mask[leash_zone] = 0

    alpha = cv2.GaussianBlur(mask, (0, 0), 2.0)
    rgba = cv2.cvtColor(bgr, cv2.COLOR_BGR2RGBA)
    rgba[:, :, 3] = alpha
    image = Image.fromarray(rgba)

    bbox = image.getbbox()
    if not bbox:
        raise RuntimeError("foreground extraction produced an empty cutout")
    image = image.crop(bbox)

    # Gentle cleanup: sharpen alpha edges, posterize colors, and make it read as a small pet.
    alpha_chan = image.getchannel("A").point(lambda v: 255 if v > 42 else 0)
    rgb = image.convert("RGB")
    small = rgb.resize(
        (max(1, rgb.width // 3), max(1, rgb.height // 3)),
        Image.Resampling.BILINEAR,
    )
    rgb = small.resize(rgb.size, Image.Resampling.NEAREST)
    rgb = ImageOps.posterize(rgb, 5)
    image = Image.merge("RGBA", (*rgb.split(), alpha_chan))

    # Add a Codex-pet-like chunky outline.
    outline_alpha = alpha_chan.filter(ImageFilter.MaxFilter(9))
    outline = Image.new("RGBA", image.size, (58, 42, 32, 255))
    outlined = Image.new("RGBA", image.size, (0, 0, 0, 0))
    outlined.paste(outline, (0, 0), outline_alpha)
    outlined.alpha_composite(image)
    outlined.save(OUT_RAW / "potato-cutout.png")
    return outlined


def fit_sprite(sprite: Image.Image) -> Image.Image:
    target_h = 166
    target_w = 138
    scale = min(target_w / sprite.width, target_h / sprite.height)
    size = (max(1, round(sprite.width * scale)), max(1, round(sprite.height * scale)))
    return sprite.resize(size, Image.Resampling.LANCZOS)


def affine(sprite: Image.Image, sx: float = 1.0, sy: float = 1.0, rotate: float = 0.0, flip: bool = False) -> Image.Image:
    img = ImageOps.mirror(sprite) if flip else sprite.copy()
    new_size = (max(1, round(img.width * sx)), max(1, round(img.height * sy)))
    img = img.resize(new_size, Image.Resampling.BICUBIC)
    if rotate:
        img = img.rotate(rotate, resample=Image.Resampling.BICUBIC, expand=True)
    return img


def place(sprite: Image.Image, x: int = 0, y: int = 0) -> Image.Image:
    cell = Image.new("RGBA", (CELL_W, CELL_H), (0, 0, 0, 0))
    left = (CELL_W - sprite.width) // 2 + x
    bottom = 190 + y
    top = bottom - sprite.height
    cell.alpha_composite(sprite, (left, top))
    return cell


def draw_paw(cell: Image.Image, side: str, raised: int) -> None:
    draw = ImageDraw.Draw(cell, "RGBA")
    cx = 126 if side == "right" else 66
    cy = 106 - raised
    color = (201, 137, 83, 255)
    outline = (58, 42, 32, 255)
    draw.ellipse((cx - 13, cy - 10, cx + 13, cy + 12), fill=outline)
    draw.ellipse((cx - 10, cy - 8, cx + 10, cy + 9), fill=color)


def draw_tear(cell: Image.Image) -> None:
    draw = ImageDraw.Draw(cell, "RGBA")
    # Attached to the face area, not a detached effect.
    draw.ellipse((116, 83, 126, 97), fill=(71, 160, 230, 255), outline=(38, 83, 132, 255))


def make_frames(base: Image.Image) -> dict[str, list[Image.Image]]:
    frames: dict[str, list[Image.Image]] = {}

    frames["idle"] = [
        place(affine(base, sy=1 + d, sx=1 - d * 0.35), y=y)
        for d, y in [(0, 0), (0.012, -1), (0.02, -2), (0.012, -1), (0, 0), (-0.01, 1)]
    ]

    rr = []
    for i in range(8):
        phase = math.sin(i / 8 * math.tau)
        rr.append(place(affine(base, sx=1.02, sy=0.98 + 0.04 * abs(phase), rotate=-5 + phase * 5), x=round(phase * 7), y=round(-5 * abs(phase))))
    frames["running-right"] = rr
    frames["running-left"] = [ImageOps.mirror(frame) for frame in rr]

    wave = []
    for i, raised in enumerate([0, 18, 28, 10]):
        frame = place(affine(base, rotate=[0, -3, -4, -2][i]), y=[0, -1, -1, 0][i])
        draw_paw(frame, "right", raised)
        wave.append(frame)
    frames["waving"] = wave

    jump_specs = [(1.07, 0.92, 0, 8), (0.96, 1.08, 0, -8), (0.98, 1.03, 0, -28), (1.0, 1.0, 0, -14), (1.08, 0.9, 0, 6)]
    frames["jumping"] = [place(affine(base, sx=sx, sy=sy, rotate=rot), y=y) for sx, sy, rot, y in jump_specs]

    failed = []
    for i in range(8):
        frame = place(affine(base, sx=1.02, sy=0.92, rotate=(-8 if i % 2 else -5)), y=10 + (i % 2))
        if i >= 2:
            draw_tear(frame)
        failed.append(frame)
    frames["failed"] = failed

    frames["waiting"] = [
        place(affine(base, rotate=rot, sy=1 + stretch), x=x, y=y)
        for rot, stretch, x, y in [(0, 0, 0, 0), (2, 0.01, 1, -1), (4, 0.015, 2, -2), (2, 0.01, 1, -1), (0, 0, 0, 0), (-2, 0.005, -1, 0)]
    ]

    frames["running"] = [
        place(affine(base, sx=1 + 0.025 * math.sin(i / 6 * math.tau), sy=1 + 0.035 * math.cos(i / 6 * math.tau), rotate=3 * math.sin(i / 6 * math.tau)), y=round(-4 * abs(math.sin(i / 6 * math.tau))))
        for i in range(6)
    ]

    frames["review"] = [
        place(affine(base, sx=1.02, sy=0.99, rotate=rot), x=x, y=y)
        for rot, x, y in [(-3, -1, 0), (-5, -2, -1), (-6, -2, -1), (-4, -1, 0), (-2, 0, 1), (-3, -1, 0)]
    ]

    return frames


def save_atlas(frames: dict[str, list[Image.Image]]) -> Image.Image:
    atlas = Image.new("RGBA", (CELL_W * COLUMNS, CELL_H * ROWS), (0, 0, 0, 0))
    for row, (state, count) in enumerate(ROWS_DEF):
        state_dir = RUN_DIR / "frames" / state
        state_dir.mkdir(parents=True, exist_ok=True)
        for col in range(count):
            frame = frames[state][col]
            frame.save(state_dir / f"{col:02d}.png")
            atlas.alpha_composite(frame, (col * CELL_W, row * CELL_H))
    atlas.save(OUT_FINAL / "spritesheet.png")
    atlas.save(OUT_FINAL / "spritesheet.webp", format="WEBP", lossless=True, quality=100, method=6)
    return atlas


def main() -> None:
    ensure_dirs()
    cutout = fit_sprite(extract_pet())
    cutout.save(OUT_RAW / "potato-sprite-base.png")
    frames = make_frames(cutout)
    save_atlas(frames)
    print(OUT_FINAL / "spritesheet.png")


if __name__ == "__main__":
    main()
