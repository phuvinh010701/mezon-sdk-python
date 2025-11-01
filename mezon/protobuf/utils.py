from mezon.protobuf.rtapi import realtime_pb2

def parse_protobuf(message: bytes) -> realtime_pb2.Envelope:
    """Parse bytes message to envelope."""
    envelope = realtime_pb2.Envelope()
    envelope.ParseFromString(message)
    return envelope

def encode_protobuf(envelope: realtime_pb2.Envelope) -> bytes:
    """Encode envelope to bytes."""
    return envelope.SerializeToString()

NEOF_NAME = "message"  # from Envelope.WhichOneof signature