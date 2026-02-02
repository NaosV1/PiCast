"""
SSDP Server for UPnP Device Discovery
Handles multicast discovery and device announcements
"""

import socket
import struct
import threading
import time
import logging
from typing import Optional, Any


class SSDPServer:
    """Simple Service Discovery Protocol server"""

    SSDP_ADDR = "239.255.255.250"
    SSDP_PORT = 1900

    def __init__(self, device_uuid: str, location_url: str, config: Any):
        """
        Initialize SSDP server

        Args:
            device_uuid: Unique device identifier
            location_url: URL to device description XML
            config: Configuration object
        """
        self.device_uuid = device_uuid
        self.location_url = location_url
        self.config = config
        self.logger = logging.getLogger(__name__)

        self.running = False
        self.sock: Optional[socket.socket] = None
        self.listen_thread: Optional[threading.Thread] = None
        self.announce_thread: Optional[threading.Thread] = None

    def start(self):
        """Start SSDP server"""
        self.running = True

        # Create multicast socket
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        # Bind to SSDP port
        self.sock.bind(('', self.SSDP_PORT))

        # Join multicast group
        mreq = struct.pack("4sl", socket.inet_aton(self.SSDP_ADDR), socket.INADDR_ANY)
        self.sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)

        self.logger.info(f"SSDP server started on {self.SSDP_ADDR}:{self.SSDP_PORT}")

        # Start listening thread
        self.listen_thread = threading.Thread(target=self._listen_loop, daemon=True)
        self.listen_thread.start()

        # Start announcement thread
        self.announce_thread = threading.Thread(target=self._announce_loop, daemon=True)
        self.announce_thread.start()

        # Send initial ALIVE notifications
        self._send_alive()

    def stop(self):
        """Stop SSDP server"""
        self.running = False

        # Send byebye notifications
        self._send_byebye()

        if self.sock:
            try:
                self.sock.close()
            except:
                pass

        if self.listen_thread:
            self.listen_thread.join(timeout=2)

        if self.announce_thread:
            self.announce_thread.join(timeout=2)

        self.logger.info("SSDP server stopped")

    def _listen_loop(self):
        """Listen for M-SEARCH requests"""
        while self.running:
            try:
                data, addr = self.sock.recvfrom(1024)
                message = data.decode('utf-8', errors='ignore')

                if 'M-SEARCH' in message:
                    self._handle_msearch(message, addr)

            except socket.timeout:
                continue
            except Exception as e:
                if self.running:
                    self.logger.error(f"SSDP listen error: {e}")
                break

    def _handle_msearch(self, message: str, addr: tuple):
        """
        Handle M-SEARCH discovery request

        Args:
            message: SSDP message
            addr: Source address tuple (ip, port)
        """
        self.logger.debug(f"M-SEARCH from {addr[0]}:{addr[1]}")

        # Parse search target
        st = None
        for line in message.split('\r\n'):
            if line.startswith('ST:'):
                st = line.split(':', 1)[1].strip()
                break

        if not st:
            return

        # Respond if search target matches
        should_respond = (
            st == 'ssdp:all' or
            st == 'upnp:rootdevice' or
            st == f'uuid:{self.device_uuid}' or
            st == 'urn:schemas-upnp-org:device:MediaRenderer:1' or
            st == 'urn:schemas-upnp-org:service:AVTransport:1' or
            st == 'urn:schemas-upnp-org:service:RenderingControl:1' or
            st == 'urn:schemas-upnp-org:service:ConnectionManager:1'
        )

        if should_respond:
            self._send_msearch_response(addr, st)

    def _send_msearch_response(self, addr: tuple, st: str):
        """
        Send M-SEARCH response

        Args:
            addr: Destination address
            st: Search target
        """
        response = (
            'HTTP/1.1 200 OK\r\n'
            f'CACHE-CONTROL: max-age=1800\r\n'
            f'EXT:\r\n'
            f'LOCATION: {self.location_url}\r\n'
            f'SERVER: Linux/4.x UPnP/1.1 Pi-Audio-Renderer/1.0\r\n'
            f'ST: {st}\r\n'
            f'USN: uuid:{self.device_uuid}::{st}\r\n'
            '\r\n'
        )

        try:
            self.sock.sendto(response.encode('utf-8'), addr)
            self.logger.debug(f"Sent M-SEARCH response to {addr[0]}:{addr[1]}")
        except Exception as e:
            self.logger.error(f"Failed to send M-SEARCH response: {e}")

    def _announce_loop(self):
        """Periodically send ALIVE announcements"""
        interval = self.config.get_announce_interval()

        while self.running:
            time.sleep(interval)
            if self.running:
                self._send_alive()

    def _send_alive(self):
        """Send ssdp:alive notifications"""
        services = [
            'upnp:rootdevice',
            f'uuid:{self.device_uuid}',
            'urn:schemas-upnp-org:device:MediaRenderer:1',
            'urn:schemas-upnp-org:service:AVTransport:1',
            'urn:schemas-upnp-org:service:RenderingControl:1',
            'urn:schemas-upnp-org:service:ConnectionManager:1',
        ]

        for service in services:
            self._send_notify(service, 'ssdp:alive')

    def _send_byebye(self):
        """Send ssdp:byebye notifications"""
        services = [
            'upnp:rootdevice',
            f'uuid:{self.device_uuid}',
            'urn:schemas-upnp-org:device:MediaRenderer:1',
        ]

        for service in services:
            self._send_notify(service, 'ssdp:byebye')

    def _send_notify(self, nt: str, nts: str):
        """
        Send NOTIFY message

        Args:
            nt: Notification Type
            nts: Notification Sub Type (alive/byebye)
        """
        message = (
            'NOTIFY * HTTP/1.1\r\n'
            f'HOST: {self.SSDP_ADDR}:{self.SSDP_PORT}\r\n'
            f'CACHE-CONTROL: max-age=1800\r\n'
            f'LOCATION: {self.location_url}\r\n'
            f'NT: {nt}\r\n'
            f'NTS: {nts}\r\n'
            f'SERVER: Linux/4.x UPnP/1.1 Pi-Audio-Renderer/1.0\r\n'
            f'USN: uuid:{self.device_uuid}::{nt}\r\n'
            '\r\n'
        )

        try:
            self.sock.sendto(
                message.encode('utf-8'),
                (self.SSDP_ADDR, self.SSDP_PORT)
            )
            self.logger.debug(f"Sent NOTIFY {nts} for {nt}")
        except Exception as e:
            self.logger.error(f"Failed to send NOTIFY: {e}")
