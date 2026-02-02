"""
UPnP Device Description XML Generator
"""

from typing import Any


def generate_device_description(config: Any, base_url: str) -> str:
    """
    Generate UPnP device description XML

    Args:
        config: Configuration object
        base_url: Base URL for service descriptions

    Returns:
        XML string
    """
    uuid = config.get_device_uuid()
    name = config.get_device_name()
    manufacturer = config.get_manufacturer()
    model_name = config.get_model_name()
    model_number = config.get_model_number()
    serial = config.get_serial_number()

    xml = f'''<?xml version="1.0" encoding="utf-8"?>
<root xmlns="urn:schemas-upnp-org:device-1-0">
  <specVersion>
    <major>1</major>
    <minor>0</minor>
  </specVersion>
  <device>
    <deviceType>urn:schemas-upnp-org:device:MediaRenderer:1</deviceType>
    <friendlyName>{name}</friendlyName>
    <manufacturer>{manufacturer}</manufacturer>
    <manufacturerURL>http://www.example.com</manufacturerURL>
    <modelDescription>UPnP/DLNA Audio Renderer</modelDescription>
    <modelName>{model_name}</modelName>
    <modelNumber>{model_number}</modelNumber>
    <modelURL>http://www.example.com</modelURL>
    <serialNumber>{serial}</serialNumber>
    <UDN>uuid:{uuid}</UDN>
    <presentationURL>/</presentationURL>
    <serviceList>
      <service>
        <serviceType>urn:schemas-upnp-org:service:AVTransport:1</serviceType>
        <serviceId>urn:upnp-org:serviceId:AVTransport</serviceId>
        <SCPDURL>/AVTransport.xml</SCPDURL>
        <controlURL>/AVTransport/control</controlURL>
        <eventSubURL>/AVTransport/event</eventSubURL>
      </service>
      <service>
        <serviceType>urn:schemas-upnp-org:service:RenderingControl:1</serviceType>
        <serviceId>urn:upnp-org:serviceId:RenderingControl</serviceId>
        <SCPDURL>/RenderingControl.xml</SCPDURL>
        <controlURL>/RenderingControl/control</controlURL>
        <eventSubURL>/RenderingControl/event</eventSubURL>
      </service>
      <service>
        <serviceType>urn:schemas-upnp-org:service:ConnectionManager:1</serviceType>
        <serviceId>urn:upnp-org:serviceId:ConnectionManager</serviceId>
        <SCPDURL>/ConnectionManager.xml</SCPDURL>
        <controlURL>/ConnectionManager/control</controlURL>
        <eventSubURL>/ConnectionManager/event</eventSubURL>
      </service>
    </serviceList>
  </device>
</root>'''

    return xml


