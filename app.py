<<<<<<< HEAD
from flask import Flask, render_template, jsonify, request
from flask_cors import CORS
from config import Config
from api.routes import api_bp
import os

app = Flask(__name__)
app.config.from_object(Config)
CORS(app)

# Register blueprints
app.register_blueprint(api_bp, url_prefix='/api')

@app.route('/')
def index():
    """Main page route"""
    return render_template('index.html')

@app.route('/timeline')
def timeline():
    """Timeline view route"""
    return render_template('timeline.html')

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    # Ensure data directories exist
    os.makedirs('data/analysis_results', exist_ok=True)
    
    # Run the application
    app.run(
        host=app.config['HOST'],
        port=app.config['PORT'],
        debug=app.config['DEBUG']
    )
=======
from unittest import result
from dotenv import load_dotenv
load_dotenv()
from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
from bs4 import BeautifulSoup
import os
import re
import traceback
from datetime import datetime, timedelta
import time
from typing import Dict, List, Any, Optional, Tuple
import json
import base64
import io
import tempfile
from dataclasses import dataclass, asdict
from enum import Enum

load_dotenv()
from visual import visual_bp
from reverse_osint import reverse_osint_bp




app = Flask(__name__)
CORS(app)

app.register_blueprint(visual_bp)
app.register_blueprint(reverse_osint_bp)


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

    


# ==================== PLATFORM DETECTION RULES ====================

PLATFORM_RULES = {
    "github": {
        "url": "https://github.com/{}",
        "success_codes": [200],
        "confidence": "HIGH"
    },
    "reddit": {
        "url": "https://www.reddit.com/user/{}/about.json",
        "success_codes": [200],
        "confidence": "HIGH",
        "json_key": "name"
    },
    "gitlab": {
        "url": "https://gitlab.com/{}",
        "success_codes": [200],
        "confidence": "HIGH"
    },
    "instagram": {
    "url": "https://www.instagram.com/{}/",
    "success_codes": [200],
    "confidence": "LOW",
    "must_not_contain": "Sorry, this page isn't available"
    },
    "youtube": {
    "url": "https://www.youtube.com/@{}",
    "success_codes": [200],
    "confidence": "LOW",
    "must_not_contain": "This channel does not exist"
    },
    "facebook": {
    "url": "https://www.facebook.com/{}",
    "success_codes": [200],
    "confidence": "LOW",
    "must_not_contain": "This content isn't available"
    },
    "linkedin": {
    "url": "https://www.linkedin.com/in/{}/",
    "success_codes": [200],
    "confidence": "LOW",
    "must_not_contain": "This page doesn't exist"
    },
   "twitter": {
    "url": "https://x.com/{}",
    "success_codes": [200],
    "confidence": "LOW",
    "must_not_contain": "This account doesn't exist"
}

}



# ==================== RISK ASSESSMENT SYSTEM ====================

class RiskLevel(Enum):
    """Risk level enumeration"""
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"
    MINIMAL = "MINIMAL"


class DataCategory(Enum):
    """Data classification categories"""
    CREDENTIALS = "Credentials"
    PERSONAL_IDENTIFIERS = "Personal Identifiers"
    CONTACT_DETAILS = "Contact Details"
    BEHAVIORAL_PATTERNS = "Behavioral Patterns"
    ORGANIZATIONAL_LINKS = "Organizational Links"
    LOCATION_DATA = "Location Data"
    FINANCIAL_INFO = "Financial Information"
    SOCIAL_CONNECTIONS = "Social Connections"


@dataclass
class RiskItem:
    """Individual risk item"""
    category: str
    item: str
    risk_level: str
    score: float
    platforms: List[str]
    recency: Optional[str]
    action: str
    exploitability: str
    details: str


@dataclass
class RiskAssessment:
    """Complete risk assessment result"""
    overall_score: float
    risk_level: str
    total_exposures: int
    critical_count: int
    high_count: int
    medium_count: int
    low_count: int
    risk_items: List[RiskItem]
    recommendations: List[str]
    risk_factors: List[str]
    timeline: Optional[str]
    summary: str


class RiskClassifier:
    """Classify data into risk categories"""
    
    # Sensitivity weights for different data types
    SENSITIVITY_WEIGHTS = {
        # Credentials (Highest Risk)
        'password': 10.0,
        'password_hash': 9.0,
        'api_key': 9.5,
        'access_token': 9.0,
        'private_key': 10.0,
        'ssh_key': 9.5,
        'credential': 9.0,
        'breach': 9.5,
        
        # Personal Identifiers (High Risk)
        'ssn': 9.5,
        'social_security': 9.5,
        'passport': 9.0,
        'drivers_license': 8.5,
        'national_id': 8.5,
        'date_of_birth': 7.5,
        'dob': 7.5,
        'full_name': 6.5,
        'maiden_name': 7.0,
        
        # Financial Information (High Risk)
        'credit_card': 10.0,
        'bank_account': 9.5,
        'routing_number': 9.0,
        'cvv': 10.0,
        'bitcoin_address': 7.0,
        
        # Contact Details (Medium Risk)
        'email': 5.0,
        'phone': 6.0,
        'address': 7.0,
        'home_address': 7.5,
        'work_address': 6.0,
        
        # Location Data (Medium Risk)
        'gps_coordinates': 6.5,
        'location': 5.5,
        'check_in': 5.0,
        'geolocation': 6.0,
        
        # Behavioral Patterns (Low-Medium Risk)
        'username': 3.0,
        'profile': 3.5,
        'bio': 2.5,
        'interests': 2.0,
        'hobby': 2.0,
        'activity_pattern': 4.0,
        'browsing_history': 5.5,
        
        # Organizational Links (Medium Risk)
        'employer': 5.0,
        'company': 4.5,
        'job_title': 4.0,
        'work_email': 6.0,
        'colleagues': 4.0,
        
        # Social Connections (Low Risk)
        'friend': 2.5,
        'follower': 2.0,
        'connection': 2.5,
        'network': 3.0,
    }
    
    @staticmethod
    def classify_data(data_type: str, value: str, platform: str) -> Dict[str, Any]:
        """Classify data and assign category"""
        data_lower = data_type.lower()
        value_lower = str(value).lower()
        
        # Determine category
        category = DataCategory.BEHAVIORAL_PATTERNS.value  # Default
        base_score = 3.0
        
        # Check for credentials
        if any(term in data_lower for term in ['password', 'credential', 'token', 'key', 'breach']):
            category = DataCategory.CREDENTIALS.value
            base_score = 9.0
        
        # Check for personal identifiers
        elif any(term in data_lower for term in ['ssn', 'passport', 'id', 'birth', 'name']):
            category = DataCategory.PERSONAL_IDENTIFIERS.value
            base_score = 7.0
        
        # Check for contact details
        elif any(term in data_lower for term in ['email', 'phone', 'address']):
            category = DataCategory.CONTACT_DETAILS.value
            base_score = 5.5
        
        # Check for location data
        elif any(term in data_lower for term in ['location', 'gps', 'coordinates', 'geolocation']):
            category = DataCategory.LOCATION_DATA.value
            base_score = 6.0
        
        # Check for organizational links
        elif any(term in data_lower for term in ['company', 'employer', 'job', 'work']):
            category = DataCategory.ORGANIZATIONAL_LINKS.value
            base_score = 5.0
        
        # Get specific weight if available
        for key, weight in RiskClassifier.SENSITIVITY_WEIGHTS.items():
            if key in data_lower or key in value_lower:
                base_score = max(base_score, weight)
                break
        
        return {
            'category': category,
            'base_score': base_score,
            'data_type': data_type,
            'platform': platform
        }


