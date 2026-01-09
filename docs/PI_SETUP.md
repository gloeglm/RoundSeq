# Raspberry Pi Setup Guide for RoundSeq

This guide documents how to set up a Raspberry Pi to run RoundSeq with the Waveshare 5" Round Display.

## Hardware

- Raspberry Pi (tested on Pi with armv7l, recommended: Pi 4)
- Waveshare 5" 1080x1080 Round LCD
- HDMI cable (HDMI to Micro-HDMI for Pi 4)
- USB cable for touch input
- Optional: Blokas Pisound for MIDI output

## Initial Pi Setup

### 1. Flash Raspberry Pi OS

Use Raspberry Pi Imager to flash **Raspberry Pi OS (Legacy, 32-bit)** to an SD card.

### 2. Enable SSH

Before first boot, create an empty file called `ssh` on the boot partition:

```bash
touch /Volumes/boot/ssh  # macOS
# or
touch /boot/ssh  # Linux
```

### 3. Connect Hardware

1. Insert SD card into Pi
2. Connect Waveshare display via HDMI
3. Connect Waveshare touch via USB
4. Connect Ethernet cable
5. Power on the Pi

### 4. SSH into the Pi

```bash
ssh pi@raspberrypi.local
# Default password: raspberry
```

## Display Configuration

### 1. Edit /boot/config.txt

```bash
sudo nano /boot/config.txt
```

Add these lines at the end for the 1080x1080 display:

```ini
# Waveshare 5" Round Display
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

### 1. Fix Package Sources (for older Buster images)

If you get 404 errors with `apt update`, edit the sources:

```bash
sudo nano /etc/apt/sources.list
```

Replace contents with:

```
deb http://archive.raspbian.org/raspbian/ buster main contrib non-free rpi
```

Comment out raspi.list:

```bash
sudo nano /etc/apt/sources.list.d/raspi.list
```

Add `#` at the start of each line.

### 2. Install Dependencies

```bash
sudo apt update
sudo apt install -y python3-pip python3-venv git
sudo apt install -y libsdl2-dev libsdl2-image-dev libsdl2-mixer-dev libsdl2-ttf-dev
sudo apt install -y libmtdev-dev
```

### 3. Clone and Setup RoundSeq

```bash
git clone https://github.com/gloeglm/RoundSeq.git
cd RoundSeq
python3 -m venv venv
source venv/bin/activate
pip install kivy mido
```

Note: `python-rtmidi` may fail to install on older systems. The app will fall back to mock MIDI output.

For real MIDI output (with Pisound), also install:

```bash
sudo apt install -y libasound2-dev libjack-dev python3-dev
pip install python-rtmidi
```

## Touch Input Configuration

### 1. Configure Kivy Input

Edit or create `~/.kivy/config.ini`:

```bash
nano ~/.kivy/config.ini
```

Ensure the `[input]` section contains:

```ini
[input]
mouse = mouse
touchscreen = mtdev,/dev/input/event0
```

Also set the display size in `[graphics]`:

```ini
[graphics]
width = 1080
height = 1080
```

### 2. Input Permissions

Add the pi user to the input group:

```bash
sudo usermod -a -G input pi
```

Logout and login again for changes to take effect.

## Running RoundSeq

```bash
cd ~/RoundSeq
source venv/bin/activate
python main.py
```

## Troubleshooting

### No display output
- Check HDMI connection
- Verify config.txt settings
- Try `hdmi_safe=1` temporarily

### Display flickering/artifacts
- Use separate USB power for the display
- Increase `config_hdmi_boost` value (max 11)

### Touch not working
1. Check if Linux sees the device:
   ```bash
   cat /proc/bus/input/devices
   ```

2. Test raw touch events:
   ```bash
   sudo evtest /dev/input/event0
   ```

3. Verify Kivy config uses `mtdev` provider

### Python type errors
Ensure you're using the virtual environment:
```bash
source venv/bin/activate
```

## Auto-start on Boot (Optional)

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
User=pi
WorkingDirectory=/home/pi/RoundSeq
ExecStart=/home/pi/RoundSeq/venv/bin/python /home/pi/RoundSeq/main.py
Restart=on-failure

[Install]
WantedBy=multi-user.target
```

Enable and start:

```bash
sudo systemctl enable roundseq
sudo systemctl start roundseq
```