def generate_av_transport_scpd() -> str:
    """Generate AVTransport service description"""
    return '''<?xml version="1.0" encoding="utf-8"?>
<scpd xmlns="urn:schemas-upnp-org:service-1-0">
  <specVersion>
    <major>1</major>
    <minor>0</minor>
  </specVersion>
  <actionList>
    <action>
      <name>SetAVTransportURI</name>
      <argumentList>
        <argument>
          <name>InstanceID</name>
          <direction>in</direction>
          <relatedStateVariable>A_ARG_TYPE_InstanceID</relatedStateVariable>
        </argument>
        <argument>
          <name>CurrentURI</name>
          <direction>in</direction>
          <relatedStateVariable>AVTransportURI</relatedStateVariable>
        </argument>
        <argument>
          <name>CurrentURIMetaData</name>
          <direction>in</direction>
          <relatedStateVariable>AVTransportURIMetaData</relatedStateVariable>
        </argument>
      </argumentList>
    </action>
    <action>
      <name>Play</name>
      <argumentList>
        <argument>
          <name>InstanceID</name>
          <direction>in</direction>
          <relatedStateVariable>A_ARG_TYPE_InstanceID</relatedStateVariable>
        </argument>
        <argument>
          <name>Speed</name>
          <direction>in</direction>
          <relatedStateVariable>TransportPlaySpeed</relatedStateVariable>
        </argument>
      </argumentList>
    </action>
    <action>
      <name>Pause</name>
      <argumentList>
        <argument>
          <name>InstanceID</name>
          <direction>in</direction>
          <relatedStateVariable>A_ARG_TYPE_InstanceID</relatedStateVariable>
        </argument>
      </argumentList>
    </action>
    <action>
      <name>Stop</name>
      <argumentList>
        <argument>
          <name>InstanceID</name>
          <direction>in</direction>
          <relatedStateVariable>A_ARG_TYPE_InstanceID</relatedStateVariable>
        </argument>
      </argumentList>
    </action>
    <action>
      <name>Seek</name>
      <argumentList>
        <argument>
          <name>InstanceID</name>
          <direction>in</direction>
          <relatedStateVariable>A_ARG_TYPE_InstanceID</relatedStateVariable>
        </argument>
        <argument>
          <name>Unit</name>
          <direction>in</direction>
          <relatedStateVariable>A_ARG_TYPE_SeekMode</relatedStateVariable>
        </argument>
        <argument>
          <name>Target</name>
          <direction>in</direction>
          <relatedStateVariable>A_ARG_TYPE_SeekTarget</relatedStateVariable>
        </argument>
      </argumentList>
    </action>
    <action>
      <name>GetTransportInfo</name>
      <argumentList>
        <argument>
          <name>InstanceID</name>
          <direction>in</direction>
          <relatedStateVariable>A_ARG_TYPE_InstanceID</relatedStateVariable>
        </argument>
        <argument>
          <name>CurrentTransportState</name>
          <direction>out</direction>
          <relatedStateVariable>TransportState</relatedStateVariable>
        </argument>
        <argument>
          <name>CurrentTransportStatus</name>
          <direction>out</direction>
          <relatedStateVariable>TransportStatus</relatedStateVariable>
        </argument>
        <argument>
          <name>CurrentSpeed</name>
          <direction>out</direction>
          <relatedStateVariable>TransportPlaySpeed</relatedStateVariable>
        </argument>
      </argumentList>
    </action>
    <action>
      <name>GetPositionInfo</name>
      <argumentList>
        <argument>
          <name>InstanceID</name>
          <direction>in</direction>
          <relatedStateVariable>A_ARG_TYPE_InstanceID</relatedStateVariable>
        </argument>
        <argument>
          <name>Track</name>
          <direction>out</direction>
          <relatedStateVariable>CurrentTrack</relatedStateVariable>
        </argument>
        <argument>
          <name>TrackDuration</name>
          <direction>out</direction>
          <relatedStateVariable>CurrentTrackDuration</relatedStateVariable>
        </argument>
        <argument>
          <name>TrackMetaData</name>
          <direction>out</direction>
          <relatedStateVariable>CurrentTrackMetaData</relatedStateVariable>
        </argument>
        <argument>
          <name>TrackURI</name>
          <direction>out</direction>
          <relatedStateVariable>CurrentTrackURI</relatedStateVariable>
        </argument>
        <argument>
          <name>RelTime</name>
          <direction>out</direction>
          <relatedStateVariable>RelativeTimePosition</relatedStateVariable>
        </argument>
        <argument>
          <name>AbsTime</name>
          <direction>out</direction>
          <relatedStateVariable>AbsoluteTimePosition</relatedStateVariable>
        </argument>
        <argument>
          <name>RelCount</name>
          <direction>out</direction>
          <relatedStateVariable>RelativeCounterPosition</relatedStateVariable>
        </argument>
        <argument>
          <name>AbsCount</name>
          <direction>out</direction>
          <relatedStateVariable>AbsoluteCounterPosition</relatedStateVariable>
        </argument>
      </argumentList>
    </action>
  </actionList>
  <serviceStateTable>
    <stateVariable sendEvents="no">
      <name>A_ARG_TYPE_InstanceID</name>
      <dataType>ui4</dataType>
    </stateVariable>
    <stateVariable sendEvents="no">
      <name>AVTransportURI</name>
      <dataType>string</dataType>
    </stateVariable>
    <stateVariable sendEvents="no">
      <name>AVTransportURIMetaData</name>
      <dataType>string</dataType>
    </stateVariable>
    <stateVariable sendEvents="yes">
      <name>TransportState</name>
      <dataType>string</dataType>
      <allowedValueList>
        <allowedValue>STOPPED</allowedValue>
        <allowedValue>PLAYING</allowedValue>
        <allowedValue>PAUSED_PLAYBACK</allowedValue>
        <allowedValue>TRANSITIONING</allowedValue>
      </allowedValueList>
    </stateVariable>
    <stateVariable sendEvents="yes">
      <name>TransportStatus</name>
      <dataType>string</dataType>
      <allowedValueList>
        <allowedValue>OK</allowedValue>
        <allowedValue>ERROR_OCCURRED</allowedValue>
      </allowedValueList>
    </stateVariable>
    <stateVariable sendEvents="no">
      <name>TransportPlaySpeed</name>
      <dataType>string</dataType>
      <defaultValue>1</defaultValue>
    </stateVariable>
    <stateVariable sendEvents="no">
      <name>CurrentTrack</name>
      <dataType>ui4</dataType>
      <defaultValue>0</defaultValue>
    </stateVariable>
    <stateVariable sendEvents="no">
      <name>CurrentTrackDuration</name>
      <dataType>string</dataType>
      <defaultValue>00:00:00</defaultValue>
    </stateVariable>
    <stateVariable sendEvents="no">
      <name>CurrentTrackMetaData</name>
      <dataType>string</dataType>
    </stateVariable>
    <stateVariable sendEvents="no">
      <name>CurrentTrackURI</name>
      <dataType>string</dataType>
    </stateVariable>
    <stateVariable sendEvents="no">
      <name>RelativeTimePosition</name>
      <dataType>string</dataType>
      <defaultValue>00:00:00</defaultValue>
    </stateVariable>
    <stateVariable sendEvents="no">
      <name>AbsoluteTimePosition</name>
      <dataType>string</dataType>
      <defaultValue>00:00:00</defaultValue>
    </stateVariable>
    <stateVariable sendEvents="no">
      <name>RelativeCounterPosition</name>
      <dataType>i4</dataType>
    </stateVariable>
    <stateVariable sendEvents="no">
      <name>AbsoluteCounterPosition</name>
      <dataType>i4</dataType>
    </stateVariable>
    <stateVariable sendEvents="no">
      <name>A_ARG_TYPE_SeekMode</name>
      <dataType>string</dataType>
      <allowedValueList>
        <allowedValue>ABS_TIME</allowedValue>
        <allowedValue>REL_TIME</allowedValue>
      </allowedValueList>
    </stateVariable>
    <stateVariable sendEvents="no">
      <name>A_ARG_TYPE_SeekTarget</name>
      <dataType>string</dataType>
    </stateVariable>
  </serviceStateTable>
</scpd>'''


