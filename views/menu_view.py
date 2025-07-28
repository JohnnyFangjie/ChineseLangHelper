"""
Menu view for selecting lessons
"""
from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                             QLabel, QScrollArea, QGridLayout, QFileDialog)
from PySide6.QtGui import QFont
from typing import List, Dict, Any, Callable
from .modals import AddLessonModal, ConfirmLessonDelete


class MenuView(QWidget):
    """Menu view widget for lesson selection"""
    
    # Signal emitted when a lesson is selected
    lesson_selected = Signal(str)  # filename
    add_lesson_requested = Signal(str, str)
    delete_lesson_requested = Signal(str)
    import_lesson_requested = Signal()
    
    def __init__(self):
        super().__init__()
        self.lesson_buttons = []
        self.init_ui()
        self.addLesson_modal = None
    
    def init_ui(self):
        """Initialize the user interface"""
        layout = QVBoxLayout(self)
        
        # Title
        title_label = QLabel("Chinese Learning Helper")
        title_label.setAlignment(Qt.AlignCenter)
        title_font = QFont("Arial")
        title_font.setPointSize(18)
        title_font.setBold(True)
        title_label.setFont(title_font)
        layout.addWidget(title_label)
        
        # Subtitle
        subtitle_label = QLabel("Select a lesson file to begin:")
        subtitle_label.setAlignment(Qt.AlignCenter)
        subtitle_font = QFont("Arial")
        subtitle_font.setPointSize(12)
        subtitle_label.setFont(subtitle_font)
        layout.addWidget(subtitle_label)
        
        # Create scroll area for buttons
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        
        # Widget to contain the lesson buttons to open the lesson
        self.button_widget = QWidget()
        self.button_layout = QGridLayout(self.button_widget)
        self.button_layout.setSpacing(10)
        
        scroll_area.setWidget(self.button_widget)
        layout.addWidget(scroll_area)
        
        # Control buttons
        controls_layout = QHBoxLayout()
        
        # Refresh button
        self.refresh_button = QPushButton("Refresh Files")
        self.refresh_button.setMaximumWidth(150)
        controls_layout.addWidget(self.refresh_button)
        
        # Add Lesson button
        self.addLesson_button = QPushButton("Add Lesson")
        self.addLesson_button.setMaximumWidth(150)
        self.addLesson_button.clicked.connect(self.show_addLeson_modal)
        controls_layout.addWidget(self.addLesson_button)
        
        # Import Lesson
        self.importLesson_button = QPushButton("Import Lesson")
        self.importLesson_button.setMaximumWidth(150)
        self.importLesson_button.clicked.connect(self.import_lesson_requested.emit)
        controls_layout.addWidget(self.importLesson_button)

        # Add some stretch to center the refresh button
        controls_layout.addStretch()
        
        layout.addLayout(controls_layout)
        
        # Status label
        self.status_label = QLabel("Ready")
        self.status_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.status_label)
    
    def clear_lessons(self):
        """Clear all lesson buttons"""
        self.lesson_buttons.clear()
        while self.button_layout.count():
            child = self.button_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
    
    def populate_lessons(self, lessons_info: List[Dict[str, Any]]):
        """Populate the view with lesson buttons"""
        self.clear_lessons()
        
        if not lessons_info:
            self._show_no_files_message()
            return
        
        # Create buttons in a grid layout
        row = 0
        col = 0
        max_cols = 3  # Maximum buttons per row
        
        for lesson_info in lessons_info:
            button = self._create_lesson_button(lesson_info)
            self.lesson_buttons.append(button)
            
            # Add button to grid
            self.button_layout.addWidget(button, row, col)
            
            col += 1
            if col >= max_cols:
                col = 0
                row += 1
        
        self.status_label.setText(f"Found {len(lessons_info)} lesson file(s)")
    
    def _create_lesson_button(self, lesson_info: Dict[str, Any]) -> QPushButton:
        """Create a button for a lesson AKA. A button that when pressed, opens the designated lesson."""
        button = QPushButton(lesson_info['name'])
        button.setMinimumSize(200, 80)
        button.setMaximumSize(250, 100)
        
        # Create tooltip
        tooltip = f"File: {lesson_info['filename']}\n{lesson_info['description']}\nWords: {lesson_info['word_count']}"
        if not lesson_info['valid']:
            tooltip += f"\nError: {lesson_info['error']}"
            button.setEnabled(False)
            button.setStyleSheet("color: gray;")
        button.setToolTip(tooltip)
        
        # Create small delete button
        delete_btn = QPushButton("×", button)  # Using × symbol
        delete_btn.setFixedSize(20, 20)
        delete_btn.setStyleSheet("""
            QPushButton {
                background-color: #ff4444;
                color: white;
                border: none;
                border-radius: 10px;
                font-weight: bold;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #ff6666;
            }
            QPushButton:pressed {
                background-color: #cc3333;
            }
        """)
        delete_btn.setToolTip("Delete lesson")
        
        # Position delete button in top-right corner
        delete_btn.move(button.width() - 25, 5)
        
        # Handle resize to keep delete button in corner
        def on_resize():
            delete_btn.move(button.width() - 25, 5)
        
        button.resizeEvent = lambda event: (QPushButton.resizeEvent(button, event), on_resize())[1]
        
        # Connect main button to signal
        filename = lesson_info['filename']
        button.clicked.connect(lambda: self.lesson_selected.emit(filename))
        
        # Connect delete button - you can connect this to your deletion logic
        delete_btn.clicked.connect(lambda: self.show_deleteLesson_modal(filename))
        
        return button

    def show_addLeson_modal(self):
        """Show the create lesson modal"""
        # Create modal if it doesn't exist
        if not self.addLesson_modal:
            self.addLesson_modal = AddLessonModal(self)
            # Connect the modal's signal to your view's signal
            self.addLesson_modal.lesson_created.connect(self.add_lesson_requested.emit)
        
        # Reset and show the modal
        self.addLesson_modal.reset()
        self.addLesson_modal.exec()  # This blocks until modal is closed
    
    
    def show_deleteLesson_modal(self, filename):
            """Show the Deletion Confirmation modal"""
            self.deleteLesson_modal = ConfirmLessonDelete(filename=filename)
            self.deleteLesson_modal.deletion_confirmed.connect(self.delete_lesson_requested.emit)
            
            self.deleteLesson_modal.exec()

    def _show_no_files_message(self):
        """Show message when no lesson files are found"""
        no_files_label = QLabel("No JSON files found in the data folder.\n"
                               "Add some lesson files to get started!")
        no_files_label.setAlignment(Qt.AlignCenter)
        no_files_label.setStyleSheet("color: gray; font-size: 14px;")
        self.button_layout.addWidget(no_files_label, 0, 0, 1, 3)
        self.status_label.setText("No lesson files found")
    
    def set_status(self, message: str):
        """Set the status message"""
        self.status_label.setText(message)
    
    def connect_refresh(self, callback: Callable):
        """Connect the refresh button to a callback"""
        self.refresh_button.clicked.connect(callback)
