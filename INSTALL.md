# Installation Guide

Complete installation guide for Raspberry Pi 2 DLNA Audio Renderer.

## Prerequisites

- Raspberry Pi 2 Model B
- MicroSD card (8GB minimum, 16GB recommended)
- Ethernet cable
- Power supply
- Audio output (3.5mm speakers or HDMI)

## Step 1: Prepare Raspberry Pi OS

### 1.1 Flash Raspberry Pi OS

1. Download Raspberry Pi OS Lite (or Desktop) from https://www.raspberrypi.org/software/
2. Flash to MicroSD card using Raspberry Pi Imager or Etcher
3. Insert card into Raspberry Pi and boot

### 1.2 Initial Configuration

```bash
# Run configuration tool
sudo raspi-config

# Configure:
# - Expand Filesystem
# - Set Hostname (e.g., audiocast)
# - Set Timezone
# - Enable SSH (optional, for remote access)
# - Audio -> Force 3.5mm jack (if using headphone jack)

# Reboot
sudo reboot
```

## Step 2: Install System Dependencies

```bash
# Update package list
sudo apt-get update

# Upgrade system (optional but recommended)
sudo apt-get upgrade -y

# Install required packages
sudo apt-get install -y \
    mpv \
    alsa-utils \
    python3 \
    python3-pip \
    python3-dev \
    git

# Verify installations
mpv --version
python3 --version
```

## Step 3: Configure Audio

### 3.1 Test Audio Output

```bash
# List audio devices
aplay -L

# Test audio (should hear white noise)
speaker-test -t wav -c 2

# Press Ctrl+C to stop
```

### 3.2 Configure ALSA

Create `~/.asoundrc`:

```bash
cat > ~/.asoundrc << 'EOF'
defaults.pcm.card 0
defaults.pcm.device 0
defaults.ctl.card 0
EOF
```

### 3.3 Set Volume

```bash
# List controls
amixer scontrols

# Set PCM volume to 80%
amixer set PCM 80%

# Test again
speaker-test -t wav -c 2
```

## Step 4: Install Audio Renderer

### 4.1 Clone Repository

```bash
# Navigate to home directory
cd /home/pi

# Clone repository (replace with actual URL)
git clone https://github.com/yourusername/pi-audio-renderer.git dlna-renderer

# Or if you have the files on a USB drive:
# cp -r /media/usb/dlna-renderer /home/pi/

cd dlna-renderer
```

### 4.2 Install Python Dependencies

```bash
# Install requirements
pip3 install -r requirements.txt

# Verify installation
python3 -c "import yaml; import netifaces; print('Dependencies OK')"
```

## Step 5: Configure Renderer

### 5.1 Generate Unique UUID

```bash
# Generate UUID
python3 -c "import uuid; print(uuid.uuid4())"

# Copy the output (e.g., a1b2c3d4-e5f6-7890-abcd-ef1234567890)
```

### 5.2 Edit Configuration

```bash
# Copy example config
cp config.yaml config.yaml.backup

# Edit config
nano config.yaml
```

Update at minimum:

```yaml
device:
  name: "Living Room Audio"  # Change to your preferred name
  uuid: "PASTE-YOUR-UUID-HERE"  # Use UUID from step 5.1
```

Save with Ctrl+O, Enter, then exit with Ctrl+X.

### 5.3 Verify Network Settings

```bash
# Check interface name
ip addr

# If your interface is not eth0, update config.yaml:
# network.interface: "YOUR_INTERFACE_NAME"
```

## Step 6: Test Manual Run

### 6.1 Run Renderer

```bash
# Run in foreground
python3 -m src.main

# You should see:
# ============================================================
# Raspberry Pi Audio Renderer Starting
# ============================================================
# INFO - Network interface: eth0
# INFO - IP address: 192.168.1.XXX
# INFO - Starting mpv player...
# INFO - Starting HTTP server...
# INFO - Starting SSDP server...
# ============================================================
# Audio Renderer Started Successfully
# Device Name: Living Room Audio
# ============================================================
```

### 6.2 Test Discovery from Smartphone

1. Install BubbleUPnP (Android) or AllCast (Android/iOS)
2. Open app
3. Go to Library → Devices or Renderers
4. Look for your device name (e.g., "Living Room Audio")
5. If found, SUCCESS! If not, see Troubleshooting below

### 6.3 Test Playback

