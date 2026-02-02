"""
Base test utilities and configuration for Mezon SDK tests.
"""

import logging
import time
from dataclasses import dataclass, field
from typing import List, Optional, Tuple

from mezon import MezonClient


@dataclass
class TestConfig:
    """
    Configuration for test suite.

    Args:
        client_id (str): Bot client ID
        api_key (str): Bot API key
        clan_id (int): Test clan ID
        channel_id (int): Test text channel ID
        user_id (int): Test user ID for interactions
        voice_channel_id (Optional[int]): Test voice channel ID
        role_id (Optional[int]): Test role ID
        token_receiver_id (Optional[int]): User ID for token transfers
    """

    client_id: str
    api_key: str
    clan_id: int
    channel_id: int
    user_id: int
    user_name: str
    user_id_2: int
    user_name_2: str
    voice_channel_id: Optional[int] = None
    role_id: Optional[int] = None
    token_receiver_id: Optional[int] = None


@dataclass
class TestResults:
    """
    Container for test results.

    Args:
        passed (List[str]): Names of passed tests
        failed (List[Tuple[str, str]]): Names and errors of failed tests
        skipped (List[Tuple[str, str]]): Names and reasons for skipped tests
    """

    passed: List[str] = field(default_factory=list)
    failed: List[Tuple[str, str]] = field(default_factory=list)
    skipped: List[Tuple[str, str]] = field(default_factory=list)


class BaseTestSuite:
    """
    Base class for test suites with shared functionality.

    Args:
        client (MezonClient): Initialized Mezon client
        config (TestConfig): Test configuration
        results (TestResults): Shared test results container
    """

    def __init__(
        self,
        client: MezonClient,
        config: TestConfig,
        results: TestResults,
    ):
        self.client = client
        self.config = config
        self.results = results
        self.logger = logging.getLogger(self.__class__.__name__)

    def log_result(self, name: str, success: bool, error: Optional[str] = None) -> None:
        """
        Log test result.

        Args:
            name (str): Test name
            success (bool): Whether test passed
            error (Optional[str]): Error message if failed
        """
        if success:
            self.results.passed.append(name)
            print(f"✓ {name}")
        else:
            self.results.failed.append((name, error or "Unknown error"))
            print(f"✗ {name}: {error}")

    def skip_test(self, name: str, reason: str) -> None:
        """
        Mark test as skipped.

        Args:
            name (str): Test name
            reason (str): Reason for skipping
        """
        self.results.skipped.append((name, reason))
        print(f"⊘ {name}: {reason}")

    async def run_all(self) -> None:
        """Run all tests in this suite. Override in subclasses."""
        raise NotImplementedError("Subclasses must implement run_all()")


def print_test_summary(results: TestResults, start_time: float) -> None:
    """
    Print comprehensive test summary.

    Args:
        results (TestResults): Test results to summarize
        start_time (float): Test start timestamp
    """
    print("\n" + "=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)

    total = len(results.passed) + len(results.failed) + len(results.skipped)
    passed = len(results.passed)
    failed = len(results.failed)
    skipped = len(results.skipped)

    elapsed_time = time.time() - start_time

    print(f"\nTotal Time: {elapsed_time:.2f} seconds")
    print(f"Total: {total} | Passed: {passed} | Failed: {failed} | Skipped: {skipped}")
    print("\n⏱️  Rate Limiter: All API calls are limited to 1 request per 1.5 seconds")

    if results.passed:
        print("\n✓ PASSED:")
        for test in results.passed:
            print(f"  - {test}")

    if results.failed:
        print("\n✗ FAILED:")
        for test, error in results.failed:
            print(f"  - {test}: {error}")

    if results.skipped:
        print("\n⊘ SKIPPED:")
        for test, reason in results.skipped:
            print(f"  - {test}: {reason}")

    print("\n" + "=" * 80)
    if failed == 0:
        print("🎉 ALL TESTS PASSED!")
    else:
        print(f"⚠️  {failed} test(s) failed")
    print("=" * 80)
