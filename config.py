import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Application configuration"""
    
    # Flask settings
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    DEBUG = os.environ.get('DEBUG', 'True').lower() == 'true'
    HOST = os.environ.get('HOST', '0.0.0.0')
    PORT = int(os.environ.get('PORT', 5000))
    
    # API Keys (for future Instagram API integration)
    INSTAGRAM_CLIENT_ID = os.environ.get('INSTAGRAM_CLIENT_ID', '')
    INSTAGRAM_CLIENT_SECRET = os.environ.get('INSTAGRAM_CLIENT_SECRET', '')
    
    # Data settings
    MAX_POSTS_TO_ANALYZE = 50
    DEFAULT_CONFIDENCE_THRESHOLD = 0.6
    
    # Location inference settings
    EXACT_GPS_CONFIDENCE = 0.95
    VISUAL_INFERENCE_CONFIDENCE = 0.60
    TEXT_INFERENCE_CONFIDENCE = 0.50
    
    # Map settings
    DEFAULT_MAP_CENTER = [20.5937, 78.9629]  # Center of India
    DEFAULT_ZOOM_LEVEL = 5
    
    # File paths
    DATA_DIR = 'data'
    DEMO_DATA_FILE = 'data/demo_posts.json'
    RESULTS_DIR = 'data/analysis_results'