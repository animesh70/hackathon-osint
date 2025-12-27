from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
from bs4 import BeautifulSoup
import os
import re
from datetime import datetime
import time
from typing import Dict, List, Any, Optional, Tuple
import json
import base64
import io
import tempfile

# Image and Video processing
from PIL import Image
from PIL.ExifTags import TAGS, GPSTAGS
import cv2

app = Flask(__name__)
CORS(app)

# Configuration
ANTHROPIC_API_KEY = os.environ.get('ANTHROPIC_API_KEY', '')
GROQ_API_KEY = os.environ.get('GROQ_API_KEY', '')
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY', '')
HUGGINGFACE_API_KEY = os.environ.get('HUGGINGFACE_API_KEY', '')
GITHUB_TOKEN = os.environ.get('GITHUB_TOKEN', '')
HIBP_API_KEY = os.environ.get('HIBP_API_KEY', '')

# Determine which AI service to use
AI_SERVICE = None
if GROQ_API_KEY:
    AI_SERVICE = 'groq'
elif GEMINI_API_KEY:
    AI_SERVICE = 'gemini'
elif ANTHROPIC_API_KEY:
    AI_SERVICE = 'anthropic'
elif HUGGINGFACE_API_KEY:
    AI_SERVICE = 'huggingface'


class GitHubCollector:
    """Collect data from GitHub API"""
    
    def __init__(self, token=None):
        self.token = token
        self.headers = {
            'Authorization': f'token {token}' if token else '',
            'Accept': 'application/vnd.github.v3+json'
        }
    
    def collect(self, username: str) -> Dict[str, Any]:
        """Collect GitHub profile data"""
        try:
            user_url = f'https://api.github.com/users/{username}'
            user_response = requests.get(user_url, headers=self.headers, timeout=10)
            
            if user_response.status_code != 200:
                return {'error': 'User not found', 'found': False}
            
            user_data = user_response.json()
            
            repos_url = f'https://api.github.com/users/{username}/repos'
            repos_response = requests.get(repos_url, headers=self.headers, timeout=10)
            repos_data = repos_response.json() if repos_response.status_code == 200 else []
            
            commits_data = []
            for repo in repos_data[:3]:
                commits_url = f"https://api.github.com/repos/{username}/{repo['name']}/commits"
                commits_response = requests.get(commits_url, headers=self.headers, timeout=10)
                if commits_response.status_code == 200:
                    commits_data.extend(commits_response.json()[:5])
            
            return {
                'found': True,
                'platform': 'GitHub',
                'profile': {
                    'username': user_data.get('login'),
                    'name': user_data.get('name'),
                    'bio': user_data.get('bio'),
                    'location': user_data.get('location'),
                    'email': user_data.get('email'),
                    'company': user_data.get('company'),
                    'blog': user_data.get('blog'),
                    'twitter': user_data.get('twitter_username'),
                    'public_repos': user_data.get('public_repos'),
                    'followers': user_data.get('followers'),
                    'following': user_data.get('following'),
                    'created_at': user_data.get('created_at'),
                    'updated_at': user_data.get('updated_at')
                },
                'repositories': [
                    {
                        'name': repo.get('name'),
                        'description': repo.get('description'),
                        'language': repo.get('language'),
                        'stars': repo.get('stargazers_count'),
                        'forks': repo.get('forks_count'),
                        'updated': repo.get('updated_at')
                    }
                    for repo in repos_data[:10]
                ],
                'recent_commits': [
                    {
                        'message': commit.get('commit', {}).get('message'),
                        'date': commit.get('commit', {}).get('author', {}).get('date'),
                        'author': commit.get('commit', {}).get('author', {}).get('name')
                    }
                    for commit in commits_data
                ]
            }
        except Exception as e:
            return {'error': str(e), 'found': False}


class TwitterCollector:
    """Collect data from Twitter/X"""
    
    def collect(self, username: str) -> Dict[str, Any]:
        try:
            return {
                'found': True,
                'platform': 'Twitter/X',
                'profile': {
                    'username': username,
                    'note': 'Twitter API access required for full data collection'
                },
                'posts': [],
                'warning': 'Limited data available without Twitter API credentials'
            }
        except Exception as e:
            return {'error': str(e), 'found': False}


