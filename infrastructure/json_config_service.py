import json
import os
from core.interfaces.config_service import IConfigService


class JsonConfigService(IConfigService):

    def __init__(self, path: str = "config.json"):
        self._path = path

    def load(self) -> dict:
        if not os.path.exists(self._path):
            print("[INFO] Config file not found. Creating default config.")
            default = self._default_config()
            self.save(default)
            return default

        try:
            with open(self._path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as ex:
            print(f"[ERROR] Failed loading config: {ex}")
            return self._default_config()

    def save(self, config: dict) -> None:
        with open(self._path, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=4)

    def _default_config(self) -> dict:
        return {
            "default_directory": "",
            "deleted_directory": "",
            "destinations": [],
            "conflict_policy": "ask",
        }
