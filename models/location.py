from typing import List, Optional

class Location:
    """Represents a geographic location with confidence metrics"""
    
    def __init__(
        self,
        lat: float,
        lng: float,
        location_type: str,  # 'exact', 'approx', 'cluster'
        name: str,
        confidence: str,  # 'high', 'medium', 'low'
        description: str,
        image_features: Optional[List[str]] = None,
        radius: Optional[int] = None,
        count: Optional[int] = None
    ):
        self.lat = lat
        self.lng = lng
        self.location_type = location_type
        self.name = name
        self.confidence = confidence
        self.description = description
        self.image_features = image_features or []
        self.radius = radius
        self.count = count
    
    def to_dict(self):
        """Convert location to dictionary"""
        data = {
            'lat': self.lat,
            'lng': self.lng,
            'type': self.location_type,
            'location': self.name,
            'confidence': self.confidence,
            'description': self.description,
            'imageFeatures': self.image_features
        }
        
        if self.radius:
            data['radius'] = self.radius
        if self.count:
            data['count'] = self.count
        
        return data
    
    @classmethod
    def from_dict(cls, data: dict):
        """Create Location from dictionary"""
        return cls(
            lat=data['lat'],
            lng=data['lng'],
            location_type=data['type'],
            name=data['location'],
            confidence=data['confidence'],
            description=data['description'],
            image_features=data.get('imageFeatures', []),
            radius=data.get('radius'),
            count=data.get('count')
        )