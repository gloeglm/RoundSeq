# RoundSeq - Circular Touchscreen MIDI Sequencer

## Project Overview

A touchscreen-based MIDI sequencer built for a circular display, designed to send MIDI commands to external synthesizers via hardware MIDI output.

## Hardware Components

| Component | Model | Interface |
|-----------|-------|-----------|
| Computer | Raspberry Pi 4/5 (40-pin GPIO) | - |
| Display | Waveshare 5" 1080×1080 Round LCD | HDMI (display) + USB (touch) |
| Audio/MIDI | Blokas Pisound | GPIO HAT, DIN-5 MIDI |

### Hardware Integration

```
Raspberry Pi
├── HDMI ──────► Waveshare Display (video signal)
├── USB ◄────── Waveshare Display (touch input)
└── GPIO ──────► Pisound HAT
                 ├── MIDI OUT (DIN-5) ──► External Synth
                 └── MIDI IN  (DIN-5) ◄── External Controller
```

## Development Workflow

Development happens on macOS, deployment to Raspberry Pi.

```
┌─────────────────────────────────────────────────────────────────┐
│                    DEVELOPMENT (macOS)                          │
├─────────────────────────────────────────────────────────────────┤
│  • Kivy app runs in 1080×1080 window                            │
│  • Mouse clicks simulate touch input                            │
│  • MockMidiService logs output (or uses IAC Driver)             │
│  • Fast iteration, full IDE support                             │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼ rsync / git
┌─────────────────────────────────────────────────────────────────┐
│                    DEPLOYMENT (Raspberry Pi 4)                  │
├─────────────────────────────────────────────────────────────────┤
│  • Fullscreen on round display                                  │
│  • Real touch input                                             │
│  • PisoundMidiService for hardware MIDI out                     │
└─────────────────────────────────────────────────────────────────┘
```

### Platform Detection

The app auto-detects the environment and configures accordingly:
- **macOS**: Windowed mode, mock/software MIDI
- **Raspberry Pi**: Fullscreen, Pisound MIDI

## Software Stack

| Layer | Technology | Purpose |
|-------|------------|---------|
| OS (dev) | macOS | Development environment |
| OS (prod) | Raspberry Pi OS (32-bit Legacy for older Pis) | Tested on Buster |
| UI Framework | Kivy | Touch UI with circular layout support |
| MIDI | mido + python-rtmidi | MIDI message handling |
| Audio Backend (prod) | ALSA + Pisound | Hardware MIDI interface |

**Note**: python-rtmidi may fail to install on older Pis (armv7l). The app falls back to mock MIDI.

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Kivy Application                     │
├─────────────────────────────────────────────────────────┤
│  Screens                                                │
│  ├── NotePlayScreen (initial milestone)                 │
│  ├── SequencerScreen (future)                           │
│  └── SettingsScreen (future)                            │
├─────────────────────────────────────────────────────────┤
│  Custom Widgets                                         │
│  ├── CircularSafeArea    - constrains content to circle │
│  ├── PieSliceButton      - radial note buttons          │
│  ├── CircularNoteLayout  - arranges notes in ring       │
│  └── CenterDisplay       - status/octave display        │
├─────────────────────────────────────────────────────────┤
│  Services                                               │
│  ├── MidiService         - mido wrapper, port mgmt      │
│  └── ConfigService       - user preferences (future)    │
└─────────────────────────────────────────────────────────┘
```

## UI Design for Round Display

The 1080×1080 framebuffer contains a circular visible area. UI must account for invisible corners.

```
Safe area calculations:
- Display diameter: 1080px
- Visible radius: 540px
- Safe content radius: ~480px (with margin)
- Center point: (540, 540)
```

### Initial UI Layout (Milestone 1)

```
            ┌─────┐
         ┌──┤ C#  ├──┐
       ┌─┤D └─────┘ C├─┐
     ┌─┤D#├─┐     ┌─┤B├─┐
     │ └──┘ │     │ └──┘│
     │E     │     │    A#
     │ ┌──┐ │ OCT │ ┌──┐│
     └─┤F ├─┘  4  └─┤A├─┘
       └─┤F#┌───┐G#├─┘
         └──┤ G ├──┘
            └───┘

