"""
Shared test helpers for the Mezon SDK test suite.
"""


def compute_mention_indices(text: str, at_name: str) -> tuple[int, int]:
    """
    Compute the start (s) and end (e) character indices for a mention in a text.

    The Mezon platform uses these indices to identify and highlight mention tokens
    in message text.  The convention (matching the JS SDK) is:

        text[s:e] == at_name   (e.g. "@Alice")

    ``s`` is the 0-based inclusive start index; ``e`` is the exclusive end index
    (past-the-end), so ``e - s == len(at_name)``.

    Args:
        text: The full message text.
        at_name: The mention token including the leading ``@`` (e.g. ``"@Alice"``).

    Returns:
        A ``(s, e)`` tuple such that ``text[s:e] == at_name``.

    Raises:
        ValueError: If *at_name* is not found in *text*.
    """
    s = text.index(at_name)
    e = s + len(at_name)
    return s, e
