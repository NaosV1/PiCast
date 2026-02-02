# Quick Start Guide

Fast setup guide for experienced users. For detailed instructions, see INSTALL.md.

## Prerequisites

- Raspberry Pi 2 with Raspberry Pi OS
- Ethernet connection
- Audio output configured

## Installation (5 minutes)

```bash
# 1. Update system
sudo apt-get update
sudo apt-get install -y mpv alsa-utils python3 python3-pip git

# 2. Clone/copy project
cd /home/pi
# git clone <repo-url> dlna-renderer
cd dlna-renderer

# 3. Install Python deps
pip3 install -r requirements.txt

# 4. Generate UUID and configure
python3 -c "import uuid; print(uuid.uuid4())"
# Copy UUID, then edit config.yaml and paste it

nano config.yaml
# Update device.uuid and device.name

# 5. Test run
python3 -m src.main
# Ctrl+C to stop

# 6. Install service
sudo cp systemd/pi-audiocast.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable pi-audiocast
sudo systemctl start pi-audiocast

# 7. Check status
sudo systemctl status pi-audiocast
```

## Quick Commands

```bash
# View logs
journalctl -u pi-audiocast -f

# Restart service
sudo systemctl restart pi-audiocast

# Stop service
sudo systemctl stop pi-audiocast

# Manual run (for testing)
python3 -m src.main

# Test audio
speaker-test -t wav -c 2

# Check volume
amixer get PCM
```

## Compatible Apps

**Android:**
- BubbleUPnP (Recommended)
- AllCast
- VLC for Android
- Hi-Fi Cast

**iOS:**
- AllCast
- VLC for iOS
- DLNA Player

## Troubleshooting

```bash
# Not discoverable?
sudo systemctl status pi-audiocast
journalctl -u pi-audiocast -n 50
ip addr show eth0

# No audio?
speaker-test -t wav -c 2
amixer set PCM 80%

# High CPU?
htop
vcgencmd measure_temp
```

## Configuration

Edit `config.yaml`:

```yaml
device:
  name: "Your Device Name"  # Shown in apps
  uuid: "your-unique-uuid"   # Must be unique

network:
  interface: "eth0"          # Network interface
  http_port: 8000            # HTTP server port

audio:
  default_volume: 50         # Initial volume (0-100)

logging:
  level: "INFO"              # DEBUG for troubleshooting
```

## Architecture

```
Smartphone → [LAN] → Raspberry Pi
                     ├─ SSDP Server (discovery)
                     ├─ HTTP Server (control)
                     └─ mpv Player (audio)
```

## Default Ports

- **1900/UDP**: SSDP discovery
- **8000/TCP**: HTTP/SOAP control

## Memory Usage

- Idle: ~250 MB
- Playing: ~350 MB
- Total available on RPi2: 1 GB

## Performance Tips

```bash
# 1. Reduce GPU memory
sudo nano /boot/config.txt
# Add: gpu_mem=64

# 2. CPU performance mode
sudo apt-get install cpufrequtils
sudo cpufreq-set -g performance

# 3. Disable swap (optional)
sudo dphys-swapfile swapoff
sudo systemctl disable dphys-swapfile

sudo reboot
```

## File Structure

```
dlna-renderer/
├── config.yaml           # Configuration
├── requirements.txt      # Python dependencies
├── src/
│   ├── main.py          # Entry point
│   ├── config.py        # Config loader
│   ├── ssdp_server.py   # SSDP discovery
│   ├── http_server.py   # HTTP/SOAP server
│   ├── player/
│   │   └── mpv_controller.py  # Audio player
│   └── services/
│       ├── av_transport.py      # Playback control
│       ├── rendering_control.py # Volume control
│       └── connection_manager.py
├── systemd/
│   └── pi-audiocast.service  # Systemd service
└── tests/               # Unit tests
```

## Common Issues

| Issue | Solution |
|-------|----------|
| Device not found | Check `systemctl status pi-audiocast` |
| No audio | Run `speaker-test`, check volume |
| Playback stutters | Check CPU with `htop`, reduce bitrate |
| Service won't start | Check logs: `journalctl -u pi-audiocast -xe` |

## Advanced

### Debug Mode

```bash
# Edit config.yaml
logging:
  level: "DEBUG"

# Restart
sudo systemctl restart pi-audiocast

# View detailed logs
journalctl -u pi-audiocast -f
```

### Custom mpv Options

Edit `src/player/mpv_controller.py` to add custom mpv flags.

### Multiple Devices

Run separate instances on different RPi devices. Each needs:
- Unique UUID in config.yaml
- Unique device name
- Same network

### Firewall Configuration

If using firewall:

```bash
sudo ufw allow 1900/udp  # SSDP
sudo ufw allow 8000/tcp  # HTTP
```

## Testing Checklist

- [ ] Device appears in DLNA app
- [ ] Play button starts audio
- [ ] Pause/resume works
- [ ] Volume control works
- [ ] Service auto-starts on boot
- [ ] CPU usage < 50% during playback
- [ ] Memory usage < 400 MB
- [ ] No audio dropouts

## Support

- Logs: `journalctl -u pi-audiocast -f`
- Manual test: `python3 -m src.main`
- Audio test: `speaker-test -t wav -c 2`
- Network test: `ip addr; ip maddr`

See README.md and INSTALL.md for more details.
