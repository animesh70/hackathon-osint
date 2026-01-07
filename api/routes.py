from flask import jsonify, request, Blueprint
from services.instagram_analyzer import InstagramAnalyzer
from services.location_inference import LocationInferenceService
from services.geo_utils import GeoUtils
import json
from datetime import datetime

# Create the blueprint RIGHT HERE (not in __init__.py)
api_bp = Blueprint('api', __name__)

analyzer = InstagramAnalyzer()
location_service = LocationInferenceService()

# Rest of your code stays exactly the same...

@api_bp.route('/analyze', methods=['POST'])
def analyze_user():
    """
    Analyze a user's public posts for location data
    
    Request JSON:
    {
        "username": "user_handle",
        "platform": "instagram"
    }
    """
    try:
        data = request.get_json()
        username = data.get('username', 'demo_user')
        platform = data.get('platform', 'instagram')
        
        # Analyze posts
        posts = analyzer.analyze_user(username, platform)
        
        # Calculate statistics
        stats = analyzer.get_statistics(posts)
        
        # Convert to dict format
        posts_data = [post.to_dict() for post in posts]
        
        return jsonify({
            'success': True,
            'username': username,
            'platform': platform,
            'posts': posts_data,
            'statistics': stats,
            'analyzed_at': datetime.now().isoformat()
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@api_bp.route('/demo-data', methods=['GET'])
def get_demo_data():
    """Get demo data for testing"""
    try:
        posts = analyzer.analyze_user('demo_user')
        posts_data = [post.to_dict() for post in posts]
        stats = analyzer.get_statistics(posts)
        
        return jsonify({
            'success': True,
            'posts': posts_data,
            'statistics': stats
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@api_bp.route('/calculate-distance', methods=['POST'])
def calculate_distance():
    """
    Calculate distance between two points
    
    Request JSON:
    {
        "lat1": 28.6139,
        "lng1": 77.2090,
        "lat2": 19.0760,
        "lng2": 72.8777
    }
    """
    try:
        data = request.get_json()
        lat1 = float(data['lat1'])
        lng1 = float(data['lng1'])
        lat2 = float(data['lat2'])
        lng2 = float(data['lng2'])
        
        distance = GeoUtils.calculate_distance(lat1, lng1, lat2, lng2)
        
        return jsonify({
            'success': True,
            'distance_km': round(distance, 2)
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400

@api_bp.route('/export', methods=['POST'])
def export_analysis():
    """Export analysis results as JSON"""
    try:
        data = request.get_json()
        username = data.get('username', 'demo_user')
        
        posts = analyzer.analyze_user(username)
        posts_data = [post.to_dict() for post in posts]
        stats = analyzer.get_statistics(posts)
        
        export_data = {
            'username': username,
            'analyzed_at': datetime.now().isoformat(),
            'statistics': stats,
            'posts': posts_data
        }
        
        # Save to file
        filename = f"analysis_{username}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        filepath = f"data/analysis_results/{filename}"
        
        with open(filepath, 'w') as f:
            json.dump(export_data, f, indent=2)
        
        return jsonify({
            'success': True,
            'filename': filename,
            'data': export_data
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@api_bp.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat()
    })