class HaveIBeenPwnedCollector:
    """Check for data breaches"""
    
    def __init__(self, api_key=None):
        self.api_key = api_key
        self.headers = {
            'hibp-api-key': api_key if api_key else '',
            'user-agent': 'OSINT-Dashboard'
        }
    
    def collect(self, email: str) -> Dict[str, Any]:
        try:
            if not self.api_key:
                return {
                    'found': False,
                    'error': 'HaveIBeenPwned API key required',
                    'breaches': []
                }
            
            url = f'https://haveibeenpwned.com/api/v3/breachedaccount/{email}'
            response = requests.get(url, headers=self.headers, timeout=10)
            
            if response.status_code == 404:
                return {
                    'found': True,
                    'email': email,
                    'breaches': [],
                    'status': 'No breaches found'
                }
            elif response.status_code == 200:
                breaches = response.json()
                return {
                    'found': True,
                    'email': email,
                    'breach_count': len(breaches),
                    'breaches': [
                        {
                            'name': breach.get('Name'),
                            'title': breach.get('Title'),
                            'domain': breach.get('Domain'),
                            'breach_date': breach.get('BreachDate'),
                            'added_date': breach.get('AddedDate'),
                            'pwn_count': breach.get('PwnCount'),
                            'description': breach.get('Description'),
                            'data_classes': breach.get('DataClasses', [])
                        }
                        for breach in breaches
                    ],
                    'status': 'Breaches found'
                }
            else:
                return {
                    'found': False,
                    'error': f'API returned status code {response.status_code}'
                }
        except Exception as e:
            return {'error': str(e), 'found': False}


class LinkedInCollector:
    def collect(self, username: str) -> Dict[str, Any]:
        return {
            'found': True,
            'platform': 'LinkedIn',
            'profile': {
                'username': username,
                'note': 'LinkedIn API access required'
            },
            'warning': 'Limited data available'
        }


class RedditCollector:
    def collect(self, username: str) -> Dict[str, Any]:
        try:
            headers = {'User-Agent': 'OSINT-Dashboard/1.0'}
            url = f'https://www.reddit.com/user/{username}/about.json'
            response = requests.get(url, headers=headers, timeout=10)
            
            if response.status_code != 200:
                return {'error': 'User not found', 'found': False}
            
            data = response.json().get('data', {})
            
            return {
                'found': True,
                'platform': 'Reddit',
                'profile': {
                    'username': data.get('name'),
                    'created': datetime.fromtimestamp(data.get('created_utc', 0)).isoformat(),
                    'karma': {
                        'post': data.get('link_karma'),
                        'comment': data.get('comment_karma'),
                        'total': data.get('total_karma')
                    },
                    'is_gold': data.get('is_gold'),
                    'is_mod': data.get('is_mod'),
                    'verified': data.get('verified')
                }
            }
        except Exception as e:
            return {'error': str(e), 'found': False}


