import json
import os


class ConfigManager:

    DEFAULT_CONFIG = {
        "destination_folders": [],
        "deleted_folder": "",
        "conflict_policy": None,
    }

    def __init__(self, config_path="config.json"):
        self._config_path = config_path
        self._config = self._load()

    def _load(self):
        if not os.path.exists(self._config_path):
            return self.DEFAULT_CONFIG.copy()

        try:
            with open(self._config_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as ex:
            print(f"[ERROR] Failed loading config: {ex}")
            return self.DEFAULT_CONFIG.copy()

    def save(self):
        try:
            with open(self._config_path, "w", encoding="utf-8") as f:
                json.dump(self._config, f, indent=4)
        except Exception as ex:
            print(f"[ERROR] Failed saving config: {ex}")

    def get_destinations(self):
        return self._config.get("destination_folders", [])

    def set_destinations(self, folders):
        self._config["destination_folders"] = folders
        self.save()

    def get_deleted_folder(self):
        return self._config.get("deleted_folder", "")

    def set_deleted_folder(self, path):
        self._config["deleted_folder"] = path
        self.save()

    def get_conflict_policy(self):
        return self._config.get("conflict_policy")

    def set_conflict_policy(self, policy):
        self._config["conflict_policy"] = policy
        self.save()
