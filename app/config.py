import json
import os
import uuid
from dataclasses import asdict, dataclass, field
from typing import List

CONFIG_DIR = os.path.expanduser("~/.config/dispatch")
CONFIG_FILE = os.path.join(CONFIG_DIR, "config.json")


@dataclass
class Mapping:
    id: str
    name: str
    key_str: str       # serialized pynput key, e.g. "Key.right" or "a"
    press_type: str    # "short" | "long" | "any"
    osc_address: str   # e.g. "/atem/cut"
    osc_args: str      # space-separated args string, e.g. "1" or "1 2.5"
    enabled: bool = True

    @classmethod
    def new(cls, name: str = "New Mapping") -> "Mapping":
        return cls(
            id=str(uuid.uuid4()),
            name=name,
            key_str="",
            press_type="short",
            osc_address="",
            osc_args="",
            enabled=True,
        )

    def copy(self) -> "Mapping":
        return Mapping(**asdict(self))


@dataclass
class OSCConfig:
    host: str = "127.0.0.1"
    port: int = 3333


@dataclass
class AppSettings:
    long_press_threshold_ms: int = 500


@dataclass
class AppConfig:
    osc: OSCConfig = field(default_factory=OSCConfig)
    settings: AppSettings = field(default_factory=AppSettings)
    mappings: List[Mapping] = field(default_factory=list)

    def save(self) -> None:
        os.makedirs(CONFIG_DIR, exist_ok=True)
        data = {
            "osc": asdict(self.osc),
            "settings": asdict(self.settings),
            "mappings": [asdict(m) for m in self.mappings],
        }
        with open(CONFIG_FILE, "w") as f:
            json.dump(data, f, indent=2)

    @classmethod
    def load_default(cls) -> "AppConfig":
        if not os.path.exists(CONFIG_FILE):
            return cls()
        try:
            with open(CONFIG_FILE) as f:
                data = json.load(f)
            osc = OSCConfig(**data.get("osc", {}))
            settings = AppSettings(**data.get("settings", {}))
            mappings = [Mapping(**m) for m in data.get("mappings", [])]
            return cls(osc=osc, settings=settings, mappings=mappings)
        except Exception:
            return cls()
