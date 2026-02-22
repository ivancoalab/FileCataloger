import os
import shutil


class MoveResult:
    SUCCESS = "success"
    CONFLICT = "conflict"
    ERROR = "error"


class FileMover:

    def __init__(self, history):
        self._history = history

    def move(self, source_path: str, destination_folder: str, conflict_policy=None):
        # def move(self, source_path: str, destination_folder: str):
        try:
            if not os.path.exists(source_path):
                return MoveResult.ERROR, "Source does not exist"

            if not os.path.isdir(destination_folder):
                return MoveResult.ERROR, "Destination folder invalid"

            filename = os.path.basename(source_path)
            destination_path = os.path.join(destination_folder, filename)

            if not os.path.exists(destination_folder):
                print("Destination folder invalid")
                return False

            if os.path.exists(destination_path):
                # return MoveResult.CONFLICT, destination_path
                if conflict_policy == "replace":
                    os.remove(destination_path)
                elif conflict_policy == "rename":
                    base, ext = os.path.splitext(filename)
                    counter = 1
                    while os.path.exists(destination_path):
                        new_name = f"{base}_{counter}{ext}"
                        destination_path = os.path.join(destination_folder, new_name)
                        counter += 1
                else:
                    # cancel or undefined
                    return False

            shutil.move(source_path, destination_path)

            self._history.record(source_path, destination_path)

            return MoveResult.SUCCESS, destination_path

        except Exception as ex:
            return MoveResult.ERROR, str(ex)

    def move_back(self, current_path: str, original_path: str):
        import os
        import shutil

        if not os.path.exists(current_path):
            print("Undo failed: file no longer exists.")
            return False

        if os.path.exists(original_path):
            print("Undo failed: original location occupied.")
            return False

        shutil.move(current_path, original_path)
        return True

    def undo(self):
        record = self._history.undo_last()
        if not record:
            print("Nothing to undo or undo failed.")
            return False

        original_path = record["from"]
        moved_path = record["to"]

        if not os.path.exists(moved_path):
            print("Undo failed: file no longer exists.")
            return False

        if os.path.exists(original_path):
            print("Undo failed: original location occupied.")
            return False

        result = shutil.move(moved_path, os.path.dirname(original_path))
        if result:
            print("Undo successful.")
            return record
        else:
            print("Undo move failed.")
            return None
