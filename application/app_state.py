import json
import os
from typing import Any, Dict


class AppState:
    DEFAULT_MAX_HISTORY = 500

    def __init__(self, file_path: str = "app_state.json"):
        self._file_path = file_path
        self._data = self._load()

    def _load(self) -> Dict[str, Any]:
        if not os.path.exists(self._file_path):
            return self._default_state()

        try:
            with open(self._file_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as ex:
            print(f"[WARN] Failed to load state: {ex}")
            return self._default_state()

    def _save(self):
        try:
            with open(self._file_path, "w", encoding="utf-8") as f:
                json.dump(self._data, f, indent=4)
        except Exception as ex:
            print(f"[ERROR] Failed to save state: {ex}")

    def _default_state(self) -> Dict[str, Any]:
        return {
            "settings": {
                "default_directory": "",
                "last_directory": "",
                "max_history": self.DEFAULT_MAX_HISTORY,
            },
            "window": {"geometry": None, "splitter_sizes": None},
            "move_history": [],
        }

    # ---------- Settings ----------

    def get_setting(self, key: str):
        return self._data["settings"].get(key)

    def set_setting(self, key: str, value: Any):
        self._data["settings"][key] = value
        self._save()

    # ---------- Window State ----------

    def get_window_state(self):
        return self._data.get("window", {})

    def set_window_state(self, geometry, splitter_sizes):
        self._data["window"]["geometry"] = geometry
        self._data["window"]["splitter_sizes"] = splitter_sizes
        self._save()

    # ---------- Move History ----------

    def get_move_history(self):
        return self._data.get("move_history", [])

    def set_move_history(self, history_list):
        self._data["move_history"] = history_list
        self._save()
