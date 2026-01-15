# Raspberry Pi Setup Guide for RoundSeq

This guide documents how to set up a Raspberry Pi to run RoundSeq with the Waveshare 5" Round Display.

## Hardware

- Raspberry Pi 4 (recommended, 2GB+ RAM)
- Waveshare 5" 1080x1080 Round LCD
- Micro-HDMI to HDMI cable (Pi 4 uses micro-HDMI, not full-size)
- USB cable for touch input
- MicroSD card (16GB+ recommended)
- Optional: Blokas Pisound for hardware MIDI output

## Initial Pi Setup

### 1. Flash Raspberry Pi OS

Use [Raspberry Pi Imager](https://www.raspberrypi.com/software/) to flash **Raspberry Pi OS Lite (64-bit)** to an SD card.

Click the gear icon (⚙️) to pre-configure:
- **Hostname**: e.g., `raspi`
- **Enable SSH**: Use public-key authentication (paste your public key)
- **Username/password**: Set your username (e.g., `raspberry`)
- **WiFi**: Optional, or use ethernet for initial setup

To generate an SSH key on macOS/Linux:
```bash
ssh-keygen -t ed25519 -f ~/.ssh/roundseq_pi -C "roundseq-pi"
cat ~/.ssh/roundseq_pi.pub  # Copy this to Pi Imager
```

### 2. Connect Hardware

1. Insert SD card into Pi
2. Connect Waveshare display via micro-HDMI (use HDMI0 port, closest to USB-C)
3. Connect Waveshare touch USB cable
4. Connect ethernet or ensure WiFi is configured
5. Power on the Pi

### 3. SSH into the Pi

```bash
ssh -i ~/.ssh/roundseq_pi <username>@<hostname>.local
```

Or add to `~/.ssh/config` for easier access:
```
Host raspi
    HostName raspi.local
    User raspberry
    IdentityFile ~/.ssh/roundseq_pi
```

Then simply: `ssh raspi`

## Display Configuration

The HDMI must be configured for the 1080x1080 resolution to avoid display distortion during boot.

Edit `/boot/firmware/config.txt`:

```bash
sudo nano /boot/firmware/config.txt
```

Add these lines at the end:

```ini
# Waveshare 5" Round Display (1080x1080)
hdmi_force_hotplug=1
hdmi_group=2
hdmi_mode=87
hdmi_cvt=1080 1080 60 1 0 0 0
hdmi_drive=2
config_hdmi_boost=4
```

Reboot after saving:

```bash
sudo reboot
```

## Software Installation

### 1. Install System Dependencies

```bash
sudo apt update
sudo apt install -y python3-pip python3-venv git
sudo apt install -y libsdl2-dev libsdl2-image-dev libsdl2-mixer-dev libsdl2-ttf-dev
sudo apt install -y libmtdev-dev
```

### 2. Deploy RoundSeq

From your development machine, use rsync:

```bash
rsync -avz --exclude 'venv' --exclude '__pycache__' --exclude '.git' \
  ./ <username>@<hostname>.local:~/RoundSeq/
```

Or clone from git on the Pi:

```bash
git clone <repository-url> ~/RoundSeq
```

### 3. Create Virtual Environment and Install Packages

```bash
cd ~/RoundSeq
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install kivy mido python-rtmidi
```

Note: On Pi 4 with 64-bit OS, `python-rtmidi` installs successfully. On older Pis (armv7l, 32-bit), it may fail to build - the app will fall back to mock MIDI output.

## Touch Input Configuration

Kivy automatically detects the Waveshare touchscreen via `probesysfs` - no manual configuration needed on Pi 4 with 64-bit OS.

### Input Permissions

Add your user to the input group:

```bash
sudo usermod -a -G input $USER
```

Logout and login again for changes to take effect.

## Running RoundSeq

```bash
cd ~/RoundSeq
source venv/bin/activate
python main.py
```

## Auto-start on Boot

Create a systemd service:

```bash
sudo nano /etc/systemd/system/roundseq.service
```

```ini
[Unit]
Description=RoundSeq MIDI Sequencer
After=multi-user.target

[Service]
Type=simple
User=<your-username>
WorkingDirectory=/home/<your-username>/RoundSeq
Environment=PYTHONUNBUFFERED=1
ExecStart=/home/<your-username>/RoundSeq/venv/bin/python /home/<your-username>/RoundSeq/main.py
Restart=on-failure

[Install]
WantedBy=multi-user.target
```

Replace `<your-username>` with your actual username. The `PYTHONUNBUFFERED=1` ensures log output appears immediately in journalctl.

Enable and start:

```bash
sudo systemctl daemon-reload
sudo systemctl enable roundseq
sudo systemctl start roundseq
```

Useful commands:
```bash
sudo systemctl status roundseq    # Check status
sudo systemctl stop roundseq      # Stop
sudo systemctl restart roundseq   # Restart
journalctl -u roundseq -f         # View logs
```

## Troubleshooting

### Display distortion during boot
Ensure the HDMI config is set in `/boot/firmware/config.txt` (see Display Configuration above).

### No display output
- Check micro-HDMI connection (use HDMI0 port)
- Verify config.txt settings
- Try `hdmi_safe=1` temporarily

### Touch not working

1. Check if Linux sees the device:
   ```bash
   cat /proc/bus/input/devices
   ```
   Look for "Waveshare" and note the event number.

2. Test raw touch events:
   ```bash
   sudo apt install evtest
   sudo evtest /dev/input/event0
   ```

3. Check user is in input group:
   ```bash
   groups
   ```

4. If auto-detection fails (older systems), manually configure `~/.kivy/config.ini`:
   ```ini
   [input]
   mouse = mouse
   touchscreen = mtdev,/dev/input/event0
   ```
   Remove any `%(name)s = probesysfs` line to avoid duplicate events.

### App crashes or won't start
Check logs:
```bash
journalctl -u roundseq -n 50
# or
cat ~/.kivy/logs/kivy_*.txt
```
