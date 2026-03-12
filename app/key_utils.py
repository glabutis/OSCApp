"""Utilities for converting pynput key objects to/from serializable strings."""

from pynput import keyboard

# Human-readable display names for common keys
_DISPLAY_NAMES = {
    "Key.page_down": "Page Down",
    "Key.page_up": "Page Up",
    "Key.right": "Right Arrow",
    "Key.left": "Left Arrow",
    "Key.up": "Up Arrow",
    "Key.down": "Down Arrow",
    "Key.space": "Space",
    "Key.enter": "Return",
    "Key.esc": "Escape",
    "Key.tab": "Tab",
    "Key.backspace": "Backspace",
    "Key.delete": "Delete",
    "Key.home": "Home",
    "Key.end": "End",
    "Key.insert": "Insert",
    "Key.f1": "F1",
    "Key.f2": "F2",
    "Key.f3": "F3",
    "Key.f4": "F4",
    "Key.f5": "F5",
    "Key.f6": "F6",
    "Key.f7": "F7",
    "Key.f8": "F8",
    "Key.f9": "F9",
    "Key.f10": "F10",
    "Key.f11": "F11",
    "Key.f12": "F12",
    "Key.media_next": "Media Next",
    "Key.media_previous": "Media Previous",
    "Key.media_play_pause": "Media Play/Pause",
    "Key.volume_up": "Volume Up",
    "Key.volume_down": "Volume Down",
    "Key.volume_mute": "Volume Mute",
    "Key.cmd": "Command",
    "Key.ctrl": "Ctrl",
    "Key.shift": "Shift",
    "Key.alt": "Alt",
}


def key_to_str(key) -> str:
    """Convert a pynput key object to a serializable string."""
    if isinstance(key, keyboard.Key):
        return f"Key.{key.name}"
    if isinstance(key, keyboard.KeyCode):
        if key.char:
            return key.char
        if key.vk:
            return f"vk:{key.vk}"
    return str(key)


def str_to_key(s: str):
    """Convert a serialized string back to a pynput key object."""
    if not s:
        return None
    if s.startswith("Key."):
        name = s[4:]
        try:
            return keyboard.Key[name]
        except KeyError:
            return None
    if s.startswith("vk:"):
        try:
            return keyboard.KeyCode.from_vk(int(s[3:]))
        except (ValueError, TypeError):
            return None
    if len(s) == 1:
        return keyboard.KeyCode.from_char(s)
    return None


def key_display(key_str: str) -> str:
    """Return a human-readable label for a serialized key string."""
    if not key_str:
        return "Not set"
    if key_str in _DISPLAY_NAMES:
        return _DISPLAY_NAMES[key_str]
    if key_str.startswith("Key."):
        return key_str[4:].replace("_", " ").title()
    if key_str.startswith("vk:"):
        return f"VK {key_str[3:]}"
    # Single character — display uppercase
    return key_str.upper()


def keys_match(key, key_str: str) -> bool:
    """Check whether a pynput key object matches a serialized key string."""
    return key_to_str(key) == key_str