class RiskScorer:
    """Calculate risk scores with various factors"""
    
    @staticmethod
    def calculate_score(
        base_score: float,
        platforms: List[str],
        recency_days: Optional[int] = None,
        has_breach: bool = False,
        is_public: bool = True
    ) -> float:
        """Calculate final risk score with various factors"""
        score = base_score
        
        # Cross-platform correlation bonus
        if len(platforms) > 1:
            correlation_bonus = min(len(platforms) - 1, 3) * 0.5
            score += correlation_bonus
        
        # Recency factor (more recent = higher risk)
        if recency_days is not None:
            if recency_days <= 30:  # Within last month
                score += 1.5
            elif recency_days <= 90:  # Within last 3 months
                score += 1.0
            elif recency_days <= 365:  # Within last year
                score += 0.5
        
        # Breach factor
        if has_breach:
            score += 2.0
        
        # Public accessibility factor
        if is_public:
            score += 0.5
        
        # Cap at 10
        return min(round(score, 1), 10.0)
    
    @staticmethod
    def determine_risk_level(score: float) -> RiskLevel:
        """Determine risk level from score"""
        if score >= 8.5:
            return RiskLevel.CRITICAL
        elif score >= 6.5:
            return RiskLevel.HIGH
        elif score >= 4.0:
            return RiskLevel.MEDIUM
        elif score >= 2.0:
            return RiskLevel.LOW
        else:
            return RiskLevel.MINIMAL
    
    @staticmethod
    def assess_exploitability(category: str, platforms: List[str], score: float) -> str:
        """Assess how exploitable this data is"""
        if score >= 8.5:
            return "Immediate exploitation risk - attackers can use this for account takeover, identity theft, or targeted attacks"
        elif score >= 6.5:
            return "High exploitation potential - can be used for social engineering, phishing, or credential stuffing"
        elif score >= 4.0:
            return "Moderate exploitation risk - useful for profiling and targeted reconnaissance"
        elif score >= 2.0:
            return "Low exploitation potential - primarily useful for social engineering context"
        else:
            return "Minimal direct exploitation risk - general public information"


