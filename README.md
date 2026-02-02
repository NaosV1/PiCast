# Raspberry Pi 2 DLNA Audio Renderer

A lightweight DLNA/UPnP audio renderer for Raspberry Pi 2, allowing you to stream audio from smartphones and tablets over Ethernet.

## Features

- 🎵 DLNA/UPnP renderer compatible with popular apps (BubbleUPnP, AllCast, VLC, etc.)
- 🚀 Lightweight design optimized for Raspberry Pi 2 (~250-360 MB RAM)
- 🎛️ Full playback control (play, pause, stop, volume)
- 📡 Network discovery via SSDP
- 🔧 Configurable via YAML
- 🔄 Auto-start on boot via systemd

## System Requirements

### Hardware
- Raspberry Pi 2 Model B
- Ethernet connection (LAN)
- Audio output (3.5mm jack or HDMI)
- MicroSD card (8GB minimum)

### Software
- Raspberry Pi OS (Raspbian) Lite or Desktop
- Python 3.7+
- mpv media player

## Installation

### 1. Prepare Raspberry Pi

```bash
# Update system
sudo apt-get update && sudo apt-get upgrade -y

# Install system dependencies
sudo apt-get install -y mpv alsa-utils python3 python3-pip git

# Configure audio output (if needed)
sudo raspi-config
# Select: System Options -> Audio -> Force 3.5mm jack
```

### 2. Configure ALSA (Audio)

Create `~/.asoundrc`:
```
defaults.pcm.card 0
defaults.pcm.device 0
defaults.ctl.card 0
```

Test audio:
```bash
speaker-test -t wav -c 2
```

### 3. Install the Renderer

```bash
# Clone repository
cd /home/pi
git clone https://github.com/NaosV1/PiCast dlna-renderer
cd dlna-renderer

# Install Python dependencies
pip3 install -r requirements.txt
```

### 4. Configure

```bash
# Edit configuration
cp config.yaml config.yaml.backup
nano config.yaml

# At minimum, change the UUID to something unique:
# device.uuid: "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
```

Generate a unique UUID:
```bash
python3 -c "import uuid; print(uuid.uuid4())"
```

### 5. Test Manual Run

```bash
# Run the renderer
python3 -m src.main

# Leave it running and test from your smartphone
# Use an app like BubbleUPnP to discover the device
```

### 6. Install as System Service

```bash
# Copy service file
sudo cp systemd/pi-audiocast.service /etc/systemd/system/

# Reload systemd
sudo systemctl daemon-reload

# Enable auto-start on boot
sudo systemctl enable pi-audiocast

# Start service
sudo systemctl start pi-audiocast

# Check status
sudo systemctl status pi-audiocast
```

## Usage

### From Smartphone/Tablet

1. Install a DLNA/UPnP client app:
   - **Android**: BubbleUPnP, AllCast, VLC for Android
   - **iOS**: AllCast, VLC for iOS, DLNA Player

2. Ensure device is on the same network as Raspberry Pi

3. Open the app and look for "Raspberry Pi Audio Renderer" (or your custom name)

4. Select it as the renderer/player

5. Choose audio to play - it will stream to the Raspberry Pi

### Supported Audio Formats

mpv supports 100+ formats including:
- MP3, AAC, FLAC, WAV, OGG
- Streaming protocols: HTTP, HTTPS
- Internet radio streams

## Troubleshooting

### Device Not Discovered

```bash
# Check service is running
sudo systemctl status pi-audiocast

# Check network interface
ip addr show eth0

# Check multicast is enabled
ip maddr show eth0

# Monitor SSDP traffic
sudo tcpdump -i eth0 udp port 1900 -vv

# Check firewall
sudo iptables -L
```

### Audio Not Playing

```bash
# Test ALSA
speaker-test -t wav -c 2

# Check volume
amixer scontrols
amixer set PCM 80%

# Check logs
journalctl -u pi-audiocast -f

# Or direct log file
tail -f renderer.log
```

### High CPU/Memory Usage

```bash
# Monitor resources
htop

# Check temperature
vcgencmd measure_temp

# View memory usage
free -h
```

### Service Won't Start

```bash
# Check logs
journalctl -u pi-audiocast -xe

# Check permissions
ls -la /home/pi/dlna-renderer

# Test manual run
python3 -m src.main
```

## Configuration Options

See `config.yaml` for all options. Key settings:

- `device.name`: Name shown in DLNA apps
- `device.uuid`: Must be unique per device
- `network.interface`: Network interface (eth0 for RPi2)
- `audio.default_volume`: Initial volume level
- `logging.level`: DEBUG for troubleshooting, INFO for production

## Performance Tips

### Optimize for Raspberry Pi 2

Edit `/boot/config.txt`:
```
# Minimize GPU memory for audio-only use
gpu_mem=64
```

Set CPU governor to performance:
```bash
sudo apt-get install cpufrequtils
sudo cpufreq-set -g performance
```

### Disable Swap (Optional)

Reduces SD card wear:
```bash
sudo dphys-swapfile swapoff
sudo dphys-swapfile uninstall
sudo systemctl disable dphys-swapfile
```

## Architecture

```
Smartphone/Tablet          Raspberry Pi 2
┌─────────────────┐         ┌──────────────────────────┐
│  DLNA App       │         │  Python DLNA Service     │
│  (BubbleUPnP)   │ ◄──────►│  - SSDP Discovery        │
│                 │   LAN   │  - HTTP Server           │
└─────────────────┘         │  - SOAP Handler          │
                            │  - UPnP Services         │
                            │           │              │
                            │           │ JSON IPC     │
                            │           ▼              │
                            │  ┌────────────────────┐  │
                            │  │  mpv Player        │  │
                            │  │  (Native)          │  │
                            │  └────────┬───────────┘  │
                            │           │              │
                            │  ┌────────▼───────────┐  │
                            │  │  ALSA Audio Output │  │
                            │  └────────────────────┘  │
                            └──────────────────────────┘
```

## Development

### Running Tests

```bash
python3 -m pytest tests/ -v
```

### Debug Mode

Edit `config.yaml`:
```yaml
logging:
  level: "DEBUG"
```

Restart service:
```bash
sudo systemctl restart pi-audiocast
journalctl -u pi-audiocast -f
```

## License

MIT License - see LICENSE file

## Credits

- Built with Python and mpv
- SSDP via ssdpy library
- UPnP/DLNA protocol implementation

## Support

For issues and questions, please open an issue on GitHub.
