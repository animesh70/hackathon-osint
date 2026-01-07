from typing import List, Tuple, Optional
from models.location import Location

class LocationInferenceService:
    """Service for inferring locations from images and text"""
    
    def __init__(self):
        # In a real implementation, this would load ML models
        self.landmarks_db = self._load_landmarks_database()
    
    def _load_landmarks_database(self) -> dict:
        """Load known landmarks database"""
        return {
            "india_gate": {"lat": 28.6129, "lng": 77.2295, "name": "India Gate, Delhi"},
            "marine_drive": {"lat": 18.9432, "lng": 72.8236, "name": "Marine Drive, Mumbai"},
            "goa_beach": {"lat": 15.2993, "lng": 74.1240, "name": "Goa Beaches"},
            "cubbon_park": {"lat": 12.9762, "lng": 77.5929, "name": "Cubbon Park, Bangalore"}
        }
    
    def infer_from_image(self, image_path: str) -> Optional[Location]:
        """
        Infer location from image using computer vision
        In production, this would use AI/ML models
        """
        # Placeholder for actual image analysis
        # Would use models like:
        # - Object detection for landmarks
        # - Scene classification
        # - Text recognition for signs
        pass
    
    def infer_from_text(self, text: str) -> Optional[List[str]]:
        """
        Extract location clues from text
        """
        # Placeholder for NLP-based location extraction
        # Would use NER (Named Entity Recognition)
        location_keywords = []
        
        # Simple keyword matching (would be more sophisticated in production)
        cities = ["Delhi", "Mumbai", "Goa", "Bangalore", "Kerala", "Chennai", "Kolkata"]
        for city in cities:
            if city.lower() in text.lower():
                location_keywords.append(city)
        
        return location_keywords if location_keywords else None
    
    def calculate_confidence(
        self,
        has_gps: bool,
        image_features: List[str],
        text_clues: List[str]
    ) -> Tuple[str, str]:
        """
        Calculate confidence level based on available data
        Returns: (confidence_level, confidence_description)
        """
        if has_gps:
            return ("high", "GPS metadata available")
        
        feature_count = len(image_features) + len(text_clues)
        
        if feature_count >= 3:
            return ("medium", "Multiple visual and textual clues")
        elif feature_count >= 1:
            return ("low", "Limited location indicators")
        else:
            return ("very_low", "Insufficient location data")
    
    def cluster_nearby_locations(
        self,
        locations: List[Location],
        radius_km: float = 10
    ) -> List[Location]:
        """
        Cluster locations that are close together
        """
        from .geo_utils import GeoUtils
        
        clustered = []
        processed = set()
        
        for i, loc1 in enumerate(locations):
            if i in processed:
                continue
            
            cluster = [loc1]
            for j, loc2 in enumerate(locations[i+1:], start=i+1):
                if j in processed:
                    continue
                
                distance = GeoUtils.calculate_distance(
                    loc1.lat, loc1.lng,
                    loc2.lat, loc2.lng
                )
                
                if distance <= radius_km:
                    cluster.append(loc2)
                    processed.add(j)
            
            if len(cluster) > 1:
                # Create cluster location
                avg_lat = sum(l.lat for l in cluster) / len(cluster)
                avg_lng = sum(l.lng for l in cluster) / len(cluster)
                
                cluster_loc = Location(
                    lat=avg_lat,
                    lng=avg_lng,
                    location_type='cluster',
                    name=f"{cluster[0].name} Area",
                    confidence='high',
                    description=f"Multiple posts from same area",
                    image_features=[f for loc in cluster for f in loc.image_features],
                    count=len(cluster)
                )
                clustered.append(cluster_loc)
            else:
                clustered.append(loc1)
            
            processed.add(i)
        
        return clustered