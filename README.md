# 🐾 Desktop Pets

[English](./README.md) | [中文](./README_zh.md)

My custom desktop pets for [Codex](https://openai.com/codex) and [Clawd on Desk](https://github.com/rullerzhou-afk/clawd-on-desk).

## Pets

| Name | Description |
|------|-------------|
| **baby-potato** | A champagne teddy-bear-like poodle-bichon mix (baby version) |
| **child-potato** | A champagne teddy-bear-like poodle-bichon mix (grown-up version) |
| **cheese** | A short-legged, chubby blue-and-white British Shorthair cat |
| **my-cat** | A fluffy cream-golden long-haired cat |

## Repo Structure

```
<pet-name>/
├── codex/
│   ├── pet.json            # Codex pet manifest
│   └── spritesheet.webp    # 1536×1872 sprite atlas (8×9 grid, 192×208 per frame)
├── clawd-on-desk/
│   ├── theme.json           # Clawd on Desk theme config
│   ├── assets/              # APNG animations for each state
│   ├── *-contact-sheet.png  # Reference contact sheet
│   └── codex-spritesheet-source.webp
└── source/
    └── <hatch-run-name>/    # Original hatch-pet generation assets
        ├── pet_request.json     # Generation request config
        ├── imagegen-jobs.json   # Image generation job records
        ├── prompts/             # Prompts used for generation
        ├── references/          # Reference images
        ├── decoded/             # Decoded individual row images
        ├── frames/              # Frame extraction data
        ├── qa/                  # QA contact sheets and review data
        └── final/               # Final spritesheet output
```

## Quick Install (macOS)

```bash
./install.sh
```

This copies pets to:
- **Codex:** `~/.codex/pets/<pet-name>/`
- **Clawd on Desk:** `~/Library/Application Support/clawd-on-desk/themes/<pet-name>/`

Then restart the apps to see your pets.

## Manual Install

### Codex App

Copy the `codex/` contents to `~/.codex/pets/<pet-name>/`:

```bash
cp -r baby-potato/codex/ ~/.codex/pets/baby-potato/
```

Restart Codex, then activate via **Settings > Appearance > Pets**, or type `/pet` in the composer.

**Required files:**

| File | Description |
|------|-------------|
| `pet.json` | Manifest with id, displayName, description, spritesheetPath |
| `spritesheet.webp` | 1536×1872 px, 8 columns × 9 rows (192×208 per cell), transparent background |

<details>
<summary><b>Sprite sheet row layout</b></summary>

| Row | State | Frames |
|-----|-------|--------|
| 0 | idle | 6 |
| 1 | running-right | 8 |
| 2 | running-left | 8 |
| 3 | waving | 4 |
| 4 | jumping | 5 |
| 5 | failed | 8 |
| 6 | waiting | 6 |
| 7 | running (busy) | 6 |
| 8 | review | 6 |

</details>

### Clawd on Desk

Copy the `clawd-on-desk/` contents to `~/Library/Application Support/clawd-on-desk/themes/<pet-name>/`:

```bash
cp -r baby-potato/clawd-on-desk/ ~/Library/Application\ Support/clawd-on-desk/themes/baby-potato/
```

Restart Clawd on Desk, then activate via **Settings > Theme**.

**Required files:**

| File | Description |
|------|-------------|
| `theme.json` | Theme config (schemaVersion, name, viewBox, states, etc.) |
| `assets/` | Animation files (APNG/GIF/WebP/SVG) for each state |

<details>
<summary><b>Animation states</b></summary>

| State | Description |
|-------|-------------|
| idle | Default breathing/blinking loop |
| thinking | Processing/waiting for response |
| working | Active work (typing, building, juggling, conducting, sweeping, carrying) |
| error | Error/sad reaction |
| attention | Happy/greeting |
| notification | Alert notification |
| sleeping | Deep sleep |
| waking | Wake-up transition |
| yawning | Transition to sleep |
| dozing | Light sleep |
| collapsing | Falling asleep transition |

**Supported formats:** SVG (best for eye tracking), APNG (best quality animations), GIF, WebP, PNG, JPG

</details>

## Creating New Pets

### For Codex

1. Create a 1536×1872 sprite sheet with 9 rows of animations on transparent background
2. Write a `pet.json` with id, displayName, description
3. Place both in `~/.codex/pets/<pet-name>/`

Or use the built-in hatch-pet skill: type `/pet` then describe what you want.

**Full walkthrough:** See [examples/generate-pet-with-codex.md](examples/generate-pet-with-codex.md) for a step-by-step guide using Cheese as the example (generating from real pet photos with review gates).

### For Clawd on Desk

1. Run `node scripts/create-theme.js <name>` from the clawd-on-desk repo, or manually create the folder
2. Add APNG/GIF assets for each animation state
3. Configure `theme.json` with viewBox, states mapping, and timings
4. Validate with `node scripts/validate-theme.js path/to/theme`

Minimum viable theme needs only 4 images (idle, thinking, working, sleeping) — other states can use `fallbackTo`.

## Platform Comparison

| | Codex | Clawd on Desk |
|---|---|---|
| Install path | `~/.codex/pets/<name>/` | `~/Library/Application Support/clawd-on-desk/themes/<name>/` |
| Config file | `pet.json` | `theme.json` (schemaVersion 1) |
| Art assets | Single spritesheet (1536×1872, 8×9 grid) | Individual APNG/GIF/SVG per state |
| Activate | Settings > Pets or `/pet` | Settings > Theme |
| Min assets | 1 spritesheet | 4 images (idle, thinking, working, sleeping) |

## License

Personal use. Pet artwork is original.
