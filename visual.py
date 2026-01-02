# ==================== IMPORTS ====================

from flask import Blueprint, request, jsonify
from dotenv import load_dotenv
import os
import requests
import json
import base64
import tempfile
import traceback
import time
from datetime import datetime
from PIL import Image
from PIL.ExifTags import TAGS, GPSTAGS
import re

# ==================== LOAD ENVIRONMENT VARIABLES ====================
# Load .env file BEFORE accessing any environment variables
load_dotenv()

# ==================== LOAD CONFIGURATION ====================
print("\n" + "="*60)
print("📌 LOADING CONFIGURATION")
print("="*60)

AI_SERVICE = os.getenv("AI_SERVICE", "").lower().strip()
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "").strip()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "").strip()
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "").strip()

# Debug output
print(f"AI_SERVICE: '{AI_SERVICE}' (empty={not AI_SERVICE})")
print(f"GROQ_API_KEY: {'✓ Set (' + GROQ_API_KEY[:10] + '...)' if GROQ_API_KEY else '✗ Not set'}")
print(f"GEMINI_API_KEY: {'✓ Set (' + GEMINI_API_KEY[:10] + '...)' if GEMINI_API_KEY else '✗ Not set'}")
print(f"ANTHROPIC_API_KEY: {'✓ Set (' + ANTHROPIC_API_KEY[:10] + '...)' if ANTHROPIC_API_KEY else '✗ Not set'}")

# Validate AI service configuration
if AI_SERVICE:
    print(f"\n[CONFIG] ✓ AI Service selected: {AI_SERVICE}")
    if AI_SERVICE == "groq" and not GROQ_API_KEY:
        print("[CONFIG] ⚠️ Groq selected but no API key found")
        AI_SERVICE = None
    elif AI_SERVICE == "gemini" and not GEMINI_API_KEY:
        print("[CONFIG] ⚠️ Gemini selected but no API key found")
        AI_SERVICE = None
    elif AI_SERVICE == "anthropic" and not ANTHROPIC_API_KEY:
        print("[CONFIG] ⚠️ Anthropic selected but no API key found")
        AI_SERVICE = None
    else:
        print(f"[CONFIG] ✓ API key found for {AI_SERVICE}")
else:
    print("\n[CONFIG] ✗ No AI service configured")
    print("[CONFIG] Please set AI_SERVICE in .env file (groq/gemini/anthropic)")

print("="*60 + "\n")

visual_bp = Blueprint("visual", __name__)


# ==================== EXIF EXTRACTOR ====================
class EXIFExtractor:
    @staticmethod
    def extract_exif(image_path):
        """Extract EXIF data including GPS coordinates"""
        try:
            print(f"[EXIF] Extracting from: {image_path}")
            image = Image.open(image_path)
            exif_data = image._getexif()
            
            if not exif_data:
                print("[EXIF] No EXIF data found")
                return {'has_exif': False, 'coordinates': None}

            gps_data = {}
            for tag_id, value in exif_data.items():
                tag = TAGS.get(tag_id, tag_id)
                if tag == 'GPSInfo':
                    print("[EXIF] GPS info found")
                    for gps_tag_id in value:
                        gps_tag = GPSTAGS.get(gps_tag_id, gps_tag_id)
                        gps_data[gps_tag] = value[gps_tag_id]

            coords = EXIFExtractor.parse_gps(gps_data) if gps_data else None
            
            if coords:
                print(f"[EXIF] ✓ Coordinates found: {coords}")
            
            return {'has_exif': True, 'coordinates': coords}

        except Exception as e:
            print(f"[EXIF] Error: {e}")
            return {'has_exif': False, 'coordinates': None}

    @staticmethod
    def parse_gps(gps_data):
        """Parse GPS data to coordinates"""
        try:
            def convert_to_degrees(gps_val):
                return float(gps_val[0]) + float(gps_val[1])/60 + float(gps_val[2])/3600
            
            lat = convert_to_degrees(gps_data['GPSLatitude'])
            lon = convert_to_degrees(gps_data['GPSLongitude'])
            
            if gps_data.get('GPSLatitudeRef') == 'S':
                lat = -lat
            if gps_data.get('GPSLongitudeRef') == 'W':
                lon = -lon
                
            return {'latitude': round(lat, 6), 'longitude': round(lon, 6)}
        except Exception as e:
            print(f"[GPS] Parse error: {e}")
            return None


