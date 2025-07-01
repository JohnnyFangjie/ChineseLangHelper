"""
Lesson management service for handling lesson files and operations
"""
import os
import json
from typing import List, Optional, Dict, Any
from models.lesson import Lesson, Word


class LessonManager:
    """Manages lesson files and operations"""
    
    def __init__(self, data_folder: str = "data"):
        self.data_folder = data_folder
        self.ensure_data_folder_exists()
    
    def ensure_data_folder_exists(self) -> None:
        """Create data folder if it doesn't exist and add sample data"""
        if not os.path.exists(self.data_folder):
            os.makedirs(self.data_folder)
            self._create_sample_lesson()
    
    def _create_sample_lesson(self) -> None:
        """Create a sample lesson file for demonstration"""
        sample_words = [
            Word("你好", "nǐ hǎo", "hello"),
            Word("谢谢", "xiè xiè", "thank you"),
            Word("再见", "zài jiàn", "goodbye"),
            Word("对不起", "duì bù qǐ", "sorry"),
            Word("不客气", "bù kè qì", "you're welcome"),
            Word("早上好", "zǎo shàng hǎo", "good morning")
        ]
        
        sample_lesson = Lesson(
            name="Basic Greetings",
            description="Common Chinese greetings and polite expressions",
            words=sample_words
        )
        
        filepath = os.path.join(self.data_folder, "basic_greetings.json")
        sample_lesson.save_to_file(filepath)
    
    def get_lesson_files(self) -> List[str]:
        """Get list of all JSON lesson files"""
        try:
            return [f for f in os.listdir(self.data_folder) if f.endswith('.json')]
        except FileNotFoundError:
            return []
    
    def get_lesson_info(self, filename: str) -> Dict[str, Any]:
        """Get lesson information without loading full lesson"""
        filepath = os.path.join(self.data_folder, filename)
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            return {
                'filename': filename,
                'name': data.get('name', filename.replace('.json', '')),
                'description': data.get('description', 'No description available'),
                'word_count': len(data.get('words', [])),
                'valid': True,
                'error': None
            }
        except Exception as e:
            return {
                'filename': filename,
                'name': filename.replace('.json', ''),
                'description': f"Error reading file: {str(e)}",
                'word_count': 0,
                'valid': False,
                'error': str(e)
            }
    
    def load_lesson(self, filename: str) -> Optional[Lesson]:
        """Load a lesson from file"""
        filepath = os.path.join(self.data_folder, filename)
        
        try:
            return Lesson.from_file(filepath)
        except Exception as e:
            print(f"Error loading lesson {filename}: {e}")
            return None
    
    def save_lesson(self, lesson: Lesson, filename: Optional[str] = None) -> bool:
        """Save a lesson to file"""
        if filename:
            lesson.filename = filename
        elif not lesson.filename:
            # Generate filename from lesson name
            safe_name = "".join(c for c in lesson.name if c.isalnum() or c in (' ', '-', '_')).strip()
            safe_name = safe_name.replace(' ', '_').lower()
            lesson.filename = f"{safe_name}.json"
        
        filepath = os.path.join(self.data_folder, lesson.filename)
        
        try:
            lesson.save_to_file(filepath)
            return True
        except Exception as e:
            print(f"Error saving lesson: {e}")
            return False
    
    def create_new_lesson(self, name: str, description: str = "") -> Lesson:
        """Create a new empty lesson"""
        return Lesson(
            name=name,
            description=description,
            words=[]
        )
    
    def delete_lesson(self, filename: str) -> bool:
        """Delete a lesson file"""
        filepath = os.path.join(self.data_folder, filename)
        
        try:
            os.remove(filepath)
            return True
        except Exception as e:
            print(f"Error deleting lesson {filename}: {e}")
            return False
    
    def duplicate_lesson(self, original_filename: str, new_name: str) -> Optional[Lesson]:
        """Create a duplicate of an existing lesson with a new name"""
        original_lesson = self.load_lesson(original_filename)
        if not original_lesson:
            return None
        
        # Create new lesson with copied data
        new_lesson = Lesson(
            name=new_name,
            description=f"Copy of {original_lesson.description}",
            words=original_lesson.words.copy()
        )
        
        if self.save_lesson(new_lesson):
            return new_lesson
        return None
    
    def get_all_lessons_info(self) -> List[Dict[str, Any]]:
        """Get information for all lesson files"""
        lesson_files = self.get_lesson_files()
        return [self.get_lesson_info(filename) for filename in sorted(lesson_files)]

    def update_name(self):
        pass

    def update_description(self):
        pass

    