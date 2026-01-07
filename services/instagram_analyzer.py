import json
from typing import List, Dict
from models.post import Post
from models.location import Location

class InstagramAnalyzer:
    """Analyzes Instagram posts for location data"""
    
    def __init__(self):
        self.demo_data = self._load_demo_data()
    
    def _load_demo_data(self) -> List[Dict]:
        """Load demo data from JSON file"""
        try:
            with open('data/demo_posts.json', 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            return self._get_default_demo_data()
    
    def _get_default_demo_data(self) -> List[Dict]:
        """Return default demo data if file not found"""
        return [
            {
                "id": "1",
                "username": "demo_user",
                "platform": "instagram",
                "date": "2026-01-02T10:30:00",
                "caption": "Beautiful morning at India Gate! 🇮🇳",
                "location": {
                    "lat": 28.6139,
                    "lng": 77.2090,
                    "type": "exact",
                    "location": "Delhi",
                    "confidence": "high",
                    "description": "Photo with GPS metadata",
                    "imageFeatures": ["India Gate visible", "Urban setting"]
                }
            },
            {
                "id": "2",
                "username": "demo_user",
                "platform": "instagram",
                "date": "2026-01-05T14:20:00",
                "caption": "Weekend vibes at Marine Drive 🌊",
                "location": {
                    "lat": 19.0760,
                    "lng": 72.8777,
                    "type": "cluster",
                    "location": "Mumbai Area",
                    "confidence": "high",
                    "description": "Multiple posts from same area",
                    "imageFeatures": ["Marine Drive", "Coastal area", "High-rise buildings"],
                    "count": 3
                }
            },
            {
                "id": "3",
                "username": "demo_user",
                "platform": "instagram",
                "date": "2026-01-10T09:15:00",
                "caption": "Beach therapy 🏖️",
                "location": {
                    "lat": 15.2993,
                    "lng": 74.1240,
                    "type": "approx",
                    "location": "Goa Region",
                    "confidence": "medium",
                    "description": "Inferred from image content",
                    "imageFeatures": ["Beach", "Palm trees", "Coastal signboards in Hindi"],
                    "radius": 20000
                }
            },
            {
                "id": "4",
                "username": "demo_user",
                "platform": "instagram",
                "date": "2026-01-15T16:45:00",
                "caption": "Back to the tech hub 💻",
                "location": {
                    "lat": 12.9716,
                    "lng": 77.5946,
                    "type": "exact",
                    "location": "Bangalore",
                    "confidence": "high",
                    "description": "Photo with GPS metadata",
                    "imageFeatures": ["Tech park visible", "Cubbon Park"]
                }
            },
            {
                "id": "5",
                "username": "demo_user",
                "platform": "instagram",
                "date": "2026-01-18T11:30:00",
                "caption": "God's own country 🌴",
                "location": {
                    "lat": 9.9312,
                    "lng": 76.2673,
                    "type": "approx",
                    "location": "Kerala Coast",
                    "confidence": "low",
                    "description": "Inferred from image content",
                    "imageFeatures": ["Backwaters", "Traditional boats", "Malayalam text"],
                    "radius": 30000
                }
            }
        ]
    
    def analyze_user(self, username: str, platform: str = "instagram") -> List[Post]:
        """
        Analyze posts from a user (currently returns demo data)
        In production, this would connect to Instagram API
        """
        posts = []
        for post_data in self.demo_data:
            post = Post.from_dict(post_data)
            posts.append(post)
        
        return posts
    
    def get_statistics(self, posts: List[Post]) -> Dict:
        """Calculate statistics from posts"""
        if not posts:
            return {
                'total': 0,
                'exact': 0,
                'approx': 0,
                'clusters': 0,
                'time_span': '0 days'
            }
        
        exact_count = sum(1 for p in posts if p.location and p.location.location_type == 'exact')
        approx_count = sum(1 for p in posts if p.location and p.location.location_type == 'approx')
        cluster_count = sum(1 for p in posts if p.location and p.location.location_type == 'cluster')
        
        # Calculate time span
        dates = [p.date for p in posts]
        if len(dates) > 1:
            dates.sort()
            time_span = (dates[-1] - dates[0]).days
            time_span_str = f"{time_span} days"
        else:
            time_span_str = "0 days"
        
        return {
            'total': len(posts),
            'exact': exact_count,
            'approx': approx_count,
            'clusters': cluster_count,
            'time_span': time_span_str
        }