- Outer ring: 12 note buttons (pie slices)
- Center: Octave display + octave up/down
```

## Implementation Milestones

### Milestone 1: Note Buttons with MIDI Output
**Goal**: Simple UI with touchable note buttons that send MIDI

#### Phase 1A: Local Development (macOS)
- [x] Project setup (venv, dependencies, folder structure)
- [x] Kivy app skeleton with 1080×1080 window
- [x] Platform detection (macOS vs Pi)
- [x] CircularSafeArea container widget
- [x] PieSliceButton widget with proper touch/click collision
- [x] CircularNoteLayout arranging 12 notes
- [x] MidiService interface with MockMidiService implementation
- [x] Connect touch/click events to MIDI output (console logging)
- [x] Center octave display and octave +/- controls
- [x] Touch sliding between notes (finger drag changes active note)

#### Phase 1B: Hardware Deployment (Raspberry Pi)
- [x] Kivy touchscreen configuration for round display (mtdev provider)
- [x] Fullscreen/borderless mode working
- [x] Python 3.7 compatibility (older Pis)
- [x] Setup documentation (docs/PI_SETUP.md)
- [ ] RtmidiService implementation (real MIDI out via Pisound)
- [ ] Auto-start service
- [ ] Test with Pisound and external synth (requires Pi 4 with 40-pin GPIO)

### Milestone 2: Visual Feedback and Polish
- [ ] Button press animations (color change, scale)
- [ ] Velocity sensitivity (touch duration or pressure if available)
- [ ] Visual feedback for active notes
- [ ] Configurable color schemes

### Milestone 3: Basic Sequencer
- [ ] Step sequencer data model
- [ ] Sequence playback engine (timing via Kivy Clock)
- [ ] Visual step grid (adapted for circular display)
- [ ] Play/pause/stop transport controls
- [ ] Tempo control

### Milestone 4: Advanced Features
- [ ] Multiple patterns/sequences
- [ ] MIDI input (record from external controller)
- [ ] Save/load sequences to file
- [ ] Settings screen (MIDI channel, velocity, scale modes)
- [ ] MIDI clock sync (send/receive)

### Future: Testing & Infrastructure
- [ ] Automated UI testing with pytest-kivy (simulate touches, verify all notes work)
- [ ] CI/CD pipeline (GitHub Actions)
- [ ] Disable debug colors for production

## Project Structure

```
RoundSeq/
├── main.py                 # Application entry point
├── roundseq/
│   ├── __init__.py
│   ├── app.py              # Main Kivy App class
│   ├── platform.py         # Platform detection (macOS vs Pi)
│   ├── config.py           # Display and app configuration
│   ├── geometry.py         # Radial math utilities
│   ├── widgets/
│   │   ├── __init__.py
│   │   ├── circular_safe_area.py
│   │   ├── pie_slice_button.py
│   │   ├── circular_note_layout.py
│   │   └── center_display.py
│   ├── screens/
│   │   ├── __init__.py
│   │   └── note_play_screen.py
│   ├── services/
│   │   ├── __init__.py
│   │   ├── midi_service.py      # Abstract interface + factory
│   │   ├── mock_midi_service.py # Console logging (dev/fallback)
│   │   └── rtmidi_service.py    # Real MIDI via rtmidi (prod)
│   └── kv/
│       ├── main.kv
│       └── note_play_screen.kv
├── tests/
│   └── test_geometry.py    # Geometry module unit tests
├── requirements.txt
├── requirements-pi.txt     # Minimal deps for older Pis
├── docs/
│   └── PI_SETUP.md         # Raspberry Pi setup guide
├── config/
│   └── kivy_config.ini     # Touchscreen input configuration (Pi)
└── scripts/
    ├── install-pi.sh       # Pi setup script
    └── deploy.sh           # rsync to Pi
