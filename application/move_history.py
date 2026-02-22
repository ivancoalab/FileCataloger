class MoveHistory:

    def __init__(self):
        self._history = []

    def record(self, source_path: str, destination_path: str):
        self._history.append({"from": source_path, "to": destination_path})
        print({"from": source_path, "to": destination_path})

    def get_last(self):
        if not self._history:
            return None
        return self._history[-1]

    def get_all(self):
        return list(self._history)

    def undo_last(self):
        if not self._history:
            print("Nothing to undo.")
            return None

        record = self._history.pop()
        # self._save()

        return record  # returns dict with "from" and "to"
