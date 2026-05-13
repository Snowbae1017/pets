# Example: Generate a Desktop Pet with Codex App

This walkthrough uses **Cheese** (a blue-and-white British Shorthair cat) as the example to show the full flow of generating a custom Codex desktop pet from your own pet photos.

## Prerequisites

- [Codex App](https://openai.com/codex) (macOS) — has built-in `/pet` skill with `$imagegen`
- Pet photos: a few face and body shots in a folder (e.g. `~/Downloads/cheese/`)
- Image generation model: `gpt-image-2` (or your preferred model)

## Prompt

Open Codex App, start a new session, and enter:

```
I want to generate a desktop digital pet from my real pet's photos. The photos are
in ~/Downloads/cheese — there are face/look shots and body shots. She's a short-legged,
chubby blue-and-white British Shorthair cat. Please follow the Codex App pet requirements
to generate the sprites. The generated pet should preserve the real cat's fur flow
texture and expression/demeanor — don't make it overly cartoony or anime-like.
Show me the base image for review first — only continue with the rest of the animation
generation after I approve it.
```

> **Tip:** Codex CLI (`codex`) also supports this — just run the same prompt in terminal.

## What Happens Behind the Scenes

Codex uses its built-in `hatch-pet` skill, which orchestrates the full generation pipeline:

### Phase 1: Setup & Photo Analysis

1. Codex reads your photo folder and identifies reference images
2. Creates a working directory (e.g. `~/Downloads/cheese/hatch-pet-run-codex/`)
3. Copies references into `references/` and resizes for API use
4. Analyzes pet features to write `pet_request.json` — captures pet identity notes, chroma key selection, atlas spec, etc.

### Phase 2: Base Pet Generation (with review gate)

5. Writes `prompts/base-pet.md` — the authoritative sprite spec:
   - Pet description (extracted from photos + your text)
   - Style contract (pixel-art-adjacent, chibi, thick outline, flat shading)
   - Chroma key background color
6. Calls `$imagegen` (gpt-image-2) with your reference photos + the prompt
7. **Shows you the base sprite for approval** — this is the review gate you asked for

At this point you'll see something like:

```
Here's the base sprite for Cheese. The style is pixel-art chibi with:
- Gray-blue cap and cheeks, white muzzle
- Round amber eyes, pink nose
- Short legs, stocky compact body
- Flat #00FF00 chroma-key background

Does this look good? I can adjust before continuing.
```

If not satisfied, you can request revisions (multiple rounds are normal):

```
The face markings aren't quite right — please refer to the real photos for the gray
mask + white nose bridge. The fur flow should be more visible, it looks too smooth
like a rubber toy right now.
```

Each revision produces a variant saved to `previews/` — Cheese went through 5 variants:
- `cheese-base-v1.png` — initial attempt
- `cheese-base-v2-furflow.png` — added fur texture
- `cheese-base-v3-unobstructed-furflow.png` — unblocked face
- `cheese-base-v4-balanced-fur.png` — balanced fur detail
- `cheese-base-v5-v1-face-softened-v2-fur.png` — final approved ✓

### Phase 3: Animation Row Generation

Once the base is approved, Codex generates each animation row. The atlas is 1536×1872 (8 columns × 9 rows, each cell 192×208):

| Row | State | Frames | Description |
|-----|-------|--------|-------------|
| 0 | idle | 6 | Breathing/blinking loop |
| 1 | running-right | 8 | Rightward locomotion |
| 2 | running-left | 8 | Leftward (mirror of row 1) |
| 3 | waving | 4 | Greeting gesture |
| 4 | jumping | 5 | Jump arc |
| 5 | failed | 8 | Sad/deflated reaction |
| 6 | waiting | 6 | Patient waiting |
| 7 | running | 6 | Active working/busy |
| 8 | review | 6 | Inspecting/reviewing |

Each row is generated with:
- All reference photos as identity anchors
- The approved base sprite as identity reference
- A layout guide image showing frame slot boundaries
- A row-specific animation prompt

`running-left` uses a mirror policy — it flips `running-right` horizontally (no extra generation needed if the pet has no side-specific markings).

### Phase 4: Assembly & Validation

8. Extracts individual frames from each row strip (chroma key removal → transparent PNG)
9. Assembles all frames into the final `spritesheet.png` / `spritesheet.webp`
10. Generates a QA contact sheet and validation report
11. Creates `pet.json` manifest

## Output Structure

```
~/Downloads/cheese/hatch-pet-run-codex/
├── pet_request.json          # Full generation config
├── imagegen-jobs.json        # Job tracking (status, sha256, etc.)
├── prompts/
│   ├── base-pet.md           # Base sprite prompt
│   ├── variants/             # Revision prompts (v2, v3, ...)
│   └── rows/                 # Per-row animation prompts
├── references/
│   ├── reference-01..05.jpg  # Your pet photos (copied)
│   ├── canonical-base.png    # Approved base sprite
│   ├── api-sized/            # Resized for API calls
│   └── layout-guides/        # Frame slot guide images
├── previews/                 # Base sprite iterations
├── decoded/                  # Individual row strip PNGs
│   ├── base.png
│   ├── idle.png
│   ├── running-right.png
│   └── ...
├── frames/                   # Extracted per-frame PNGs
│   ├── idle/00.png..05.png
│   ├── running-right/00.png..07.png
│   └── ...
├── qa/
│   ├── contact-sheet.png     # All frames overview
│   ├── review.json           # Frame validation report
│   ├── run-summary.json
│   └── videos/               # Per-state preview animations
└── final/
    ├── spritesheet.png       # Final atlas (PNG)
    ├── spritesheet.webp      # Final atlas (WebP, lossless)
    └── validation.json
```

## Installing the Pet

After generation completes:

```bash
# Copy to Codex pets directory
mkdir -p ~/.codex/pets/cheese
cp final/spritesheet.webp ~/.codex/pets/cheese/
cat > ~/.codex/pets/cheese/pet.json << 'EOF'
{
  "id": "cheese",
  "displayName": "Cheese",
  "description": "A short-legged, chubby blue-and-white British Shorthair cat.",
  "spritesheetPath": "spritesheet.webp"
}
EOF
```

Restart Codex → **Settings > Appearance > Pets** → select Cheese.

Or use the install script from this repo:

```bash
./install.sh
```

## Bonus: Generate Clawd on Desk Theme from Codex Assets

After the Codex pet is done, you can reuse the generation assets (base sprite, references, decoded rows) to produce a [Clawd on Desk](https://github.com/rullerzhou-afk/clawd-on-desk) theme — which needs individual APNG animations per state rather than a single spritesheet.

### Prompt

In a new Codex App / Codex CLI session (or Claude Code with image generation capability):

```
I've already generated a Codex desktop pet for my cat Cheese. The generation assets
are in ~/Downloads/cheese/hatch-pet-run-codex/ (includes base sprite, reference photos,
decoded row strips, and individual frames).

Now I want to generate a Clawd on Desk theme for the same pet. Please reference the
existing theme in ~/pets/baby-potato/clawd-on-desk/ (theme.json + assets/) as a
structural example for the output format, state mapping, viewBox, transitions, mini
states, etc.

Generate APNG animations for all required Clawd on Desk states (idle, thinking,
working variants, error, sleeping, waking, yawning, dozing, collapsing, notification,
attention, reactions, mini states). Keep Cheese's identity consistent with the approved
Codex base sprite. Output to ~/Downloads/cheese/clawd-on-desk/.
```

### What the Agent Does

1. Reads the existing Codex generation assets (base sprite, decoded frames, references)
2. Studies the reference theme structure (`baby-potato/clawd-on-desk/`) for:
   - `theme.json` schema (viewBox, states, sleepSequence, workingTiers, miniMode, transitions)
   - Required animation states and naming convention (`<pet>-<state>.apng`)
   - Asset dimensions and timing parameters
3. Generates APNG animations for each state, preserving Cheese's identity from the canonical base
4. Produces `theme.json` with appropriate state mappings, working tiers, and transition timings
5. Outputs a preview image (`cheese-preview.png`) and contact sheet

### Clawd on Desk States (full set)

| Category | States |
|----------|--------|
| Core | idle, thinking, working-typing, error, sleeping |
| Sleep cycle | yawning, dozing, collapsing, waking |
| Working variants | building, carrying, conducting, juggling, sweeping |
| Reactions | happy (attention), notification, react-drag, react-poke, react-left |
| Mini mode | mini-idle, mini-alert, mini-happy, mini-enter, mini-peek, mini-crabwalk, mini-sleep |

### Install

```bash
cp -r ~/Downloads/cheese/clawd-on-desk/ ~/Library/Application\ Support/clawd-on-desk/themes/cheese/
```

Or use `./install.sh` from this repo.

## Tips

- **More reference photos = better identity preservation.** Cheese used 5 photos (2 face, 3 body) — the more angles the model sees, the less it hallucinates features.
- **Be specific in revision feedback.** "It doesn't look right" is too vague — say exactly what's wrong: "the gray mask area is too small" or "the eyes are too large, looks like anime".
- **The base sprite is the most important step.** All animation rows derive their identity from it, so invest time getting it right.
- **Chroma key is auto-selected** to avoid colors in your pet's palette. Cheese uses green `#00FF00` (not magenta) because gray-blue cats don't have green tones.
- **Generation model matters.** `gpt-image-2` handles the pixel-art chibi style well with reference-grounded generation. Swap in your preferred model if you have one.
- **Clawd on Desk from Codex assets is much faster** — the identity is already locked in, you just need different animation states and APNG format instead of a spritesheet.
