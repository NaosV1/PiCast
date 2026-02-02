"""
Main application entry point
"""

import sys
import signal
import logging
import time

from .config import Config
from .utils import setup_logging, get_ip_address
from .player.mpv_controller import MPVController
from .http_server import UPnPHTTPServer
from .ssdp_server import SSDPServer


class AudioRenderer:
    """Main DLNA Audio Renderer application"""

    def __init__(self, config_path: str = "config.yaml"):
        """
        Initialize audio renderer

        Args:
            config_path: Path to configuration file
        """
        # Load configuration
        self.config = Config(config_path)

        # Setup logging
        setup_logging(self.config)
        self.logger = logging.getLogger(__name__)

        self.logger.info("=" * 60)
        self.logger.info("Raspberry Pi Audio Renderer Starting")
        self.logger.info("=" * 60)

        # Get network info
        interface = self.config.get_network_interface()
        self.ip_address = get_ip_address(interface)

        if not self.ip_address:
            self.logger.error(f"Failed to get IP address for interface {interface}")
            sys.exit(1)

        self.logger.info(f"Network interface: {interface}")
        self.logger.info(f"IP address: {self.ip_address}")

        # Initialize components
        self.player = None
        self.http_server = None
        self.ssdp_server = None

        # Setup signal handlers
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)

        self.running = False

    def _signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        self.logger.info(f"Received signal {signum}, shutting down...")
        self.stop()

    def start(self):
        """Start the audio renderer"""
        try:
            # Start mpv player
            self.logger.info("Starting mpv player...")
            self.player = MPVController(
                self.config.get_mpv_ipc_socket(),
                self.config
            )

            if not self.player.start():
                self.logger.error("Failed to start mpv")
                return False

            # Start HTTP server
            self.logger.info("Starting HTTP server...")
            http_port = self.config.get_http_port()
            self.http_server = UPnPHTTPServer(
                self.ip_address,
                http_port,
                self.config,
                self.player
            )
            self.http_server.start()

            # Start SSDP server
            self.logger.info("Starting SSDP server...")
            device_uuid = self.config.get_device_uuid()
            location_url = f"http://{self.ip_address}:{http_port}/description.xml"
            self.ssdp_server = SSDPServer(device_uuid, location_url, self.config)
            self.ssdp_server.start()

            self.running = True

            self.logger.info("=" * 60)
            self.logger.info("Audio Renderer Started Successfully")
            self.logger.info(f"Device Name: {self.config.get_device_name()}")
            self.logger.info(f"Device UUID: {device_uuid}")
            self.logger.info(f"Location URL: {location_url}")
            self.logger.info("Ready to receive audio streams")
            self.logger.info("=" * 60)

            return True

        except Exception as e:
            self.logger.error(f"Failed to start renderer: {e}", exc_info=True)
            self.stop()
            return False

    def stop(self):
        """Stop the audio renderer"""
        if not self.running:
            return

        self.logger.info("Stopping audio renderer...")
        self.running = False

        # Stop SSDP server
        if self.ssdp_server:
            try:
                self.ssdp_server.stop()
            except Exception as e:
                self.logger.error(f"Error stopping SSDP server: {e}")

        # Stop HTTP server
        if self.http_server:
            try:
                self.http_server.stop()
            except Exception as e:
                self.logger.error(f"Error stopping HTTP server: {e}")

        # Stop player
        if self.player:
            try:
                self.player.stop_mpv()
            except Exception as e:
                self.logger.error(f"Error stopping player: {e}")

        self.logger.info("Audio renderer stopped")

    def run(self):
        """Run the audio renderer (blocking)"""
        if not self.start():
            sys.exit(1)

        # Main loop
        try:
            while self.running:
                time.sleep(1)
        except KeyboardInterrupt:
            self.logger.info("Interrupted by user")
        finally:
            self.stop()


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(description='Raspberry Pi DLNA Audio Renderer')
    parser.add_argument(
        '-c', '--config',
        default='config.yaml',
        help='Path to configuration file (default: config.yaml)'
    )
    args = parser.parse_args()

    renderer = AudioRenderer(args.config)
    renderer.run()


if __name__ == '__main__':
    main()
