# GUI guide — screens, workflow, interactions, accessibility

Interface documentation required by the software guidelines §10.2. Covers both windows in
[`src/thief_agent/gui/`](../src/thief_agent/gui/): the **Live GUI** (rulebook Ch. 7.3) and
the **Replay Viewer** (Ch. 7.4).

---

## 1. Screens and states

### 1.1 Live GUI

![Live GUI with belief heatmap](images/thief-gui-belief-map.png)

| Region | Shows | Source |
|---|---|---|
| Banner | Turn state + connection, protocol state, step, deadline | `status_banner.banner`, `palette.banner_style` |
| Board | Belief heatmap, own marker, barriers | `tk_canvas.GridCanvas` |
| Side panel | Colour legend and the live read-out (role, tracked opponent, step, protocol state, most-likely cell, peak bucket, known barriers) | `live_model.legend_rows` |
| Caption | What the shading means and the hidden-position guarantee | `tk_live.LiveWindow.render` |

**States.** The banner has exactly two:

| State | Appearance | When | Meaning |
|---|---|---|---|
| `YOUR TURN` | green | protocol state in `{READY, MOVE}` | Input accepted |
| `LOCKED` | grey | any other state (`CONFIG`, `NEGOTIATE`, `COMMIT`, `REVEAL`, `DONE`) | Input rejected — prevents an out-of-turn or illegal action |

Both are driven by the same `status_banner.input_locked` predicate the protocol uses, so
the banner cannot disagree with the state machine. To see the LOCKED state directly:

```bash
uv run python -m thief_agent view --gui --state COMMIT
```

Board cells render in four mutually exclusive ways: **own marker** (blue `P` / amber `T`
disc), **barrier** (grey with an X), **belief-shaded cell** (0-9 red ramp with a numeral),
or **cold** (bucket 0). The opponent's true cell is never drawn — `leaks_opponent_position`
asserts exactly one player marker exists, and it is unit-tested.

### 1.2 Replay Viewer

![Replay viewer, verified](images/thief-replay-verified-ok.png)

| Region | Shows |
|---|---|
| Badge | `VERIFIED OK` (green) or `TAMPERED at steps …` (red) |
| Board | Recorded positions with a recency-shaded trail |
| Info panel | Sub-game, frame index, recorded step, mover, action, integrity explanation, failed steps, hint |
| Controls | **◀ Previous**, **Next ▶**, **Sub-game ↻**, and a `frame N / M (step S)` counter |

The badge is a *result*, not a caption: it is `replay_verify.replay_status`, which
recomputes `SHA-256(nonce, payload)` for every record. The red state is reachable and
demonstrated:

![Replay viewer, tampered](images/thief-replay-tampered.png)

## 2. Typical workflows

**A — inspect the belief map from a real match**

```bash
uv run python -m thief_agent artifacts --out /tmp/demo --game-id demo --seed 7
uv run python -m thief_agent view --gui --replay-dir /tmp/demo --game-id demo --step 8
```

1. The first command plays a local six-sub-game series and records both tracks.
2. The second replays the recorded trajectories through the real scent kernel, rebuilds the
   posterior the Cop actually held at step 8, and paints it.
3. Read the peak cell in the side panel, then compare it with the shading.

Without `--replay-dir` the window opens on the step-1 opening position, whose posterior is
legitimately flat — no evidence has been received yet.

**B — audit a finished match**

```bash
uv run python -m thief_agent replay --dir docs/evidence/G020 --game-id G020 --gui
```

1. The badge reports the verdict for the currently selected sub-game.
2. **Next ▶** advances one recorded turn; the board, counter and info panel update together.
3. **◀ Previous** steps back. Both buttons disable themselves at the ends of the log, so the
   cursor cannot leave the frame list.
4. **Sub-game ↻** cycles through the six logs of the series.

**C — headless / no display**

```bash
uv run python -m thief_agent view                                  # ASCII board + heatmap
uv run python -m thief_agent replay --dir docs/evidence/G020 --game-id G020
```

Same model layer, text renderer. This is the path CI uses, and the fallback on a machine
with no X display.

## 3. Interactions and feedback

| Interaction | Feedback |
|---|---|
| Click **Next ▶** / **◀ Previous** | Board, `frame N / M (step S)` counter and info panel update in one repaint |
| Reach either end of the log | The button greys out (`state="disabled"`) — the affordance disappears rather than failing silently |
| Click **Sub-game ↻** | Sub-game number changes in both the info panel and the badge; the cursor keeps its position |
| Load a directory with no replayable logs | Badge reads `NO REPLAYABLE LOGS` on red instead of an empty window |
| Load a tampered log | Badge turns red and names the failing step; the info panel lists `Failed steps` |
| Protocol enters a non-move state | Banner turns grey and reads `LOCKED` |

Every state change is announced in at least two places, so a missed repaint in one region
is still visible in another.

## 4. Accessibility

**What is done**

- **Colour is never the only channel.** The turn banner carries the words `YOUR TURN` /
  `LOCKED`; the integrity badge carries `VERIFIED OK` / `TAMPERED at steps …`; heat cells
  carry their 0-9 bucket numeral. A viewer who cannot distinguish red from green still gets
  every verdict from text.
- **Contrast.** Text is near-white on dark panels; badge text is white on saturated
  green/red; bucket numerals switch to a light tint on hot cells specifically so they stay
  legible (`palette.label_color`).
- **No motion, no timing.** Nothing animates, flashes, or auto-advances; there is no
  time-limited interaction in either window.
- **Text scales with the board.** Marker glyphs are sized from `cell_px`, so a larger
  window enlarges the text with it.
- **A non-visual path exists.** The headless renderer emits the same information as plain
  text, usable with any terminal reader.

**Known gaps — not yet addressed**

- No screen-reader testing. Tk canvas items expose no accessibility tree, so the board is
  effectively invisible to assistive technology; the headless renderer is the workaround.
- No keyboard navigation or shortcuts — Previous/Next require a pointer.
- Colours have not been validated against a formal WCAG contrast-ratio target, nor tested
  with a colour-blindness simulator.
- Window size is fixed at construction; there is no zoom control beyond the OS.

These are stated rather than quietly omitted. None of them affects league play, which is
driven entirely from the CLI.

## 5. Reproducing the screenshots

```bash
uv run python scripts/capture_gui.py live   --dir <evidence-dir> --game-id <id> \
    --role thief --out docs/images/thief-gui-belief-map.png
uv run python scripts/capture_gui.py replay --dir docs/evidence/G020 --game-id G020 \
    --expect "VERIFIED OK" --out docs/images/thief-replay-verified-ok.png
```

The capture tool photographs the real window with `ffmpeg -f x11grab` and **refuses** to
shoot a uniform belief map or a verdict that does not match `--expect`, so a screenshot
cannot misrepresent the state it claims to show.
