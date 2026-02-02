"""
ConnectionManager Service Implementation
Handles protocol info and connections
"""

import logging
from typing import Dict, Any


class ConnectionManagerService:
    """UPnP ConnectionManager service"""

    SERVICE_TYPE = "urn:schemas-upnp-org:service:ConnectionManager:1"

    # Supported audio formats
    PROTOCOL_INFO = (
        "http-get:*:audio/mpeg:*,"
        "http-get:*:audio/mp3:*,"
        "http-get:*:audio/mp4:*,"
        "http-get:*:audio/x-m4a:*,"
        "http-get:*:audio/aac:*,"
        "http-get:*:audio/flac:*,"
        "http-get:*:audio/x-flac:*,"
        "http-get:*:audio/ogg:*,"
        "http-get:*:audio/vorbis:*,"
        "http-get:*:audio/wav:*,"
        "http-get:*:audio/x-wav:*,"
        "http-get:*:audio/L16:*,"
        "http-get:*:application/ogg:*"
    )

    def __init__(self, player):
        """
        Initialize ConnectionManager service

        Args:
            player: MPVController instance
        """
        self.player = player
        self.logger = logging.getLogger(__name__)

    def handle_action(self, action: str, args: Dict[str, str]) -> Dict[str, str]:
        """
        Handle ConnectionManager action

        Args:
            action: Action name
            args: Action arguments

        Returns:
            Response arguments dict
        """
        handler_name = f"_handle_{action}"
        handler = getattr(self, handler_name, None)

        if handler:
            self.logger.info(f"ConnectionManager action: {action}")
            return handler(args)
        else:
            self.logger.warning(f"Unknown ConnectionManager action: {action}")
            raise ValueError(f"Unknown action: {action}")

    def _handle_GetProtocolInfo(self, args: Dict[str, str]) -> Dict[str, str]:
        """Get supported protocol info"""
        return {
            'Source': '',  # We don't serve content
            'Sink': self.PROTOCOL_INFO  # We can play these formats
        }

    def _handle_GetCurrentConnectionIDs(self, args: Dict[str, str]) -> Dict[str, str]:
        """Get current connection IDs"""
        return {
            'ConnectionIDs': '0'  # Single connection
        }

    def _handle_GetCurrentConnectionInfo(self, args: Dict[str, str]) -> Dict[str, str]:
        """Get connection info"""
        return {
            'RcsID': '0',
            'AVTransportID': '0',
            'ProtocolInfo': '',
            'PeerConnectionManager': '',
            'PeerConnectionID': '-1',
            'Direction': 'Input',
            'Status': 'OK'
        }
