import json
import os
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from models.word import Word

@dataclass
class Lesson:
    """Represents a lesson containing multiple words"""
    name: str
    description: str
    words: List[Word]
    filename: Optional[str] = None
    
    def __post_init__(self):
        """Ensure words are Word objects"""
        if self.words and isinstance(self.words[0], dict):
            self.words = [Word.from_dict(word) for word in self.words]
    
    def add_word(self, word: Word) -> bool:
        """Add a word to the lesson. Returns True if added, False if already exists"""
        if any(w.chinese == word.chinese for w in self.words):
            return False
        self.words.append(word)
        return True
    
    def remove_word(self, chinese: str) -> bool:
        """Remove a word by Chinese text. Returns True if removed, False if not found"""
        for i, word in enumerate(self.words):
            if word.chinese == chinese:
                self.words.pop(i)
                return True
        return False
    
    def get_word_count(self) -> int:
        """Get the number of words in this lesson"""
        return len(self.words)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            'name': self.name,
            'description': self.description,
            'words': [word.to_dict() for word in self.words]
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any], filename: Optional[str] = None) -> 'Lesson':
        """Create Lesson from dictionary"""
        words_data = data.get('words', [])
        words = [Word.from_dict(word_data) for word_data in words_data]
        
        return cls(
            name=data.get('name', 'Unknown Lesson'),
            description=data.get('description', ''),
            words=words,
            filename=filename
        )
    
    @classmethod
    def from_file(cls, filepath: str) -> 'Lesson':
        """Load lesson from JSON file"""
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        filename = os.path.basename(filepath)
        return cls.from_dict(data, filename)
    
    def save_to_file(self, filepath: str) -> None:
        """Save lesson to JSON file"""
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(self.to_dict(), f, ensure_ascii=False, indent=2)
        
        # Update filename if not set
        if not self.filename:
            self.filename = os.path.basename(filepath)