```

## Dependencies

```
# requirements.txt (full)
kivy>=2.2.0
mido>=1.3.0
python-rtmidi>=1.5.0

# requirements-pi.txt (for older Pis where rtmidi fails)
kivy
mido
```

**Note**: On older Raspberry Pis (armv7l, Python 3.7), python-rtmidi may fail to build. Use requirements-pi.txt and the app will fall back to mock MIDI output.

## macOS Development Setup

### 1. Create Virtual Environment
```bash
cd RoundSeq
python3 -m venv venv
source venv/bin/activate
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Run the App
```bash
python main.py
```

The app will launch in a 1080×1080 window. Click to simulate touch.

### 4. Optional: Software MIDI (instead of mock)
macOS has a built-in IAC Driver for software MIDI routing:
1. Open "Audio MIDI Setup" app
2. Window → Show MIDI Studio
3. Double-click "IAC Driver", enable it
4. The app can then send MIDI to other apps (e.g., GarageBand, a soft synth)

## Raspberry Pi Setup

### 1. OS Installation
- Use Raspberry Pi OS Lite (64-bit recommended)
- No desktop environment needed

### 2. System Dependencies
```bash
sudo apt update
sudo apt install -y python3-pip python3-venv
sudo apt install -y libsdl2-dev libsdl2-image-dev libsdl2-mixer-dev libsdl2-ttf-dev
sudo apt install -y libmtdev-dev  # Touch input
```

### 3. Pisound Driver
```bash
curl https://blokas.io/pisound/install.sh | sh
```

### 4. Kivy Touchscreen Configuration
Create `~/.kivy/config.ini`:
```ini
[input]
mouse = mouse
touchscreen = mtdev,/dev/input/event0

[graphics]
width = 1080
height = 1080
```

**Note**: Use `mtdev` provider for the Waveshare display. The `hidinput` provider may not work correctly. Check `/proc/bus/input/devices` to find the correct event device.

### 5. Auto-start Application
Configure systemd service to launch app on boot. See `docs/PI_SETUP.md` for complete instructions.

## Deployment (Mac → Pi)

### Using rsync
```bash
# From Mac, sync project to Pi (exclude venv, cache)
rsync -avz --exclude 'venv' --exclude '__pycache__' --exclude '.git' \
  ./ pi@raspberrypi.local:~/RoundSeq/
```

### Using the deploy script
```bash
./scripts/deploy.sh
```

### On the Pi
```bash
cd ~/RoundSeq
source venv/bin/activate
python main.py
```

## Technical Notes

### Touch Collision for Pie Slices
Custom `collide_point()` must check:
1. Distance from center (between inner and outer radius)
2. Angle from center (within slice bounds)

```python
def collide_point(self, x, y):
    dx = x - self.center_x
    dy = y - self.center_y
    distance = sqrt(dx*dx + dy*dy)
    angle = atan2(dy, dx)

    return (self.inner_radius <= distance <= self.outer_radius and
            self.start_angle <= angle <= self.end_angle)
```

### MIDI Note Mapping
Standard MIDI note numbers:
- C4 (middle C) = 60
- Octave = 12 semitones
- Note range: 0-127

### Timing Considerations
- Kivy's `Clock.schedule_interval()` for sequencer timing
- Pisound MIDI latency: ~2.1ms (acceptable for live play)
- Consider MIDI clock for sync with external gear

## Open Questions

- Velocity control method: touch duration, touch area size, or fixed?
- Scale mode: chromatic only, or selectable scales?
- Visual theme: dark mode default for OLED-like appearance?
- Sequencer grid layout: how to adapt step grid to circular display?

## References

- [Kivy Documentation](https://kivy.org/doc/stable/)
- [KivyMD Documentation](https://kivymd.readthedocs.io/)
- [Pisound Documentation](https://blokas.io/pisound/docs/)
- [Waveshare 5" Round LCD](https://www.waveshare.com/product/5inch-1080x1080-lcd.htm)
- [mido MIDI Library](https://mido.readthedocs.io/)
