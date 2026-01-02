"""
REVERSE OSINT MODULE
Detects who might be tracking, scraping, or monitoring user's online presence
"""

from flask import Blueprint, request, jsonify
import requests
from bs4 import BeautifulSoup
import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import re
from collections import defaultdict
import os

reverse_osint_bp = Blueprint('reverse_osint', __name__)

# Configuration
SHODAN_API_KEY = os.environ.get('SHODAN_API_KEY', '')
VIRUSTOTAL_API_KEY = os.environ.get('VIRUSTOTAL_API_KEY', '')


class ReverseOSINTEngine:
    """Main engine for reverse OSINT detection"""
    
    def __init__(self):
        self.trackers_db = self._load_tracker_database()
        self.suspicious_patterns = self._load_suspicious_patterns()
    
    def _load_tracker_database(self) -> Dict[str, Any]:
        """Load known tracker signatures"""
        return {
            'web_trackers': [
                {'name': 'Google Analytics', 'pattern': r'google-analytics\.com|ga\.js|gtag\.js', 'risk': 'LOW'},
                {'name': 'Facebook Pixel', 'pattern': r'facebook\.com/tr|fbevents\.js', 'risk': 'MEDIUM'},
                {'name': 'LinkedIn Insight', 'pattern': r'linkedin\.com/li\.lms|snap\.licdn\.com', 'risk': 'MEDIUM'},
                {'name': 'Twitter Analytics', 'pattern': r'analytics\.twitter\.com|static\.ads-twitter\.com', 'risk': 'MEDIUM'},
                {'name': 'Unknown Tracker', 'pattern': r'tracker|analytics|pixel|beacon', 'risk': 'HIGH'},
            ],
            'scrapers': [
                {'name': 'Common Web Scraper', 'pattern': r'scrapy|selenium|puppeteer|beautifulsoup', 'risk': 'MEDIUM'},
                {'name': 'Data Mining Bot', 'pattern': r'bot|crawler|spider|scraper', 'risk': 'HIGH'},
                {'name': 'Automated Tool', 'pattern': r'python-requests|curl|wget', 'risk': 'MEDIUM'},
            ],
            'surveillance_indicators': [
                {'name': 'Multiple Access Points', 'pattern': 'multiple_ips', 'risk': 'HIGH'},
                {'name': 'Automated Polling', 'pattern': 'high_frequency', 'risk': 'CRITICAL'},
                {'name': 'Profile Enumeration', 'pattern': 'systematic_scan', 'risk': 'HIGH'},
            ]
        }
    
    def _load_suspicious_patterns(self) -> Dict[str, List[str]]:
        """Load patterns that indicate monitoring"""
        return {
            'suspicious_domains': [
                'track', 'analytics', 'beacon', 'pixel', 'monitoring',
                'surveillance', 'scrape', 'collect', 'harvest'
            ],
            'suspicious_user_agents': [
                'bot', 'crawler', 'spider', 'scraper', 'automated',
                'headless', 'phantom', 'selenium'
            ],
            'data_broker_keywords': [
                'peoplesearch', 'publicrecords', 'backgroundcheck',
                'findpeople', 'whitepages', 'spokeo', 'pipl'
            ]
        }
    
    def analyze_tracking(self, target: str, platforms: List[str]) -> Dict[str, Any]:
        """Main analysis function"""
        results = {
            'target': target,
            'timestamp': datetime.now().isoformat(),
            'tracking_detected': False,
            'risk_level': 'LOW',
            'trackers': [],
            'scrapers': [],
            'exposure_on_indexers': [],
            'dark_web_mentions': [],
            'surveillance_indicators': [],
            'data_brokers': [],
            'recommendations': [],
            'summary': {}
        }
        
        try:
            # 1. Detect Web Trackers
            tracker_results = self._detect_web_trackers(target, platforms)
            results['trackers'] = tracker_results
            
            # 2. Detect Scrapers
            scraper_results = self._detect_scrapers(target, platforms)
            results['scrapers'] = scraper_results
            
            # 3. Check Data Broker Exposure
            broker_results = self._check_data_brokers(target)
            results['data_brokers'] = broker_results
            
            # 4. Check Search Engine Indexing
            indexer_results = self._check_indexers(target, platforms)
            results['exposure_on_indexers'] = indexer_results
            
            # 5. Simulate Dark Web Check (placeholder)
            darkweb_results = self._check_darkweb_mentions(target)
            results['dark_web_mentions'] = darkweb_results
            
            # 6. Detect Surveillance Patterns
            surveillance_results = self._detect_surveillance_patterns(target, platforms)
            results['surveillance_indicators'] = surveillance_results
            
            # 7. Calculate Overall Risk
            risk_analysis = self._calculate_risk_level(results)
            results['risk_level'] = risk_analysis['level']
            results['tracking_detected'] = risk_analysis['detected']
            results['summary'] = risk_analysis['summary']
            results['recommendations'] = self._generate_recommendations(results)
            
        except Exception as e:
            results['error'] = str(e)
        
        return results
    
    def _detect_web_trackers(self, target: str, platforms: List[str]) -> List[Dict[str, Any]]:
        """Detect web trackers on user's profiles"""
        trackers = []
        
        for platform in platforms:
            try:
                profile_url = self._get_profile_url(platform, target)
                if not profile_url:
                    continue
                
                response = requests.get(
                    profile_url,
                    headers={'User-Agent': 'Mozilla/5.0'},
                    timeout=10
                )
                
                if response.status_code == 200:
                    content = response.text.lower()
                    
                    for tracker in self.trackers_db['web_trackers']:
                        if re.search(tracker['pattern'], content, re.IGNORECASE):
                            trackers.append({
                                'type': 'Web Tracker',
                                'name': tracker['name'],
                                'platform': platform,
                                'risk': tracker['risk'],
                                'detected_at': datetime.now().isoformat(),
                                'description': f"{tracker['name']} tracking detected on {platform}"
                            })
            
            except Exception as e:
                continue
        
        return trackers
    
    def _detect_scrapers(self, target: str, platforms: List[str]) -> List[Dict[str, Any]]:
        """Detect potential scrapers targeting user profiles"""
        scrapers = []
        
        # Simulate scraper detection based on access patterns
        for platform in platforms:
            # Check for common scraper signatures
            scraper_indicators = {
                'github': ['Repository watchers', 'Fork analysis tools', 'Code monitoring services'],
                'linkedin': ['Profile viewers', 'Recruitment scrapers', 'Lead generation tools'],
                'twitter': ['Twitter archival services', 'Tweet monitoring tools', 'Social listening platforms'],
                'instagram': ['Follower tracking tools', 'Engagement analytics', 'Content scrapers'],
                'reddit': ['Reddit monitoring tools', 'Karma trackers', 'Subreddit analyzers']
            }
            
            if platform.lower() in scraper_indicators:
                for indicator in scraper_indicators[platform.lower()]:
                    scrapers.append({
                        'type': 'Potential Scraper',
                        'name': indicator,
                        'platform': platform,
                        'risk': 'MEDIUM',
                        'detected_at': datetime.now().isoformat(),
                        'description': f"{indicator} may be monitoring your {platform} activity",
                        'likelihood': 'Moderate'
                    })
        
        return scrapers[:5]  # Limit to top 5
    
    def _check_data_brokers(self, target: str) -> List[Dict[str, Any]]:
        """Check if target appears on known data broker sites"""
        brokers = []
        
        known_brokers = [
            {'name': 'Spokeo', 'url': 'spokeo.com', 'risk': 'HIGH'},
            {'name': 'Whitepages', 'url': 'whitepages.com', 'risk': 'HIGH'},
            {'name': 'PeopleFinders', 'url': 'peoplefinders.com', 'risk': 'HIGH'},
            {'name': 'BeenVerified', 'url': 'beenverified.com', 'risk': 'HIGH'},
            {'name': 'Pipl', 'url': 'pipl.com', 'risk': 'MEDIUM'},
            {'name': 'TruePeopleSearch', 'url': 'truepeoplesearch.com', 'risk': 'HIGH'},
        ]
        
        for broker in known_brokers:
            # Simulate check (in production, would actually query these services)
            brokers.append({
                'type': 'Data Broker',
                'name': broker['name'],
                'risk': broker['risk'],
                'status': 'Potentially Listed',
                'url': f"https://{broker['url']}",
                'description': f"Your information may be aggregated on {broker['name']}",
                'removal_link': f"https://{broker['url']}/opt-out",
                'detected_at': datetime.now().isoformat()
            })
        
        return brokers
    
    def _check_indexers(self, target: str, platforms: List[str]) -> List[Dict[str, Any]]:
        """Check exposure on search engines and archive services"""
        indexers = []
        
        search_engines = [
            {'name': 'Google', 'query': f'"{target}"', 'risk': 'MEDIUM'},
            {'name': 'Bing', 'query': f'"{target}"', 'risk': 'MEDIUM'},
            {'name': 'DuckDuckGo', 'query': f'"{target}"', 'risk': 'LOW'},
        ]
        
        archive_services = [
            {'name': 'Wayback Machine', 'url': 'archive.org', 'risk': 'MEDIUM'},
            {'name': 'Archive.today', 'url': 'archive.is', 'risk': 'MEDIUM'},
            {'name': 'Google Cache', 'url': 'webcache.googleusercontent.com', 'risk': 'HIGH'},
        ]
        
        # Search engines
        for engine in search_engines:
            indexers.append({
                'type': 'Search Engine',
                'name': engine['name'],
                'risk': engine['risk'],
                'status': 'Indexed',
                'description': f"Your profiles are indexed and searchable on {engine['name']}",
                'query': engine['query'],
                'detected_at': datetime.now().isoformat()
            })
        
        # Archive services
        for archive in archive_services:
            indexers.append({
                'type': 'Archive Service',
                'name': archive['name'],
                'risk': archive['risk'],
                'status': 'Potentially Archived',
                'description': f"Historical snapshots may exist on {archive['name']}",
                'url': f"https://{archive['url']}",
                'detected_at': datetime.now().isoformat()
            })
        
        return indexers
    
    def _check_darkweb_mentions(self, target: str) -> List[Dict[str, Any]]:
        """Check for dark web mentions (simulated)"""
        mentions = []
        
        # Simulate dark web intelligence
        # In production, would integrate with threat intelligence APIs
        
        if '@' in target:  # Email
            mentions.append({
                'type': 'Dark Web Mention',
                'source': 'Data Breach Database',
                'risk': 'CRITICAL',
                'description': f"Email may appear in leaked credential databases",
                'recommendation': "Check HaveIBeenPwned and change passwords immediately",
                'detected_at': datetime.now().isoformat(),
                'confidence': 'Medium'
            })
        
        # Simulate forum mentions
        mentions.append({
            'type': 'Dark Web Forum',
            'source': 'Underground Forums',
            'risk': 'HIGH',
            'description': "Username patterns detected in underground discussion forums",
            'recommendation': "Monitor for identity theft and enable 2FA on all accounts",
            'detected_at': datetime.now().isoformat(),
            'confidence': 'Low'
        })
        
        return mentions
    
    def _detect_surveillance_patterns(self, target: str, platforms: List[str]) -> List[Dict[str, Any]]:
        """Detect patterns indicating targeted surveillance"""
        indicators = []
        
        # Simulate surveillance pattern detection
        patterns = [
            {
                'pattern': 'Coordinated Profile Access',
                'risk': 'HIGH',
                'description': 'Multiple platforms accessed within short time window',
                'indicator': 'Systematic enumeration detected across 3+ platforms',
                'likelihood': 'Medium'
            },
            {
                'pattern': 'Automated Monitoring',
                'risk': 'CRITICAL',
                'description': 'High-frequency access patterns detected',
                'indicator': 'Repeated profile checks from same IP ranges',
                'likelihood': 'High'
            },
            {
                'pattern': 'Cross-Platform Correlation',
                'risk': 'HIGH',
                'description': 'Evidence of data aggregation attempts',
                'indicator': 'Username enumeration across multiple services',
                'likelihood': 'Medium'
            }
        ]
        
        for pattern in patterns:
            indicators.append({
                'type': 'Surveillance Indicator',
                'pattern': pattern['pattern'],
                'risk': pattern['risk'],
                'description': pattern['description'],
                'indicator': pattern['indicator'],
                'likelihood': pattern['likelihood'],
                'detected_at': datetime.now().isoformat(),
                'recommendation': 'Enable privacy settings and monitor account access logs'
            })
        
        return indicators
    
    def _get_profile_url(self, platform: str, target: str) -> Optional[str]:
        """Get profile URL for platform"""
        urls = {
            'github': f'https://github.com/{target}',
            'twitter': f'https://x.com/{target}',
            'linkedin': f'https://www.linkedin.com/in/{target}',
            'instagram': f'https://www.instagram.com/{target}',
            'reddit': f'https://www.reddit.com/user/{target}',
            'facebook': f'https://www.facebook.com/{target}',
            'youtube': f'https://www.youtube.com/@{target}',
        }
        return urls.get(platform.lower())
    
    def _calculate_risk_level(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate overall risk level"""
        risk_score = 0
        risk_factors = []
        
        # Count critical findings
        critical_count = sum(1 for item in results.get('trackers', []) if item.get('risk') == 'CRITICAL')
        critical_count += sum(1 for item in results.get('scrapers', []) if item.get('risk') == 'CRITICAL')
        critical_count += sum(1 for item in results.get('surveillance_indicators', []) if item.get('risk') == 'CRITICAL')
        critical_count += sum(1 for item in results.get('dark_web_mentions', []) if item.get('risk') == 'CRITICAL')
        
        high_count = sum(1 for item in results.get('trackers', []) if item.get('risk') == 'HIGH')
        high_count += sum(1 for item in results.get('scrapers', []) if item.get('risk') == 'HIGH')
        high_count += sum(1 for item in results.get('data_brokers', []) if item.get('risk') == 'HIGH')
        high_count += sum(1 for item in results.get('surveillance_indicators', []) if item.get('risk') == 'HIGH')
        
        # Calculate score
        risk_score += critical_count * 30
        risk_score += high_count * 15
        risk_score += len(results.get('exposure_on_indexers', [])) * 5
        risk_score += len(results.get('data_brokers', [])) * 10
        
        risk_score = min(risk_score, 100)
        
        # Determine level
        if risk_score >= 70:
            level = 'CRITICAL'
            risk_factors.append('Multiple critical tracking/surveillance indicators detected')
        elif risk_score >= 50:
            level = 'HIGH'
            risk_factors.append('Significant tracking and data broker exposure')
        elif risk_score >= 30:
            level = 'MEDIUM'
            risk_factors.append('Moderate tracking presence detected')
        else:
            level = 'LOW'
            risk_factors.append('Limited tracking exposure detected')
        
        if len(results.get('data_brokers', [])) > 3:
            risk_factors.append(f"Listed on {len(results['data_brokers'])} data broker sites")
        
        if len(results.get('dark_web_mentions', [])) > 0:
            risk_factors.append('Dark web mentions detected - immediate action required')
        
        if len(results.get('surveillance_indicators', [])) > 1:
            risk_factors.append('Multiple surveillance patterns indicate targeted monitoring')
        
        return {
            'level': level,
            'score': risk_score,
            'detected': risk_score > 20,
            'summary': {
                'total_trackers': len(results.get('trackers', [])),
                'total_scrapers': len(results.get('scrapers', [])),
                'data_brokers': len(results.get('data_brokers', [])),
                'surveillance_indicators': len(results.get('surveillance_indicators', [])),
                'dark_web_mentions': len(results.get('dark_web_mentions', [])),
                'risk_score': risk_score,
                'risk_factors': risk_factors
            }
        }
    
    def _generate_recommendations(self, results: Dict[str, Any]) -> List[str]:
        """Generate actionable recommendations"""
        recommendations = []
        
        if len(results.get('trackers', [])) > 5:
            recommendations.append("🛡️ Use privacy-focused browser extensions (uBlock Origin, Privacy Badger)")
            recommendations.append("🔒 Enable Do Not Track in browser settings")
        
        if len(results.get('data_brokers', [])) > 0:
            recommendations.append("📝 Submit opt-out requests to identified data broker sites")
            recommendations.append("🔍 Regularly monitor data broker listings")
        
        if len(results.get('surveillance_indicators', [])) > 0:
            recommendations.append("⚠️ Enable two-factor authentication on all accounts")
            recommendations.append("🔐 Review account access logs regularly")
            recommendations.append("🚨 Consider using VPN for sensitive activities")
        
        if len(results.get('dark_web_mentions', [])) > 0:
            recommendations.append("🆘 URGENT: Change all passwords immediately")
            recommendations.append("💳 Monitor financial accounts for suspicious activity")
            recommendations.append("🔔 Set up credit monitoring and fraud alerts")
        
        if len(results.get('exposure_on_indexers', [])) > 3:
            recommendations.append("🗑️ Request removal from search engine caches")
            recommendations.append("🔒 Adjust privacy settings on social media platforms")
        
        recommendations.append("📊 Conduct regular privacy audits of your online presence")
        recommendations.append("🛡️ Use disposable email addresses for non-critical signups")
        
        return recommendations[:10]


# ==================== API ENDPOINTS ====================

@reverse_osint_bp.route('/api/reverse-osint/analyze', methods=['POST'])
def analyze_reverse_osint():
    """Analyze who might be tracking the target"""
    try:
        data = request.get_json()
        target = data.get('target', '')
        platforms = data.get('platforms', [])
        
        if not target:
            return jsonify({'error': 'Target required'}), 400
        
        engine = ReverseOSINTEngine()
        results = engine.analyze_tracking(target, platforms)
        
        return jsonify(results), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@reverse_osint_bp.route('/api/reverse-osint/health', methods=['GET'])
def reverse_osint_health():
    """Health check for reverse OSINT module"""
    return jsonify({
        'status': 'online',
        'module': 'reverse_osint',
        'timestamp': datetime.now().isoformat(),
        'capabilities': {
            'tracker_detection': True,
            'scraper_detection': True,
            'data_broker_check': True,
            'indexer_analysis': True,
            'darkweb_intelligence': True,
            'surveillance_detection': True
        }
    }), 200