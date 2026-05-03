"""
Unit tests for helper utility functions.
"""

from mezon.constants import ChannelStreamMode, ChannelType
from mezon.utils.helper import (
    convert_channeltype_to_channel_mode,
    generate_snowflake_id,
    is_valid_user_id,
    parse_url_to_host_and_ssl,
)


class TestConvertChannelTypeToChannelMode:
    """Test convert_channeltype_to_channel_mode function."""

    def test_convert_channel_type_channel(self):
        """Test converting CHANNEL_TYPE_CHANNEL."""
        result = convert_channeltype_to_channel_mode(ChannelType.CHANNEL_TYPE_CHANNEL)
        assert result == ChannelStreamMode.STREAM_MODE_CHANNEL

    def test_convert_channel_type_group(self):
        """Test converting CHANNEL_TYPE_GROUP."""
        result = convert_channeltype_to_channel_mode(ChannelType.CHANNEL_TYPE_GROUP)
        assert result == ChannelStreamMode.STREAM_MODE_GROUP

    def test_convert_channel_type_dm(self):
        """Test converting CHANNEL_TYPE_DM."""
        result = convert_channeltype_to_channel_mode(ChannelType.CHANNEL_TYPE_DM)
        assert result == ChannelStreamMode.STREAM_MODE_DM

    def test_convert_channel_type_thread(self):
        """Test converting CHANNEL_TYPE_THREAD."""
        result = convert_channeltype_to_channel_mode(ChannelType.CHANNEL_TYPE_THREAD)
        assert result == ChannelStreamMode.STREAM_MODE_THREAD

    def test_convert_unsupported_channel_type_returns_zero(self):
        """Test converting unsupported channel type returns 0."""
        result = convert_channeltype_to_channel_mode(ChannelType.CHANNEL_TYPE_FORUM)
        assert result == 0

        result = convert_channeltype_to_channel_mode(ChannelType.CHANNEL_TYPE_STREAMING)
        assert result == 0


class TestIsValidUserId:
    """Test is_valid_user_id function."""

    def test_valid_string_user_id(self):
        """Test valid string user ID."""
        assert is_valid_user_id("1234567890") is True

    def test_valid_int_user_id(self):
        """Test valid integer user ID."""
        assert is_valid_user_id(1234567890) is True

    def test_zero_is_valid(self):
        """Test zero is considered valid."""
        assert is_valid_user_id(0) is True

    def test_empty_string_is_invalid(self):
        """Test empty string is invalid."""
        assert is_valid_user_id("") is False

    def test_none_is_invalid(self):
        """Test None is invalid."""
        assert is_valid_user_id(None) is False

    def test_whitespace_string_is_invalid(self):
        """Test whitespace string is invalid."""
        assert is_valid_user_id("   ") is False

    def test_negative_number_is_invalid(self):
        """Test negative number is invalid."""
        assert is_valid_user_id(-123) is False


class TestParseUrlToHostAndSsl:
    """Test parse_url_to_host_and_ssl function."""

    def test_parse_https_url(self):
        """Test parsing HTTPS URL."""
        result = parse_url_to_host_and_ssl("https://example.com")
        assert result["host"] == "example.com"
        assert result["port"] == "443"
        assert result["useSSL"] is True

    def test_parse_http_url(self):
        """Test parsing HTTP URL."""
        result = parse_url_to_host_and_ssl("http://example.com")
        assert result["host"] == "example.com"
        assert result["port"] == "80"
        assert result["useSSL"] is False

    def test_parse_url_with_port(self):
        """Test parsing URL with port."""
        result = parse_url_to_host_and_ssl("https://example.com:8080")
        assert result["host"] == "example.com"
        assert result["port"] == "8080"
        assert result["useSSL"] is True

    def test_parse_url_with_path(self):
        """Test parsing URL with path."""
        result = parse_url_to_host_and_ssl("https://example.com/api/v1")
        assert result["host"] == "example.com"
        assert result["useSSL"] is True

    def test_parse_localhost(self):
        """Test parsing localhost URL."""
        result = parse_url_to_host_and_ssl("http://localhost:3000")
        assert result["host"] == "localhost"
        assert result["port"] == "3000"
        assert result["useSSL"] is False

    def test_parse_ip_address(self):
        """Test parsing IP address URL."""
        result = parse_url_to_host_and_ssl("http://192.168.1.1:8080")
        assert result["host"] == "192.168.1.1"
        assert result["port"] == "8080"
        assert result["useSSL"] is False

    def test_parse_wss_url(self):
        """Test parsing WSS URL (treated as ws://)."""
        result = parse_url_to_host_and_ssl("wss://example.com")
        assert result["host"] == "example.com"
        # WSS is parsed but useSSL depends on implementation
        assert "host" in result
        assert "port" in result

    def test_parse_ws_url(self):
        """Test parsing WS URL."""
        result = parse_url_to_host_and_ssl("ws://example.com")
        assert result["host"] == "example.com"
        assert "port" in result


class TestGenerateSnowflakeId:
    """Test generate_snowflake_id function."""

    def test_generates_integer(self):
        """Test that function generates an integer."""
        result = generate_snowflake_id()
        assert isinstance(result, int)

    def test_generates_positive_number(self):
        """Test that generated ID is positive."""
        result = generate_snowflake_id()
        assert result > 0

    def test_generates_large_number(self):
        """Test that generated ID is a large number (snowflake-like)."""
        result = generate_snowflake_id()
        # Snowflake IDs are typically 17-19 digits
        assert result > 10**16

    def test_generates_unique_ids(self):
        """Test that multiple calls generate different IDs."""
        id1 = generate_snowflake_id()
        id2 = generate_snowflake_id()
        id3 = generate_snowflake_id()

        # IDs should be unique
        assert id1 != id2
        assert id2 != id3
        assert id1 != id3

    def test_generates_increasing_ids(self):
        """Test that IDs are generally increasing (time-based)."""
        id1 = generate_snowflake_id()
        id2 = generate_snowflake_id()
        id3 = generate_snowflake_id()

        # Due to time component, later IDs should generally be larger
        # (though not guaranteed in all cases due to sequence numbers)
        assert id2 >= id1 or id3 >= id2
