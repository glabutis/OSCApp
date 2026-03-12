"""
Global keyboard listener with short/long press detection.

Threading model:
- pynput runs its listener in a background thread.
- Key action callbacks are invoked from that background thread.
- Callers (e.g. MainWindow) are responsible for marshalling to the Qt main
  thread via Qt signals.
"""

import sys
import threading
import time
from typing import Callable, Optional

from pynput import keyboard

from .key_utils import key_to_str


class InputListener:
    """
    Listens globally for keyboard events and fires callbacks for short/long
    press detection.

    Typical usage::

        listener = InputListener()
        listener.set_threshold(500)
        listener.set_action_callback(lambda key, ptype: print(key, ptype))
        listener.start()
    """

    def __init__(self) -> None:
        self._threshold: float = 0.5        # seconds
        self._action_cb: Optional[Callable] = None
        self._listener: Optional[keyboard.Listener] = None
        self._lock = threading.Lock()
        self._pressed: dict = {}            # key_str -> {time, long_fired, timer}
        self._capture_cb: Optional[Callable] = None
        self._running = False
        self._error: Optional[str] = None

    # ── Public API ───────────────────────────────────────────────────────────

    def set_threshold(self, ms: int) -> None:
        """Set the long-press threshold in milliseconds."""
        self._threshold = max(100, ms) / 1000.0

    def set_action_callback(self, cb: Callable[[str, str], None]) -> None:
        """
        Set callback invoked when a key action is detected.

        ``cb(key_str, press_type)`` where *press_type* is ``"short"`` or
        ``"long"``.  Called from the pynput listener thread.
        """
        self._action_cb = cb

    def start(self) -> None:
        """Start the keyboard listener."""
        if self._running:
            return
        try:
            self._listener = keyboard.Listener(
                on_press=self._on_press,
                on_release=self._on_release,
            )
            self._listener.start()
            self._running = True
            self._error = None
        except Exception as exc:
            self._running = False
            self._error = str(exc)
            raise

    def stop(self) -> None:
        """Stop the keyboard listener and cancel all pending timers."""
        self._running = False
        if self._listener:
            self._listener.stop()
            self._listener = None
        with self._lock:
            for info in self._pressed.values():
                info.get("timer", _NullTimer()).cancel()
            self._pressed.clear()

    def capture_next_key(self, cb: Callable[[str], None]) -> None:
        """
        Intercept the very next key press and deliver it to *cb(key_str)*.
        Normal action processing is bypassed for that one event.
        """
        with self._lock:
            self._capture_cb = cb

    def cancel_capture(self) -> None:
        """Cancel any pending key-capture request."""
        with self._lock:
            self._capture_cb = None

    @property
    def is_running(self) -> bool:
        return self._running

    @property
    def last_error(self) -> Optional[str]:
        return self._error

    # ── Internal ─────────────────────────────────────────────────────────────

    def _on_press(self, key) -> None:
        key_str = key_to_str(key)

        # Capture mode: deliver key and return without normal processing
        with self._lock:
            if self._capture_cb:
                cb = self._capture_cb
                self._capture_cb = None
                try:
                    cb(key_str)
                except Exception:
                    pass
                return

            # Debounce key-repeat: ignore if already tracking this key
            if key_str in self._pressed:
                return

            # Start tracking
            timer = threading.Timer(self._threshold, self._fire_long, args=[key_str])
            self._pressed[key_str] = {
                "time": time.monotonic(),
                "long_fired": False,
                "timer": timer,
            }

        timer.start()

    def _on_release(self, key) -> None:
        key_str = key_to_str(key)

        with self._lock:
            info = self._pressed.pop(key_str, None)

        if info is None:
            return

        info["timer"].cancel()

        if not info["long_fired"]:
            self._dispatch(key_str, "short")

    def _fire_long(self, key_str: str) -> None:
        with self._lock:
            if key_str not in self._pressed:
                return
            if self._pressed[key_str]["long_fired"]:
                return
            self._pressed[key_str]["long_fired"] = True

        self._dispatch(key_str, "long")

    def _dispatch(self, key_str: str, press_type: str) -> None:
        if self._action_cb:
            try:
                self._action_cb(key_str, press_type)
            except Exception:
                pass


class _NullTimer:
    """Stand-in timer with a no-op cancel() for safe cleanup."""
    def cancel(self):
        pass
