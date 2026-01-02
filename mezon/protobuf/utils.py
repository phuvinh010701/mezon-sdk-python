from typing import Type, Any
from mezon.protobuf.rtapi import realtime_pb2

def parse_protobuf(message: bytes) -> realtime_pb2.Envelope:
    """Parse bytes message to envelope."""
    envelope = realtime_pb2.Envelope()
    envelope.ParseFromString(message)
    return envelope

def encode_protobuf(envelope: realtime_pb2.Envelope) -> bytes:
    """Encode envelope to bytes."""
    return envelope.SerializeToString()

def parse_api_protobuf(data: bytes, message_class: Type) -> Any:
    """Parse binary API response to specific protobuf message type.

    Args:
        data: Binary protobuf data
        message_class: Protobuf message class to parse into

    Returns:
        Parsed protobuf message instance
    """
    message = message_class()
    message.ParseFromString(data)
    return message

NEOF_NAME = "message"  # from Envelope.WhichOneof signature