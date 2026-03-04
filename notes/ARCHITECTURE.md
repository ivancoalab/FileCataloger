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

1. Persistence Layer (Introduced in Phase 8)
Overview

We introduced a JSON-based persistence system to store:

Application configuration

Session state

Window geometry

Splitter state

Last working directory

Limited move history

Persistence file location:

/project_root/config.json

2. ConfigManager
Responsibility

Encapsulates all read/write operations to config.json.

Key Design Decisions

Single source of truth for persistent state.

History size is configurable.

Uses safe JSON loading (fallback to defaults).

Writes are explicit (no auto-save on every change unless triggered).

Stored Structure

{
  "last_directory": "C:/example/path",
  "window_geometry": "...base64 QByteArray...",
  "splitter_state": "...base64 QByteArray...",
  "max_history": 50,
  "move_history": []
}

3. Persistent Move History
Change in HistoryManager

Previously:

In-memory only

Now:

History list synchronized with config

Limited to max_history

Oldest entries trimmed when limit exceeded

Architectural Principle

HistoryManager remains logic-focused.
Persistence responsibility stays in ConfigManager.

4. Default Directory Strategy

Startup behavior:

If last_directory exists → load it

Else → use os.getcwd() (portable-safe)

If stored directory no longer exists → fallback to os.getcwd()

When navigating directories:

Every directory change updates last_directory

Saved on app close

5. Window Geometry Persistence

Handled in:

closeEvent()

Stored:

saveGeometry()

splitter.saveState()

Restored during initialization after UI setup.

Important:
Restore must happen AFTER splitter and central widget exist.

6. Selection Model Refactor

Removed:
_list_view.clicked.connect(...)
Replaced with:

_list_view.selectionModel().currentChanged.connect(...)

Reason

Decouples UI input from business logic

Keyboard navigation now fully supported

Prevents duplicate preview refresh

Centralizes selection reaction logic

Rule:
setCurrentIndex() must NOT manually call _on_item_selected().

7. Preview System Stabilization
Previous Problem

Splitter auto-resized when preview widget changed.

QLabel size hints caused layout instability.

Metadata imposed horizontal minimum width.

Final Architecture

Preview area is now:

Splitter
 └── PreviewContainer (QWidget)
      └── QVBoxLayout
           ├── PreviewContentWidget (image/text/etc)
           └── MetadataWidget
Critical Fixes

Metadata labels use setWordWrap(True)

No fixed minimum widths

No widget replacement in splitter (container remains constant)

Only content inside container changes

This guarantees:

Splitter position stability

Window resize freedom

Clean separation of preview & metadata

8. Current Application State (End of Phase 8.3)

System now supports:

✔ Persistent working directory
✔ Portable startup behavior
✔ Persistent window geometry
✔ Persistent splitter position
✔ Configurable limited move history
✔ Keyboard + mouse unified selection handling
✔ Stable preview layout
✔ Responsive metadata

Application is now structurally stable and professionally architected.

🔒 Recommended Next Phase (Not Implemented Yet)

Potential Phase 8.4:

Persist last selected file

Separate session.json from config.json

Thumbnail caching

Async preview loading


# FileCataloger – Architecture Overview (Up to Phase 9.3)

## 1. Architectural Principles

The application follows a clean separation between:

* **UI Components** (presentation layer)
* **Input Routing** (keyboard/mouse handling)
* **Core Logic** (file operations)
* **Configuration Layer** (JSON-driven behavior)

Design goals achieved so far:

* Single source of truth for file movement
* Unified activation path (mouse + keyboard)
* Focus-independent hotkey handling
* Modular UI components
* No duplicated input systems

---

# 2. High-Level Structure

```
FileCataloger
│
├── main_window.py
│     ├── UI Layout
│     ├── Global Event Filter (keyboard router)
│     ├── Destination activation handler
│     └── File movement orchestration
│
├── ui/widgets/
│     └── destination_widget.py
│
├── config_manager.py
│
└── config.json
```

---

# 3. Core Components

## 3.1 MainWindow

**Responsibilities:**

* Builds main layout
* Manages file list view
* Routes all keyboard input
* Coordinates file movement
* Maintains mapping of destination widgets

### Key Architectural Decisions

* Global keyboard routing installed at application level:

```python
QApplication.instance().installEventFilter(self)
```

* Single activation method:

```python
_activate_destination_by_path(path)
```

This ensures mouse clicks and hotkeys trigger the same flow.

---

## 3.2 DestinationWidget

Encapsulated UI component.

**Responsibilities:**

* Visual representation of a destination
* Hover styling
* Flash feedback on activation
* Emits activation event

**Does NOT:**

* Move files
* Contain business logic
* Access configuration

### Visual Feedback

Flash implemented via temporary stylesheet change:

```python
QTimer.singleShot(...)
```

This ensures consistent and visible feedback.

---

## 3.3 Input Routing (Event Filter)

Installed globally to avoid focus dependency.

### Handles:

* Enter → `_handle_enter()`
* Backspace → `_go_back()`
* Delete → Move to deleted folder
* Hotkeys (numbers + symbols) → Activate destination

### Hotkey Handling Strategy

Uses:

```python
event.text()
```

Rationale:

* Supports numbers
* Supports symbols (`/`, `*`, `-`, `+`)
* Independent of keyboard layout
* Works from any focused widget

---

# 4. Activation Flow

## Mouse Flow

```
DestinationWidget Click
    ↓
_activate_destination_by_path(path)
    ↓
widget._blink()
    ↓
_move_current_file(path)
```

## Keyboard Flow

```
KeyPress
    ↓
Global eventFilter
    ↓
_activate_destination_by_path(path)
    ↓
widget._blink()
    ↓
_move_current_file(path)
```

Unified execution path.

---

# 5. Configuration Layer

## config.json

Structure:

```json
{
  "destination_folders": [
    {
      "name": "Amazon",
      "path": "C:/...",
      "hotkey": "0"
    }
  ],
  "deleted_folder": "C:/TEMP/Deleted",
  "conflict_policy": null
}
```

The configuration drives:

* Destination buttons
* Hotkeys
* Deleted folder target

UI dynamically reflects configuration.

---

# 6. Architectural Guarantees Achieved

* No duplicated shortcut systems
* No focus-dependent keyboard failures
* No business logic inside UI widgets
* Single point of movement logic
* Clean separation of concerns

---

# 7. Known Future Hardening Areas

Potential Phase 9.4+ improvements:

* Hotkey duplication validation on config load
* Structured logging system
* Conflict policy enforcement
* Visual warning for invalid configuration
* Optional shortcut modifier support (Ctrl/Alt combinations)

---

# 8. Current Stability Status

✔ Mouse activation stable
✔ Keyboard activation stable (numbers + symbols)
✔ Global focus independence
✔ Flash visual feedback functional
✔ Navigation keys unaffected
✔ Deleted folder logic intact

Architecture is currently coherent and production-structured for a desktop file workflow tool.

---

End of Phase 9.3 Architecture Snapshot