class EXIFExtractor:
    """Extract EXIF metadata from images"""
    
    @staticmethod
    def extract_exif(image_path: str) -> Dict[str, Any]:
        """Extract all EXIF data from an image"""
        try:
            image = Image.open(image_path)
            exif_data = image._getexif()
            
            if not exif_data:
                return {'error': 'No EXIF data found', 'has_exif': False}
            
            exif_dict = {}
            gps_data = {}
            
            for tag_id, value in exif_data.items():
                tag = TAGS.get(tag_id, tag_id)
                
                if tag == 'GPSInfo':
                    for gps_tag_id in value:
                        gps_tag = GPSTAGS.get(gps_tag_id, gps_tag_id)
                        gps_data[gps_tag] = value[gps_tag_id]
                else:
                    if isinstance(value, bytes):
                        try:
                            value = value.decode('utf-8', errors='ignore')
                        except:
                            value = str(value)
                    exif_dict[tag] = value
            
            coordinates = None
            if gps_data:
                coordinates = EXIFExtractor.parse_gps(gps_data)
            
            return {
                'has_exif': True,
                'coordinates': coordinates,
                'camera': {
                    'make': exif_dict.get('Make', 'Unknown'),
                    'model': exif_dict.get('Model', 'Unknown'),
                    'software': exif_dict.get('Software', 'Unknown')
                },
                'settings': {
                    'iso': exif_dict.get('ISOSpeedRatings', 'Unknown'),
                    'aperture': exif_dict.get('FNumber', 'Unknown'),
                    'shutter_speed': exif_dict.get('ExposureTime', 'Unknown'),
                    'focal_length': exif_dict.get('FocalLength', 'Unknown')
                },
                'datetime': {
                    'original': exif_dict.get('DateTimeOriginal', 'Unknown'),
                    'digitized': exif_dict.get('DateTimeDigitized', 'Unknown')
                },
                'gps_raw': gps_data,
                'full_exif': exif_dict
            }
        except Exception as e:
            return {'error': str(e), 'has_exif': False}
    
    @staticmethod
    def parse_gps(gps_data: Dict) -> Optional[Dict[str, float]]:
        """Parse GPS coordinates from EXIF GPS data"""
        try:
            lat = gps_data.get('GPSLatitude')
            lat_ref = gps_data.get('GPSLatitudeRef')
            lon = gps_data.get('GPSLongitude')
            lon_ref = gps_data.get('GPSLongitudeRef')
            alt = gps_data.get('GPSAltitude')
            
            if not (lat and lon and lat_ref and lon_ref):
                return None
            
            latitude = EXIFExtractor.convert_to_degrees(lat)
            if lat_ref == 'S':
                latitude = -latitude
            
            longitude = EXIFExtractor.convert_to_degrees(lon)
            if lon_ref == 'W':
                longitude = -longitude
            
            result = {
                'latitude': round(latitude, 6),
                'longitude': round(longitude, 6)
            }
            
            if alt:
                result['altitude'] = float(alt)
            
            return result
        except Exception as e:
            print(f"GPS parsing error: {e}")
            return None
    
    @staticmethod
    def convert_to_degrees(value) -> float:
        """Convert GPS coordinates to degrees"""
        d, m, s = value
        return float(d) + (float(m) / 60.0) + (float(s) / 3600.0)


class VideoFrameExtractor:
    """Extract frames from video for analysis"""
    
    @staticmethod
    def extract_frames(video_path: str, num_frames: int = 5) -> List[str]:
        """Extract evenly spaced frames from video"""
        try:
            cap = cv2.VideoCapture(video_path)
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            
            if total_frames == 0:
                return []
            
            frame_indices = [int(total_frames * i / (num_frames + 1)) for i in range(1, num_frames + 1)]
            extracted_frames = []
            
            for idx in frame_indices:
                cap.set(cv2.CAP_PROP_POS_FRAMES, idx)
                ret, frame = cap.read()
                
                if ret:
                    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.jpg')
                    cv2.imwrite(temp_file.name, frame)
                    extracted_frames.append(temp_file.name)
            
            cap.release()
            return extracted_frames
            
        except Exception as e:
            print(f"Frame extraction error: {e}")
            return []


