"""
AVTransport Service Implementation
Handles playback control actions
"""

import logging
from typing import Dict, Any
from .soap_handler import format_time, parse_time


class AVTransportService:
    """UPnP AVTransport service"""

    SERVICE_TYPE = "urn:schemas-upnp-org:service:AVTransport:1"

    def __init__(self, player):
        """
        Initialize AVTransport service

        Args:
            player: MPVController instance
        """
        self.player = player
        self.logger = logging.getLogger(__name__)

        self.current_uri = ""
        self.current_uri_metadata = ""

    def handle_action(self, action: str, args: Dict[str, str]) -> Dict[str, str]:
        """
        Handle AVTransport action

        Args:
            action: Action name
            args: Action arguments

        Returns:
            Response arguments dict
        """
        handler_name = f"_handle_{action}"
        handler = getattr(self, handler_name, None)

        if handler:
            self.logger.info(f"AVTransport action: {action}")
            return handler(args)
        else:
            self.logger.warning(f"Unknown AVTransport action: {action}")
            raise ValueError(f"Unknown action: {action}")

    def _handle_SetAVTransportURI(self, args: Dict[str, str]) -> Dict[str, str]:
        """Set the transport URI"""
        self.current_uri = args.get('CurrentURI', '')
        self.current_uri_metadata = args.get('CurrentURIMetaData', '')

        self.logger.info(f"SetAVTransportURI: {self.current_uri}")

        # Don't auto-play, just set the URI
        return {}

    def _handle_Play(self, args: Dict[str, str]) -> Dict[str, str]:
        """Start playback"""
        if not self.current_uri:
            raise ValueError("No URI set")

        self.logger.info(f"Playing: {self.current_uri}")
        success = self.player.play(self.current_uri)

        if not success:
            raise RuntimeError("Failed to start playback")

        return {}

    def _handle_Pause(self, args: Dict[str, str]) -> Dict[str, str]:
        """Pause playback"""
        self.logger.info("Pausing playback")
        self.player.pause()
        return {}

    def _handle_Stop(self, args: Dict[str, str]) -> Dict[str, str]:
        """Stop playback"""
        self.logger.info("Stopping playback")
        self.player.stop()
        return {}

    def _handle_Seek(self, args: Dict[str, str]) -> Dict[str, str]:
        """Seek to position"""
        unit = args.get('Unit', 'ABS_TIME')
        target = args.get('Target', '00:00:00')

        if unit == 'ABS_TIME' or unit == 'REL_TIME':
            position = parse_time(target)
            self.logger.info(f"Seeking to {position}s")
            self.player.seek(position)

        return {}

    def _handle_GetTransportInfo(self, args: Dict[str, str]) -> Dict[str, str]:
        """Get transport state"""
        status = self.player.get_status()
        state = status['state']

        return {
            'CurrentTransportState': state,
            'CurrentTransportStatus': 'OK',
            'CurrentSpeed': '1'
        }

    def _handle_GetPositionInfo(self, args: Dict[str, str]) -> Dict[str, str]:
        """Get position information"""
        status = self.player.get_status()

        position = status.get('position', 0)
        duration = status.get('duration', 0)

        return {
            'Track': '1',
            'TrackDuration': format_time(duration),
            'TrackMetaData': self.current_uri_metadata,
            'TrackURI': self.current_uri,
            'RelTime': format_time(position),
            'AbsTime': format_time(position),
            'RelCount': '0',
            'AbsCount': '0'
        }

    def _handle_GetMediaInfo(self, args: Dict[str, str]) -> Dict[str, str]:
        """Get media information"""
        status = self.player.get_status()
        duration = status.get('duration', 0)

        return {
            'NrTracks': '1',
            'MediaDuration': format_time(duration),
            'CurrentURI': self.current_uri,
            'CurrentURIMetaData': self.current_uri_metadata,
            'NextURI': '',
            'NextURIMetaData': '',
            'PlayMedium': 'NETWORK',
            'RecordMedium': 'NOT_IMPLEMENTED',
            'WriteStatus': 'NOT_IMPLEMENTED'
        }
