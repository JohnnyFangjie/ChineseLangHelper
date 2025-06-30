"""
Chinese language processing services
"""
from typing import Optional, List
from models.lesson import Word

try:
    from pypinyin import lazy_pinyin, Style
    from pycccedict.cccedict import CcCedict
    CHINESE_SUPPORT = True
except ImportError:
    CHINESE_SUPPORT = False


class ChineseService:
    """Service for Chinese language processing"""
    
    def __init__(self):
        self.chinese_support = CHINESE_SUPPORT
        self.ccdict = None
        
        if CHINESE_SUPPORT:
            try:
                self.ccdict = CcCedict()
            except Exception as e:
                print(f"Warning: Could not initialize CcCedict: {e}")
                self.ccdict = None
    
    def is_chinese_support_available(self) -> bool:
        """Check if Chinese language support is available"""
        return self.chinese_support
    
    def generate_pinyin(self, chinese_text: str) -> str:
        """Generate pinyin for Chinese text"""
        if not self.chinese_support:
            return "Pinyin generation not available"
        
        try:
            return " ".join(lazy_pinyin(chinese_text, style=Style.TONE))
        except Exception as e:
            return f"Error generating pinyin: {str(e)}"
    
    def get_translation(self, chinese_text: str) -> str:
        """Get English translation for Chinese text"""
        if not self.ccdict:
            return "Translation not available"
        
        try:
            definitions = self.ccdict.get_definitions(chinese_text)
            if definitions:
                if isinstance(definitions, list) and definitions:
                    return '; '.join(definitions)
                elif isinstance(definitions, str):
                    return definitions
                else:
                    return str(definitions)
        except Exception as e:
            return f"Error getting translation: {str(e)}"
        
        return "Translation not found"
    
    def create_word_from_chinese(self, chinese_text: str) -> Word:
        """Create a Word object from Chinese text with auto-generated pinyin and translation"""
        pinyin = self.generate_pinyin(chinese_text)
        translation = self.get_translation(chinese_text)
        
        return Word(
            chinese=chinese_text,
            pinyin=pinyin,
            english=translation
        )
    
    def validate_chinese_text(self, text: str) -> tuple[bool, str]:
        """
        Validate Chinese text input
        Returns (is_valid, error_message)
        """
        if not text or not text.strip():
            return False, "Please enter Chinese characters"
        
        # Add more validation rules as needed
        # For example, check if text contains Chinese characters
        # This is a basic implementation
        
        return True, ""


# Global service instance
chinese_service = ChineseService()