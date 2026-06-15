"""
配置管理
"""

import json
from pathlib import Path
from typing import Optional

CONFIG_DIR = Path.home() / ".api_balance_monitor"
CONFIG_FILE = CONFIG_DIR / "config.json"

DEFAULT_ENABLED = ["deepseek", "mimo", "kimi"]

DEFAULT_CONFIG = {
    "version": "2.0",
    "license": {
        "key": "",
        "type": "free",
        "activated_at": None  # 激活时间
    },
    "settings": {
        "refresh_interval": 300000,
        "alert_threshold": 10.0,
        "autostart": False,
        "window_x": 100,
        "window_y": 100
    },
    "providers": {
        "deepseek": {"enabled": True},
        "mimo": {"enabled": True},
        "kimi": {"enabled": True},
        "siliconflow": {"enabled": False},
        "zhipu": {"enabled": False},
        "volcengine": {"enabled": False},
        "qianfan": {"enabled": False},
        "dashscope": {"enabled": False},
        "tencent": {"enabled": False},
        "minimax": {"enabled": False},
        "xunfei": {"enabled": False},
        "baichuan": {"enabled": False},
        "lingyi": {"enabled": False},
        "jingdong": {"enabled": False}
    }
}


class Config:
    def __init__(self):
        self._config = DEFAULT_CONFIG.copy()
        self._config_path = CONFIG_FILE
        self.load()

    def load(self):
        CONFIG_DIR.mkdir(exist_ok=True)
        if CONFIG_FILE.exists():
            try:
                with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                    saved = json.load(f)
                    self._merge(saved)
            except Exception:
                pass

    def save(self):
        CONFIG_DIR.mkdir(exist_ok=True)
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(self._config, f, indent=2, ensure_ascii=False)

    def _merge(self, saved: dict):
        for key in ["version", "license", "settings"]:
            if key in saved:
                if isinstance(self._config[key], dict) and isinstance(saved[key], dict):
                    self._config[key].update(saved[key])
                else:
                    self._config[key] = saved[key]
        if "providers" in saved:
            for name, cfg in saved["providers"].items():
                if name in self._config["providers"]:
                    self._config["providers"][name].update(cfg)
                else:
                    self._config["providers"][name] = cfg

    @property
    def license_key(self) -> str:
        return self._config["license"].get("key", "")

    @license_key.setter
    def license_key(self, value: str):
        self._config["license"]["key"] = value

    @property
    def license_type(self) -> str:
        return self._config["license"].get("type", "free")

    @license_type.setter
    def license_type(self, value: str):
        self._config["license"]["type"] = value

    @property
    def license_activated_at(self) -> Optional[str]:
        return self._config["license"].get("activated_at")

    @license_activated_at.setter
    def license_activated_at(self, value: Optional[str]):
        self._config["license"]["activated_at"] = value

    @property
    def is_pro(self) -> bool:
        return self.license_type == "pro"

    @property
    def refresh_interval(self) -> int:
        return self._config["settings"].get("refresh_interval", 300000)

    @refresh_interval.setter
    def refresh_interval(self, value: int):
        self._config["settings"]["refresh_interval"] = value

    @property
    def alert_threshold(self) -> float:
        return self._config["settings"].get("alert_threshold", 10.0)

    @alert_threshold.setter
    def alert_threshold(self, value: float):
        self._config["settings"]["alert_threshold"] = value

    @property
    def autostart(self) -> bool:
        return self._config["settings"].get("autostart", False)

    @autostart.setter
    def autostart(self, value: bool):
        self._config["settings"]["autostart"] = value

    @property
    def window_x(self) -> int:
        return self._config["settings"].get("window_x", 100)

    @window_x.setter
    def window_x(self, value: int):
        self._config["settings"]["window_x"] = value

    @property
    def window_y(self) -> int:
        return self._config["settings"].get("window_y", 100)

    @window_y.setter
    def window_y(self, value: int):
        self._config["settings"]["window_y"] = value

    def get_provider_config(self, name: str) -> dict:
        return self._config["providers"].get(name, {"enabled": False})

    def set_provider_config(self, name: str, config: dict):
        self._config["providers"][name] = config

    def get_enabled_providers(self) -> list:
        enabled = []
        for name, cfg in self._config["providers"].items():
            if cfg.get("enabled", False):
                enabled.append(name)
        return enabled
