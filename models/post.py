from datetime import datetime
from typing import List, Optional

class Post:
    """Represents a social media post with location data"""
    
    def __init__(
        self,
        post_id: str,
        username: str,
        platform: str,
        date: str,
        caption: Optional[str] = None,
        image_url: Optional[str] = None,
        location: Optional['Location'] = None
    ):
        self.post_id = post_id
        self.username = username
        self.platform = platform
        self.date = datetime.fromisoformat(date) if isinstance(date, str) else date
        self.caption = caption
        self.image_url = image_url
        self.location = location
    
    def to_dict(self):
        """Convert post to dictionary"""
        return {
            'id': self.post_id,
            'username': self.username,
            'platform': self.platform,
            'date': self.date.isoformat(),
            'caption': self.caption,
            'image_url': self.image_url,
            'location': self.location.to_dict() if self.location else None
        }
    
    @classmethod
    def from_dict(cls, data: dict):
        """Create Post from dictionary"""
        from .location import Location
        
        location = None
        if data.get('location'):
            location = Location.from_dict(data['location'])
        
        return cls(
            post_id=data['id'],
            username=data['username'],
            platform=data['platform'],
            date=data['date'],
            caption=data.get('caption'),
            image_url=data.get('image_url'),
            location=location
        )