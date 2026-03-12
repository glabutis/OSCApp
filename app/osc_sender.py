"""OSC UDP sender wrapping python-osc."""

import socket
from typing import Any, List

from pythonosc import udp_client


class OSCSender:
    def __init__(self, host: str = "127.0.0.1", port: int = 3333) -> None:
        self._host = host
        self._port = port
        self._client: udp_client.SimpleUDPClient | None = None
        self._connect()

    # ── Public API ───────────────────────────────────────────────────────────

    def update(self, host: str, port: int) -> None:
        """Update destination and reconnect."""
        self._host = host
        self._port = port
        self._connect()

    def send(self, address: str, args_str: str = "") -> tuple[bool, str]:
        """
        Send an OSC message.

        Returns ``(success, error_message)``.
        """
        if not self._client:
            return False, "No client configured"
        if not address or not address.startswith("/"):
            return False, f"Invalid OSC address: {address!r}"
        try:
            args = _parse_args(args_str)
            self._client.send_message(address, args if args else None)
            return True, ""
        except Exception as exc:
            return False, str(exc)

    @property
    def host(self) -> str:
        return self._host

    @property
    def port(self) -> int:
        return self._port

    # ── Internal ─────────────────────────────────────────────────────────────

    def _connect(self) -> None:
        try:
            self._client = udp_client.SimpleUDPClient(self._host, self._port)
        except Exception:
            self._client = None


def _parse_args(args_str: str) -> List[Any]:
    """
    Parse a space-separated argument string into typed Python values.

    Tries int → float → string for each token.  Quoted strings are
    supported, e.g. ``"hello world"`` counts as one token.
    """
    if not args_str.strip():
        return []

    tokens = _tokenize(args_str)
    result = []
    for token in tokens:
        # Integer?
        try:
            result.append(int(token))
            continue
        except ValueError:
            pass
        # Float?
        try:
            result.append(float(token))
            continue
        except ValueError:
            pass
        # String (strip surrounding quotes)
        if len(token) >= 2 and token[0] in ('"', "'") and token[-1] == token[0]:
            token = token[1:-1]
        result.append(token)

    return result


def _tokenize(s: str) -> List[str]:
    """Split respecting double/single-quoted tokens."""
    tokens = []
    current = []
    in_quote = None
    for ch in s:
        if in_quote:
            if ch == in_quote:
                in_quote = None
                current.append(ch)
            else:
                current.append(ch)
        elif ch in ('"', "'"):
            in_quote = ch
            current.append(ch)
        elif ch == " ":
            if current:
                tokens.append("".join(current))
                current = []
        else:
            current.append(ch)
    if current:
        tokens.append("".join(current))
    return tokens
