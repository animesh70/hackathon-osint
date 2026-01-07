import math
from typing import Tuple

class GeoUtils:
    """Utility functions for geographic calculations"""
    
    EARTH_RADIUS_KM = 6371.0
    
    @staticmethod
    def calculate_distance(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
        """
        Calculate distance between two points using Haversine formula
        Returns distance in kilometers
        """
        # Convert to radians
        lat1_rad = math.radians(lat1)
        lat2_rad = math.radians(lat2)
        lng1_rad = math.radians(lng1)
        lng2_rad = math.radians(lng2)
        
        # Haversine formula
        dlat = lat2_rad - lat1_rad
        dlng = lng2_rad - lng1_rad
        
        a = (math.sin(dlat / 2) ** 2 + 
             math.cos(lat1_rad) * math.cos(lat2_rad) * 
             math.sin(dlng / 2) ** 2)
        
        c = 2 * math.asin(math.sqrt(a))
        distance = GeoUtils.EARTH_RADIUS_KM * c
        
        return distance
    
    @staticmethod
    def get_bounding_box(
        lat: float,
        lng: float,
        radius_km: float
    ) -> Tuple[float, float, float, float]:
        """
        Get bounding box coordinates for a given point and radius
        Returns: (min_lat, min_lng, max_lat, max_lng)
        """
        # Approximate conversion (1 degree latitude ≈ 111 km)
        lat_offset = radius_km / 111.0
        lng_offset = radius_km / (111.0 * math.cos(math.radians(lat)))
        
        min_lat = lat - lat_offset
        max_lat = lat + lat_offset
        min_lng = lng - lng_offset
        max_lng = lng + lng_offset
        
        return (min_lat, min_lng, max_lat, max_lng)
    
    @staticmethod
    def is_within_radius(
        lat1: float,
        lng1: float,
        lat2: float,
        lng2: float,
        radius_km: float
    ) -> bool:
        """Check if two points are within a given radius"""
        distance = GeoUtils.calculate_distance(lat1, lng1, lat2, lng2)
        return distance <= radius_km
    
    @staticmethod
    def get_center_point(locations: list) -> Tuple[float, float]:
        """Get center point of multiple locations"""
        if not locations:
            return (0.0, 0.0)
        
        avg_lat = sum(loc['lat'] for loc in locations) / len(locations)
        avg_lng = sum(loc['lng'] for loc in locations) / len(locations)
        
        return (avg_lat, avg_lng)