from typing import Dict
from dataclasses import dataclass, asdict

@dataclass
class Word:
    """Represents a single Chinese word with its translations"""
    chinese: str
    pinyin: str
    english: str
    
    def to_dict(self) -> Dict[str, str]:
        """Convert to dictionary for JSON serialization"""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, str]) -> 'Word':
        """Create Word from dictionary"""
        return cls(
            chinese=data.get('chinese', ''),
            pinyin=data.get('pinyin', ''),
            english=data.get('english', '')
        )