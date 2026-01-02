"""
Main test runner for Mezon SDK comprehensive test suite.

Usage:
    python -m tests.test_runner

Or import and run programmatically:
    from tests.test_runner import run_all_tests
    asyncio.run(run_all_tests(config))

Environment Variables:
    MEZON_CLIENT_ID: Bot client ID (required)
    MEZON_API_KEY: Bot API key (required)
    MEZON_CLAN_ID: Test clan ID (required)
    MEZON_CHANNEL_ID: Test channel ID (required)
    MEZON_USER_ID: Test user ID (required)
    MEZON_VOICE_CHANNEL_ID: Voice channel ID (optional)
    MEZON_ROLE_ID: Role ID (optional)
    MEZON_TOKEN_RECEIVER_ID: Token receiver user ID (optional)
    MEZON_FRIEND_USERNAME: Friend username for tests (optional)
"""

import asyncio
import logging
import os
import time
from typing import Optional

from mezon import MezonClient

from tests.base import TestConfig, TestResults, print_test_summary
from tests.test_binary_api import BinaryApiTests
from tests.test_clans import ClanTests
from tests.test_friends import FriendTests
from tests.test_health import HealthTests
from tests.test_interactive import InteractiveTests
from tests.test_messages import MessageTests
from tests.test_quick_menu import QuickMenuTests
from tests.test_session import SessionTests
from tests.test_streaming import StreamingTests
from tests.test_tokens import TokenTests
from tests.test_users import UserTests


# ============================================================================
# CONFIGURATION - Set via environment variables
# ============================================================================


def get_config_from_env() -> TestConfig:
    """
    Load test configuration from environment variables.

    Returns:
        TestConfig: Configuration loaded from environment

    Raises:
        ValueError: If required environment variables are missing
    """
    client_id = os.getenv("MEZON_CLIENT_ID")
    api_key = os.getenv("MEZON_API_KEY")
    clan_id = os.getenv("MEZON_CLAN_ID")
    channel_id = os.getenv("MEZON_CHANNEL_ID")
    user_id = os.getenv("MEZON_USER_ID")

    missing = []
    if not client_id:
        missing.append("MEZON_CLIENT_ID")
    if not api_key:
        missing.append("MEZON_API_KEY")
    if not clan_id:
        missing.append("MEZON_CLAN_ID")
    if not channel_id:
        missing.append("MEZON_CHANNEL_ID")
    if not user_id:
        missing.append("MEZON_USER_ID")

    if missing:
        raise ValueError(
            f"Missing required environment variables: {', '.join(missing)}\n"
            "Please set them before running tests:\n"
            "  export MEZON_CLIENT_ID=your_client_id\n"
            "  export MEZON_API_KEY=your_api_key\n"
            "  export MEZON_CLAN_ID=your_clan_id\n"
            "  export MEZON_CHANNEL_ID=your_channel_id\n"
            "  export MEZON_USER_ID=your_user_id"
        )

    return TestConfig(
        client_id=client_id,
        api_key=api_key,
        clan_id=clan_id,
        channel_id=channel_id,
        user_id=user_id,
        voice_channel_id=os.getenv("MEZON_VOICE_CHANNEL_ID"),
        role_id=os.getenv("MEZON_ROLE_ID"),
        token_receiver_id=os.getenv("MEZON_TOKEN_RECEIVER_ID"),
        friend_username=os.getenv("MEZON_FRIEND_USERNAME"),
    )


async def run_all_tests(
    config: Optional[TestConfig] = None,
    log_level: int = logging.DEBUG,
    enable_logging: bool = True,
) -> TestResults:
    """
    Run comprehensive test suite.

    Args:
        config (Optional[TestConfig]): Test configuration, loads from env if None
        log_level (int): Logging level
        enable_logging (bool): Whether to enable logging

    Returns:
        TestResults: Results of all tests
    """
    if config is None:
        config = get_config_from_env()

    results = TestResults()
    start_time = time.time()

    # Initialize client
    client = MezonClient(
        client_id=config.client_id,
        api_key=config.api_key,
        enable_logging=enable_logging,
        log_level=log_level,
    )

    try:
        # Setup
        print("\n" + "=" * 80)
        print("MEZON SDK COMPREHENSIVE TEST SUITE")
        print("=" * 80)

        await client.login(enable_auto_reconnect=True)
        await asyncio.sleep(3)  # Wait for clans to load

        session = await client.get_session()
        print(f"✓ Logged in as: {session.user_id}")
        print("✓ Rate limiter active: 1 request per 1.5 seconds")

        # Create test suite instances
        test_suites = [
            ("MESSAGE OPERATIONS", MessageTests(client, config, results)),
            ("INTERACTIVE UI", InteractiveTests(client, config, results)),
            ("USER OPERATIONS", UserTests(client, config, results)),
            ("CLAN OPERATIONS", ClanTests(client, config, results)),
            ("BINARY API", BinaryApiTests(client, config, results)),
            ("SESSION MANAGEMENT", SessionTests(client, config, results)),
            ("FRIEND OPERATIONS", FriendTests(client, config, results)),
            ("QUICK MENU", QuickMenuTests(client, config, results)),
            ("STREAMING", StreamingTests(client, config, results)),
            ("TOKEN TRANSFERS", TokenTests(client, config, results)),
            ("HEALTH CHECKS", HealthTests(client, config, results)),
        ]

        # Run all test suites
        for suite_name, suite in test_suites:
            print(f"\n{'─' * 40}")
            print(f"📋 {suite_name}")
            print(f"{'─' * 40}")
            await suite.run_all()

        # Print summary
        print_test_summary(results, start_time)

    except KeyboardInterrupt:
        print("\n⚠️  Interrupted by user")
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        import traceback

        traceback.print_exc()
    finally:
        await client.close_socket()

    return results


def main():
    """Entry point for running tests from command line."""
    print(
        """
╔══════════════════════════════════════════════════════════════════════════════╗
║                   MEZON SDK COMPREHENSIVE TEST SUITE                         ║
║                                                                              ║
║  Tests ALL features including:                                               ║
║  • Messages (send, edit, delete, react, reply, ephemeral, attachments)       ║
║  • Interactive UI (buttons, embeds, forms, multi-row)                        ║
║  • Users & DM (fetch, send DM, cache)                                        ║
║  • Clans (channels, roles, voice, cache)                                     ║
║  • Binary API (protobuf vs JSON, performance comparison)                     ║
║  • Session (get, refresh, properties, serialization)                         ║
║  • Friends (list, add, accept, pagination)                                   ║
║  • Quick Menu (add, delete)                                                  ║
║  • Streaming (register channel)                                              ║
║  • Tokens (send, transaction detail)                                         ║
║  • Health (healthcheck, readycheck)                                          ║
║                                                                              ║
║  Required environment variables:                                             ║
║    MEZON_CLIENT_ID, MEZON_API_KEY, MEZON_CLAN_ID,                            ║
║    MEZON_CHANNEL_ID, MEZON_USER_ID                                           ║
║                                                                              ║
║  Optional environment variables:                                             ║
║    MEZON_VOICE_CHANNEL_ID, MEZON_ROLE_ID,                                    ║
║    MEZON_TOKEN_RECEIVER_ID, MEZON_FRIEND_USERNAME                            ║
╚══════════════════════════════════════════════════════════════════════════════╝
    """
    )

    asyncio.run(run_all_tests())


if __name__ == "__main__":
    main()

