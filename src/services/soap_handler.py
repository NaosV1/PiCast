"""
SOAP Request Handler for UPnP Services
"""

import xml.etree.ElementTree as ET
import logging
from typing import Dict, Any, Optional, Callable


class SOAPHandler:
    """SOAP message parser and response generator"""

    SOAP_NS = "http://schemas.xmlsoap.org/soap/envelope/"
    ENCODING_STYLE = "http://schemas.xmlsoap.org/soap/encoding/"

    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def parse_soap_request(self, body: bytes) -> Optional[Dict[str, Any]]:
        """
        Parse SOAP request body

        Args:
            body: SOAP XML body

        Returns:
            Dict with action, service_type, and arguments
        """
        try:
            root = ET.fromstring(body)

            # Find SOAP Body
            body_elem = root.find('.//{http://schemas.xmlsoap.org/soap/envelope/}Body')
            if body_elem is None:
                self.logger.error("SOAP Body not found")
                return None

            # Get first child (action element)
            action_elem = list(body_elem)[0]
            action_name = action_elem.tag.split('}')[-1]  # Remove namespace
            service_type = action_elem.tag.split('}')[0].strip('{')

            # Parse arguments
            args = {}
            for arg in action_elem:
                arg_name = arg.tag.split('}')[-1]
                args[arg_name] = arg.text or ""

            return {
                'action': action_name,
                'service_type': service_type,
                'args': args
            }

        except Exception as e:
            self.logger.error(f"Failed to parse SOAP request: {e}")
            return None

    def create_soap_response(self, action: str, service_type: str, args: Dict[str, str]) -> str:
        """
        Create SOAP response

        Args:
            action: Action name
            service_type: Service type URN
            args: Response arguments

        Returns:
            SOAP XML string
        """
        # Create response envelope
        envelope = ET.Element('s:Envelope')
        envelope.set('xmlns:s', self.SOAP_NS)
        envelope.set('s:encodingStyle', self.ENCODING_STYLE)

        body = ET.SubElement(envelope, 's:Body')

        # Create response element
        response = ET.SubElement(body, f'u:{action}Response')
        response.set('xmlns:u', service_type)

        # Add arguments
        for key, value in args.items():
            arg_elem = ET.SubElement(response, key)
            arg_elem.text = str(value)

        # Convert to string
        xml_str = ET.tostring(envelope, encoding='unicode')
        return f'<?xml version="1.0" encoding="utf-8"?>\n{xml_str}'

    def create_soap_error(self, error_code: int, error_description: str) -> str:
        """
        Create SOAP fault response

        Args:
            error_code: UPnP error code
            error_description: Error description

        Returns:
            SOAP fault XML string
        """
        envelope = ET.Element('s:Envelope')
        envelope.set('xmlns:s', self.SOAP_NS)
        envelope.set('s:encodingStyle', self.ENCODING_STYLE)

        body = ET.SubElement(envelope, 's:Body')
        fault = ET.SubElement(body, 's:Fault')

        faultcode = ET.SubElement(fault, 'faultcode')
        faultcode.text = 's:Client'

        faultstring = ET.SubElement(fault, 'faultstring')
        faultstring.text = 'UPnPError'

        detail = ET.SubElement(fault, 'detail')
        upnp_error = ET.SubElement(detail, 'UPnPError')
        upnp_error.set('xmlns', 'urn:schemas-upnp-org:control-1-0')

        error_code_elem = ET.SubElement(upnp_error, 'errorCode')
        error_code_elem.text = str(error_code)

        error_desc_elem = ET.SubElement(upnp_error, 'errorDescription')
        error_desc_elem.text = error_description

        xml_str = ET.tostring(envelope, encoding='unicode')
        return f'<?xml version="1.0" encoding="utf-8"?>\n{xml_str}'


def format_time(seconds: float) -> str:
    """
    Format seconds to H:MM:SS

    Args:
        seconds: Time in seconds

    Returns:
        Formatted time string
    """
    if seconds < 0 or seconds == float('inf'):
        return "00:00:00"

    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)

    return f"{hours}:{minutes:02d}:{secs:02d}"


def parse_time(time_str: str) -> float:
    """
    Parse H:MM:SS to seconds

    Args:
        time_str: Time string

    Returns:
        Seconds
    """
    try:
        parts = time_str.split(':')
        if len(parts) == 3:
            hours, minutes, seconds = map(int, parts)
            return hours * 3600 + minutes * 60 + seconds
        elif len(parts) == 2:
            minutes, seconds = map(int, parts)
            return minutes * 60 + seconds
        else:
            return float(parts[0])
    except:
        return 0.0
