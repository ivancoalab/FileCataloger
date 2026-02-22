from PySide6.QtWidgets import QMessageBox


def ask_conflict_resolution(parent, filename):
    msg = QMessageBox(parent)
    msg.setWindowTitle("File already exists")
    msg.setText(f"The file '{filename}' already exists in destination.")
    msg.setInformativeText("What would you like to do?")

    replace_btn = msg.addButton("Replace", QMessageBox.AcceptRole)
    rename_btn = msg.addButton("Rename", QMessageBox.ActionRole)
    cancel_btn = msg.addButton("Cancel", QMessageBox.RejectRole)

    msg.exec()

    if msg.clickedButton() == replace_btn:
        return "replace"
    elif msg.clickedButton() == rename_btn:
        return "rename"
    else:
        return None
