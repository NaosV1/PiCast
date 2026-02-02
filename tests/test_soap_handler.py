"""
Tests for SOAP handler
"""

import pytest
from src.services.soap_handler import SOAPHandler, format_time, parse_time


def test_format_time():
    """Test time formatting"""
    assert format_time(0) == "0:00:00"
    assert format_time(65) == "0:01:05"
    assert format_time(3665) == "1:01:05"
    assert format_time(3600) == "1:00:00"


def test_parse_time():
    """Test time parsing"""
    assert parse_time("0:00:00") == 0
    assert parse_time("0:01:05") == 65
    assert parse_time("1:01:05") == 3665
    assert parse_time("1:30") == 90


def test_soap_request_parsing():
    """Test SOAP request parsing"""
    handler = SOAPHandler()

    soap_request = """<?xml version="1.0" encoding="utf-8"?>
<s:Envelope xmlns:s="http://schemas.xmlsoap.org/soap/envelope/"
            s:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/">
  <s:Body>
    <u:Play xmlns:u="urn:schemas-upnp-org:service:AVTransport:1">
      <InstanceID>0</InstanceID>
      <Speed>1</Speed>
    </u:Play>
  </s:Body>
</s:Envelope>"""

    result = handler.parse_soap_request(soap_request.encode('utf-8'))

    assert result is not None
    assert result['action'] == 'Play'
    assert result['service_type'] == 'urn:schemas-upnp-org:service:AVTransport:1'
    assert result['args']['InstanceID'] == '0'
    assert result['args']['Speed'] == '1'


def test_soap_response_creation():
    """Test SOAP response creation"""
    handler = SOAPHandler()

    response = handler.create_soap_response(
        'GetVolume',
        'urn:schemas-upnp-org:service:RenderingControl:1',
        {'CurrentVolume': '50'}
    )

    assert '<?xml version' in response
    assert 'GetVolumeResponse' in response
    assert 'CurrentVolume' in response
    assert '50' in response


def test_soap_error_creation():
    """Test SOAP error creation"""
    handler = SOAPHandler()

    error = handler.create_soap_error(401, "Invalid Action")

    assert '<?xml version' in error
    assert 'Fault' in error
    assert '401' in error
    assert 'Invalid Action' in error


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
