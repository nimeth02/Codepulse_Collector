from PyQt6.QtWidgets import QPlainTextEdit, QCompleter
from PyQt6.QtCore import Qt, QStringListModel
from PyQt6.QtGui import QTextCursor

class CodeEditor(QPlainTextEdit):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.completer = None
        self.setup_completer()

    def setup_completer(self):
        """Initialize code completion with basic keywords"""
        # Initial completion list - can be expanded based on context
        completions = [
            # Python keywords
            'def', 'class', 'if', 'else', 'elif', 'for', 'while', 'try', 'except',
            'finally', 'with', 'as', 'import', 'from', 'return', 'yield', 'break',
            'continue', 'pass', 'raise', 'True', 'False', 'None',
            # Common Python built-ins
            'print', 'len', 'str', 'int', 'float', 'list', 'dict', 'set', 'tuple',
            'range', 'enumerate', 'zip', 'map', 'filter', 'lambda',
            # Qt-specific completions
            'QWidget', 'QMainWindow', 'QApplication', 'QVBoxLayout', 'QHBoxLayout',
            'QPushButton', 'QLabel', 'QLineEdit', 'QTextEdit', 'QPlainTextEdit',
            'QComboBox', 'QCheckBox', 'QRadioButton', 'QSpinBox', 'QSlider',
            'QProgressBar', 'QMessageBox', 'QDialog', 'QFileDialog'
        ]

        self.completer = QCompleter(completions, self)
        self.completer.setWidget(self)
        self.completer.setCompletionMode(QCompleter.CompletionMode.PopupCompletion)
        self.completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        self.completer.activated.connect(self.insert_completion)

    def insert_completion(self, completion):
        """Insert the selected completion into the editor"""
        tc = self.textCursor()
        extra = len(completion) - len(self.completer.completionPrefix())
        tc.movePosition(QTextCursor.MoveOperation.Left)
        tc.movePosition(QTextCursor.MoveOperation.EndOfWord)
        tc.insertText(completion[-extra:])
        self.setTextCursor(tc)

    def text_under_cursor(self):
        """Get the current word being typed"""
        tc = self.textCursor()
        tc.select(QTextCursor.SelectionType.WordUnderCursor)
        return tc.selectedText()

    def keyPressEvent(self, event):
        """Handle key press events for code completion"""
        if self.completer and self.completer.popup().isVisible():
            # Handle completion popup navigation
            if event.key() in (Qt.Key.Key_Enter, Qt.Key.Key_Return, Qt.Key.Key_Tab, Qt.Key.Key_Space):
                event.ignore()
                return

        # Show completions on Ctrl+Space
        if event.modifiers() == Qt.KeyboardModifier.ControlModifier and event.key() == Qt.Key.Key_Space:
            completion_prefix = self.text_under_cursor()
            self.completer.setCompletionPrefix(completion_prefix)
            
            if completion_prefix:
                popup = self.completer.popup()
                popup.setCurrentIndex(self.completer.completionModel().index(0, 0))
                cr = self.cursorRect()
                cr.setWidth(self.completer.popup().sizeHintForColumn(0)
                        + self.completer.popup().verticalScrollBar().sizeHint().width())
                self.completer.complete(cr)
            return

        super().keyPressEvent(event)

        # Auto-show completions while typing
        completion_prefix = self.text_under_cursor()
        
        if len(completion_prefix) >= 2:  # Only show after 2 characters
            self.completer.setCompletionPrefix(completion_prefix)
            
            if completion_prefix:
                popup = self.completer.popup()
                popup.setCurrentIndex(self.completer.completionModel().index(0, 0))
                cr = self.cursorRect()
                cr.setWidth(self.completer.popup().sizeHintForColumn(0)
                        + self.completer.popup().verticalScrollBar().sizeHint().width())
                self.completer.complete(cr)

    def update_completions(self, new_completions):
        """Update the completion list with new suggestions"""
        model = QStringListModel(new_completions)
        self.completer.setModel(model)