"""
Lesson view for displaying and managing word lists
"""
import random
from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                             QLabel, QTableWidget, QTableWidgetItem, QHeaderView,
                             QCheckBox, QFrame, QLineEdit)
from PySide6.QtGui import QFont
from typing import List, Callable
from models.lesson import Lesson, Word
from .modals import ConfirmLessonDelete

class LessonView(QWidget):
    """View for displaying and managing a lesson's word list"""
    
    # Signals
    back_requested = Signal()
    word_added = Signal(str)  # Chinese text
    back_requested = Signal()
    word_added = Signal(str)  # Chinese text
    word_deleted = Signal(int)  # Row index - ADD THIS LINE

    lesson_delete_requested = Signal(str) # filename
    
    def __init__(self):
        super().__init__()
        self.current_lesson = None
        self.display_words = []  # Words in current display order
        self.init_ui()
        self.deleteLesson_modal = None
    
    def init_ui(self):
        """Initialize the user interface"""
        layout = QVBoxLayout(self)
        
        # Back button (first row)
        self.back_button = QPushButton("← Back to Menu")
        self.back_button.clicked.connect(self.back_requested.emit)
        self.back_button.setMaximumWidth(150)
        layout.addWidget(self.back_button, alignment=Qt.AlignLeft)
        
        # Lesson title (second row)
        self.lesson_title_label = QLabel("")
        self.lesson_title_label.setAlignment(Qt.AlignLeft)
        lesson_font = QFont("SimSun")
        lesson_font.setPointSize(16)
        lesson_font.setBold(True)
        self.lesson_title_label.setFont(lesson_font)
        layout.addWidget(self.lesson_title_label)
        
        # Lesson description (third row)
        self.lesson_description_label = QLabel("")
        self.lesson_description_label.setAlignment(Qt.AlignLeft)
        self.lesson_description_label.setWordWrap(True)
        self.lesson_description_label.setStyleSheet("color: gray; margin-bottom: 10px;")
        layout.addWidget(self.lesson_description_label)
        
        # Controls row
        self._create_controls_section(layout)
        
        # Separator line
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setFrameShadow(QFrame.Sunken)
        layout.addWidget(separator)
        
        # Add new word section
        self._create_add_word_section(layout)
        
        # Word table
        self._create_word_table(layout)

        # Footer
        self._create_footer(layout)
        
    def _create_controls_section(self, parent_layout):
        """Create the controls section with word count and toggles"""
        controls_layout = QHBoxLayout()
        
        # Word count label
        self.word_count_label = QLabel("")
        self.word_count_label.setAlignment(Qt.AlignLeft)
        controls_layout.addWidget(self.word_count_label)
        
        # Spacer
        controls_layout.addStretch()
        
        # Column visibility toggles
        toggle_layout = QHBoxLayout()
        
        self.chinese_checkbox = QCheckBox("Chinese")
        self.chinese_checkbox.setChecked(True)
        self.chinese_checkbox.toggled.connect(self._toggle_chinese_column)
        toggle_layout.addWidget(self.chinese_checkbox)
        
        self.pinyin_checkbox = QCheckBox("Pinyin")
        self.pinyin_checkbox.setChecked(True)
        self.pinyin_checkbox.toggled.connect(self._toggle_pinyin_column)
        toggle_layout.addWidget(self.pinyin_checkbox)
        
        self.english_checkbox = QCheckBox("English")
        self.english_checkbox.setChecked(True)
        self.english_checkbox.toggled.connect(self._toggle_english_column)
        toggle_layout.addWidget(self.english_checkbox)
        
        controls_layout.addLayout(toggle_layout)
        
        # Shuffle button
        self.shuffle_button = QPushButton("🔀 Shuffle")
        self.shuffle_button.clicked.connect(self._shuffle_words)
        self.shuffle_button.setMaximumWidth(100)
        controls_layout.addWidget(self.shuffle_button)
        
        parent_layout.addLayout(controls_layout)
    
    def _create_add_word_section(self, parent_layout):
        """Create the add new word section"""
        add_word_layout = QVBoxLayout()
        
        # Add word title
        add_word_title = QLabel("Add New Word:")
        add_word_title.setStyleSheet("font-weight: bold; margin-top: 5px;")
        add_word_layout.addWidget(add_word_title)
        
        # Input and button layout
        input_layout = QHBoxLayout()
        
        self.chinese_input = QLineEdit()
        self.chinese_input.setPlaceholderText("Enter Chinese characters...")
        self.chinese_input.setMaximumWidth(200)
        self.chinese_input.returnPressed.connect(self._add_word)
        input_layout.addWidget(self.chinese_input)
        
        self.add_word_button = QPushButton("Add Word")
        self.add_word_button.clicked.connect(self._add_word)
        self.add_word_button.setMaximumWidth(100)
        input_layout.addWidget(self.add_word_button)
        
        # Status label for add word feedback
        self.add_word_status = QLabel("")
        self.add_word_status.setStyleSheet("color: gray; font-size: 10px;")
        input_layout.addWidget(self.add_word_status)
        
        input_layout.addStretch()
        
        add_word_layout.addLayout(input_layout)
        parent_layout.addLayout(add_word_layout)
    
    def _create_word_table(self, parent_layout):
        """Create the word table widget"""
        self.word_table = QTableWidget()
        self.word_table.setColumnCount(4)
        self.word_table.setHorizontalHeaderLabels(["Chinese", "Pinyin", "English", "Delete"])
        
        # Configure table appearance
        header = self.word_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Stretch)  # Chinese column stretches
        header.setSectionResizeMode(1, QHeaderView.Stretch)  # Pinyin column stretches  
        header.setSectionResizeMode(2, QHeaderView.Stretch)  # English column stretches
        header.setSectionResizeMode(3, QHeaderView.Fixed)    # Delete column fixed width
        
        # Set the delete column to be narrow
        self.word_table.setColumnWidth(3, 60)
        
        self.word_table.setAlternatingRowColors(True)
        self.word_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.word_table.setEditTriggers(QTableWidget.NoEditTriggers)
        
        # Set font for better Chinese character display
        table_font = QFont("SimSun")
        table_font.setPointSize(12)
        self.word_table.setFont(table_font)
        
        parent_layout.addWidget(self.word_table)
    
    def _create_footer(self, parent_layout):
        footer_layout = QHBoxLayout()

        self.delete_lesson_button = QPushButton("Delete Lesson") # Opens Confirmation Modal
        self.delete_lesson_button.setMaximumWidth(100)
        self.delete_lesson_button.clicked.connect(self.show_deleteLesson_modal)
        footer_layout.addWidget(self.delete_lesson_button)


        self.file_info_label = QLabel("")
        self.file_info_label.setAlignment(Qt.AlignCenter)
        self.file_info_label.setStyleSheet("color: gray; font-size: 10px;")
        footer_layout.addWidget(self.file_info_label)

        parent_layout.addLayout(footer_layout)


    def set_lesson(self, lesson: Lesson):
        """Set the current lesson and populate the view"""
        self.current_lesson = lesson
        self.display_words = lesson.words.copy()
        self._populate_lesson_info()
        self._populate_word_table()
        self._clear_add_word_status()
    
    def _populate_lesson_info(self):
        """Update lesson information labels"""
        if not self.current_lesson:
            return
        
        self.lesson_title_label.setText(self.current_lesson.name)
        self.lesson_description_label.setText(self.current_lesson.description)
        self.word_count_label.setText(f"Total words: {self.current_lesson.get_word_count()}")
        
        filename = self.current_lesson.filename or "Unsaved lesson"
        self.file_info_label.setText(f"File: {filename}")
    
    def _populate_word_table(self):
        """Populate the word table with current display words"""
        if not self.display_words:
            self.word_table.setRowCount(0)
            return
    
        self.word_table.setRowCount(len(self.display_words))
    
        for row, word in enumerate(self.display_words):
            # Chinese characters
            chinese_item = QTableWidgetItem(word.chinese)
            chinese_font = QFont("SimSun")
            chinese_font.setPointSize(14)
            chinese_item.setFont(chinese_font)
            self.word_table.setItem(row, 0, chinese_item)
        
            # Pinyin
            pinyin_item = QTableWidgetItem(word.pinyin)
            self.word_table.setItem(row, 1, pinyin_item)
        
            # English
            english_item = QTableWidgetItem(word.english)
            self.word_table.setItem(row, 2, english_item)
            
            # Delete button - use setCellWidget instead of setItem
            delete_button = QPushButton("🗑️")
            delete_button.setMaximumWidth(50)
            delete_button.setMaximumHeight(30)
            delete_button.setToolTip("Delete this word")
            # CHANGE THIS LINE - emit signal instead of handling directly
            delete_button.clicked.connect(lambda checked, r=row: self.word_deleted.emit(r))
            self.word_table.setCellWidget(row, 3, delete_button)
    
        # Adjust row heights for better readability
        self.word_table.resizeRowsToContents()
    
        # Apply current column visibility settings
        self._update_column_visibility()
    
    def show_deleteLesson_modal(self):
        """Show the Deletion Confirmation modal"""
        if not self.deleteLesson_modal:
            self.deleteLesson_modal = ConfirmLessonDelete(filename=self.current_lesson.filename)
            self.deleteLesson_modal.deletion_confirmed.connect(self.lesson_delete_requested.emit)
        

        
        self.deleteLesson_modal.exec()

    def _toggle_chinese_column(self, checked):
        """Toggle visibility of Chinese column"""
        self.word_table.setColumnHidden(0, not checked)
    
    def _toggle_pinyin_column(self, checked):
        """Toggle visibility of Pinyin column"""
        self.word_table.setColumnHidden(1, not checked)
    
    def _toggle_english_column(self, checked):
        """Toggle visibility of English column"""
        self.word_table.setColumnHidden(2, not checked)
    
    def _update_column_visibility(self):
        """Update column visibility based on checkbox states"""
        self.word_table.setColumnHidden(0, not self.chinese_checkbox.isChecked())
        self.word_table.setColumnHidden(1, not self.pinyin_checkbox.isChecked())
        self.word_table.setColumnHidden(2, not self.english_checkbox.isChecked())
    
    def _shuffle_words(self):
        """Shuffle the order of words in the table"""
        if self.display_words:
            random.shuffle(self.display_words)
            self._populate_word_table()
    
    def _add_word(self):
        """Handle adding a new word"""
        chinese_text = self.chinese_input.text().strip()
        if chinese_text:
            self.word_added.emit(chinese_text)
    
    def word_add_success(self, word: Word):
        """Handle successful word addition"""
        self.display_words.append(word)
        self._populate_lesson_info()  # Update word count
        self._populate_word_table()
        self.chinese_input.clear()
        self.set_add_word_status("Word added successfully!", "green")
        
        # Scroll to bottom to show new word
        self.word_table.scrollToBottom()
    
    def word_add_error(self, message: str):
        """Handle word addition error"""
        self.set_add_word_status(message, "red")
    
    def set_add_word_status(self, message: str, color: str = "gray"):
        """Set the add word status message"""
        self.add_word_status.setText(message)
        self.add_word_status.setStyleSheet(f"color: {color}; font-size: 10px;")
    
    def _clear_add_word_status(self):
        """Clear the add word status message"""
        self.add_word_status.setText("")
        self.chinese_input.clear()
    
    def reset_view(self):
        """Reset the view when switching away"""
        self._clear_add_word_status()

    def word_delete_success(self, row: int):
        """Handle successful word deletion from controller"""
        if 0 <= row < len(self.display_words):
            # Remove from display_words
            del self.display_words[row]
            
            # Update UI
            self._populate_lesson_info()  # Update word count
            self._populate_word_table()   # Refresh the word table
            
            self.set_add_word_status("Word deleted successfully!", "red")

    def word_delete_error(self, message: str):
        """Handle word deletion error from controller"""
        self.set_add_word_status(message, "red")
        