def generate_rendering_control_scpd() -> str:
    """Generate RenderingControl service description"""
    return '''<?xml version="1.0" encoding="utf-8"?>
<scpd xmlns="urn:schemas-upnp-org:service-1-0">
  <specVersion>
    <major>1</major>
    <minor>0</minor>
  </specVersion>
  <actionList>
    <action>
      <name>GetVolume</name>
      <argumentList>
        <argument>
          <name>InstanceID</name>
          <direction>in</direction>
          <relatedStateVariable>A_ARG_TYPE_InstanceID</relatedStateVariable>
        </argument>
        <argument>
          <name>Channel</name>
          <direction>in</direction>
          <relatedStateVariable>A_ARG_TYPE_Channel</relatedStateVariable>
        </argument>
        <argument>
          <name>CurrentVolume</name>
          <direction>out</direction>
          <relatedStateVariable>Volume</relatedStateVariable>
        </argument>
      </argumentList>
    </action>
    <action>
      <name>SetVolume</name>
      <argumentList>
        <argument>
          <name>InstanceID</name>
          <direction>in</direction>
          <relatedStateVariable>A_ARG_TYPE_InstanceID</relatedStateVariable>
        </argument>
        <argument>
          <name>Channel</name>
          <direction>in</direction>
          <relatedStateVariable>A_ARG_TYPE_Channel</relatedStateVariable>
        </argument>
        <argument>
          <name>DesiredVolume</name>
          <direction>in</direction>
          <relatedStateVariable>Volume</relatedStateVariable>
        </argument>
      </argumentList>
    </action>
    <action>
      <name>GetMute</name>
      <argumentList>
        <argument>
          <name>InstanceID</name>
          <direction>in</direction>
          <relatedStateVariable>A_ARG_TYPE_InstanceID</relatedStateVariable>
        </argument>
        <argument>
          <name>Channel</name>
          <direction>in</direction>
          <relatedStateVariable>A_ARG_TYPE_Channel</relatedStateVariable>
        </argument>
        <argument>
          <name>CurrentMute</name>
          <direction>out</direction>
          <relatedStateVariable>Mute</relatedStateVariable>
        </argument>
      </argumentList>
    </action>
    <action>
      <name>SetMute</name>
      <argumentList>
        <argument>
          <name>InstanceID</name>
          <direction>in</direction>
          <relatedStateVariable>A_ARG_TYPE_InstanceID</relatedStateVariable>
        </argument>
        <argument>
          <name>Channel</name>
          <direction>in</direction>
          <relatedStateVariable>A_ARG_TYPE_Channel</relatedStateVariable>
        </argument>
        <argument>
          <name>DesiredMute</name>
          <direction>in</direction>
          <relatedStateVariable>Mute</relatedStateVariable>
        </argument>
      </argumentList>
    </action>
  </actionList>
  <serviceStateTable>
    <stateVariable sendEvents="no">
      <name>A_ARG_TYPE_InstanceID</name>
      <dataType>ui4</dataType>
    </stateVariable>
    <stateVariable sendEvents="no">
      <name>A_ARG_TYPE_Channel</name>
      <dataType>string</dataType>
      <allowedValueList>
        <allowedValue>Master</allowedValue>
      </allowedValueList>
    </stateVariable>
    <stateVariable sendEvents="yes">
      <name>Volume</name>
      <dataType>ui2</dataType>
      <allowedValueRange>
        <minimum>0</minimum>
        <maximum>100</maximum>
        <step>1</step>
      </allowedValueRange>
    </stateVariable>
    <stateVariable sendEvents="yes">
      <name>Mute</name>
      <dataType>boolean</dataType>
    </stateVariable>
  </serviceStateTable>
</scpd>'''


