from PySide6.QtWidgets import QTextEdit
from core.interfaces.preview_handler import IPreviewHandler


class HexPreviewHandler(IPreviewHandler):

    def can_handle(self, file_path: str) -> bool:
        return True  # fallback universal

    def load(self, file_path: str):
        editor = QTextEdit()
        editor.setReadOnly(True)

        try:
            with open(file_path, "rb") as f:
                data = f.read(2048)

            hex_lines = []
            for i in range(0, len(data), 16):
                chunk = data[i : i + 16]
                hex_part = " ".join(f"{b:02X}" for b in chunk)
                ascii_part = "".join(chr(b) if 32 <= b <= 126 else "." for b in chunk)
                hex_lines.append(f"{i:08X}  {hex_part:<48}  {ascii_part}")

            editor.setPlainText("\n".join(hex_lines))

        except Exception as ex:
            editor.setPlainText(f"Failed to load file\n\n{ex}")

        return editor
