#!/bin/bash
#
# Quick installation script for Raspberry Pi Audio Renderer
# Run with: bash install.sh
#

set -e

echo "============================================================"
echo "Raspberry Pi Audio Renderer - Installation Script"
echo "============================================================"
echo ""

# Check if running on Raspberry Pi
if ! grep -q "Raspberry Pi" /proc/cpuinfo 2>/dev/null; then
    echo "WARNING: This doesn't appear to be a Raspberry Pi"
    echo "Continue anyway? (y/n)"
    read -r response
    if [[ ! "$response" =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

echo "Step 1: Updating system packages..."
sudo apt-get update

echo ""
echo "Step 2: Installing system dependencies..."
sudo apt-get install -y mpv alsa-utils python3 python3-pip git

echo ""
echo "Step 3: Installing Python dependencies..."
pip3 install -r requirements.txt

echo ""
echo "Step 4: Configuring audio..."

# Create .asoundrc if it doesn't exist
if [ ! -f ~/.asoundrc ]; then
    cat > ~/.asoundrc << 'EOF'
defaults.pcm.card 0
defaults.pcm.device 0
defaults.ctl.card 0
EOF
    echo "Created ~/.asoundrc"
else
    echo "~/.asoundrc already exists, skipping"
fi

echo ""
echo "Step 5: Generating configuration..."

# Generate UUID
NEW_UUID=$(python3 -c "import uuid; print(uuid.uuid4())")

# Check if config.yaml exists
if [ -f config.yaml ]; then
    echo "config.yaml already exists"
    echo "Create new config with UUID $NEW_UUID? (y/n)"
    read -r response
    if [[ "$response" =~ ^[Yy]$ ]]; then
        cp config.yaml config.yaml.backup.$(date +%s)
        sed -i "s/uuid:.*/uuid: \"$NEW_UUID\"/" config.yaml
        echo "Updated config.yaml with new UUID"
    fi
else
    echo "ERROR: config.yaml not found!"
    exit 1
fi

echo ""
echo "Step 6: Testing audio output..."
echo "You should hear white noise for 3 seconds..."
timeout 3 speaker-test -t wav -c 2 || echo "Audio test completed"

echo ""
echo "Step 7: Testing renderer (5 seconds)..."
timeout 5 python3 -m src.main || echo "Basic test completed"

echo ""
echo "============================================================"
echo "Installation Complete!"
echo "============================================================"
echo ""
echo "Configuration:"
echo "  - Device UUID: $NEW_UUID"
echo "  - Config file: $(pwd)/config.yaml"
echo ""
echo "Next steps:"
echo ""
echo "1. Edit configuration (optional):"
echo "   nano config.yaml"
echo ""
echo "2. Test manual run:"
echo "   python3 -m src.main"
echo ""
echo "3. Install as system service:"
echo "   sudo cp systemd/pi-audiocast.service /etc/systemd/system/"
echo "   sudo systemctl daemon-reload"
echo "   sudo systemctl enable pi-audiocast"
echo "   sudo systemctl start pi-audiocast"
echo ""
echo "4. Check status:"
echo "   sudo systemctl status pi-audiocast"
echo ""
echo "5. View logs:"
echo "   journalctl -u pi-audiocast -f"
echo ""
echo "For detailed instructions, see INSTALL.md"
echo "============================================================"
