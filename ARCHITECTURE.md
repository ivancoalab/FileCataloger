# File Cataloger – Architecture Overview

## 1. Project Goal

A modular, extensible File Cataloger application built with:

- Python 3.x
- PySide6 (Qt)
- Clean separation of concerns
- Small, maintainable functions
- Independent modules
- Console logging (no heavy logging framework)
- JSON-based configuration
- In-memory move history (for now)

Primary objectives:

- Browse filesystem (including folders)
- Fast preview of common file types
- Move files via keyboard shortcuts
- Undo last move
- Modular preview system
- Graceful failure (no hard crashes)

---

## 2. High-Level Architecture

The project follows a layered architecture:

UI (Presentation Layer)
↓
Application Layer (Business Logic)
↓
Infrastructure Layer (System / IO / Preview Handlers)


No layer should directly break abstraction boundaries.

UI must not call shutil directly.
All file movement must go through FileMover.

---

## 3. Project Structure
application/
file_mover.py
move_history.py

infrastructure/
preview/
preview_manager.py
metadata_widget.py
preview_handlers/
image_handler.py
text_handler.py
pdf_handler.py
media_handler.py
zip_handler.py
hex_handler.py

ui/
main_window.py
conflict_dialog.py

config_manager.py
main.py
config.json
move_history.json (optional, currently in-memory)

---

## 4. Core Components

### 4.1 MainWindow (UI Layer)

Responsibilities:
- Render split layout
- Directory label above splitter
- Left: file/folder list
- Right: preview area
- Bottom-right: destination folders
- Keyboard navigation
- F6 = Move
- Ctrl+Z = Undo
- Delete = Move to Deleted folder
- Refresh list after move
- Keep selection position

Must NOT:
- Call shutil directly
- Contain business logic
- Handle file IO directly

---

### 4.2 FileMover (Application Layer)

Encapsulates:
shutil.move()

Responsibilities:
- Validate destination folder
- Perform move
- Return final path
- Use MoveHistory to record operation

Interface:
move(source_path: str, destination_folder: str) -> str | None
undo() -> bool

Undo uses MoveHistory.

---

### 4.3 MoveHistory (Application Layer)

Currently in-memory.

Structure stored:
{
"from": original_path,
"to": destination_path
}

Responsibilities:
- record(source, destination)
- undo_last()

Does NOT:
- Perform file movement
- Access UI

Undo returns record dictionary.

---

### 4.4 Preview System (Infrastructure Layer)

Implements a handler registry pattern.

### PreviewManager

Contains:
self._handlers = [
ImagePreviewHandler(),
TextPreviewHandler(),
PdfPreviewHandler(),
MediaPreviewHandler(),
ZipPreviewHandler(),
HexPreviewHandler() # fallback
]


Flow:
for handler in handlers:
if handler.can_handle(path):
return handler.load(path)

fallback → HexPreviewHandler


Each handler must implement:
can_handle(path: str) -> bool
load(path: str) -> QWidget


Handlers must be independent and small.

---

## 5. Supported Preview Types

| Type     | Handler |
|----------|---------|
| Images   | ImagePreviewHandler |
| Text     | TextPreviewHandler |
| PDF      | PdfPreviewHandler |
| Media    | MediaPreviewHandler |
| ZIP      | ZipPreviewHandler |
| Unknown  | HexPreviewHandler |

ZIP handler lists internal files (read-only).

Hex handler displays hex dump preview.

---

## 6. UI Behavior Rules

- Folder double-click navigates into folder
- Thousands of files supported
- Selection persists after move
- After move:
  - Remove item from list
  - Select next item
  - If last → select new last
  - If empty → no error
- Conflict dialog appears if file exists
- Conflict options:
  - Overwrite
  - Rename with sequence
  - Apply to future cases (checkbox)

---

## 7. Config System

config.json contains:

- Destination folders
- Deleted folder
- Default folder

Currently local file in project root.

Future: AppData migration possible.

---

## 8. Design Principles

- Small functions (fit on screen)
- Single Responsibility Principle
- No hidden side effects
- Graceful failure
- Modular preview system
- Extensible handlers
- No tight coupling between UI and IO
- Business logic not in UI

---

## 9. Known Stable Features

✔ Folder navigation  
✔ Preview system working  
✔ Media playback  
✔ ZIP listing  
✔ Hex fallback  
✔ File move  
✔ Undo (in-memory)  
✔ Conflict resolution dialog  
✔ Keyboard shortcuts  
✔ List refresh after move  

---

## 10. Future Expansion Ideas

- Persistent move history (JSON)
- Multi-level undo/redo
- Batch selection move
- Thumbnail cache
- Background preview loading
- Async file scanning
- Drag & drop
- Tagging system
- SQLite indexing
- Virtual collections
- Performance optimization for very large folders

---

## 11. Important Contracts

FileMover.move() must always return:

full_final_path (including filename)


MoveHistory must always store dict with:
{
"from": ...,
"to": ...
}


Preview handlers must not throw unhandled exceptions.

UI must not manipulate filesystem directly.

---

## 12. Development Philosophy

The system must:

- Not crash if a handler fails
- Not crash if a folder does not exist
- Log to console instead of raising UI exceptions
- Allow removal of modules without breaking core

---

END OF ARCHITECTURE DOCUMENT