# ==================== COORDINATE EXTRACTOR ====================
class CoordinateExtractor:
    """Extract coordinates from text responses"""
    
    @staticmethod
    def extract_coordinates(text):
        """Try to extract lat/lon coordinates from text"""
        try:
            # Pattern 1: "lat: X, lon: Y" or "latitude: X, longitude: Y"
            pattern1 = r'lat(?:itude)?[:\s]+(-?\d+\.?\d*)[,\s]+lon(?:gitude)?[:\s]+(-?\d+\.?\d*)'
            match1 = re.search(pattern1, text, re.IGNORECASE)
            if match1:
                lat, lon = float(match1.group(1)), float(match1.group(2))
                if -90 <= lat <= 90 and -180 <= lon <= 180:
                    return {'latitude': round(lat, 6), 'longitude': round(lon, 6)}
            
            # Pattern 2: "(X, Y)" format
            pattern2 = r'\((-?\d+\.?\d*),\s*(-?\d+\.?\d*)\)'
            match2 = re.search(pattern2, text)
            if match2:
                lat, lon = float(match2.group(1)), float(match2.group(2))
                if -90 <= lat <= 90 and -180 <= lon <= 180:
                    return {'latitude': round(lat, 6), 'longitude': round(lon, 6)}
            
            return None
        except Exception as e:
            print(f"[COORDS] Extraction error: {e}")
            return None


