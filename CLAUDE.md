# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

RoundSeq is a circular touchscreen MIDI sequencer for Raspberry Pi with a 1080×1080 round display (Waveshare 5"). Built with Kivy and mido/python-rtmidi for MIDI output. Development happens on macOS (windowed mode, mock MIDI), deployment to Raspberry Pi (fullscreen, hardware MIDI via Pisound HAT).

## Commands

```bash
# Run the app (macOS development)
python main.py

# Run tests
python -m pytest tests/

# Deploy to Pi (SSH profile: raspi)
rsync -avz --exclude 'venv' --exclude '__pycache__' --exclude '.git' \
  ./ raspi:~/RoundSeq/

# Restart app on Pi
ssh raspi "sudo systemctl restart roundseq"

# View Pi logs
ssh raspi "sudo journalctl -u roundseq -n 50 --no-pager"
```

## Architecture

```
main.py → roundseq.app.run() → RoundSeqApp (Kivy App)
                                    │
                                    ├── MidiService (factory selects impl by platform)
                                    │   ├── RtmidiService (Pi/real MIDI)
                                    │   └── MockMidiService (macOS/fallback)
                                    │
                                    └── NotePlayScreen
                                        ├── CircularNoteLayout (12 pie-slice buttons)
                                        │   └── PieSliceButton (radial button with Mesh rendering)
                                        └── CenterDisplay (octave +/- controls, note name)
```

**Key modules:**
- `roundseq/geometry.py` - Pure radial math: polar↔cartesian, angle containment, arc/ring collision detection
- `roundseq/config.py` - Display dimensions (1080×1080), colors, MIDI settings
- `roundseq/platform.py` - Platform detection (checks `/proc/device-tree/model` for Pi)

**Touch flow:**
1. User touches screen → `CircularNoteLayout.on_touch_down()`
2. Layout uses `geometry.point_in_arc()` for collision detection
3. Activates `PieSliceButton` → callback to `NotePlayScreen._on_note_on()`
4. `MidiService.note_on()` sends MIDI message
5. Sliding between notes handled via `on_touch_move()` tracking

## Display Configuration

The round display has visible area only in the circle - corners are hidden. Safe content radius is ~480px from center (540, 540).

```python
# Key constants from config.py
DISPLAY_WIDTH = DISPLAY_HEIGHT = 1080
OUTER_RADIUS = 513  # Note buttons outer edge
INNER_RADIUS = 297  # Note buttons inner edge
CENTER_RADIUS = 243  # Center display area
```

## Platform Behavior

- **macOS**: Windowed 1080×1080, mock MIDI (logs to console), mouse simulates touch
- **Raspberry Pi**: Fullscreen, real MIDI via rtmidi, touch input via mtdev
- Platform auto-detected at startup; MIDI service selected via factory pattern

## Dependencies

- **kivy** ≥2.2.0 - GUI framework
- **mido** ≥1.3.0 - MIDI message abstraction
- **python-rtmidi** ≥1.5.0 - Hardware MIDI (may fail on older Pi armv7l, app falls back to mock)

## Additional Documentation

- `PROJECT_PLAN.md` - Full project overview, milestones, hardware details
- `docs/PI_SETUP.md` - Raspberry Pi deployment guide (OS, display config, systemd service)
