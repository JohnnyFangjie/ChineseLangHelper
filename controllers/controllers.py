"""
Main application controller that coordinates between models, views, and services
"""
from PySide6.QtWidgets import QMainWindow, QStackedWidget, QMessageBox
from PySide6.QtCore import QObject
from models.lesson import Lesson
from models.word import Word
from services.lesson_manager_service import LessonManager
from services.chinese_lang_service import chinese_service
from views.menu_view import MenuView
from views.lesson_view import LessonView
from views.modals import AddLessonModal



class MainController(QMainWindow):
    """Main application controller and window"""
    
    def __init__(self):
        super().__init__()
        
        # Initialize services
        self.lesson_manager = LessonManager()
        self.chinese_service = chinese_service
        
        # Current state
        self.current_lesson = None
        
        # Initialize UI
        self.init_ui()
        self.connect_signals()
        
        # Load initial data
        self.refresh_lessons()
    
    def init_ui(self):
        """Initialize the user interface"""
        self.setWindowTitle("Chinese Learning Helper")
        self.setGeometry(100, 100, 900, 700)
        
        # Create stacked widget for view switching
        self.stacked_widget = QStackedWidget()
        self.setCentralWidget(self.stacked_widget)
        
        # Create views
        self.menu_view = MenuView()
        self.lesson_view = LessonView()
        self.addLesson_modal = AddLessonModal()
        
        # Add views to stack
        self.stacked_widget.addWidget(self.menu_view)  # Index 0
        self.stacked_widget.addWidget(self.lesson_view)  # Index 1
        
        # Start with menu view
        self.show_menu_view()
    
    def connect_signals(self):
        """Connect view signals to controller methods"""
        # Menu view signals
        self.menu_view.lesson_selected.connect(self.load_lesson)
        self.menu_view.connect_refresh(self.refresh_lessons)
        self.menu_view.add_lesson_requested.connect(self.add_new_lesson)

        # Lesson view signals
        self.lesson_view.back_requested.connect(self.show_menu_view)
        self.lesson_view.word_added.connect(self.add_word_to_lesson)
        self.lesson_view.word_deleted.connect(self.delete_word_from_lesson)
        self.lesson_view.lesson_delete_requested.connect(self.delete_lesson)
    
    def show_menu_view(self):
        """Switch to menu view"""
        self.lesson_view.reset_view()
        self.stacked_widget.setCurrentIndex(0)
        self.refresh_lessons()  # Refresh in case files were modified
    
    def show_lesson_view(self):
        """Switch to lesson view"""
        self.stacked_widget.setCurrentIndex(1)
    
    def refresh_lessons(self):
        """Refresh the lesson list in menu view"""
        lessons_info = self.lesson_manager.get_all_lessons_info()
        self.menu_view.populate_lessons(lessons_info)
        
        if not lessons_info:
            self.menu_view.set_status("No lesson files found. Create some JSON files in the 'data' folder.")
        else:
            self.menu_view.set_status(f"Found {len(lessons_info)} lesson file(s)")
    
    def load_lesson(self, filename: str):
        """Load and display a lesson"""
        lesson = self.lesson_manager.load_lesson(filename)
        
        if lesson is None:
            self.show_error("Error", f"Could not load lesson file: {filename}")
            return
        
        self.current_lesson = lesson
        self.lesson_view.set_lesson(lesson)
        self.show_lesson_view()
    
    def add_word_to_lesson(self, chinese_text: str):
        """Add a new word to the current lesson"""
        if not self.current_lesson:
            self.lesson_view.word_add_error("No lesson loaded")
            return
        
        # Validate input
        is_valid, error_message = self.chinese_service.validate_chinese_text(chinese_text)
        if not is_valid:
            self.lesson_view.word_add_error(error_message)
            return
        
        # Check if word already exists
        if any(word.chinese == chinese_text for word in self.current_lesson.words):
            self.lesson_view.word_add_error("Word already exists in this lesson")
            return
        
        # Create new word with auto-generated pinyin and translation
        try:
            new_word = self.chinese_service.create_word_from_chinese(chinese_text)
        except Exception as e:
            self.lesson_view.word_add_error(f"Error processing Chinese text: {str(e)}")
            return
        
        # Add word to lesson
        success = self.current_lesson.add_word(new_word)
        if not success:
            self.lesson_view.word_add_error("Failed to add word to lesson")
            return
        
        # Save lesson to file
        if not self.lesson_manager.save_lesson(self.current_lesson):
            # Remove the word if saving failed
            self.current_lesson.remove_word(chinese_text)
            self.lesson_view.word_add_error("Failed to save lesson file")
            return
        
        # Notify view of successful addition
        self.lesson_view.word_add_success(new_word)
    
    def delete_word_from_lesson(self, row: int):
        """Delete a word from the current lesson"""
        if not self.current_lesson:
            self.lesson_view.word_delete_error("No lesson loaded")
            return
        
        # Check if row is valid
        if row < 0 or row >= len(self.lesson_view.display_words):
            self.lesson_view.word_delete_error("Invalid word selection")
            return
        
        # Get the word to delete
        word_to_delete = self.lesson_view.display_words[row]
        
        # Remove word from lesson
        success = self.current_lesson.remove_word(word_to_delete.chinese)
        if not success:
            self.lesson_view.word_delete_error("Failed to remove word from lesson")
            return
        
        # Save lesson to file
        if not self.lesson_manager.save_lesson(self.current_lesson):
            # Re-add the word if saving failed
            self.current_lesson.add_word(word_to_delete)
            self.lesson_view.word_delete_error("Failed to save lesson file")
            return
        
        # Notify view of successful deletion
        self.lesson_view.word_delete_success(row)

    def add_new_lesson(self, name: str, description: str):
        """Create a new lesson from modal input"""
        try:
            # Create new lesson object
            new_lesson = Lesson(name=name, description=description, words=[])
            
            # Generate filename (you might want to sanitize the name)
            filename = f"{name.lower().replace(' ', '_')}.json"
            new_lesson.filename = filename
            
            # Save the lesson
            if self.lesson_manager.save_lesson(new_lesson):
                self.show_info("Success", f"Lesson '{name}' created successfully!")
                self.refresh_lessons()  # Refresh the lesson list
            else:
                self.show_error("Error", "Failed to create lesson file")
                
        except Exception as e:
            self.show_error("Error", f"Failed to create lesson: {str(e)}")

    def delete_lesson(self, filename: str):
        """Deletes a lesson"""
        print(f"Deleting lesson: {filename}")
        
        try:
            if self.lesson_manager.delete_lesson(filename):
                self.show_info("Success", f"Lesson file '{filename}' deleted successfully!")
                self.refresh_lessons()
                self.show_menu_view()
            else:
                self.show_error("Error", "Failed to delete lesson file")
        
        except Exception as e:
            self.show_error("Error", f"Failed to delete lesson: {str(e)}")

    def show_error(self, title: str, message: str):
        """Show error message dialog"""
        QMessageBox.critical(self, title, message)
    
    def show_info(self, title: str, message: str):
        """Show information message dialog"""
        QMessageBox.information(self, title, message)
    
    def show_warning(self, title: str, message: str):
        """Show warning message dialog"""
        QMessageBox.warning(self, title, message)