1. In BubbleUPnP/AllCast, select a local audio file
2. Tap the "Cast" icon
3. Select your Raspberry Pi renderer
4. Tap Play
5. Audio should play through Raspberry Pi

### 6.4 Stop Manual Run

Press Ctrl+C to stop the renderer.

## Step 7: Install as System Service

### 7.1 Install Service

```bash
# Copy service file
sudo cp systemd/pi-audiocast.service /etc/systemd/system/

# Edit service if needed (change user, path, etc.)
sudo nano /etc/systemd/system/pi-audiocast.service

# Reload systemd
sudo systemctl daemon-reload

# Enable auto-start on boot
sudo systemctl enable pi-audiocast
```

### 7.2 Start Service

```bash
# Start service
sudo systemctl start pi-audiocast

# Check status
sudo systemctl status pi-audiocast

# Should show:
# ● pi-audiocast.service - Raspberry Pi DLNA Audio Renderer
#    Loaded: loaded
#    Active: active (running)
```

### 7.3 View Logs

```bash
# Follow logs in real-time
journalctl -u pi-audiocast -f

# View recent logs
journalctl -u pi-audiocast -n 50

# Press Ctrl+C to exit
```

## Step 8: Verify Auto-Start

```bash
# Reboot
sudo reboot

# Wait for boot (1-2 minutes)

# SSH back in (if using SSH)
ssh pi@audiocast.local

# Check service status
sudo systemctl status pi-audiocast

# Should be active (running)
```

## Step 9: Optimize Performance (Optional)

### 9.1 Reduce GPU Memory

Edit `/boot/config.txt`:

```bash
sudo nano /boot/config.txt

# Add or modify:
gpu_mem=64

# Save and exit
```

### 9.2 Set CPU Governor

```bash
# Install cpufrequtils
sudo apt-get install -y cpufrequtils

# Set to performance mode
sudo cpufreq-set -g performance

# Make permanent
echo 'GOVERNOR="performance"' | sudo tee /etc/default/cpufrequtils

# Enable service
sudo systemctl enable cpufrequtils
```

### 9.3 Disable Swap (Optional)

```bash
# Disable swap
sudo dphys-swapfile swapoff
sudo dphys-swapfile uninstall
sudo systemctl disable dphys-swapfile
```

Reboot for changes to take effect:

```bash
sudo reboot
```

## Troubleshooting

### Device Not Discovered

```bash
# Check service is running
sudo systemctl status pi-audiocast

# Check logs for errors
journalctl -u pi-audiocast -n 100

# Verify network
ip addr show eth0

# Check multicast
ip maddr show eth0

# Ping from another device
ping 192.168.1.XXX  # Replace with Pi IP

# Check firewall (should have none by default)
sudo iptables -L
```

### Audio Not Playing

```bash
# Check ALSA
speaker-test -t wav -c 2

# Check volume
amixer scontrols
amixer get PCM

# Check logs
journalctl -u pi-audiocast -f

# Test mpv directly
mpv http://stream.live.vc.bbcmedia.co.uk/bbc_world_service
```

### High CPU/Memory

```bash
# Monitor resources
htop

# Check temperature
vcgencmd measure_temp

# View memory
free -h

# Check service limits
systemctl show pi-audiocast | grep -i memory
```

### Service Fails to Start

```bash
# Check detailed logs
sudo journalctl -u pi-audiocast -xe

# Check permissions
ls -la /home/pi/dlna-renderer

# Test manual run
cd /home/pi/dlna-renderer
python3 -m src.main

# Check dependencies
pip3 list
```

## Uninstall

```bash
# Stop and disable service
sudo systemctl stop pi-audiocast
sudo systemctl disable pi-audiocast

# Remove service file
sudo rm /etc/systemd/system/pi-audiocast.service

# Reload systemd
sudo systemctl daemon-reload

# Remove application
rm -rf /home/pi/dlna-renderer

# Remove Python packages (optional)
pip3 uninstall -y pyyaml netifaces python-mpv-jsonipc ssdpy

# Remove system packages (optional)
sudo apt-get remove --purge mpv
```

## Next Steps

- Customize device name in `config.yaml`
- Adjust volume settings
- Enable debug logging if needed
- Set up multiple renderers in different rooms
- Explore advanced mpv configuration

## Support

For issues and questions:
- Check logs: `journalctl -u pi-audiocast -f`
- Review README.md for configuration options
- Open an issue on GitHub