class AIAnalyzer:
    """Universal AI Analyzer supporting multiple providers"""
    
    def __init__(self, service_type):
        self.service = service_type
    
    def analyze_data(self, collected_data: Dict[str, Any], target: str) -> Dict[str, Any]:
        """Analyze OSINT data using available AI service"""
        
        if not self.service:
            return {
                'error': 'No AI API key configured',
                'entities': [],
                'patterns': [],
                'correlations': [],
                'summary': 'Analysis unavailable - Please add an AI API key to .env'
            }
        
        analysis_prompt = f"""Analyze this OSINT data collected for target: {target}

Data collected:
{json.dumps(collected_data, indent=2)}

Please provide:
1. Extracted entities (names, locations, organizations, emails, usernames)
2. Behavioral patterns and activity insights
3. Cross-platform correlations
4. Risk assessment and exposure level
5. Summary of findings

Format your response as JSON with these keys:
- entities: {{names: [], locations: [], organizations: [], emails: [], usernames: []}}
- patterns: [list of observed patterns]
- correlations: [list of cross-platform connections]
- risk_assessment: {{score: 0-10, level: "LOW/MEDIUM/HIGH/CRITICAL", factors: []}}
- summary: "brief summary"
"""
        
        try:
            if self.service == 'groq':
                return self._analyze_with_groq(analysis_prompt)
            elif self.service == 'gemini':
                return self._analyze_with_gemini(analysis_prompt)
            elif self.service == 'anthropic':
                return self._analyze_with_anthropic(analysis_prompt)
            elif self.service == 'huggingface':
                return self._analyze_with_huggingface(analysis_prompt)
            else:
                return {'error': 'Unknown AI service', 'summary': 'Analysis failed'}
        except Exception as e:
            return {
                'error': str(e),
                'summary': 'Analysis failed',
                'entities': {},
                'patterns': [],
                'correlations': []
            }
    
    def analyze_image_for_geolocation(self, image_path: str, exif_data: Dict = None) -> Dict[str, Any]:
        """Analyze image for geolocation using available AI service with vision"""
        
        if not self.service:
            return {
                'error': 'No AI API key configured',
                'coordinates_estimate': None,
                'confidence': 0,
                'analysis': 'Analysis unavailable'
            }
        
        try:
            with open(image_path, 'rb') as img_file:
                image_data = base64.standard_b64encode(img_file.read()).decode('utf-8')
            
            image_ext = os.path.splitext(image_path)[1].lower()
            media_types = {
                '.jpg': 'image/jpeg',
                '.jpeg': 'image/jpeg',
                '.png': 'image/png',
                '.gif': 'image/gif',
                '.webp': 'image/webp'
            }
            media_type = media_types.get(image_ext, 'image/jpeg')
            
            exif_context = ""
            if exif_data and exif_data.get('has_exif'):
                exif_context = f"""
EXIF Data Available:
- Camera: {exif_data.get('camera', {}).get('make')} {exif_data.get('camera', {}).get('model')}
- Timestamp: {exif_data.get('datetime', {}).get('original', 'Unknown')}
- GPS in EXIF: {'Yes' if exif_data.get('coordinates') else 'No'}
"""
                if exif_data.get('coordinates'):
                    exif_context += f"- GPS Coordinates: {exif_data['coordinates']['latitude']}, {exif_data['coordinates']['longitude']}\n"
            
            prompt = f"""Analyze this image for OSINT geolocation purposes. {exif_context}

Please identify and analyze:

1. **Landmarks and Distinctive Buildings**: Any recognizable structures, monuments, or unique architecture
2. **Visible Text**: Signs, billboards, license plates, street names, store names, or any readable text
3. **Architecture and Urban Features**: Building styles, road infrastructure, urban planning patterns
4. **Environmental Clues**: Vegetation types, terrain, climate indicators, weather conditions
5. **Cultural Indicators**: Language on signs, vehicle types, architectural styles specific to regions
6. **Shadow Analysis**: If visible, analyze shadows to estimate time of day and geographical hints
7. **Additional Context**: Any other details that could help determine location

Based on your analysis, provide:
- Your best estimate of the location (city, region, or country)
- Confidence level (0-100%)
- Specific clues that support your conclusion
- Alternative possible locations if uncertain

Format your response as JSON:
{{
  "location_estimate": "City, Region, Country or best guess",
  "coordinates_estimate": {{"latitude": XX.XXXX, "longitude": XX.XXXX}} or null,
  "confidence": 0-100,
  "primary_clues": ["clue1", "clue2", "clue3"],
  "landmarks_identified": ["landmark1", "landmark2"],
  "text_detected": ["text1", "text2"],
  "architectural_style": "description",
  "environmental_notes": "description",
  "analysis": "detailed explanation of findings and reasoning",
  "alternative_locations": ["location1", "location2"] or []
}}

Be thorough and specific in your analysis."""

            if self.service == 'groq':
                return self._analyze_image_with_groq(image_data, media_type, prompt)
            elif self.service == 'gemini':
                return self._analyze_image_with_gemini(image_data, media_type, prompt)
            elif self.service == 'anthropic':
                return self._analyze_image_with_anthropic(image_data, media_type, prompt)
            else:
                return {
                    'error': f'{self.service} does not support image analysis',
                    'coordinates_estimate': None,
                    'confidence': 0,
                    'analysis': 'Image analysis not available with this AI service'
                }
                
        except Exception as e:
            return {
                'error': str(e),
                'coordinates_estimate': None,
                'confidence': 0,
                'analysis': f'Analysis failed: {str(e)}'
            }
    
    def _analyze_with_groq(self, prompt: str) -> Dict[str, Any]:
        """Analyze using Groq API"""
        url = "https://api.groq.com/openai/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type": "application/json"
        }
        data = {
            "model": "llama-3.1-70b-versatile",
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.7,
            "max_tokens": 2000
        }
        
        response = requests.post(url, headers=headers, json=data, timeout=30)
        response.raise_for_status()
        
        result = response.json()
        response_text = result['choices'][0]['message']['content']
        
        return self._parse_ai_response(response_text)
    
    def _analyze_with_gemini(self, prompt: str) -> Dict[str, Any]:
        """Analyze using Google Gemini API"""
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
        headers = {"Content-Type": "application/json"}
        data = {
            "contents": [{
                "parts": [{"text": prompt}]
            }]
        }
        
        response = requests.post(url, headers=headers, json=data, timeout=30)
        response.raise_for_status()
        
        result = response.json()
        response_text = result['candidates'][0]['content']['parts'][0]['text']
        
        return self._parse_ai_response(response_text)
    
    def _analyze_with_anthropic(self, prompt: str) -> Dict[str, Any]:
        """Analyze using Claude API"""
        import anthropic
        client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
        
        message = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=2000,
            messages=[{"role": "user", "content": prompt}]
        )
        
        response_text = message.content[0].text
        return self._parse_ai_response(response_text)
    
    def _analyze_with_huggingface(self, prompt: str) -> Dict[str, Any]:
        """Analyze using Hugging Face Inference API"""
        url = "https://api-inference.huggingface.co/models/mistralai/Mistral-7B-Instruct-v0.2"
        headers = {"Authorization": f"Bearer {HUGGINGFACE_API_KEY}"}
        data = {"inputs": prompt}
        
        response = requests.post(url, headers=headers, json=data, timeout=30)
        response.raise_for_status()
        
        result = response.json()
        response_text = result[0]['generated_text'] if isinstance(result, list) else result.get('generated_text', '')
        
        return self._parse_ai_response(response_text)
    
    def _analyze_image_with_groq(self, image_data: str, media_type: str, prompt: str) -> Dict[str, Any]:
        """Analyze image using Groq Vision API"""
        url = "https://api.groq.com/openai/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type": "application/json"
        }
        data = {
            "model": "llama-3.2-90b-vision-preview",
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:{media_type};base64,{image_data}"
                            }
                        },
                        {
                            "type": "text",
                            "text": prompt
                        }
                    ]
                }
            ],
            "temperature": 0.7,
            "max_tokens": 2000
        }
        
        response = requests.post(url, headers=headers, json=data, timeout=60)
        response.raise_for_status()
        
        result = response.json()
        response_text = result['choices'][0]['message']['content']
        
        return self._parse_vision_response(response_text)
    
    def _analyze_image_with_gemini(self, image_data: str, media_type: str, prompt: str) -> Dict[str, Any]:
        """Analyze image using Gemini Vision API"""
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
        headers = {"Content-Type": "application/json"}
        data = {
            "contents": [{
                "parts": [
                    {
                        "inline_data": {
                            "mime_type": media_type,
                            "data": image_data
                        }
                    },
                    {
                        "text": prompt
                    }
                ]
            }]
        }
        
        response = requests.post(url, headers=headers, json=data, timeout=60)
        response.raise_for_status()
        
        result = response.json()
        response_text = result['candidates'][0]['content']['parts'][0]['text']
        
        return self._parse_vision_response(response_text)
    
    def _analyze_image_with_anthropic(self, image_data: str, media_type: str, prompt: str) -> Dict[str, Any]:
        """Analyze image using Claude Vision API"""
        import anthropic
        client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
        
        message = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=2000,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image",
                            "source": {
                                "type": "base64",
                                "media_type": media_type,
                                "data": image_data
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
        
        response_text = message.content[0].text
        return self._parse_vision_response(response_text)
    
    def _parse_ai_response(self, response_text: str) -> Dict[str, Any]:
        """Parse AI response and extract JSON"""
        try:
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
            else:
                return {
                    'summary': response_text,
                    'entities': {},
                    'patterns': [],
                    'correlations': [],
                    'risk_assessment': {'score': 0, 'level': 'UNKNOWN', 'factors': []}
                }
        except json.JSONDecodeError:
            return {
                'summary': response_text,
                'entities': {},
                'patterns': [],
                'correlations': [],
                'risk_assessment': {'score': 0, 'level': 'UNKNOWN', 'factors': []}
            }
    
    def _parse_vision_response(self, response_text: str) -> Dict[str, Any]:
        """Parse vision AI response and extract JSON"""
        try:
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
            else:
                return {
                    'location_estimate': 'Unable to determine',
                    'coordinates_estimate': None,
                    'confidence': 0,
                    'analysis': response_text,
                    'primary_clues': [],
                    'landmarks_identified': [],
                    'text_detected': []
                }
        except json.JSONDecodeError:
            return {
                'location_estimate': 'Unable to determine',
                'coordinates_estimate': None,
                'confidence': 0,
                'analysis': response_text,
                'primary_clues': [],
                'landmarks_identified': [],
                'text_detected': []
            }


def calculate_risk_score(data: Dict[str, Any]) -> Dict[str, Any]:
    """Calculate risk score"""
    score = 0.0
    factors = []
    exposures = 0
    critical_issues = 0
    
    if 'haveibeenpwned' in data and data['haveibeenpwned'].get('found'):
        breach_count = data['haveibeenpwned'].get('breach_count', 0)
        if breach_count > 0:
            score += min(breach_count * 2, 4)
            critical_issues += breach_count
            factors.append(f'{breach_count} data breach(es) found')
            exposures += breach_count
    
    platforms_with_email = 0
    for platform, platform_data in data.items():
        if platform_data.get('found') and platform_data.get('profile', {}).get('email'):
            platforms_with_email += 1
            exposures += 1
    
    if platforms_with_email > 0:
        score += min(platforms_with_email * 0.5, 2)
        factors.append(f'Email exposed on {platforms_with_email} platform(s)')
    
    platforms_with_location = 0
    for platform, platform_data in data.items():
        if platform_data.get('found') and platform_data.get('profile', {}).get('location'):
            platforms_with_location += 1
            exposures += 1
    
    if platforms_with_location > 0:
        score += min(platforms_with_location * 0.3, 1.5)
        factors.append(f'Location shared on {platforms_with_location} platform(s)')
    
    platforms_found = sum(1 for p in data.values() if p.get('found'))
    score += min(platforms_found * 0.2, 1)
    
    if score >= 7:
        level = 'CRITICAL'
        critical_issues = max(critical_issues, 2)
    elif score >= 5:
        level = 'HIGH'
        critical_issues = max(critical_issues, 1)
    elif score >= 3:
        level = 'MEDIUM'
    else:
        level = 'LOW'
    
    return {
        'risk': round(min(score, 10), 1),
        'level': level,
        'exposures': exposures,
        'platforms': platforms_found,
        'critical': critical_issues,
        'factors': factors
    }


def generate_findings(data: Dict[str, Any], risk_data: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Generate findings list"""
    findings = []
    
    for platform, platform_data in data.items():
        if platform_data.get('found'):
            profile = platform_data.get('profile', {})
            email = profile.get('email')
            if email:
                findings.append({
                    'type': 'Email',
                    'value': email,
                    'risk': 'MEDIUM',
                    'platforms': platform.capitalize()
                })
            
            username = profile.get('username')
            if username:
                findings.append({
                    'type': 'Username',
                    'value': username,
                    'risk': 'LOW',
                    'platforms': platform.capitalize()
                })
            
            location = profile.get('location')
            if location:
                findings.append({
                    'type': 'Location',
                    'value': location,
                    'risk': 'MEDIUM',
                    'platforms': platform.capitalize()
                })
    
    if 'haveibeenpwned' in data and data['haveibeenpwned'].get('breach_count', 0) > 0:
        findings.append({
            'type': 'Credential',
            'value': f"Found in {data['haveibeenpwned']['breach_count']} breach database(s)",
            'risk': 'CRITICAL',
            'platforms': 'HaveIBeenPwned'
        })
    
    return findings[:10]


@app.route('/api/analyze', methods=['POST'])
def analyze():
    """Main endpoint for OSINT analysis"""
    try:
        data = request.get_json()
        target = data.get('target', '')
        platforms = data.get('platforms', [])
        
        if not target:
            return jsonify({'error': 'Target parameter required'}), 400
        
        github_collector = GitHubCollector(GITHUB_TOKEN)
        twitter_collector = TwitterCollector()
        hibp_collector = HaveIBeenPwnedCollector(HIBP_API_KEY)
        linkedin_collector = LinkedInCollector()
        reddit_collector = RedditCollector()
        
        results = {}
        
        if 'github' in platforms:
            results['github'] = github_collector.collect(target)
            time.sleep(0.5)
        
        if 'twitter' in platforms or 'x' in platforms:
            results['twitter'] = twitter_collector.collect(target)
            time.sleep(0.5)
        
        if 'linkedin' in platforms:
            results['linkedin'] = linkedin_collector.collect(target)
            time.sleep(0.5)
        
        if 'reddit' in platforms:
            results['reddit'] = reddit_collector.collect(target)
            time.sleep(0.5)
        
        if '@' in target:
            results['haveibeenpwned'] = hibp_collector.collect(target)
            time.sleep(0.5)
        
        risk_data = calculate_risk_score(results)
        
        ai_analysis = {}
        if AI_SERVICE:
            analyzer = AIAnalyzer(AI_SERVICE)
            ai_analysis = analyzer.analyze_data(results, target)
        
        response = {
            'target': target,
            'timestamp': datetime.now().isoformat(),
            'platforms_searched': platforms,
            'ai_service_used': AI_SERVICE or 'none',
            'risk_score': risk_data,
            'platform_data': results,
            'ai_analysis': ai_analysis,
            'findings': generate_findings(results, risk_data)
        }
        
        return jsonify(response), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/geolocation/image', methods=['POST'])
def analyze_image():
    """Endpoint for image geolocation analysis"""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        
        if file.filename == '':
            return jsonify({'error': 'Empty filename'}), 400
        
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file.filename)[1])
        file.save(temp_file.name)
        
        print("Extracting EXIF data...")
        exif_data = EXIFExtractor.extract_exif(temp_file.name)
        
        print(f"Analyzing image with {AI_SERVICE or 'no AI service'}...")
        vision_analysis = {}
        if AI_SERVICE:
            analyzer = AIAnalyzer(AI_SERVICE)
            vision_analysis = analyzer.analyze_image_for_geolocation(temp_file.name, exif_data)
        else:
            vision_analysis = {
                'error': 'No AI API key configured',
                'confidence': 0,
                'location_estimate': 'Unknown'
            }
        
        final_coordinates = None
        coordinate_source = 'none'
        
        if exif_data.get('coordinates'):
            final_coordinates = exif_data['coordinates']
            coordinate_source = 'exif'
        elif vision_analysis.get('coordinates_estimate'):
            final_coordinates = vision_analysis['coordinates_estimate']
            coordinate_source = 'ai_estimation'
        
        final_confidence = 100 if coordinate_source == 'exif' else vision_analysis.get('confidence', 0)
        
        os.unlink(temp_file.name)
        
        response = {
            'coordinates': final_coordinates,
            'coordinate_source': coordinate_source,
            'confidence': final_confidence,
            'exif_data': exif_data,
            'vision_analysis': vision_analysis,
            'location_estimate': vision_analysis.get('location_estimate', 'Unknown'),
            'clues': vision_analysis.get('primary_clues', []),
            'landmarks': vision_analysis.get('landmarks_identified', []),
            'text_detected': vision_analysis.get('text_detected', []),
            'analysis': vision_analysis.get('analysis', ''),
            'ai_service_used': AI_SERVICE or 'none',
            'timestamp': datetime.now().isoformat()
        }
        
        return jsonify(response), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/geolocation/video', methods=['POST'])
def analyze_video():
    """Endpoint for video geolocation analysis"""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        num_frames = int(request.form.get('num_frames', 5))
        
        if file.filename == '':
            return jsonify({'error': 'Empty filename'}), 400
        
        temp_video = tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file.filename)[1])
        file.save(temp_video.name)
        
        print(f"Extracting {num_frames} frames from video...")
        frame_paths = VideoFrameExtractor.extract_frames(temp_video.name, num_frames)
        
        if not frame_paths:
            os.unlink(temp_video.name)
            return jsonify({'error': 'Failed to extract frames from video'}), 500
        
        print(f"Analyzing {len(frame_paths)} frames with {AI_SERVICE or 'no AI service'}...")
        
        if AI_SERVICE:
            analyzer = AIAnalyzer(AI_SERVICE)
            frame_analyses = []
            
            for i, frame_path in enumerate(frame_paths):
                print(f"Analyzing frame {i+1}/{len(frame_paths)}...")
                analysis = analyzer.analyze_image_for_geolocation(frame_path)
                frame_analyses.append(analysis)
            
            vision_analysis = correlate_frame_analyses(frame_analyses)
        else:
            vision_analysis = {
                'error': 'No AI API key configured',
                'confidence': 0,
                'location_estimate': 'Unknown'
            }
        
        os.unlink(temp_video.name)
        for frame_path in frame_paths:
            os.unlink(frame_path)
        
        response = {
            'coordinates': vision_analysis.get('coordinates_estimate'),
            'coordinate_source': 'ai_estimation_video',
            'confidence': vision_analysis.get('confidence', 0),
            'frames_analyzed': vision_analysis.get('frames_analyzed', 0),
            'location_estimate': vision_analysis.get('location_estimate', 'Unknown'),
            'clues': vision_analysis.get('all_clues', []),
            'landmarks': vision_analysis.get('landmarks_identified', []),
            'text_detected': vision_analysis.get('text_detected', []),
            'analysis': vision_analysis.get('analysis', ''),
            'ai_service_used': AI_SERVICE or 'none',
            'timestamp': datetime.now().isoformat()
        }
        
        return jsonify(response), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


def correlate_frame_analyses(analyses: List[Dict]) -> Dict[str, Any]:
    """Correlate multiple frame analyses to increase confidence"""
    if not analyses:
        return {
            'error': 'No analyses to correlate',
            'coordinates_estimate': None,
            'confidence': 0
        }
    
    all_clues = []
    all_landmarks = []
    all_text = []
    location_estimates = []
    coordinates = []
    confidences = []
    
    for analysis in analyses:
        if not analysis.get('error'):
            all_clues.extend(analysis.get('primary_clues', []))
            all_landmarks.extend(analysis.get('landmarks_identified', []))
            all_text.extend(analysis.get('text_detected', []))
            location_estimates.append(analysis.get('location_estimate', ''))
            if analysis.get('coordinates_estimate'):
                coordinates.append(analysis['coordinates_estimate'])
            confidences.append(analysis.get('confidence', 0))
    
    avg_confidence = sum(confidences) / len(confidences) if confidences else 0
    location = max(set(location_estimates), key=location_estimates.count) if location_estimates else 'Unknown'
    
    avg_coords = None
    if coordinates:
        avg_lat = sum(c['latitude'] for c in coordinates) / len(coordinates)
        avg_lon = sum(c['longitude'] for c in coordinates) / len(coordinates)
        avg_coords = {'latitude': round(avg_lat, 6), 'longitude': round(avg_lon, 6)}
    
    return {
        'location_estimate': location,
        'coordinates_estimate': avg_coords,
        'confidence': round(avg_confidence, 1),
        'frames_analyzed': len(analyses),
        'all_clues': list(set(all_clues)),
        'landmarks_identified': list(set(all_landmarks)),
        'text_detected': list(set(all_text)),
        'analysis': f'Analyzed {len(analyses)} frames. Confidence increased through correlation of findings across multiple frames.'
    }


@app.route('/api/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'online',
        'timestamp': datetime.now().isoformat(),
        'ai_service': AI_SERVICE or 'none',
        'services': {
            'github': bool(GITHUB_TOKEN),
            'hibp': bool(HIBP_API_KEY),
            'groq': bool(GROQ_API_KEY),
            'gemini': bool(GEMINI_API_KEY),
            'anthropic': bool(ANTHROPIC_API_KEY),
            'huggingface': bool(HUGGINGFACE_API_KEY),
            'exif_extraction': True,
            'video_processing': True,
            'image_geolocation': AI_SERVICE in ['groq', 'gemini', 'anthropic'] if AI_SERVICE else False
        }
    }), 200


if __name__ == '__main__':
    print(f"🚀 OSINT Backend Starting...")
    print(f"📡 AI Service: {AI_SERVICE or 'None configured'}")
    print(f"🖼️  Image Geolocation: {'Enabled' if AI_SERVICE in ['groq', 'gemini', 'anthropic'] else 'Disabled (requires Groq/Gemini/Anthropic)'}")
    print(f"🎥 Video Geolocation: {'Enabled' if AI_SERVICE in ['groq', 'gemini', 'anthropic'] else 'Disabled (requires Groq/Gemini/Anthropic)'}")
    app.run(debug=True, port=5000)