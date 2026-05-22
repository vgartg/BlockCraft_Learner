# BlockCraft Learner Game

A small pygame sandbox built as a pet project to teach Python through hands-on edits. You modify the files under `mods/` and instantly see the world change — colours, blocks, gravity, world size — and gradually move on to the harder tasks listed in `TASKS.md`

![CI](https://github.com/vgartg/BlockCraft-Learner-Game/actions/workflows/ci.yml/badge.svg)
![Python](https://img.shields.io/badge/python-3.10%2B-3776AB?logo=python&logoColor=white)
![pygame](https://img.shields.io/badge/pygame-2.5.2-44a833)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE.txt)

## Demo

https://github.com/user-attachments/assets/122c656d-62f7-4d30-b45b-a681ed769d59

## Features

- Side-scrolling block world with grass, dirt, stone, wood and leaves
- Hand-rolled physics: gravity, jumping, axis-separated collisions and "snap to ground" landing
- Inventory of every block type with per-block counts and a click-to-select hotbar
- Mining and placement with support-block checks, no clipping into the player and texture-aware rendering
- Pluggable block dictionary (`mods/my_blocks.py`) — add a new block by appending a dict entry and dropping a 40×40 PNG into `assets/textures/`
- Pluggable player profile (`mods/my_player.py`) — colour, speed, jump power, start position
- Pluggable world settings (`mods/my_config.py`) — screen size, world size, gravity, FPS, sky colour
- Self-healing world generator: if generation fails, a tiny fallback world is rendered with a visible error banner

## Project layout

```
.
├── blockcraft/        engine, renderer and headless I/O helpers (do not edit)
├── mods/              what you change to learn: blocks, player, world settings
├── assets/textures/   40x40 PNG block textures
├── tests/             headless pytest suite (no display required)
├── main.py            backwards-compatible entry (same as `python -m blockcraft`)
└── TASKS.md           graded learning tasks (easy / medium / hard)
```

The `blockcraft` package holds the parts that should stay stable while users learn. The `mods/` folder is the public surface — every learning task in `TASKS.md` is solved by editing a file there or under `assets/textures/`

## Requirements

- Python 3.10 or newer
- pygame 2.5.2 (pinned)
- Windows, macOS or Linux desktop with a graphics output

On Linux you also need the SDL2 runtime libraries (`libsdl2`, `libsdl2-image`, `libsdl2-ttf`); on Debian/Ubuntu install them with `apt-get` as shown in the CI workflow

## Quickstart

```bash
pip install -r requirements.txt
python -m blockcraft
```

Or, if you prefer the legacy entry point:

```bash
python main.py
```

Once the window opens, the world generates and the player spawns on top of a dirt column near the left edge

## Controls

```
Move left / right       A / D  or  ← / →
Jump                    W / ↑ / Space
Break block             Left mouse button on a world block
Place selected block    Right mouse button on an empty cell with a neighbour
Select block (hotbar)   1..8  or  left-click on the inventory strip
Quit                    Esc  or  F4
```

## Learning tasks

`TASKS.md` ships a graded set of edits, written in Russian for the original audience of the project, grouped into three tiers:

- **Easy** — change a parameter (player colour, jump power, sky colour, world size)
- **Medium** — add a new block (sand, bedrock), pick a different spawn point, build a teleport block
- **Hard** — change behaviour (falling sand, doubled drops, day/night cycle, crafting, a wandering zombie mob)

Every task is solved by editing files under `mods/`, sometimes adding a texture under `assets/textures/`, and never by touching the `blockcraft/` package itself

## Editing the game

The three files under `mods/` are the only place where learners normally make changes:

| File | What it controls |
| --- | --- |
| `mods/my_config.py` | screen size, world size, gravity, FPS, window title, sky colour |
| `mods/my_blocks.py` | which blocks exist, whether they are solid / breakable, which texture they use |
| `mods/my_player.py` | player colour, speed, jump power, spawn coordinates |

Each file is heavily commented (in Russian) and includes example entries you can uncomment as a starting point. Texture files live in `assets/textures/` and must be 40×40 PNGs to fit the block grid

## Testing

```bash
pip install -e ".[dev]"
python -m pytest
```

The test suite runs headless — it sets `SDL_VIDEODRIVER=dummy` in `tests/conftest.py` so pygame initialises without a real window. The tests cover the mods contract, world generation, inventory bookkeeping and block-breaking semantics

## Linting

```bash
ruff check .
ruff format --check .
```

`ruff format .` rewrites the tree, `ruff check --fix .` applies safe automatic fixes. The configuration lives under `[tool.ruff]` in `pyproject.toml` with a relaxed 120-column line length, on purpose, to fit the Russian-language comments without forced wrapping

## Continuous integration

The [`ci` workflow](.github/workflows/ci.yml) runs on every push and pull request to `main`:

1. `test` job — pytest across Python 3.10, 3.11 and 3.12 with headless SDL drivers and the apt-installed SDL2 runtime
2. `lint` job — `ruff check` and `ruff format --check` on the latest Python

Both jobs run in parallel and the workflow uses GitHub's `concurrency` group so a new push cancels the previous in-flight run on the same branch
