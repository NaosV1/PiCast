"""
Tests for configuration module
"""

import pytest
import tempfile
import os


def test_config_loading():
    """Test configuration loading"""
    from src.config import Config

    # Create temporary config file
    config_content = """
device:
  name: "Test Device"
  uuid: "test-uuid-123"

network:
  interface: "eth0"
  http_port: 8000

audio:
  default_volume: 75

logging:
  level: "DEBUG"
"""

    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
        f.write(config_content)
        config_path = f.name

    try:
        config = Config(config_path)

        assert config.get_device_name() == "Test Device"
        assert config.get_device_uuid() == "test-uuid-123"
        assert config.get_network_interface() == "eth0"
        assert config.get_http_port() == 8000
        assert config.get_default_volume() == 75
        assert config.get_log_level() == "DEBUG"

    finally:
        os.unlink(config_path)


def test_config_defaults():
    """Test default values"""
    from src.config import Config

    # Create minimal config
    config_content = """
device:
  name: "Test"
"""

    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
        f.write(config_content)
        config_path = f.name

    try:
        config = Config(config_path)

        # Check defaults
        assert config.get_http_port() == 8000
        assert config.get_default_volume() == 50
        assert config.get_log_level() == "INFO"

    finally:
        os.unlink(config_path)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