# ==================== AI ANALYZER ====================
class AIAnalyzer:
    def __init__(self, service):
        self.service = service

    def analyze_image_for_geolocation(self, image_path):
        """Analyze image using AI vision"""
        if not self.service:
            print("[AI] ✗ No AI service available")
            print(f"[AI] AI_SERVICE env var: '{os.getenv('AI_SERVICE')}'")
            return {
                'location_estimate': 'No AI service configured',
                'coordinates_estimate': None,
                'confidence': 0,
                'analysis': 'Please configure AI_SERVICE in .env (groq/gemini/anthropic) and add the corresponding API key',
                'clues': [],
                'landmarks': []
            }

        try:
            print(f"[AI] ✓ Starting analysis with {self.service}")
            
            # Read and encode image
            with open(image_path, "rb") as f:
                img_base64 = base64.b64encode(f.read()).decode('utf-8')
            
            print(f"[AI] Image encoded: {len(img_base64)} bytes")
            
            if self.service == 'groq':
                return self._analyze_with_groq(img_base64)
            elif self.service == 'gemini':
                return self._analyze_with_gemini(img_base64)
            elif self.service == 'anthropic':
                return self._analyze_with_anthropic(img_base64)
            else:
                return {
                    'location_estimate': f'Unknown AI service: {self.service}',
                    'coordinates_estimate': None,
                    'confidence': 0,
                    'analysis': 'Please use groq, gemini, or anthropic',
                    'clues': [],
                    'landmarks': []
                }
            
        except Exception as e:
            print(f"[AI] Error: {e}")
            traceback.print_exc()
            return {
                'location_estimate': 'Analysis failed',
                'coordinates_estimate': None,
                'confidence': 0,
                'analysis': f'Error: {str(e)}',
                'clues': [],
                'landmarks': []
            }

    def _analyze_with_groq(self, img_base64):
        """Analyze using Groq Vision API"""
        try:
            print("[GROQ] Sending request to Groq API...")
            
            headers = {
                "Authorization": f"Bearer {GROQ_API_KEY}",
                "Content-Type": "application/json"
            }

            # Updated prompt for better location analysis
            prompt = """Analyze this image and identify the geographic location where it was taken.

Examine carefully:
- Landmarks, monuments, or famous buildings
- Architectural style and building materials
- Street signs, text, or business names (and their language)
- Vehicles, license plates
- Vegetation, landscape, terrain
- Weather patterns and climate indicators
- Cultural elements

Provide your analysis ONLY as valid JSON in this exact format:
{
  "location_estimate": "City, Country",
  "confidence": 85,
  "clues": ["Eiffel Tower visible", "French architecture", "European street layout"],
  "landmarks": ["Eiffel Tower"],
  "coordinates": {"latitude": 48.8584, "longitude": 2.2945}
}

Rules:
- location_estimate: Be specific (City, Country or Region, Country)
- confidence: 0-100 based on certainty
- clues: List 3-5 visual clues you used
- landmarks: Any recognizable landmarks
- coordinates: ONLY include if confidence is 80+ and you can determine approximate location
- Return ONLY the JSON object, no additional text

If unable to determine location, use:
{"location_estimate": "Unable to determine", "confidence": 0, "clues": [], "landmarks": []}"""

            payload = {
                "model": "meta-llama/llama-4-scout-17b-16e-instruct",
                "messages": [
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{img_base64}"
                                }
                            },
                            {
                                "type": "text",
                                "text": prompt
                            }
                        ]
                    }
                ],
                "temperature": 0.2,
                "max_tokens": 2048
            }

            response = requests.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers=headers,
                json=payload,
                timeout=60
            )
            
            print(f"[GROQ] Status: {response.status_code}")
            
            if response.status_code != 200:
                error_msg = response.text
                print(f"[GROQ] Error: {error_msg}")
                return {
                    'location_estimate': 'API Error',
                    'coordinates_estimate': None,
                    'confidence': 0,
                    'analysis': f'Groq API error: {error_msg[:200]}',
                    'clues': [],
                    'landmarks': []
                }
            
            result = response.json()
            response_text = result['choices'][0]['message']['content']
            print(f"[GROQ] Response: {response_text[:300]}")
            
            return self._parse_ai_response(response_text, "Groq")
        
        except Exception as e:
            print(f"[GROQ] Critical error: {e}")
            traceback.print_exc()
            return {
                'location_estimate': 'Groq error',
                'coordinates_estimate': None,
                'confidence': 0,
                'analysis': str(e),
                'clues': [],
                'landmarks': []
            }

    def _analyze_with_gemini(self, img_base64):
        """Analyze using Gemini API"""
        try:
            print("[GEMINI] Sending request...")
            
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash-exp:generateContent?key={GEMINI_API_KEY}"
            
            headers = {"Content-Type": "application/json"}
            
            prompt = """Analyze this image and estimate the geographic location where it was taken.

Look for landmarks, architecture, signs, vegetation, and any geographic clues.

Return ONLY valid JSON:
{
  "location_estimate": "City, Country",
  "confidence": 0-100,
  "clues": ["clue1", "clue2"],
  "landmarks": ["landmark1"],
  "coordinates": {"latitude": 0.0, "longitude": 0.0}
}

Only include coordinates if highly confident (80+). Otherwise omit coordinates field."""

            payload = {
                "contents": [{
                    "parts": [
                        {
                            "inline_data": {
                                "mime_type": "image/jpeg",
                                "data": img_base64
                            }
                        },
                        {"text": prompt}
                    ]
                }],
                "generationConfig": {
                    "temperature": 0.2,
                    "maxOutputTokens": 1024
                }
            }

            response = requests.post(url, headers=headers, json=payload, timeout=60)
            
            print(f"[GEMINI] Status: {response.status_code}")
            
            if response.status_code != 200:
                error_msg = response.text
                print(f"[GEMINI] Error: {error_msg}")
                return {
                    'location_estimate': 'API Error',
                    'coordinates_estimate': None,
                    'confidence': 0,
                    'analysis': f'Gemini API error: {error_msg[:200]}',
                    'clues': [],
                    'landmarks': []
                }
            
            result = response.json()
            
            try:
                text = result['candidates'][0]['content']['parts'][0]['text']
            except (KeyError, IndexError) as e:
                print(f"[GEMINI] Response structure error: {e}")
                return {
                    'location_estimate': 'Response parse error',
                    'coordinates_estimate': None,
                    'confidence': 0,
                    'analysis': str(result)[:200],
                    'clues': [],
                    'landmarks': []
                }
            
            print(f"[GEMINI] Response: {text[:300]}")
            
            return self._parse_ai_response(text, "Gemini")
        
        except Exception as e:
            print(f"[GEMINI] Critical error: {e}")
            traceback.print_exc()
            return {
                'location_estimate': 'Gemini error',
                'coordinates_estimate': None,
                'confidence': 0,
                'analysis': str(e),
                'clues': [],
                'landmarks': []
            }

    def _analyze_with_anthropic(self, img_base64):
        """Analyze using Claude API"""
        try:
            print("[CLAUDE] Sending request...")
            
            # Check if anthropic library is available
            try:
                import anthropic
            except ImportError:
                print("[CLAUDE] anthropic library not installed")
                return {
                    'location_estimate': 'Library missing',
                    'coordinates_estimate': None,
                    'confidence': 0,
                    'analysis': 'Please install: pip install anthropic',
                    'clues': [],
                    'landmarks': []
                }
            
            client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
            
            prompt = """Analyze this image and estimate the geographic location.

Look for landmarks, architecture, signs, vegetation, and geographic clues.

Return ONLY valid JSON:
{
  "location_estimate": "City, Country",
  "confidence": 0-100,
  "clues": ["clue1", "clue2"],
  "landmarks": ["landmark1"],
  "coordinates": {"latitude": 0.0, "longitude": 0.0}
}

Only include coordinates if highly confident (80+)."""

            message = client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=1024,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "image",
                                "source": {
                                    "type": "base64",
                                    "media_type": "image/jpeg",
                                    "data": img_base64
                                }
                            },
                            {
                                "type": "text",
                                "text": prompt
                            }
                        ]
                    }
                ]
            )
            
            text = message.content[0].text
            print(f"[CLAUDE] Response: {text[:300]}")
            
            return self._parse_ai_response(text, "Claude")
        
        except Exception as e:
            print(f"[CLAUDE] Error: {e}")
            traceback.print_exc()
            return {
                'location_estimate': 'Claude error',
                'coordinates_estimate': None,
                'confidence': 0,
                'analysis': str(e),
                'clues': [],
                'landmarks': []
            }

    def _parse_ai_response(self, text, service_name):
        """Parse AI response and extract location data"""
        try:
            # Try to find JSON in the response
            json_match = re.search(r'\{.*\}', text, re.DOTALL)
            
            if json_match:
                try:
                    parsed = json.loads(json_match.group())
                    print(f"[{service_name}] ✓ JSON parsed successfully")
                    
                    # Extract coordinates if present
                    coords = None
                    if 'coordinates' in parsed and parsed['coordinates']:
                        coords_data = parsed['coordinates']
                        if isinstance(coords_data, dict) and 'latitude' in coords_data and 'longitude' in coords_data:
                            lat = float(coords_data['latitude'])
                            lon = float(coords_data['longitude'])
                            if -90 <= lat <= 90 and -180 <= lon <= 180:
                                coords = {'latitude': round(lat, 6), 'longitude': round(lon, 6)}
                                print(f"[{service_name}] ✓ Coordinates extracted: {coords}")
                    
                    # Fallback: try to extract coordinates from text
                    if not coords:
                        coords = CoordinateExtractor.extract_coordinates(text)
                        if coords:
                            print(f"[{service_name}] ✓ Coordinates extracted from text: {coords}")
                    
                    return {
                        'location_estimate': parsed.get('location_estimate', 'Unknown'),
                        'coordinates_estimate': coords,
                        'confidence': int(parsed.get('confidence', 50)),
                        'analysis': 'Location analysis complete',
                        'clues': parsed.get('clues', []),
                        'landmarks': parsed.get('landmarks', [])
                    }
                    
                except json.JSONDecodeError as e:
                    print(f"[{service_name}] JSON decode error: {e}")
            
            # Fallback: try to extract useful info from plain text
            print(f"[{service_name}] No valid JSON, using text fallback")
            
            # Try to extract coordinates from text
            coords = CoordinateExtractor.extract_coordinates(text)
            
            # Get first line as location estimate
            location_est = text.split('\n')[0][:200] if text else 'Unable to determine'
            
            return {
                'location_estimate': location_est,
                'coordinates_estimate': coords,
                'confidence': 30,
                'analysis': text[:500],
                'clues': [],
                'landmarks': []
            }
            
        except Exception as e:
            print(f"[{service_name}] Parse error: {e}")
            return {
                'location_estimate': 'Parse error',
                'coordinates_estimate': None,
                'confidence': 0,
                'analysis': text[:200] if text else 'No response',
                'clues': [],
                'landmarks': []
            }


