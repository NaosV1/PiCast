"""
Utility functions
"""

import netifaces
import logging
from typing import Optional


def get_ip_address(interface: str = 'eth0') -> Optional[str]:
    """
    Get IP address of network interface

    Args:
        interface: Network interface name

    Returns:
        IP address or None if not found
    """
    logger = logging.getLogger(__name__)

    try:
        addrs = netifaces.ifaddresses(interface)
        if netifaces.AF_INET in addrs:
            return addrs[netifaces.AF_INET][0]['addr']
    except (ValueError, KeyError) as e:
        logger.error(f"Failed to get IP for {interface}: {e}")

    return None


def setup_logging(config):
    """
    Setup logging configuration

    Args:
        config: Configuration object
    """
    from logging.handlers import RotatingFileHandler

    level = getattr(logging, config.get_log_level().upper(), logging.INFO)
    log_file = config.get_log_file()
    max_bytes = config.get_log_max_size_mb() * 1024 * 1024
    backup_count = config.get_log_backup_count()

    # Create formatters
    file_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    console_formatter = logging.Formatter(
        '%(levelname)s - %(message)s'
    )

    # File handler with rotation
    file_handler = RotatingFileHandler(
        log_file,
        maxBytes=max_bytes,
        backupCount=backup_count
    )
    file_handler.setLevel(level)
    file_handler.setFormatter(file_formatter)

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)
    console_handler.setFormatter(console_formatter)

    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(level)
    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)

    # Reduce noise from http.server
    logging.getLogger('http.server').setLevel(logging.WARNING)
