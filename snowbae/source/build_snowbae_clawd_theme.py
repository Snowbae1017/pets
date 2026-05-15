#!/usr/bin/env python3
"""Build a Clawd on Desk theme from the Snowbae Codex pet frames."""

from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path

from PIL import Image, ImageSequence


ROOT = Path(__file__).resolve().parents[2]
RUN = ROOT / "snowbae" / "source" / "snowbae-run"
FRAMES = RUN / "frames"
OUT = ROOT / "snowbae" / "clawd-on-desk"
ASSETS = OUT / "assets"
TMP = Path("/private/tmp/snowbae-clawd-theme-build")
FFMPEG = shutil.which("ffmpeg") or "/opt/homebrew/bin/ffmpeg"

VIEW_W = 266
VIEW_H = 200
CONTENT_X = 50
CONTENT_Y = 8
CONTENT_W = 166
CONTENT_H = 182
BASELINE_Y = 190
CENTER_X = 133


STATE_DURATIONS_MS = {
    "idle": 200,
    "running-right": 120,
    "running-left": 120,
    "waving": 160,
    "jumping": 150,
    "failed": 170,
    "waiting": 180,
    "running": 130,
    "review": 180,
}


ASSET_SOURCES = {
    "snowbae-idle.apng": "idle",
    "snowbae-yawning.apng": "waiting",
    "snowbae-dozing.apng": "waiting",
    "snowbae-collapsing.apng": "failed",
    "snowbae-thinking.apng": "review",
    "snowbae-working-typing.apng": "running",
    "snowbae-working-building.apng": "running",
    "snowbae-working-juggling.apng": "jumping",
    "snowbae-working-conducting.apng": "review",
    "snowbae-working-sweeping.apng": "running",
    "snowbae-working-carrying.apng": "running",
    "snowbae-error.apng": "failed",
    "snowbae-happy.apng": "waving",
    "snowbae-notification.apng": "waving",
    "snowbae-sleeping.apng": "failed",
    "snowbae-waking.apng": "jumping",
    "snowbae-react-drag.apng": "running-left",
    "snowbae-react-poke.apng": "waving",
    "snowbae-react-left.apng": "running-left",
    "snowbae-mini-idle.apng": "idle",
    "snowbae-mini-alert.apng": "waving",
    "snowbae-mini-happy.apng": "waving",
    "snowbae-mini-enter.apng": "running-right",
    "snowbae-mini-peek.apng": "waiting",
    "snowbae-mini-crabwalk.apng": "running-right",
    "snowbae-mini-sleep.apng": "failed",
}


def load_frames(state: str) -> list[Image.Image]:
    paths = sorted((FRAMES / state).glob("*.png"))
    if not paths:
        raise SystemExit(f"no frames for state: {state}")
    return [Image.open(path).convert("RGBA") for path in paths]


def fit_frame(frame: Image.Image, *, mini: bool = False) -> Image.Image:
    bbox = frame.getbbox()
    canvas = Image.new("RGBA", (VIEW_W, VIEW_H), (0, 0, 0, 0))
    if bbox is None:
        return canvas

    sprite = frame.crop(bbox)
    max_w = CONTENT_W
    max_h = CONTENT_H
    if mini:
        max_w = round(max_w * 0.62)
        max_h = round(max_h * 0.62)

    scale = min(max_w / sprite.width, max_h / sprite.height)
    size = (max(1, round(sprite.width * scale)), max(1, round(sprite.height * scale)))
    sprite = sprite.resize(size, Image.Resampling.LANCZOS)
    left = round(CENTER_X - sprite.width / 2)
    top = round(BASELINE_Y - sprite.height)
    if mini:
        top = round(VIEW_H - sprite.height - 8)
    canvas.alpha_composite(sprite, (left, top))
    return canvas


def write_png_sequence(name: str, state: str) -> tuple[Path, int]:
    mini = "-mini-" in name
    seq_dir = TMP / name.replace(".apng", "")
    if seq_dir.exists():
        shutil.rmtree(seq_dir)
    seq_dir.mkdir(parents=True, exist_ok=True)
    frames = load_frames(state)
    for index, frame in enumerate(frames):
        fit_frame(frame, mini=mini).save(seq_dir / f"frame_{index:03d}.png")
    return seq_dir, len(frames)


