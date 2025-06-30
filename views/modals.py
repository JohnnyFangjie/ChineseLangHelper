# views/modals.py
"""
Reusable modal dialogs for the application
"""
from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QPushButton, 
                             QLabel, QLineEdit, QTextEdit, QFrame)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont


class AddLessonModal(QDialog):
    """Modal for creating a new lesson"""
    
    # Signal emitted when lesson should be created
    lesson_created = Signal(str, str)  # name, description
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui() 
    
    def init_ui(self):
        """Initialize the modal UI"""
        self.setWindowTitle("Create New Lesson")
        self.setModal(True)  # Makes it modal
        self.setFixedSize(400, 300)
        
        layout = QVBoxLayout(self)
        
        # Title
        title_label = QLabel("Create New Lesson")
        title_font = QFont()
        title_font.setPointSize(14)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)
        
        # Separator
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setFrameShadow(QFrame.Sunken)
        layout.addWidget(separator)
        
        # Lesson name input
        layout.addWidget(QLabel("Lesson Name:"))
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Enter lesson name...")
        layout.addWidget(self.name_input)
        
        # Lesson description input
        layout.addWidget(QLabel("Description (optional):"))
        self.description_input = QLineEdit()
        self.description_input.setPlaceholderText("Enter lesson description...")
        self.description_input.setMaximumHeight(100)
        layout.addWidget(self.description_input)
        
        # Error message label
        self.error_label = QLabel("")
        self.error_label.setStyleSheet("color: red; font-size: 11px;")
        layout.addWidget(self.error_label)
        
        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(self.cancel_button)
        
        self.create_button = QPushButton("Create Lesson")
        self.create_button.clicked.connect(self.create_lesson)
        self.create_button.setDefault(True)  # Enter key triggers this
        button_layout.addWidget(self.create_button)
        
        layout.addLayout(button_layout)
        
        # Focus on name input
        self.name_input.setFocus()
    
    def create_lesson(self):
        """Handle lesson creation"""
        name = self.name_input.text().strip()
        description = self.description_input.text().strip()
        
        # Validation
        if not name:
            self.show_error("Please enter a lesson name")
            return
        
        if len(name) < 2:
            self.show_error("Lesson name must be at least 2 characters")
            return
        
        # Emit signal with lesson data
        self.lesson_created.emit(name, description)
        self.accept()  # Close modal successfully
    
    def show_error(self, message: str):
        """Show error message"""
        self.error_label.setText(message)
    
    def reset(self):
        """Reset the modal for reuse"""
        self.name_input.clear()
        self.description_input.clear()
        self.error_label.clear()
        self.name_input.setFocus()