# ==================== API ENDPOINTS ====================

@visual_bp.route('/api/geolocation/image', methods=['POST'])
def analyze_image():
    """Analyze image for geolocation"""
    print("\n" + "="*60)
    print("[API] Image analysis request")
    print("="*60)
    
    temp_path = None
    
    try:
        # Validate request
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided', 'success': False}), 400

        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'Empty filename', 'success': False}), 400

        # Save temp file
        tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".jpg")
        temp_path = tmp.name
        tmp.close()  # Close file handle immediately
        file.save(temp_path)
        print(f"[API] File saved: {temp_path}")

        # Step 1: Try EXIF first (most accurate)
        exif_data = EXIFExtractor.extract_exif(temp_path)
        
        if exif_data.get('coordinates'):
            print("[API] ✓ Using EXIF coordinates (GPS metadata)")
            coords = exif_data['coordinates']
            return jsonify({
                'success': True,
                'coordinates': coords,
                'coordinate_source': 'exif',
                'confidence': 100,
                'location_estimate': f"{coords['latitude']}, {coords['longitude']}",
                'analysis': 'GPS coordinates extracted from image EXIF metadata',
                'clues': ['GPS metadata found in image'],
                'landmarks': [],
                'exif_data': exif_data,
                'ai_service_used': AI_SERVICE or 'none',
                'timestamp': datetime.now().isoformat()
            }), 200

        # Step 2: Fall back to AI analysis
        print("[API] No EXIF GPS found, using AI visual analysis...")
        print(f"[API] Current AI_SERVICE value: '{AI_SERVICE}'")
        analyzer = AIAnalyzer(AI_SERVICE)
        ai_result = analyzer.analyze_image_for_geolocation(temp_path)
        
        print(f"[API] AI analysis complete")
        print(f"[API] Location: {ai_result.get('location_estimate')}")
        print(f"[API] Confidence: {ai_result.get('confidence')}%")
        print(f"[API] Coordinates: {ai_result.get('coordinates_estimate')}")
        
        return jsonify({
            'success': True,
            'coordinates': ai_result.get('coordinates_estimate'),
            'coordinate_source': 'ai_estimation' if ai_result.get('coordinates_estimate') else 'ai_description_only',
            'confidence': ai_result.get('confidence', 0),
            'location_estimate': ai_result.get('location_estimate', 'Unable to determine'),
            'analysis': ai_result.get('analysis', ''),
            'clues': ai_result.get('clues', []),
            'landmarks': ai_result.get('landmarks', []),
            'exif_data': exif_data,
            'ai_service_used': AI_SERVICE or 'none',
            'timestamp': datetime.now().isoformat()
        }), 200

    except Exception as e:
        print(f"[API] Critical error: {e}")
        traceback.print_exc()
        return jsonify({
            'error': str(e),
            'success': False,
            'analysis': 'Server error during image analysis'
        }), 500
    
    finally:
        # Cleanup temp file
        if temp_path and os.path.exists(temp_path):
            try:
                time.sleep(0.2)
                os.unlink(temp_path)
                print(f"[CLEANUP] ✓ Temp file deleted")
            except Exception as cleanup_error:
                print(f"[CLEANUP] Warning: {cleanup_error}")


@visual_bp.route('/api/visual/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'online',
        'module': 'visual',
        'ai_service': AI_SERVICE or 'none',
        'services_available': {
            'groq': bool(GROQ_API_KEY),
            'gemini': bool(GEMINI_API_KEY),
            'anthropic': bool(ANTHROPIC_API_KEY)
        },
        'timestamp': datetime.now().isoformat()
    }), 200