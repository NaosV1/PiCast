"""
RenderingControl Service Implementation
Handles volume and mute control
"""

import logging
from typing import Dict, Any


class RenderingControlService:
    """UPnP RenderingControl service"""

    SERVICE_TYPE = "urn:schemas-upnp-org:service:RenderingControl:1"

    def __init__(self, player):
        """
        Initialize RenderingControl service

        Args:
            player: MPVController instance
        """
        self.player = player
        self.logger = logging.getLogger(__name__)
        self.muted = False

    def handle_action(self, action: str, args: Dict[str, str]) -> Dict[str, str]:
        """
        Handle RenderingControl action

        Args:
            action: Action name
            args: Action arguments

        Returns:
            Response arguments dict
        """
        handler_name = f"_handle_{action}"
        handler = getattr(self, handler_name, None)

        if handler:
            self.logger.info(f"RenderingControl action: {action}")
            return handler(args)
        else:
            self.logger.warning(f"Unknown RenderingControl action: {action}")
            raise ValueError(f"Unknown action: {action}")

    def _handle_GetVolume(self, args: Dict[str, str]) -> Dict[str, str]:
        """Get current volume"""
        volume = self.player.get_volume()
        return {
            'CurrentVolume': str(volume)
        }

    def _handle_SetVolume(self, args: Dict[str, str]) -> Dict[str, str]:
        """Set volume"""
        volume = int(args.get('DesiredVolume', '50'))
        self.logger.info(f"Setting volume to {volume}")
        self.player.set_volume(volume)
        return {}

    def _handle_GetMute(self, args: Dict[str, str]) -> Dict[str, str]:
        """Get mute state"""
        return {
            'CurrentMute': '1' if self.muted else '0'
        }

    def _handle_SetMute(self, args: Dict[str, str]) -> Dict[str, str]:
        """Set mute state"""
        desired_mute = args.get('DesiredMute', '0')
        self.muted = desired_mute in ('1', 'true', 'True')

        self.logger.info(f"Setting mute to {self.muted}")

        if self.muted:
            # Store current volume and set to 0
            self.volume_before_mute = self.player.get_volume()
            self.player.set_volume(0)
        else:
            # Restore previous volume
            if hasattr(self, 'volume_before_mute'):
                self.player.set_volume(self.volume_before_mute)

        return {}