def make_apng(name: str, state: str) -> None:
    seq_dir, count = write_png_sequence(name, state)
    out = ASSETS / name
    fps = max(1, round(1000 / STATE_DURATIONS_MS[state]))
    command = [
        FFMPEG,
        "-y",
        "-v",
        "error",
        "-framerate",
        str(fps),
        "-i",
        str(seq_dir / "frame_%03d.png"),
        "-plays",
        "0",
        "-f",
        "apng",
        str(out),
    ]
    subprocess.run(command, check=True)
    with Image.open(out) as image:
        if image.size != (VIEW_W, VIEW_H):
            raise SystemExit(f"{out} has wrong size {image.size}")
        if getattr(image, "n_frames", 1) != count:
            raise SystemExit(f"{out} has wrong frame count")


def make_preview() -> None:
    frame = load_frames("idle")[0]
    fit_frame(frame).save(ASSETS / "snowbae-preview.png")


def make_contact_sheet() -> None:
    files = sorted(ASSETS.glob("snowbae-*.apng"))
    thumb_w, thumb_h = VIEW_W, VIEW_H
    cols = 4
    rows = (len(files) + cols - 1) // cols
    sheet = Image.new("RGBA", (cols * thumb_w, rows * thumb_h), (255, 255, 255, 255))
    for index, path in enumerate(files):
        with Image.open(path) as opened:
            frame = next(ImageSequence.Iterator(opened)).convert("RGBA")
        sheet.alpha_composite(frame, ((index % cols) * thumb_w, (index // cols) * thumb_h))
    sheet.save(OUT / "snowbae-theme-contact-sheet.png")


def theme_json() -> dict[str, object]:
    return {
        "schemaVersion": 1,
        "name": "Snowbae",
        "author": "xueyuan / Codex",
        "version": "1.0.0",
        "description": "A snow-cloaked chibi desktop companion converted from the Codex Snowbae pet.",
        "viewBox": {"x": 0, "y": 0, "width": VIEW_W, "height": VIEW_H},
        "layout": {
            "contentBox": {
                "x": CONTENT_X,
                "y": CONTENT_Y,
                "width": CONTENT_W,
                "height": CONTENT_H,
            },
            "centerX": CENTER_X,
            "baselineY": BASELINE_Y,
            "visibleHeightRatio": 0.38,
            "baselineBottomRatio": 0.05,
        },
        "eyeTracking": {"enabled": False, "states": []},
        "states": {
            "idle": ["snowbae-idle.apng"],
            "yawning": ["snowbae-yawning.apng"],
            "dozing": ["snowbae-dozing.apng"],
            "collapsing": ["snowbae-collapsing.apng"],
            "thinking": ["snowbae-thinking.apng"],
            "working": ["snowbae-working-typing.apng"],
            "juggling": ["snowbae-working-juggling.apng"],
            "sweeping": ["snowbae-working-sweeping.apng"],
            "error": ["snowbae-error.apng"],
            "attention": ["snowbae-happy.apng"],
            "notification": ["snowbae-notification.apng"],
            "carrying": ["snowbae-working-carrying.apng"],
            "sleeping": ["snowbae-sleeping.apng"],
            "waking": ["snowbae-waking.apng"],
        },
        "sleepSequence": {"mode": "full"},
        "workingTiers": [
            {"minSessions": 3, "file": "snowbae-working-building.apng"},
            {"minSessions": 2, "file": "snowbae-working-juggling.apng"},
            {"minSessions": 1, "file": "snowbae-working-typing.apng"},
        ],
        "jugglingTiers": [
            {"minSessions": 2, "file": "snowbae-working-conducting.apng"},
            {"minSessions": 1, "file": "snowbae-working-juggling.apng"},
        ],
        "idleAnimations": [{"file": "snowbae-idle.apng", "duration": 5200}],
        "displayHintMap": {
            "clawd-working-building.svg": "snowbae-working-building.apng",
            "clawd-working-typing.svg": "snowbae-working-typing.apng",
            "clawd-working-juggling.svg": "snowbae-working-juggling.apng",
            "clawd-working-conducting.svg": "snowbae-working-conducting.apng",
            "clawd-working-thinking.svg": "snowbae-thinking.apng",
        },
        "timings": {
            "minDisplay": {
                "attention": 3200,
                "error": 3600,
                "sweeping": 4200,
                "notification": 3200,
                "carrying": 2600,
                "working": 1000,
                "thinking": 1000,
            },
            "autoReturn": {
                "attention": 3200,
                "error": 3600,
                "sweeping": 300000,
                "notification": 3200,
                "carrying": 2600,
            },
            "dndSkipYawn": True,
            "collapseDuration": 4200,
            "yawnDuration": 2600,
            "wakeDuration": 1800,
            "deepSleepTimeout": 600000,
            "mouseIdleTimeout": 20000,
            "mouseSleepTimeout": 60000,
        },
        "hitBoxes": {
            "default": {"x": 72, "y": 20, "w": 122, "h": 170},
            "sleeping": {"x": 62, "y": 48, "w": 142, "h": 136},
            "wide": {"x": 50, "y": 8, "w": 166, "h": 182},
        },
        "wideHitboxFiles": [
            "snowbae-error.apng",
            "snowbae-notification.apng",
            "snowbae-working-conducting.apng",
            "snowbae-working-sweeping.apng",
            "snowbae-working-carrying.apng",
        ],
        "sleepingHitboxFiles": ["snowbae-sleeping.apng", "snowbae-collapsing.apng"],
        "reactions": {
            "drag": {"file": "snowbae-react-drag.apng"},
            "clickLeft": {"file": "snowbae-react-poke.apng", "duration": 2500},
            "clickRight": {"file": "snowbae-react-poke.apng", "duration": 2500},
            "double": {"files": ["snowbae-happy.apng"], "duration": 3000},
        },
        "miniMode": {
            "supported": True,
            "flipAssets": True,
            "offsetRatio": 0.4,
            "states": {
                "mini-idle": ["snowbae-mini-idle.apng"],
                "mini-alert": ["snowbae-mini-alert.apng"],
                "mini-happy": ["snowbae-mini-happy.apng"],
                "mini-enter": ["snowbae-mini-enter.apng"],
                "mini-peek": ["snowbae-mini-peek.apng"],
                "mini-crabwalk": ["snowbae-mini-crabwalk.apng"],
                "mini-enter-sleep": ["snowbae-mini-sleep.apng"],
                "mini-sleep": ["snowbae-mini-sleep.apng"],
            },
            "timings": {
                "minDisplay": {
                    "mini-alert": 3000,
                    "mini-happy": 3000,
                    "mini-peek": 1500,
                },
                "autoReturn": {
                    "mini-alert": 3000,
                    "mini-happy": 3000,
                    "mini-peek": 1500,
                },
            },
        },
        "transitions": {
            "snowbae-idle.apng": {"out": 220},
            "snowbae-happy.apng": {"in": 120, "out": 300},
            "snowbae-error.apng": {"in": 120, "out": 360},
            "snowbae-sleeping.apng": {"in": 240},
            "snowbae-waking.apng": {"out": 220},
        },
    }


def main() -> None:
    if OUT.exists():
        shutil.rmtree(OUT)
    ASSETS.mkdir(parents=True, exist_ok=True)
    if TMP.exists():
        shutil.rmtree(TMP)
    TMP.mkdir(parents=True, exist_ok=True)

    shutil.copy2(RUN / "final" / "spritesheet.webp", OUT / "codex-spritesheet-source.webp")
    for name, state in ASSET_SOURCES.items():
        make_apng(name, state)
    make_preview()
    make_contact_sheet()
    (OUT / "theme.json").write_text(
        json.dumps(theme_json(), indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    print(json.dumps({"ok": True, "theme": str(OUT), "assets": len(ASSET_SOURCES)}, indent=2))


if __name__ == "__main__":
    main()