class AIRiskAnalyzer:
    """Use AI for intelligent risk analysis - supports multiple AI services"""
    
    def __init__(self, ai_service: str):
        self.service = ai_service
    
    def analyze_risks(self, collected_data: Dict[str, Any], target: str) -> Dict[str, Any]:
        """Use AI to analyze OSINT data and provide intelligent risk assessment"""
        
        if not self.service:
            return {
                'error': 'No AI service configured',
                'risk_items': [],
                'overall_assessment': {
                    'score': 0,
                    'level': 'UNKNOWN',
                    'summary': 'AI analysis unavailable'
                },
                'recommendations': [],
                'attack_vectors': [],
                'correlations': [],
                'timeline': 'UNKNOWN'
            }
        
        try:
            data_summary = self._prepare_data_summary(collected_data)
            
            prompt = f"""You are a cybersecurity expert analyzing OSINT (Open Source Intelligence) data for risk assessment.

Target: {target}

Collected Data Summary:
{json.dumps(data_summary, indent=2)}

Your task is to assess the risk and security implications of this exposed data. For each significant finding:

1. **Classify the data type** into categories:
   - Credentials (passwords, API keys, tokens)
   - Personal Identifiers (SSN, DOB, full name, ID numbers)
   - Contact Details (email, phone, address)
   - Behavioral Patterns (activity times, interests, routines)
   - Organizational Links (employer, colleagues, work info)
   - Location Data (GPS, addresses, check-ins)
   - Financial Information (account numbers, payment info)

2. **Assign risk level**: CRITICAL, HIGH, MEDIUM, or LOW based on:
   - Sensitivity of the information
   - Potential for exploitation
   - Ease of weaponization
   - Impact if misused

3. **Calculate risk score** (0-10) considering:
   - Base sensitivity (password=10, email=5, hobby=2)
   - Cross-platform exposure (found on multiple platforms = higher risk)
   - Recency (recent breaches = higher risk)
   - Exploitability (how easily can this be weaponized?)

4. **Suggest specific mitigation actions** for each risk item

5. **Identify patterns and correlations** across platforms that increase risk

6. **Provide an overall risk assessment** with timeline for action

Return your analysis in this JSON format:
{{
  "risk_items": [
    {{
      "category": "Credentials|Personal Identifiers|Contact Details|Behavioral Patterns|Organizational Links|Location Data|Financial Information",
      "item": "specific description of what was found",
      "risk_level": "CRITICAL|HIGH|MEDIUM|LOW",
      "score": 0.0-10.0,
      "platforms": ["platform1", "platform2"],
      "recency": "timeframe or null",
      "action": "specific recommended action",
      "exploitability": "explanation of how this could be exploited",
      "details": "additional context and implications"
    }}
  ],
  "overall_assessment": {{
    "score": 0.0-10.0,
    "level": "CRITICAL|HIGH|MEDIUM|LOW",
    "summary": "2-3 sentence overall assessment"
  }},
  "recommendations": [
    "prioritized list of actions to take",
    "ordered by urgency and impact"
  ],
  "attack_vectors": [
    "potential attack scenarios enabled by this data"
  ],
  "correlations": [
    "cross-platform patterns that increase risk"
  ],
  "timeline": "IMMEDIATE (within 24h) | URGENT (within 1 week) | MODERATE (within 1 month) | LOW (ongoing monitoring)"
}}

Be thorough but concise. Focus on actionable insights and real security implications."""

            # Call appropriate AI service
            response_text = self._call_ai_service(prompt)
            
            # Parse response
            try:
                json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
                if json_match:
                    analysis = json.loads(json_match.group())
                else:
                    analysis = self._create_fallback_analysis(response_text)
            except json.JSONDecodeError:
                analysis = self._create_fallback_analysis(response_text)
            
            return analysis
            
        except Exception as e:
            return {
                'error': str(e),
                'risk_items': [],
                'overall_assessment': {
                    'score': 0,
                    'level': 'UNKNOWN',
                    'summary': 'AI analysis failed'
                },
                'recommendations': [],
                'attack_vectors': [],
                'correlations': [],
                'timeline': 'UNKNOWN'
            }
    
    def _call_ai_service(self, prompt: str) -> str:
        """Call the appropriate AI service"""
        if self.service == 'groq':
            return self._call_groq(prompt)
        elif self.service == 'gemini':
            return self._call_gemini(prompt)
        elif self.service == 'anthropic':
            return self._call_anthropic(prompt)
        elif self.service == 'huggingface':
            return self._call_huggingface(prompt)
        else:
            raise Exception(f"Unknown AI service: {self.service}")
    
    def _call_groq(self, prompt: str) -> str:
        """Call Groq API"""
        url = "https://api.groq.com/openai/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type": "application/json"
        }
        data = {
            "model": "meta-llama/llama-4-scout-17b-16e-instruct",
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.3,
            "max_tokens": 4000
        }
        response = requests.post(url, headers=headers, json=data, timeout=60)
        response.raise_for_status()
        return response.json()['choices'][0]['message']['content']
    
    def _call_gemini(self, prompt: str) -> str:
        """Call Gemini API"""
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
        headers = {"Content-Type": "application/json"}
        data = {"contents": [{"parts": [{"text": prompt}]}]}
        response = requests.post(url, headers=headers, json=data, timeout=60)
        response.raise_for_status()
        return response.json()['candidates'][0]['content']['parts'][0]['text']
    
    def _call_anthropic(self, prompt: str) -> str:
        """Call Claude API"""
        import anthropic
        client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
        message = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=4000,
            temperature=0.3,
            messages=[{"role": "user", "content": prompt}]
        )
        return message.content[0].text
    
    def _call_huggingface(self, prompt: str) -> str:
        """Call Hugging Face API"""
        url = "https://api-inference.huggingface.co/models/mistralai/Mistral-7B-Instruct-v0.2"
        headers = {"Authorization": f"Bearer {HUGGINGFACE_API_KEY}"}
        data = {"inputs": prompt}
        response = requests.post(url, headers=headers, json=data, timeout=60)
        response.raise_for_status()
        result = response.json()
        return result[0]['generated_text'] if isinstance(result, list) else result.get('generated_text', '')
    
    def _prepare_data_summary(self, collected_data: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare a summary of collected data for AI analysis"""
        summary = {
            'platforms_searched': [],
            'data_found': []
        }
        
        for platform, data in collected_data.items():
            if data.get('found'):
                summary['platforms_searched'].append(platform)
                
                profile = data.get('profile', {})
                if profile:
                    for key, value in profile.items():
                        if value and value != 'Unknown' and value != '':
                            summary['data_found'].append({
                                'platform': platform,
                                'type': key,
                                'value': str(value)[:100]
                            })
                
                if platform == 'haveibeenpwned' and data.get('breach_count', 0) > 0:
                    breaches = data.get('breaches', [])
                    for breach in breaches[:3]:
                        summary['data_found'].append({
                            'platform': 'HaveIBeenPwned',
                            'type': 'data_breach',
                            'value': f"{breach.get('name')} - {', '.join(breach.get('data_classes', [])[:5])}"
                        })
        
        return summary
    
    def _create_fallback_analysis(self, response_text: str) -> Dict[str, Any]:
        """Create fallback analysis structure"""
        return {
            'risk_items': [],
            'overall_assessment': {
                'score': 5.0,
                'level': 'MEDIUM',
                'summary': response_text[:200] if response_text else 'Analysis completed'
            },
            'recommendations': ['Review security settings', 'Enable 2FA where possible'],
            'attack_vectors': [],
            'correlations': [],
            'timeline': 'MODERATE',
            'raw_response': response_text
        }
    # ==================== CONTENT INTELLIGENCE ====================

def extract_content_findings(canonical_profiles, results):
    """Extract content findings from canonical profiles"""
    findings = []

    for platform, data in canonical_profiles.items():
        platform_data = results.get(platform, {})
        profile = platform_data.get("profile", {})
        
        # BIO
        bio = profile.get("bio") or profile.get("description")
        if bio:
            findings.append({
                "type": "bio",
                "value": bio[:200],
                "platforms": platform,
                "risk": "LOW"
            })

        # MEDIUM ARTICLES
        if platform == "medium":
            for article in platform_data.get("articles", []):
                if article.get("title"):
                    findings.append({
                        "type": "article",
                        "value": article["title"],
                        "platforms": "medium",
                        "risk": "LOW"
                    })

        # GITHUB REPOS
        if platform == "github":
            for repo in platform_data.get("repositories", []):
                if repo.get("description"):
                    findings.append({
                        "type": "repository",
                        "value": repo["description"][:200],
                        "platforms": "github",
                        "risk": "LOW"
                    })

        # TWITTER POSTS
        if platform == "twitter":
           for post in platform_data.get("posts", []):
                   findings.append({
                       "type": "tweet",
                        "value": post,
                        "platforms": "twitter",
                       "risk": "LOW"
        })


    return findings


class RiskAssessmentEngine:
    """Main risk assessment engine combining all components"""
    
    def __init__(self, ai_service: Optional[str] = None):
        self.classifier = RiskClassifier()
        self.scorer = RiskScorer()
        self.ai_analyzer = AIRiskAnalyzer(ai_service) if ai_service else None
    
    def assess_risks(self, collected_data: Dict[str, Any], target: str) -> RiskAssessment:
        """Perform complete risk assessment on collected OSINT data"""
        risk_items = []
        
        # First pass: Basic classification and scoring
        for platform, platform_data in collected_data.items():
            if not platform_data.get('found'):
                continue
            
            # Process profile data
            profile = platform_data.get('profile', {})
            for key, value in profile.items():
                if value and value != 'Unknown' and value != '':
                    classification = self.classifier.classify_data(key, str(value), platform)
                    
                    score = self.scorer.calculate_score(
                        base_score=classification['base_score'],
                        platforms=[platform],
                        is_public=True
                    )
                    
                    risk_level = self.scorer.determine_risk_level(score)
                    exploitability = self.scorer.assess_exploitability(
                        classification['category'],
                        [platform],
                        score
                    )
                    
                    risk_items.append(RiskItem(
                        category=classification['category'],
                        item=f"{key}: {str(value)[:50]}",
                        risk_level=risk_level.value,
                        score=score,
                        platforms=[platform],
                        recency=None,
                        action=self._generate_action(classification['category'], risk_level),
                        exploitability=exploitability,
                        details=f"Found on {platform}"
                    ))
            
            # Process breaches with special handling
            if platform == 'haveibeenpwned' and platform_data.get('breach_count', 0) > 0:
                breaches = platform_data.get('breaches', [])
                for breach in breaches:
                    breach_date_str = breach.get('breach_date', breach.get('BreachDate'))
                    recency_days = None
                    if breach_date_str:
                        try:
                            breach_date = datetime.strptime(breach_date_str, '%Y-%m-%d')
                            recency_days = (datetime.now() - breach_date).days
                        except:
                            pass
                    
                    score = self.scorer.calculate_score(
                        base_score=9.0,
                        platforms=['HaveIBeenPwned'],
                        recency_days=recency_days,
                        has_breach=True,
                        is_public=True
                    )
                    
                    risk_level = self.scorer.determine_risk_level(score)
                    data_classes = breach.get('data_classes', breach.get('DataClasses', []))
                    
                    risk_items.append(RiskItem(
                        category=DataCategory.CREDENTIALS.value,
                        item=f"Data breach: {breach.get('name', breach.get('Name', 'Unknown'))}",
                        risk_level=risk_level.value,
                        score=score,
                        platforms=['HaveIBeenPwned'],
                        recency=f"{recency_days} days ago" if recency_days else None,
                        action="Change password immediately and enable 2FA",
                        exploitability=f"Compromised data includes: {', '.join(data_classes[:5])}",
                        details=breach.get('description', breach.get('Description', ''))[:200]
                    ))
        
        # Use AI for enhanced analysis if available
        ai_recommendations = []
        ai_risk_factors = []
        ai_overall_score = None
        ai_summary = ""
        ai_timeline = None
        
        if self.ai_analyzer:
            ai_analysis = self.ai_analyzer.analyze_risks(collected_data, target)
            
            if not ai_analysis.get('error'):
                # Extract AI-generated risk items
                ai_risk_items = ai_analysis.get('risk_items', [])
                for ai_item in ai_risk_items:
                    risk_items.append(RiskItem(
                        category=ai_item.get('category', 'Unknown'),
                        item=ai_item.get('item', ''),
                        risk_level=ai_item.get('risk_level', 'MEDIUM'),
                        score=float(ai_item.get('score', 5.0)),
                        platforms=ai_item.get('platforms', []),
                        recency=ai_item.get('recency'),
                        action=ai_item.get('action', 'Review and assess'),
                        exploitability=ai_item.get('exploitability', ''),
                        details=ai_item.get('details', '')
                    ))
                
                ai_recommendations = ai_analysis.get('recommendations', [])
                ai_risk_factors = ai_analysis.get('attack_vectors', []) + ai_analysis.get('correlations', [])
                
                overall = ai_analysis.get('overall_assessment', {})
                ai_overall_score = overall.get('score')
                ai_summary = overall.get('summary', '')
                ai_timeline = ai_analysis.get('timeline')
        
        # Calculate overall statistics
        risk_items.sort(key=lambda x: x.score, reverse=True)
        
        critical_count = sum(1 for item in risk_items if item.risk_level == 'CRITICAL')
        high_count = sum(1 for item in risk_items if item.risk_level == 'HIGH')
        medium_count = sum(1 for item in risk_items if item.risk_level == 'MEDIUM')
        low_count = sum(1 for item in risk_items if item.risk_level in ['LOW', 'MINIMAL'])
        
        # Calculate overall score
        if ai_overall_score is not None:
            overall_score = ai_overall_score
        elif risk_items:
            scores = [item.score for item in risk_items]
            weights = [3 if item.risk_level == 'CRITICAL' else 2 if item.risk_level == 'HIGH' else 1 for item in risk_items]
            overall_score = sum(s * w for s, w in zip(scores, weights)) / sum(weights)
        else:
            overall_score = 0.0
        
        overall_risk_level = self.scorer.determine_risk_level(overall_score).value
        
        # Generate recommendations if not from AI
        if not ai_recommendations:
            ai_recommendations = self._generate_recommendations(risk_items, critical_count, high_count)
        
        # Generate risk factors
        if not ai_risk_factors:
            ai_risk_factors = self._generate_risk_factors(risk_items)
        
        # Generate summary
        if not ai_summary:
            ai_summary = self._generate_summary(len(risk_items), critical_count, high_count, overall_risk_level)
        
        return RiskAssessment(
            overall_score=round(overall_score, 1),
            risk_level=overall_risk_level,
            total_exposures=len(risk_items),
            critical_count=critical_count,
            high_count=high_count,
            medium_count=medium_count,
            low_count=low_count,
            risk_items=risk_items[:20],
            recommendations=ai_recommendations,
            risk_factors=ai_risk_factors,
            timeline=ai_timeline or self._determine_timeline(critical_count, high_count),
            summary=ai_summary
        )
    
    def _generate_action(self, category: str, risk_level: RiskLevel) -> str:
        """Generate recommended action based on category and risk level"""
        actions = {
            DataCategory.CREDENTIALS.value: {
                RiskLevel.CRITICAL: "Change password immediately, enable 2FA, and monitor for unauthorized access",
                RiskLevel.HIGH: "Change password and enable two-factor authentication",
                RiskLevel.MEDIUM: "Consider changing password and reviewing security settings",
                RiskLevel.LOW: "Monitor account for suspicious activity"
            },
            DataCategory.PERSONAL_IDENTIFIERS.value: {
                RiskLevel.CRITICAL: "Place fraud alert with credit bureaus and monitor identity theft services",
                RiskLevel.HIGH: "Review privacy settings and limit public exposure",
                RiskLevel.MEDIUM: "Consider removing or restricting access to this information",
                RiskLevel.LOW: "Monitor for misuse"
            },
            DataCategory.CONTACT_DETAILS.value: {
                RiskLevel.CRITICAL: "Change contact information and enable spam filters",
                RiskLevel.HIGH: "Review and restrict visibility of contact details",
                RiskLevel.MEDIUM: "Enable privacy settings to limit exposure",
                RiskLevel.LOW: "Monitor for spam or phishing attempts"
            },
            DataCategory.LOCATION_DATA.value: {
                RiskLevel.CRITICAL: "Disable location sharing immediately",
                RiskLevel.HIGH: "Review and restrict location sharing settings",
                RiskLevel.MEDIUM: "Consider disabling location services for non-essential apps",
                RiskLevel.LOW: "Be aware of location sharing preferences"
            }
        }
        
        return actions.get(category, {}).get(
            risk_level,
            "Review and assess security implications"
        )
    
    def _generate_recommendations(self, risk_items: List[RiskItem], critical: int, high: int) -> List[str]:
        """Generate actionable recommendations"""
        recommendations = []
        
        if critical > 0:
            recommendations.append("🚨 URGENT: Address all critical vulnerabilities within 24 hours")
            recommendations.append("Change all passwords associated with breached accounts immediately")
            recommendations.append("Enable two-factor authentication on all accounts where available")
        
        if high > 0:
            recommendations.append("Review and strengthen security settings on all exposed platforms")
            recommendations.append("Consider using unique email addresses for different services")
        
        categories = {item.category for item in risk_items}
        
        if DataCategory.CREDENTIALS.value in categories:
            recommendations.append("Use a password manager to generate and store unique passwords")
            recommendations.append("Monitor HaveIBeenPwned for future breaches")
        
        if DataCategory.LOCATION_DATA.value in categories:
            recommendations.append("Disable location sharing on social media and review app permissions")
        
        if DataCategory.PERSONAL_IDENTIFIERS.value in categories:
            recommendations.append("Review privacy settings and limit personal information sharing")
        
        recommendations.append("Conduct regular security audits of your online presence")
        recommendations.append("Set up Google Alerts for your name and email address")
        
        return recommendations[:10]
    
    def _generate_risk_factors(self, risk_items: List[RiskItem]) -> List[str]:
        """Generate risk factors from items"""
        factors = []
        
        all_platforms = set()
        for item in risk_items:
            all_platforms.update(item.platforms)
        
        if len(all_platforms) > 3:
            factors.append(f"High cross-platform exposure: data found on {len(all_platforms)} different platforms")
        
        cred_items = [item for item in risk_items if item.category == DataCategory.CREDENTIALS.value]
        if cred_items:
            factors.append(f"{len(cred_items)} credential-related exposures increase account takeover risk")
        
        recent_items = [item for item in risk_items if item.recency and 'days' in item.recency]
        if recent_items:
            factors.append("Recent data exposures detected - immediate action required")
        
        return factors
    
    def _generate_summary(self, total: int, critical: int, high: int, level: str) -> str:
        """Generate risk assessment summary"""
        if critical > 0:
            return f"CRITICAL RISK DETECTED: Found {total} exposures including {critical} critical vulnerabilities requiring immediate action. Your data is at high risk of exploitation."
        elif high > 0:
            return f"HIGH RISK: Identified {total} exposures with {high} high-risk items. Prompt action needed to secure your accounts and data."
        elif total > 5:
            return f"MODERATE RISK: Found {total} exposures across multiple platforms. Review and strengthen your security posture."
        elif total > 0:
            return f"LOW RISK: Detected {total} minor exposures. Consider reviewing privacy settings as a precaution."
        else:
            return "MINIMAL RISK: No significant exposures detected in the analyzed data."
    
    def _determine_timeline(self, critical: int, high: int) -> str:
        """Determine action timeline based on risk"""
        if critical > 0:
            return "IMMEDIATE (within 24 hours)"
        elif high > 2:
            return "URGENT (within 1 week)"
        elif high > 0:
            return "MODERATE (within 2 weeks)"
        else:
            return "ONGOING (regular monitoring)"
    
    def to_frontend_format(self, assessment: RiskAssessment) -> Dict[str, Any]:
        """Convert assessment to frontend-compatible format"""
        return {
            'risk_score': {
                'risk': assessment.overall_score,
                'level': assessment.risk_level,
                'exposures': assessment.total_exposures,
                'platforms': len(set(p for item in assessment.risk_items for p in item.platforms)),
                'factors': assessment.risk_factors
            },
            'risk_breakdown': {
                'critical': assessment.critical_count,
                'high': assessment.high_count,
                'medium': assessment.medium_count,
                'low': assessment.low_count
            },
            'risk_items': [
                {
                    'category': item.category,
                    'item': item.item,
                    'risk': item.risk_level,
                    'score': item.score,
                    'platforms': ', '.join(item.platforms),
                    'action': item.action,
                    'exploitability': item.exploitability,
                    'details': item.details,
                    'recency': item.recency
                }
                for item in assessment.risk_items
            ],
            'recommendations': assessment.recommendations,
            'summary': assessment.summary,
            'timeline': assessment.timeline
        }


# ==================== DATA COLLECTORS ====================
# ==================== USERNAME ENUMERATION ====================

class UniversalUsernameEnumerator:
    """
    Checks if a username exists on supported platforms
    using HTTP validation (no API keys required).
    """

    def __init__(self, rules):
        self.rules = rules

    def check_username(self, username: str) -> dict:
        results = {}

        for platform, rule in self.rules.items():
            try:
                url = rule["url"].format(username)

                response = requests.get(
                    url,
                    headers={"User-Agent": "Mozilla/5.0"},
                    timeout=8
                )
                exists = False
                if response.status_code in rule.get("success_codes", []):
                    content = response.text.lower()
                    if "json_key" in rule:
                       data = response.json()
                       exists = rule["json_key"] in data.get("data", {})
                    elif "must_contain" in rule:
                       exists = rule["must_contain"].lower() in content
                    elif "must_not_contain" in rule:
                       exists = rule["must_not_contain"].lower() not in content
                    else:
                       exists = True  # fallback

                    results[platform] = {
                        "exists": exists,
                        "found": exists,
                        "profile_url": url if exists else None,
                        "confidence": rule.get("confidence", "LOW")
                    }
               
            except Exception:
                results[platform] = {"exists": False}

        return results

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
                'verification': 'api_verified',
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
        
class GitLabCollector:
      """Collect data from GitLab (public API, no auth required)"""

      def collect(self, username: str) -> Dict[str, Any]:
        try:
            # Search user
            search_url = f"https://gitlab.com/api/v4/users?username={username}"
            response = requests.get(search_url, timeout=10)

            if response.status_code != 200 or not response.json():
                return {"found": False}

            user = response.json()[0]
            user_id = user.get("id")

            # Fetch projects
            projects_url = f"https://gitlab.com/api/v4/users/{user_id}/projects"
            projects_resp = requests.get(projects_url, timeout=10)
            projects = projects_resp.json() if projects_resp.status_code == 200 else []

            return {
                "found": True,
                "verification": "api_verified",
                "platform": "GitLab",
                "profile": {
                    "username": user.get("username"),
                    "name": user.get("name"),
                    "bio": user.get("bio"),
                    "location": user.get("location"),
                    "website": user.get("website_url"),
                    "created_at": user.get("created_at"),
                    "profile_url": user.get("web_url")
                },
                "projects": [
                    {
                        "name": p.get("name"),
                        "description": p.get("description"),
                        "stars": p.get("star_count"),
                        "last_activity": p.get("last_activity_at")
                    }
                    for p in projects[:10]
                ]
            }

        except Exception as e:
            return {"found": False, "error": str(e)}
        
class InstagramCollector:
    """Lightweight Instagram presence collector (heuristic only)"""

    def collect(self, username: str) -> Dict[str, Any]:
        try:
            url = f"https://www.instagram.com/{username}/"
            headers = {"User-Agent": "Mozilla/5.0"}
            response = requests.get(url, headers=headers, timeout=10)

            if response.status_code != 200:
                return {"found": False}

            if "Sorry, this page isn't available" in response.text:
                return {"found": False}

            return {
                "found": True,
                "verification": "weak_verified",
                "platform": "Instagram",
                "profile": {
                    "username": username,
                    "profile_url": url
                }
            }

        except Exception as e:
            return {"found": False, "error": str(e)}
        
class YouTubeCollector:
    """Lightweight YouTube presence collector (heuristic only)"""

    def collect(self, username: str) -> Dict[str, Any]:
        try:
            url = f"https://www.youtube.com/@{username}"
            headers = {"User-Agent": "Mozilla/5.0"}
            response = requests.get(url, headers=headers, timeout=10)

            if response.status_code != 200:
                return {"found": False}

            if "This channel does not exist" in response.text:
                return {"found": False}

            return {
                "found": True,
                "verification": "weak_verified",
                "platform": "YouTube",
                "profile": {
                    "username": username,
                    "profile_url": url
                }
            }

        except Exception as e:
            return {"found": False, "error": str(e)}
        
class FacebookCollector:
    """Lightweight Facebook presence collector (heuristic only)"""

    def collect(self, username: str) -> Dict[str, Any]:
        try:
            url = f"https://www.facebook.com/{username}"
            headers = {"User-Agent": "Mozilla/5.0"}

            response = requests.get(url, headers=headers, timeout=10)

            if response.status_code != 200:
                return {"found": False}

            if "This content isn't available" in response.text:
                return {"found": False}

            return {
                "found": True,
                "verification": "weak_verified",
                "platform": "Facebook",
                "profile": {
                    "username": username,
                    "profile_url": url
                }
            }

        except Exception as e:
            return {"found": False, "error": str(e)}
        
class LinkedInCollector:
    """Lightweight LinkedIn presence collector (heuristic only)"""

    def collect(self, username: str) -> Dict[str, Any]:
        try:
            url = f"https://www.linkedin.com/in/{username}/"
            headers = {
                "User-Agent": "Mozilla/5.0"
            }

            response = requests.get(url, headers=headers, timeout=10)

            if response.status_code != 200:
                return {"found": False}

            if "This page doesn’t exist" in response.text:
                return {"found": False}

            return {
                "found": True,
                "verification": "weak_verified",
                "platform": "LinkedIn",
                "profile": {
                    "username": username,
                    "profile_url": url
                }
            }

        except Exception as e:
            return {"found": False, "error": str(e)}




        
class TwitterCollector:
    """Heuristic Twitter/X collector with recent posts"""

    def collect(self, username: str) -> Dict[str, Any]:
        try:
            url = f"https://x.com/{username}"
            headers = {"User-Agent": "Mozilla/5.0"}

            response = requests.get(url, headers=headers, timeout=10)

            if response.status_code != 200:
                return {"found": False}

            if "This account doesn’t exist" in response.text:
                return {"found": False}

            soup = BeautifulSoup(response.text, "html.parser")

            tweets = []
            for tweet in soup.find_all("article")[:5]:
                text_blocks = tweet.find_all("div")
                text = " ".join(
                    t.get_text(strip=True)
                    for t in text_blocks
                    if t.get_text(strip=True)
                )

                if text:
                    tweets.append(text[:280])

            return {
                "found": True,
                "verification": "weak_verified",
                "platform": "Twitter",
                "profile": {
                    "username": username,
                    "profile_url": url
                },
                "posts": tweets
            }

        except Exception as e:
            return {"found": False, "error": str(e)}






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
                'verification': 'weak_verified',
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

class AIAnalyzer:
    """
    Text-only AI Analyzer for OSINT analysis.
    No vision, no images, no EXIF.
    """

    def __init__(self, service: str):
        self.service = service

    def analyze_data(self, collected_data: Dict[str, Any], target: str) -> Dict[str, Any]:
        if not self.service:
            return {
                "summary": "AI analysis unavailable",
                "entities": {},
                "patterns": [],
                "correlations": [],
                "risk_assessment": {
                    "score": 0,
                    "level": "UNKNOWN",
                    "factors": []
                }
            }

        prompt = f"""
You are an OSINT analyst.

Target: {target}

Collected data:
{json.dumps(collected_data, indent=2)}

Return ONLY valid JSON with:
- entities
- patterns
- correlations
- risk_assessment {{ score, level, factors }}
- summary
"""

        try:
            if self.service == "groq":
                return self._call_groq(prompt)
            elif self.service == "gemini":
                return self._call_gemini(prompt)
            elif self.service == "anthropic":
                return self._call_anthropic(prompt)
            elif self.service == "huggingface":
                return self._call_huggingface(prompt)
            else:
                return {"summary": "Unsupported AI service"}

        except Exception as e:
            return {
                "summary": f"AI failed: {str(e)}",
                "entities": {},
                "patterns": [],
                "correlations": [],
                "risk_assessment": {
                    "score": 0,
                    "level": "UNKNOWN",
                    "factors": []
                }
            }

    # ---------- PROVIDERS ----------

    def _call_groq(self, prompt: str) -> Dict[str, Any]:
        response = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {GROQ_API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": "meta-llama/llama-4-scout-17b-16e-instruct",
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.3,
                "max_tokens": 2000
            },
            timeout=60
        )
        response.raise_for_status()
        return self._parse(response.json()["choices"][0]["message"]["content"])

    def _call_gemini(self, prompt: str) -> Dict[str, Any]:
        response = requests.post(
            f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}",
            headers={"Content-Type": "application/json"},
            json={"contents": [{"parts": [{"text": prompt}]}]},
            timeout=60
        )
        response.raise_for_status()
        return self._parse(
            response.json()["candidates"][0]["content"]["parts"][0]["text"]
        )

    def _call_anthropic(self, prompt: str) -> Dict[str, Any]:
        import anthropic
        client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
        msg = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=2000,
            messages=[{"role": "user", "content": prompt}]
        )
        return self._parse(msg.content[0].text)

    def _call_huggingface(self, prompt: str) -> Dict[str, Any]:
        response = requests.post(
            "https://api-inference.huggingface.co/models/mistralai/Mistral-7B-Instruct-v0.2",
            headers={"Authorization": f"Bearer {HUGGINGFACE_API_KEY}"},
            json={"inputs": prompt},
            timeout=60
        )
        response.raise_for_status()
        data = response.json()
        text = data[0]["generated_text"] if isinstance(data, list) else data.get("generated_text", "")
        return self._parse(text)

    # ---------- PARSER ----------

    def _parse(self, text: str) -> Dict[str, Any]:
        try:
            match = re.search(r"\{.*\}", text, re.DOTALL)
            if match:
                return json.loads(match.group())
        except Exception:
            pass

        return {
            "summary": text[:500],
            "entities": {},
            "patterns": [],
            "correlations": [],
            "risk_assessment": {
                "score": 0,
                "level": "UNKNOWN",
                "factors": []
            }
        }





def build_multi_modal_fusion(results, platform_presence):
    # Step 1: Verified platforms (real collected data only)
    verified_platforms = [
    platform
    for platform, data in results.items()
    if data.get("verification") == "api_verified"
]


    # Step 2: Heuristic platforms (username exists but no verified data)
    heuristic_platforms = [
        platform
        for platform, info in platform_presence.items()
        if info.get("exists") is True and platform not in verified_platforms
    ]

    # Step 3: Verified score (strong evidence)
    verified_score = min(len(verified_platforms) * 30, 60)

    # Step 4: Heuristic score (weak evidence, capped)
    heuristic_score = min(len(heuristic_platforms) * 2, 6)

    # Step 5: Correlation bonus (ONLY if verified exists)
    correlation_bonus = 0
    if len(verified_platforms) >= 2:
        correlation_bonus += 15

    # ❌ HIBP intentionally ignored (no API key)

    # Step 6: Final identity confidence
    identity_confidence = verified_score + heuristic_score + correlation_bonus

    # Hard safety rule
    if verified_score == 0:
        identity_confidence = min(identity_confidence, 20)

    identity_confidence = min(identity_confidence, 100)

    # Step 7: Confidence label
    if identity_confidence >= 70:
        confidence_level = "HIGH"
    elif identity_confidence >= 40:
        confidence_level = "MEDIUM"
    elif identity_confidence >= 20:
        confidence_level = "LOW"
    else:
        confidence_level = "WEAK"

    # Step 8: Human-readable findings
    key_findings = []

    if verified_platforms:
        key_findings.append(
            f"Verified presence on {len(verified_platforms)} trusted platform(s)"
        )

    if heuristic_platforms:
        key_findings.append(
            f"Username observed on {len(heuristic_platforms)} unverified platform(s)"
        )

    if correlation_bonus > 0:
        key_findings.append("Cross-platform correlation increases confidence")

    if not verified_platforms:
        key_findings.append("No verified platforms found — identity unconfirmed")

    return {
        "identity_confidence": identity_confidence,
        "confidence_level": confidence_level,
        "verified_platforms": verified_platforms,
        "heuristic_platforms": heuristic_platforms,
        "key_findings": key_findings
    }

def add_canonical(platform_key, data, profile_url, verification, exists):
    """
    Add platform to canonical profiles if username EXISTS,
    even if collector data is weak or partial
    """
    if exists is not True:
        return None

    return {
        "platform": platform_key.capitalize(),
        "platform_key": platform_key,
        "username": data.get("profile", {}).get("username") if data else "",
        "profile_url": profile_url,
        "verification": verification,
        "exists": True
    }





# ==================== API ENDPOINTS ====================

@app.route('/api/analyze', methods=['POST'])
def analyze():
    """Main endpoint for OSINT analysis"""
    try:
        data = request.get_json()
        target = data.get('target', '')
        selected_platforms = set(data.get('platforms', []))

        if not target:
            return jsonify({'error': 'Target parameter required'}), 400

        # 🔍 Username existence detection
        enumerator = UniversalUsernameEnumerator(PLATFORM_RULES)
        raw_presence = enumerator.check_username(target)

        platform_presence = {
            p: info for p, info in raw_presence.items()
            if p in selected_platforms
        }

        # Initialize collectors
        github_collector = GitHubCollector(GITHUB_TOKEN)
        gitlab_collector = GitLabCollector()
        reddit_collector = RedditCollector()
        instagram_collector = InstagramCollector()
        youtube_collector = YouTubeCollector()
        facebook_collector = FacebookCollector()
        linkedin_collector = LinkedInCollector()
        twitter_collector = TwitterCollector()
        hibp_collector = HaveIBeenPwnedCollector(HIBP_API_KEY)

        results = {}
        canonical_profiles = {}

        # -------- COLLECTORS --------

        if 'github' in selected_platforms:
            gh_data = github_collector.collect(target)
            results['github'] = gh_data
            cp = add_canonical(
                "github",
                gh_data,
                f"https://github.com/{target}",
                gh_data.get("verification", "weak_verified"),
                platform_presence.get("github", {}).get("exists", False)
            )
            if cp:
                canonical_profiles["github"] = cp

        if 'gitlab' in selected_platforms:
            gl_data = gitlab_collector.collect(target)
            results['gitlab'] = gl_data
            cp = add_canonical(
                "gitlab",
                gl_data,
                gl_data.get("profile", {}).get("profile_url"),
                gl_data.get("verification", "weak_verified"),
                platform_presence.get("gitlab", {}).get("exists", False)
            )
            if cp:
                canonical_profiles["gitlab"] = cp

        if 'reddit' in selected_platforms:
            rd_data = reddit_collector.collect(target)
            results['reddit'] = rd_data
            cp = add_canonical(
                "reddit",
                rd_data,
                f"https://www.reddit.com/user/{target}",
                rd_data.get("verification", "weak_verified"),
                rd_data.get("found", False)
            )
            if cp:
                canonical_profiles["reddit"] = cp

        if 'instagram' in selected_platforms:
            ig_data = instagram_collector.collect(target)
            results['instagram'] = ig_data

            cp = add_canonical(
                "instagram",
                ig_data,
                f"https://www.instagram.com/{target}/",
                "weak_verified",
                platform_presence.get("instagram", {}).get("exists", False)
            )
            if cp:
               canonical_profiles["instagram"] = cp

        if 'youtube' in selected_platforms:
            yt_data = youtube_collector.collect(target)
            results['youtube'] = yt_data

            cp = add_canonical(
                 "youtube",
                 yt_data,
                 f"https://www.youtube.com/@{target}",
                 "weak_verified",
                 platform_presence.get("youtube", {}).get("exists", False)
    )
            if cp:
               canonical_profiles["youtube"] = cp

        if 'facebook' in selected_platforms:
            fb_data = facebook_collector.collect(target)
            results['facebook'] = fb_data

            cp = add_canonical(
                "facebook",
                 fb_data,
                 f"https://www.facebook.com/{target}",
                 "weak_verified",
                  platform_presence.get("facebook", {}).get("exists", False)
    )

        if cp:
           canonical_profiles["facebook"] = cp

        if 'linkedin' in selected_platforms:
            li_data = linkedin_collector.collect(target)
            results['linkedin'] = li_data

            cp = add_canonical(
                "linkedin",
                li_data,
                f"https://www.linkedin.com/in/{target}/",
                "weak_verified",
                platform_presence.get("linkedin", {}).get("exists", False)
            )

        if cp:
            canonical_profiles["linkedin"] = cp
    






        if 'twitter' in selected_platforms:
           tw_data = twitter_collector.collect(target)
           results['twitter'] = tw_data

           cp = add_canonical(
           "twitter",
           tw_data,
            f"https://x.com/{target}",
            "weak_verified",
         platform_presence.get("twitter", {}).get("exists", False)
    )

        if cp:
            canonical_profiles["twitter"] = cp

        # Breach check
        if '@' in target:
            results['haveibeenpwned'] = hibp_collector.collect(target)

        # -------- RISK ASSESSMENT --------
        risk_engine = RiskAssessmentEngine(AI_SERVICE)
        filtered_results = {
            p: results[p]
            for p in canonical_profiles
            if results.get(p, {}).get("found") is True
        }

        risk_assessment = risk_engine.assess_risks(filtered_results, target)
        risk_report = risk_engine.to_frontend_format(risk_assessment)

        # -------- FUSION --------
        multi_modal_fusion = build_multi_modal_fusion(
            results=canonical_profiles,
            platform_presence=platform_presence
        )

        # -------- AI ANALYSIS --------
        ai_analysis = {}
        if AI_SERVICE:
            analyzer = AIAnalyzer(AI_SERVICE)
            ai_analysis = analyzer.analyze_data(results, target)

        if not ai_analysis or not ai_analysis.get("summary"):
            ai_analysis = {
                "summary": "AI analysis not available.",
                "entities": {},
                "patterns": [],
                "correlations": [],
                "risk_assessment": {"score": 0, "level": "UNKNOWN", "factors": []}
            }

        # -------- FINDINGS --------
        content_findings = extract_content_findings(
            canonical_profiles=canonical_profiles,
            results=results
        )

        profiles_list = [
            {
                "platform": v["platform"],
                "platform_key": k,
                "username": v["username"],
                "profile_url": v["profile_url"],
                "verification": v["verification"],
                "exists": True
            }
            for k, v in canonical_profiles.items()
        ]

        response = {
            "target": target,
            "timestamp": datetime.now().isoformat(),
            "profiles": profiles_list,
            "platform_presence": platform_presence,
            "multi_modal_fusion": multi_modal_fusion,
            "risk_assessment": risk_report,
            "ai_analysis": ai_analysis,
            "findings": (risk_report["risk_items"][:10] + content_findings)[:15]
        }

        return jsonify(response), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    




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
            'image_geolocation': AI_SERVICE in ['groq', 'gemini', 'anthropic'] if AI_SERVICE else False,
            'risk_assessment': True
        }
    }), 200


if __name__ == '__main__':
    print(f"🚀 CHAKRAVYUH 1.0 OSINT Backend Starting...")
    print(f"🔡 AI Service: {AI_SERVICE or 'None configured'}")
    print(f"🛡️  Risk Assessment: Enabled with {AI_SERVICE or 'basic scoring'}")
    print(f"📊 Risk Analyzer: {'AI-Enhanced' if AI_SERVICE else 'Rule-Based Only'}")
    app.run(debug=True, port=5000)
>>>>>>> d46736adb11c5fcbcb2b72c57efef6f8ae7f0354
