class MoveHistory:

    def __init__(self, app_state):
        self._app_state = app_state
        self._max_history = (
            app_state.get_setting("max_history") or app_state.DEFAULT_MAX_HISTORY
        )

        self._history = app_state.get_move_history()

    def record(self, source_path: str, destination_path: str):
        record = {"from": source_path, "to": destination_path}

        self._history.append(record)

        if len(self._history) > self._max_history:
            self._history.pop(0)

        self._app_state.set_move_history(self._history)

    def undo_last(self):
        if not self._history:
            return None

        record = self._history.pop()
        self._app_state.set_move_history(self._history)
        return record
