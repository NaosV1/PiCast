"""
MPV Player Controller
Manages audio playback using mpv via JSON IPC
"""

import subprocess
import socket
import json
import logging
import os
import time
from typing import Optional, Dict, Any
from threading import Thread, Lock


class MPVController:
    """Controller for mpv media player via IPC"""

    def __init__(self, ipc_socket_path: str, config: Any):
        """
        Initialize MPV controller

        Args:
            ipc_socket_path: Path to mpv IPC socket
            config: Configuration object
        """
        self.ipc_socket_path = ipc_socket_path
        self.config = config
        self.logger = logging.getLogger(__name__)

        self.process: Optional[subprocess.Popen] = None
        self.socket: Optional[socket.socket] = None
        self.lock = Lock()

        self.current_url: Optional[str] = None
        self.current_state = "STOPPED"  # STOPPED, PLAYING, PAUSED_PLAYBACK, TRANSITIONING
        self.current_volume = config.get_default_volume()
        self.current_position = 0
        self.current_duration = 0

        self.request_id = 0

    def start(self):
        """Start mpv process with IPC enabled"""
        # Remove old socket if exists
        if os.path.exists(self.ipc_socket_path):
            try:
                os.remove(self.ipc_socket_path)
            except OSError:
                pass

        # Build mpv command
        cmd = [
            'mpv',
            f'--input-ipc-server={self.ipc_socket_path}',
            '--idle=yes',
            '--no-video',
            '--no-terminal',
            f'--ao={self.config.get_audio_output_driver()}',
            f'--volume={self.current_volume}',
        ]

        if self.config.get_cache_enabled():
            cmd.extend([
                '--cache=yes',
                f'--demuxer-max-bytes={self.config.get_demuxer_max_bytes()}',
            ])

        self.logger.info(f"Starting mpv: {' '.join(cmd)}")

        try:
            self.process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                stdin=subprocess.PIPE
            )

            # Wait for socket to be created
            max_wait = 5
            waited = 0
            while not os.path.exists(self.ipc_socket_path) and waited < max_wait:
                time.sleep(0.1)
                waited += 0.1

            if not os.path.exists(self.ipc_socket_path):
                raise RuntimeError("mpv IPC socket not created")

            self.logger.info("mpv started successfully")
            return True

        except Exception as e:
            self.logger.error(f"Failed to start mpv: {e}")
            return False

    def stop_mpv(self):
        """Stop mpv process"""
        if self.socket:
            try:
                self.socket.close()
            except:
                pass
            self.socket = None

        if self.process:
            try:
                self.process.terminate()
                self.process.wait(timeout=5)
            except:
                self.process.kill()
            self.process = None

        # Clean up socket file
        if os.path.exists(self.ipc_socket_path):
            try:
                os.remove(self.ipc_socket_path)
            except:
                pass

        self.logger.info("mpv stopped")

    def _connect_socket(self) -> bool:
        """Connect to mpv IPC socket"""
        if self.socket:
            return True

        try:
            self.socket = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
            self.socket.connect(self.ipc_socket_path)
            self.socket.settimeout(2.0)
            return True
        except Exception as e:
            self.logger.error(f"Failed to connect to mpv socket: {e}")
            self.socket = None
            return False

    def _send_command(self, command: list) -> Optional[Dict[str, Any]]:
        """
        Send command to mpv via IPC

        Args:
            command: Command list (e.g., ['loadfile', 'url.mp3'])

        Returns:
            Response dict or None on error
        """
        with self.lock:
            if not self._connect_socket():
                return None

            self.request_id += 1
            request = {
                "command": command,
                "request_id": self.request_id
            }

            try:
                message = json.dumps(request) + '\n'
                self.socket.sendall(message.encode('utf-8'))

                # Read response
                response_data = b''
                while True:
                    chunk = self.socket.recv(4096)
                    if not chunk:
                        break
                    response_data += chunk
                    if b'\n' in response_data:
                        break

                if response_data:
                    response = json.loads(response_data.decode('utf-8').strip())
                    return response
                else:
                    return None

            except socket.timeout:
                self.logger.warning("mpv command timeout")
                return None
            except Exception as e:
                self.logger.error(f"mpv command error: {e}")
                # Close socket on error
                if self.socket:
                    try:
                        self.socket.close()
                    except:
                        pass
                    self.socket = None
                return None

    def _get_property(self, property_name: str) -> Any:
        """Get property value from mpv"""
        response = self._send_command(['get_property', property_name])
        if response and response.get('error') == 'success':
            return response.get('data')
        return None

    def play(self, url: str) -> bool:
        """
        Start playing audio from URL

        Args:
            url: Audio stream URL

        Returns:
            True if successful
        """
        self.logger.info(f"Playing: {url}")

        self.current_state = "TRANSITIONING"
        self.current_url = url

        response = self._send_command(['loadfile', url, 'replace'])

        if response and response.get('error') == 'success':
            self.current_state = "PLAYING"
            self.logger.info("Playback started")
            return True
        else:
            self.current_state = "STOPPED"
            self.logger.error(f"Failed to play: {response}")
            return False

    def pause(self) -> bool:
        """Pause playback"""
        self.logger.info("Pausing playback")

        response = self._send_command(['set_property', 'pause', True])

        if response and response.get('error') == 'success':
            self.current_state = "PAUSED_PLAYBACK"
            return True
        else:
            self.logger.error("Failed to pause")
            return False

    def resume(self) -> bool:
        """Resume playback"""
        self.logger.info("Resuming playback")

        response = self._send_command(['set_property', 'pause', False])

        if response and response.get('error') == 'success':
            self.current_state = "PLAYING"
            return True
        else:
            self.logger.error("Failed to resume")
            return False

    def stop(self) -> bool:
        """Stop playback"""
        self.logger.info("Stopping playback")

        response = self._send_command(['stop'])

        self.current_state = "STOPPED"
        self.current_url = None
        self.current_position = 0
        self.current_duration = 0

        return True

    def set_volume(self, level: int) -> bool:
        """
        Set volume level

        Args:
            level: Volume (0-100)

        Returns:
            True if successful
        """
        level = max(0, min(100, level))
        self.logger.info(f"Setting volume to {level}")

        response = self._send_command(['set_property', 'volume', level])

        if response and response.get('error') == 'success':
            self.current_volume = level
            return True
        else:
            self.logger.error("Failed to set volume")
            return False

    def get_volume(self) -> int:
        """Get current volume level"""
        volume = self._get_property('volume')
        if volume is not None:
            self.current_volume = int(volume)
        return self.current_volume

    def get_position(self) -> float:
        """Get current playback position in seconds"""
        position = self._get_property('time-pos')
        if position is not None:
            self.current_position = float(position)
        return self.current_position

    def get_duration(self) -> float:
        """Get total duration in seconds"""
        duration = self._get_property('duration')
        if duration is not None:
            self.current_duration = float(duration)
        return self.current_duration

    def seek(self, position: float) -> bool:
        """
        Seek to position

        Args:
            position: Position in seconds

        Returns:
            True if successful
        """
        self.logger.info(f"Seeking to {position}")

        response = self._send_command(['seek', position, 'absolute'])

        if response and response.get('error') == 'success':
            self.current_position = position
            return True
        else:
            self.logger.error("Failed to seek")
            return False

    def get_status(self) -> Dict[str, Any]:
        """
        Get current player status

        Returns:
            Status dictionary
        """
        # Update position if playing
        if self.current_state == "PLAYING":
            self.get_position()
            self.get_duration()

        return {
            'state': self.current_state,
            'url': self.current_url,
            'volume': self.current_volume,
            'position': self.current_position,
            'duration': self.current_duration,
        }

    def is_playing(self) -> bool:
        """Check if currently playing"""
        paused = self._get_property('pause')
        if paused is False:
            self.current_state = "PLAYING"
            return True
        elif paused is True:
            self.current_state = "PAUSED_PLAYBACK"
            return False
        else:
            self.current_state = "STOPPED"
            return False
