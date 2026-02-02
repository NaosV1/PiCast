"""
Configuration management for the DLNA renderer
"""

import yaml
import os
from typing import Dict, Any


class Config:
    """Configuration loader and accessor"""

    def __init__(self, config_path: str = "config.yaml"):
        """
        Load configuration from YAML file

        Args:
            config_path: Path to config.yaml file
        """
        self.config_path = config_path
        self.config: Dict[str, Any] = {}
        self.load()

    def load(self):
        """Load configuration from file"""
        if not os.path.exists(self.config_path):
            raise FileNotFoundError(f"Configuration file not found: {self.config_path}")

        with open(self.config_path, 'r') as f:
            self.config = yaml.safe_load(f)

    def get(self, key: str, default: Any = None) -> Any:
        """
        Get configuration value using dot notation

        Args:
            key: Configuration key (e.g., 'device.name')
            default: Default value if key not found

        Returns:
            Configuration value or default
        """
        keys = key.split('.')
        value = self.config

        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)
                if value is None:
                    return default
            else:
                return default

        return value

    def get_device_name(self) -> str:
        """Get device friendly name"""
        return self.get('device.name', 'Raspberry Pi Audio Renderer')

    def get_device_uuid(self) -> str:
        """Get device UUID"""
        return self.get('device.uuid', '12345678-1234-1234-1234-123456789012')

    def get_manufacturer(self) -> str:
        """Get manufacturer name"""
        return self.get('device.manufacturer', 'Custom')

    def get_model_name(self) -> str:
        """Get model name"""
        return self.get('device.model_name', 'Pi Audio Renderer')

    def get_model_number(self) -> str:
        """Get model number"""
        return self.get('device.model_number', '1.0')

    def get_serial_number(self) -> str:
        """Get serial number"""
        return self.get('device.serial_number', 'RPI2-001')

    def get_network_interface(self) -> str:
        """Get network interface"""
        return self.get('network.interface', 'eth0')

    def get_http_port(self) -> int:
        """Get HTTP server port"""
        return self.get('network.http_port', 8000)

    def get_ssdp_multicast_ip(self) -> str:
        """Get SSDP multicast IP"""
        return self.get('network.ssdp_multicast_ip', '239.255.255.250')

    def get_ssdp_port(self) -> int:
        """Get SSDP port"""
        return self.get('network.ssdp_port', 1900)

    def get_announce_interval(self) -> int:
        """Get SSDP announcement interval in seconds"""
        return self.get('network.announce_interval', 30)

    def get_mpv_ipc_socket(self) -> str:
        """Get mpv IPC socket path"""
        return self.get('audio.mpv_ipc_socket', '/tmp/mpv-socket')

    def get_default_volume(self) -> int:
        """Get default volume level"""
        return self.get('audio.default_volume', 50)

    def get_audio_output_driver(self) -> str:
        """Get audio output driver"""
        return self.get('audio.output_driver', 'alsa')

    def get_cache_enabled(self) -> bool:
        """Get cache enabled setting"""
        return self.get('audio.cache', True)

    def get_demuxer_max_bytes(self) -> str:
        """Get demuxer max bytes setting"""
        return self.get('audio.demuxer_max_bytes', '2M')

    def get_log_level(self) -> str:
        """Get logging level"""
        return self.get('logging.level', 'INFO')

    def get_log_file(self) -> str:
        """Get log file path"""
        return self.get('logging.file', 'renderer.log')

    def get_log_max_size_mb(self) -> int:
        """Get max log file size in MB"""
        return self.get('logging.max_size_mb', 10)

    def get_log_backup_count(self) -> int:
        """Get number of backup log files"""
        return self.get('logging.backup_count', 3)
