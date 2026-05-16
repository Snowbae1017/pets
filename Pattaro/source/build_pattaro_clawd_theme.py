#!/usr/bin/env python3
"""Build a Clawd on Desk theme from the Pattaro Codex pet frames."""

from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path

from PIL import Image, ImageSequence


PET_DIR = Path(__file__).resolve().parents[1]
RUN = PET_DIR / "source" / "Pattaro-run"
FRAMES = RUN / "frames"
OUT = PET_DIR / "clawd-on-desk"
ASSETS = OUT / "assets"
TMP = Path("/private/tmp/pattaro-clawd-theme-build")
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
    "pattaro-idle.apng": "idle",
    "pattaro-yawning.apng": "waiting",
    "pattaro-dozing.apng": "waiting",
    "pattaro-collapsing.apng": "failed",
    "pattaro-thinking.apng": "review",
    "pattaro-working-typing.apng": "running",
    "pattaro-working-building.apng": "running",
    "pattaro-working-juggling.apng": "jumping",
    "pattaro-working-conducting.apng": "review",
    "pattaro-working-sweeping.apng": "running",
    "pattaro-working-carrying.apng": "running",
    "pattaro-error.apng": "failed",
    "pattaro-happy.apng": "waving",
    "pattaro-notification.apng": "waving",
    "pattaro-sleeping.apng": "failed",
    "pattaro-waking.apng": "jumping",
    "pattaro-react-drag.apng": "running-left",
    "pattaro-react-poke.apng": "waving",
    "pattaro-react-left.apng": "running-left",
    "pattaro-mini-idle.apng": "idle",
    "pattaro-mini-alert.apng": "waving",
    "pattaro-mini-happy.apng": "waving",
    "pattaro-mini-enter.apng": "running-right",
    "pattaro-mini-peek.apng": "waiting",
    "pattaro-mini-crabwalk.apng": "running-right",
    "pattaro-mini-sleep.apng": "failed",
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
    fit_frame(frame).save(ASSETS / "pattaro-preview.png")


def make_contact_sheet() -> None:
    files = sorted(ASSETS.glob("pattaro-*.apng"))
    thumb_w, thumb_h = VIEW_W, VIEW_H
    cols = 4
    rows = (len(files) + cols - 1) // cols
    sheet = Image.new("RGBA", (cols * thumb_w, rows * thumb_h), (255, 255, 255, 255))
    for index, path in enumerate(files):
        with Image.open(path) as opened:
            frame = next(ImageSequence.Iterator(opened)).convert("RGBA")
        sheet.alpha_composite(frame, ((index % cols) * thumb_w, (index // cols) * thumb_h))
    sheet.save(OUT / "pattaro-theme-contact-sheet.png")


def asset(name: str) -> str:
    return f"pattaro-{name}.apng"


def theme_json() -> dict[str, object]:
    return {
        "schemaVersion": 1,
        "name": "Pattaro",
        "author": "xueyuan / Codex",
        "version": "1.0.0",
        "description": (
            "A petite twin-braided chibi desktop companion converted from the "
            "Codex Pattaro pet."
        ),
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
            "idle": [asset("idle")],
            "yawning": [asset("yawning")],
            "dozing": [asset("dozing")],
            "collapsing": [asset("collapsing")],
            "thinking": [asset("thinking")],
            "working": [asset("working-typing")],
            "juggling": [asset("working-juggling")],
            "sweeping": [asset("working-sweeping")],
            "error": [asset("error")],
            "attention": [asset("happy")],
            "notification": [asset("notification")],
            "carrying": [asset("working-carrying")],
            "sleeping": [asset("sleeping")],
            "waking": [asset("waking")],
        },
        "sleepSequence": {"mode": "full"},
        "workingTiers": [
            {"minSessions": 3, "file": asset("working-building")},
            {"minSessions": 2, "file": asset("working-juggling")},
            {"minSessions": 1, "file": asset("working-typing")},
        ],
        "jugglingTiers": [
            {"minSessions": 2, "file": asset("working-conducting")},
            {"minSessions": 1, "file": asset("working-juggling")},
        ],
        "idleAnimations": [{"file": asset("idle"), "duration": 5200}],
        "displayHintMap": {
            "clawd-working-building.svg": asset("working-building"),
            "clawd-working-typing.svg": asset("working-typing"),
            "clawd-working-juggling.svg": asset("working-juggling"),
            "clawd-working-conducting.svg": asset("working-conducting"),
            "clawd-working-thinking.svg": asset("thinking"),
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
            "default": {"x": 64, "y": 16, "w": 138, "h": 174},
            "sleeping": {"x": 50, "y": 34, "w": 166, "h": 150},
            "wide": {"x": 50, "y": 8, "w": 166, "h": 182},
        },
        "wideHitboxFiles": [
            asset("error"),
            asset("notification"),
            asset("working-conducting"),
            asset("working-sweeping"),
            asset("working-carrying"),
        ],
        "sleepingHitboxFiles": [asset("sleeping"), asset("collapsing")],
        "reactions": {
            "drag": {"file": asset("react-drag")},
            "clickLeft": {"file": asset("react-poke"), "duration": 2500},
            "clickRight": {"file": asset("react-poke"), "duration": 2500},
            "double": {"files": [asset("happy")], "duration": 3000},
        },
        "miniMode": {
            "supported": True,
            "flipAssets": True,
            "offsetRatio": 0.4,
            "states": {
                "mini-idle": [asset("mini-idle")],
                "mini-alert": [asset("mini-alert")],
                "mini-happy": [asset("mini-happy")],
                "mini-enter": [asset("mini-enter")],
                "mini-peek": [asset("mini-peek")],
                "mini-crabwalk": [asset("mini-crabwalk")],
                "mini-enter-sleep": [asset("mini-sleep")],
                "mini-sleep": [asset("mini-sleep")],
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
            asset("idle"): {"out": 220},
            asset("happy"): {"in": 120, "out": 300},
            asset("error"): {"in": 120, "out": 360},
            asset("sleeping"): {"in": 240},
            asset("waking"): {"out": 220},
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