def generate_connection_manager_scpd() -> str:
    """Generate ConnectionManager service description"""
    return '''<?xml version="1.0" encoding="utf-8"?>
<scpd xmlns="urn:schemas-upnp-org:service-1-0">
  <specVersion>
    <major>1</major>
    <minor>0</minor>
  </specVersion>
  <actionList>
    <action>
      <name>GetProtocolInfo</name>
      <argumentList>
        <argument>
          <name>Source</name>
          <direction>out</direction>
          <relatedStateVariable>SourceProtocolInfo</relatedStateVariable>
        </argument>
        <argument>
          <name>Sink</name>
          <direction>out</direction>
          <relatedStateVariable>SinkProtocolInfo</relatedStateVariable>
        </argument>
      </argumentList>
    </action>
    <action>
      <name>GetCurrentConnectionIDs</name>
      <argumentList>
        <argument>
          <name>ConnectionIDs</name>
          <direction>out</direction>
          <relatedStateVariable>CurrentConnectionIDs</relatedStateVariable>
        </argument>
      </argumentList>
    </action>
    <action>
      <name>GetCurrentConnectionInfo</name>
      <argumentList>
        <argument>
          <name>ConnectionID</name>
          <direction>in</direction>
          <relatedStateVariable>A_ARG_TYPE_ConnectionID</relatedStateVariable>
        </argument>
        <argument>
          <name>RcsID</name>
          <direction>out</direction>
          <relatedStateVariable>A_ARG_TYPE_RcsID</relatedStateVariable>
        </argument>
        <argument>
          <name>AVTransportID</name>
          <direction>out</direction>
          <relatedStateVariable>A_ARG_TYPE_AVTransportID</relatedStateVariable>
        </argument>
        <argument>
          <name>ProtocolInfo</name>
          <direction>out</direction>
          <relatedStateVariable>A_ARG_TYPE_ProtocolInfo</relatedStateVariable>
        </argument>
        <argument>
          <name>PeerConnectionManager</name>
          <direction>out</direction>
          <relatedStateVariable>A_ARG_TYPE_ConnectionManager</relatedStateVariable>
        </argument>
        <argument>
          <name>PeerConnectionID</name>
          <direction>out</direction>
          <relatedStateVariable>A_ARG_TYPE_ConnectionID</relatedStateVariable>
        </argument>
        <argument>
          <name>Direction</name>
          <direction>out</direction>
          <relatedStateVariable>A_ARG_TYPE_Direction</relatedStateVariable>
        </argument>
        <argument>
          <name>Status</name>
          <direction>out</direction>
          <relatedStateVariable>A_ARG_TYPE_ConnectionStatus</relatedStateVariable>
        </argument>
      </argumentList>
    </action>
  </actionList>
  <serviceStateTable>
    <stateVariable sendEvents="yes">
      <name>SourceProtocolInfo</name>
      <dataType>string</dataType>
    </stateVariable>
    <stateVariable sendEvents="yes">
      <name>SinkProtocolInfo</name>
      <dataType>string</dataType>
    </stateVariable>
    <stateVariable sendEvents="yes">
      <name>CurrentConnectionIDs</name>
      <dataType>string</dataType>
      <defaultValue>0</defaultValue>
    </stateVariable>
    <stateVariable sendEvents="no">
      <name>A_ARG_TYPE_ConnectionID</name>
      <dataType>i4</dataType>
    </stateVariable>
    <stateVariable sendEvents="no">
      <name>A_ARG_TYPE_RcsID</name>
      <dataType>i4</dataType>
    </stateVariable>
    <stateVariable sendEvents="no">
      <name>A_ARG_TYPE_AVTransportID</name>
      <dataType>i4</dataType>
    </stateVariable>
    <stateVariable sendEvents="no">
      <name>A_ARG_TYPE_ProtocolInfo</name>
      <dataType>string</dataType>
    </stateVariable>
    <stateVariable sendEvents="no">
      <name>A_ARG_TYPE_ConnectionManager</name>
      <dataType>string</dataType>
    </stateVariable>
    <stateVariable sendEvents="no">
      <name>A_ARG_TYPE_Direction</name>
      <dataType>string</dataType>
      <allowedValueList>
        <allowedValue>Input</allowedValue>
        <allowedValue>Output</allowedValue>
      </allowedValueList>
    </stateVariable>
    <stateVariable sendEvents="no">
      <name>A_ARG_TYPE_ConnectionStatus</name>
      <dataType>string</dataType>
      <allowedValueList>
        <allowedValue>OK</allowedValue>
        <allowedValue>ContentFormatMismatch</allowedValue>
        <allowedValue>InsufficientBandwidth</allowedValue>
        <allowedValue>UnreliableChannel</allowedValue>
        <allowedValue>Unknown</allowedValue>
      </allowedValueList>
    </stateVariable>
  </serviceStateTable>
</scpd>'''
