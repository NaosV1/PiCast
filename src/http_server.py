"""
HTTP Server for UPnP Device Description and SOAP Control
"""

from http.server import HTTPServer, BaseHTTPRequestHandler
import logging
import threading
from typing import Any

from .device_description import (
    generate_device_description,
    generate_av_transport_scpd,
    generate_rendering_control_scpd,
    generate_connection_manager_scpd
)
from .services.soap_handler import SOAPHandler
from .services.av_transport import AVTransportService
from .services.rendering_control import RenderingControlService
from .services.connection_manager import ConnectionManagerService


class UPnPHTTPRequestHandler(BaseHTTPRequestHandler):
    """HTTP request handler for UPnP services"""

    def log_message(self, format, *args):
        """Override to use Python logging"""
        logger = logging.getLogger('http_server')
        logger.debug(f"{self.address_string()} - {format % args}")

    def do_GET(self):
        """Handle GET requests for XML descriptions"""
        logger = logging.getLogger('http_server')
        logger.debug(f"GET {self.path}")

        if self.path == '/description.xml':
            self._serve_device_description()
        elif self.path == '/AVTransport.xml':
            self._serve_xml(generate_av_transport_scpd())
        elif self.path == '/RenderingControl.xml':
            self._serve_xml(generate_rendering_control_scpd())
        elif self.path == '/ConnectionManager.xml':
            self._serve_xml(generate_connection_manager_scpd())
        elif self.path == '/':
            self._serve_root()
        else:
            self.send_error(404, "Not Found")

    def do_POST(self):
        """Handle POST requests for SOAP control"""
        logger = logging.getLogger('http_server')
        logger.debug(f"POST {self.path}")

        # Read body
        content_length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_length)

        # Parse SOAP request
        soap_handler = SOAPHandler()
        request = soap_handler.parse_soap_request(body)

        if not request:
            self._send_soap_error(401, "Invalid Action")
            return

        # Route to appropriate service
        try:
            if '/AVTransport/control' in self.path:
                service = self.server.av_transport_service
            elif '/RenderingControl/control' in self.path:
                service = self.server.rendering_control_service
            elif '/ConnectionManager/control' in self.path:
                service = self.server.connection_manager_service
            else:
                self.send_error(404, "Service Not Found")
                return

            # Handle action
            response_args = service.handle_action(request['action'], request['args'])

            # Create SOAP response
            soap_response = soap_handler.create_soap_response(
                request['action'],
                service.SERVICE_TYPE,
                response_args
            )

            # Send response
            self.send_response(200)
            self.send_header('Content-Type', 'text/xml; charset="utf-8"')
            self.send_header('Content-Length', len(soap_response))
            self.end_headers()
            self.wfile.write(soap_response.encode('utf-8'))

        except Exception as e:
            logger.error(f"Error handling SOAP action: {e}", exc_info=True)
            self._send_soap_error(501, str(e))

    def do_SUBSCRIBE(self):
        """Handle SUBSCRIBE requests for eventing (minimal implementation)"""
        logger = logging.getLogger('http_server')
        logger.debug(f"SUBSCRIBE {self.path}")

        # Return not implemented
        self.send_response(200)
        self.send_header('SID', 'uuid:dummy-subscription-id')
        self.send_header('TIMEOUT', 'Second-1800')
        self.end_headers()

    def do_UNSUBSCRIBE(self):
        """Handle UNSUBSCRIBE requests"""
        logger = logging.getLogger('http_server')
        logger.debug(f"UNSUBSCRIBE {self.path}")

        self.send_response(200)
        self.end_headers()

    def _serve_device_description(self):
        """Serve device description XML"""
        config = self.server.config
        base_url = self.server.base_url

        xml = generate_device_description(config, base_url)

        self.send_response(200)
        self.send_header('Content-Type', 'text/xml; charset="utf-8"')
        self.send_header('Content-Length', len(xml))
        self.end_headers()
        self.wfile.write(xml.encode('utf-8'))

    def _serve_xml(self, xml: str):
        """Serve XML content"""
        self.send_response(200)
        self.send_header('Content-Type', 'text/xml; charset="utf-8"')
        self.send_header('Content-Length', len(xml))
        self.end_headers()
        self.wfile.write(xml.encode('utf-8'))

    def _serve_root(self):
        """Serve simple root page"""
        html = """<!DOCTYPE html>
<html>
<head>
    <title>Raspberry Pi Audio Renderer</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; }
        h1 { color: #333; }
        .info { background: #f0f0f0; padding: 20px; border-radius: 5px; }
    </style>
</head>
<body>
    <h1>Raspberry Pi Audio Renderer</h1>
    <div class="info">
        <p>DLNA/UPnP Audio Renderer is running.</p>
        <p>Use a DLNA client app (BubbleUPnP, AllCast, etc.) to stream audio to this device.</p>
        <p><a href="/description.xml">Device Description</a></p>
    </div>
</body>
</html>"""

        self.send_response(200)
        self.send_header('Content-Type', 'text/html; charset="utf-8"')
        self.send_header('Content-Length', len(html))
        self.end_headers()
        self.wfile.write(html.encode('utf-8'))

    def _send_soap_error(self, error_code: int, error_description: str):
        """Send SOAP error response"""
        soap_handler = SOAPHandler()
        soap_error = soap_handler.create_soap_error(error_code, error_description)

        self.send_response(500)
        self.send_header('Content-Type', 'text/xml; charset="utf-8"')
        self.send_header('Content-Length', len(soap_error))
        self.end_headers()
        self.wfile.write(soap_error.encode('utf-8'))


class UPnPHTTPServer:
    """UPnP HTTP server wrapper"""

    def __init__(self, host: str, port: int, config: Any, player: Any):
        """
        Initialize HTTP server

        Args:
            host: Bind host
            port: Bind port
            config: Configuration object
            player: MPVController instance
        """
        self.host = host
        self.port = port
        self.config = config
        self.player = player
        self.logger = logging.getLogger(__name__)

        self.base_url = f"http://{host}:{port}/description.xml"

        # Create services
        self.av_transport_service = AVTransportService(player)
        self.rendering_control_service = RenderingControlService(player)
        self.connection_manager_service = ConnectionManagerService(player)

        # Create HTTP server
        self.httpd = HTTPServer((host, port), UPnPHTTPRequestHandler)
        self.httpd.config = config
        self.httpd.base_url = self.base_url
        self.httpd.av_transport_service = self.av_transport_service
        self.httpd.rendering_control_service = self.rendering_control_service
        self.httpd.connection_manager_service = self.connection_manager_service

        self.server_thread = None
        self.running = False

    def start(self):
        """Start HTTP server in background thread"""
        self.running = True
        self.server_thread = threading.Thread(target=self._serve, daemon=True)
        self.server_thread.start()
        self.logger.info(f"HTTP server started on {self.host}:{self.port}")

    def stop(self):
        """Stop HTTP server"""
        self.running = False
        if self.httpd:
            self.httpd.shutdown()
        if self.server_thread:
            self.server_thread.join(timeout=2)
        self.logger.info("HTTP server stopped")

    def _serve(self):
        """Server thread function"""
        try:
            self.httpd.serve_forever()
        except Exception as e:
            if self.running:
                self.logger.error(f"HTTP server error: {e}")
