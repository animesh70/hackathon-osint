from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
from bs4 import BeautifulSoup
import os
import re
from datetime import datetime, timedelta
import time
from typing import Dict, List, Any, Optional, Tuple
import json
import base64
import io
import tempfile
from dataclasses import dataclass, asdict
from enum import Enum

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
            "model": "llama-3.1-70b-versatile",
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
                'critical': assessment.critical_count,
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


# ==================== IMAGE/VIDEO PROCESSING ====================

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


# ==================== AI ANALYZER ====================

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


# ==================== API ENDPOINTS ====================

@app.route('/api/analyze', methods=['POST'])
def analyze():
    """Main endpoint for OSINT analysis with AI-powered risk assessment"""
    try:
        data = request.get_json()
        target = data.get('target', '')
        platforms = data.get('platforms', [])
        
        if not target:
            return jsonify({'error': 'Target parameter required'}), 400
        
        # Initialize collectors
        github_collector = GitHubCollector(GITHUB_TOKEN)
        twitter_collector = TwitterCollector()
        hibp_collector = HaveIBeenPwnedCollector(HIBP_API_KEY)
        linkedin_collector = LinkedInCollector()
        reddit_collector = RedditCollector()
        
        # Collect data from requested platforms
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
        
        # Check for breaches if target looks like email
        if '@' in target:
            results['haveibeenpwned'] = hibp_collector.collect(target)
            time.sleep(0.5)
        
        # Perform comprehensive risk assessment
        print("🔍 Performing risk assessment...")
        risk_engine = RiskAssessmentEngine(AI_SERVICE)
        risk_assessment = risk_engine.assess_risks(results, target)
        risk_report = risk_engine.to_frontend_format(risk_assessment)
        
        # Legacy AI analysis (kept for backward compatibility)
        ai_analysis = {}
        if AI_SERVICE:
            analyzer = AIAnalyzer(AI_SERVICE)
            ai_analysis = analyzer.analyze_data(results, target)
        
        # Prepare response
        response = {
            'target': target,
            'timestamp': datetime.now().isoformat(),
            'platforms_searched': platforms,
            'ai_service_used': AI_SERVICE or 'none',
            'risk_assessment': risk_report,  # NEW: Comprehensive risk assessment
            'platform_data': results,
            'ai_analysis': ai_analysis,  # Legacy analysis
            'findings': risk_report['risk_items'][:10]  # Top 10 findings
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
            'image_geolocation': AI_SERVICE in ['groq', 'gemini', 'anthropic'] if AI_SERVICE else False,
            'risk_assessment': True
        }
    }), 200


if __name__ == '__main__':
    print(f"🚀 CHAKRAVYUH 1.0 OSINT Backend Starting...")
    print(f"🔡 AI Service: {AI_SERVICE or 'None configured'}")
    print(f"🖼️  Image Geolocation: {'Enabled' if AI_SERVICE in ['groq', 'gemini', 'anthropic'] else 'Disabled (requires Groq/Gemini/Anthropic)'}")
    print(f"🎥 Video Geolocation: {'Enabled' if AI_SERVICE in ['groq', 'gemini', 'anthropic'] else 'Disabled (requires Groq/Gemini/Anthropic)'}")
    print(f"🛡️  Risk Assessment: Enabled with {AI_SERVICE or 'basic scoring'}")
    print(f"📊 Risk Analyzer: {'AI-Enhanced' if AI_SERVICE else 'Rule-Based Only'}")
    app.run(debug=True, port=5000)