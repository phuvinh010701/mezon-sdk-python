"""
Unit tests for mention index (s/e) computation.

The `s` field is the start character index of `@mention` within the message text.
The `e` field is the end character index (exclusive: index of char after the last
character of the username).

Reference semantics (matching the JS SDK):
    text[s:e] == f"@{username}"
"""

from mezon.models import ApiMessageMention
from tests.helpers import compute_mention_indices


class TestMentionIndices:
    """Unit tests for correct mention start/end index computation."""

    def test_single_mention_at_start(self) -> None:
        """@user at position 0: s=0, e=len('@user')."""
        username = "Alice"
        text = f"@{username} Hello there"
        s, e = compute_mention_indices(text, f"@{username}")
        assert s == 0
        assert e == len(username) + 1  # +1 for '@'
        assert text[s:e] == f"@{username}"

    def test_mention_creates_correct_model(self) -> None:
        """ApiMessageMention stores computed indices correctly."""
        username = "Alice"
        text = f"@{username} Test mention"
        s, e = compute_mention_indices(text, f"@{username}")
        mention = ApiMessageMention(username=username, s=s, e=e)
        assert mention.s == 0
        assert mention.e == len(username) + 1
        assert text[mention.s : mention.e] == f"@{username}"

    def test_second_mention_indices_are_correct(self) -> None:
        """
        When two mentions appear in a message the second mention's s must be
        greater than the first mention's e, and s < e always.
        """
        user1 = "Alice"
        user2 = "Bob"
        text = f"@{user1} Hey! @{user2} Multiple mentions test"

        s1, e1 = compute_mention_indices(text, f"@{user1}")
        s2, e2 = compute_mention_indices(text, f"@{user2}")

        # Basic slice correctness
        assert text[s1:e1] == f"@{user1}"
        assert text[s2:e2] == f"@{user2}"

        # Order invariants
        assert s1 < e1, "start must be before end for mention 1"
        assert s2 < e2, "start must be before end for mention 2"
        assert e1 < s2, "mention 2 must start after mention 1 ends"

    def test_second_mention_exact_values(self) -> None:
        """
        Regression: old code used s=len(u1)+len(u2)+6, e=len(u2)+6 which gives s > e.
        Correct: s = len('@user1') + len(' Hey! '), e = s + len('@user2').
        """
        user1 = "Alice"
        user2 = "Bob"
        separator = " Hey! "
        text = f"@{user1}{separator}@{user2} Multiple mentions test"

        # Correct values
        expected_s2 = len(f"@{user1}") + len(separator)
        expected_e2 = expected_s2 + len(f"@{user2}")

        s2, e2 = compute_mention_indices(text, f"@{user2}")

        assert s2 == expected_s2
        assert e2 == expected_e2
        assert text[s2:e2] == f"@{user2}"

    def test_buggy_formula_vs_correct_formula(self) -> None:
        """
        Regression: old formula gives s > e (invalid); new formula gives s < e (valid).

        Old (buggy):  s = len(u1) + len(u2) + 6,  e = len(u2) + 6  →  s > e ✗
        New (correct): s = text.index("@u2"),       e = s + len("@u2")  →  s < e ✓
        """
        user1 = "Alice"
        user2 = "Bob"
        separator = " Hey! "
        text = f"@{user1}{separator}@{user2} Multiple mentions test"

        # Old buggy formula
        s_buggy = len(user1) + len(user2) + 6
        e_buggy = len(user2) + 6
        assert s_buggy > e_buggy, "Old formula must produce invalid s > e"

        # New correct formula via helper
        s_new, e_new = compute_mention_indices(text, f"@{user2}")
        assert s_new < e_new, "New formula must produce valid s < e"
        assert text[s_new:e_new] == f"@{user2}", (
            "New formula must slice the correct token"
        )

    def test_role_mention_indices(self) -> None:
        """Role mentions follow the same s/e semantics."""
        rolename = "Dev"
        text = f"@{rolename} Test role mention"
        s, e = compute_mention_indices(text, f"@{rolename}")
        assert s == 0
        assert e == len(rolename) + 1
        assert text[s:e] == f"@{rolename}"

    def test_mention_not_at_start_of_text(self) -> None:
        """Mention embedded mid-sentence has a non-zero start index."""
        username = "Charlie"
        prefix = "Hello "
        text = f"{prefix}@{username} nice to meet you"
        s, e = compute_mention_indices(text, f"@{username}")
        assert s == len(prefix)
        assert e == len(prefix) + len(username) + 1
        assert text[s:e] == f"@{username}"
