"""
Mezon SDK Test Suite

Comprehensive tests for all SDK features organized into submodules.
"""

from tests.base import BaseTestSuite, TestConfig
from tests.test_messages import MessageTests
from tests.test_mentions import MentionTests
from tests.test_buzz import BuzzTests
from tests.test_interactive import InteractiveTests
from tests.test_users import UserTests
from tests.test_clans import ClanTests
from tests.test_binary_api import BinaryApiTests
from tests.test_session import SessionTests
from tests.test_friends import FriendTests
from tests.test_quick_menu import QuickMenuTests
from tests.test_streaming import StreamingTests
from tests.test_tokens import TokenTests
from tests.test_health import HealthTests

__all__ = [
    "BaseTestSuite",
    "TestConfig",
    "MessageTests",
    "MentionTests",
    "BuzzTests",
    "InteractiveTests",
    "UserTests",
    "ClanTests",
    "BinaryApiTests",
    "SessionTests",
    "FriendTests",
    "QuickMenuTests",
    "StreamingTests",
    "TokenTests",
    "HealthTests",
]
