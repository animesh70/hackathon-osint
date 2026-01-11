"""
Challenge 7: Real-World OSINT Robustness Handler
Standalone module for handling messy real-world OSINT data

Usage:
    from challenge7_backend import RealWorldOSINTHandler
    
    handler = RealWorldOSINTHandler()
    clean_data = handler.process_results(results, target)
"""

import hashlib
from datetime import datetime
from typing import Dict, List, Any

class RealWorldOSINTHandler:
    """
    Challenge 7: Handle Real-World OSINT Conditions
    - Incomplete/outdated data
    - Duplicate/noisy records
    - Platform restrictions
    - Scattered information
    - Unknown exposure patterns
    """
    
    def __init__(self):
        self.platform_restrictions = {
            'instagram': {'rate_limit': True, 'requires_login': True, 'data_quality': 'LOW'},
            'facebook': {'rate_limit': True, 'requires_login': True, 'data_quality': 'LOW'},
            'linkedin': {'rate_limit': True, 'requires_login': True, 'data_quality': 'LOW'},
            'twitter': {'rate_limit': True, 'requires_login': False, 'data_quality': 'MEDIUM'},
            'github': {'rate_limit': False, 'requires_login': False, 'data_quality': 'HIGH'},
            'gitlab': {'rate_limit': False, 'requires_login': False, 'data_quality': 'HIGH'},
            'reddit': {'rate_limit': False, 'requires_login': False, 'data_quality': 'HIGH'}
        }
    
    def process_results(self, results: Dict, target: str) -> Dict:
        """
        Main entry point - processes all OSINT results
        
        Args:
            results: Dict of platform results
            target: Target identifier
            
        Returns:
            Dict with enhanced data including:
            - consolidated_intelligence
            - behavioral_patterns
            - data_quality
            - duplicates_removed count
        """
        # Step 1: Apply platform-specific handling
        for platform_name, data in results.items():
            if data.get('found'):
                # Add platform restrictions info
                results[platform_name] = self.handle_platform_restrictions(platform_name, data)
                
                # Detect outdated data
                results[platform_name] = self.detect_outdated_data(results[platform_name], platform_name)
                
                # Handle incomplete profiles
                if results[platform_name].get('profile'):
                    results[platform_name]['profile'] = self.handle_incomplete_data(
                        results[platform_name]['profile']
                    )
        
        # Step 2: Extract and deduplicate findings
        all_findings = self._extract_all_findings(results)
        deduplicated_findings = self.deduplicate_data(all_findings)
        
        # Step 3: Consolidate scattered data
        consolidated_intel = self.consolidate_scattered_data(results)
        
        # Step 4: Detect behavioral patterns
        behavioral_patterns = self.detect_unknown_patterns(results)
        
        # Step 5: Calculate data quality
        quality_metrics = self.calculate_data_quality_score(results)
        
        return {
            'consolidated_intelligence': consolidated_intel,
            'behavioral_patterns': behavioral_patterns,
            'data_quality': quality_metrics,
            'duplicates_removed': len(all_findings) - len(deduplicated_findings),
            'processed_results': results
        }
    
    def deduplicate_data(self, data_list: List[Dict]) -> List[Dict]:
        """Remove duplicate entries using content hashing"""
        seen = set()
        deduplicated = []
        
        for item in data_list:
            # Create hash from key fields
            content = f"{item.get('type', '')}-{item.get('value', '')}-{item.get('platforms', '')}"
            content_hash = hashlib.md5(content.encode()).hexdigest()
            
            if content_hash not in seen:
                seen.add(content_hash)
                deduplicated.append(item)
        
        return deduplicated
    
    def handle_incomplete_data(self, profile: Dict) -> Dict:
        """Fill missing fields with smart defaults"""
        defaults = {
            'username': 'Unknown',
            'name': 'Not Available',
            'bio': 'No bio provided',
            'location': 'Location not disclosed',
            'email': 'Not public',
            'created_at': 'Unknown',
            'followers': 0,
            'following': 0
        }
        
        # Only fill if truly missing
        for key, default_value in defaults.items():
            if key not in profile or profile[key] in [None, '', 'None', 'null']:
                profile[key] = default_value
        
        # Calculate data quality
        filled_fields = sum(1 for v in profile.values() if v not in defaults.values())
        total_fields = len(profile)
        profile['data_completeness'] = round((filled_fields / total_fields) * 100, 1)
        
        return profile
    
    def detect_outdated_data(self, data: Dict, platform: str) -> Dict:
        """Mark data as potentially outdated"""
        data['freshness'] = 'FRESH'
        
        timestamp_fields = ['created_at', 'updated_at', 'last_activity', 'breach_date']
        
        for field in timestamp_fields:
            if field in data:
                try:
                    date_str = str(data[field])
                    
                    # Parse various date formats
                    for fmt in ['%Y-%m-%d', '%Y-%m-%dT%H:%M:%S', '%Y-%m-%dT%H:%M:%SZ']:
                        try:
                            date_obj = datetime.strptime(date_str.split('.')[0].replace('Z', ''), fmt)
                            days_old = (datetime.now() - date_obj).days
                            
                            if days_old > 365:
                                data['freshness'] = 'STALE'
                                data['days_old'] = days_old
                            elif days_old > 180:
                                data['freshness'] = 'AGING'
                                data['days_old'] = days_old
                            
                            break
                        except:
                            continue
                except:
                    pass
        
        return data
    
    def handle_platform_restrictions(self, platform: str, raw_data: Dict) -> Dict:
        """Handle rate limits and access restrictions"""
        platform_info = self.platform_restrictions.get(
            platform.lower(), 
            {'data_quality': 'MEDIUM'}
        )
        
        return {
            **raw_data,
            'platform_restrictions': platform_info,
            'reliability_note': f"Data quality: {platform_info['data_quality']}"
        }
    
    def consolidate_scattered_data(self, all_results: Dict) -> Dict:
        """Merge scattered information across platforms"""
        consolidated = {
            'emails': set(),
            'usernames': set(),
            'names': set(),
            'locations': set(),
            'companies': set(),
            'skills': set(),
            'links': set()
        }
        
        for platform, data in all_results.items():
            if not data.get('found'):
                continue
            
            profile = data.get('profile', {})
            
            if profile.get('email') and profile['email'] != 'Not public':
                consolidated['emails'].add(profile['email'])
            
            if profile.get('username') and profile['username'] != 'Unknown':
                consolidated['usernames'].add(profile['username'])
            
            if profile.get('name') and profile['name'] != 'Not Available':
                consolidated['names'].add(profile['name'])
            
            if profile.get('location') and profile['location'] != 'Location not disclosed':
                consolidated['locations'].add(profile['location'])
            
            if profile.get('company'):
                consolidated['companies'].add(profile['company'])
            
            if profile.get('blog'):
                consolidated['links'].add(profile['blog'])
        
        # Convert sets to lists
        return {k: list(v) for k, v in consolidated.items()}
    
    def detect_unknown_patterns(self, results: Dict) -> List[str]:
        """Identify unusual patterns in collected data"""
        patterns = []
        
        # Pattern 1: Privacy-conscious behavior
        platforms_found = sum(1 for v in results.values() if v.get('found'))
        has_email = any(
            v.get('profile', {}).get('email') not in [None, '', 'Not public'] 
            for v in results.values() if v.get('found')
        )
        
        if platforms_found >= 3 and not has_email:
            patterns.append("🔍 Privacy-conscious: Active on multiple platforms but email not exposed")
        
        # Pattern 2: Dormant accounts
        old_accounts = []
        for platform, data in results.items():
            if data.get('found') and data.get('freshness') == 'STALE':
                old_accounts.append(platform)
        
        if old_accounts:
            patterns.append(f"⏰ Dormant accounts detected on: {', '.join(old_accounts)}")
        
        # Pattern 3: Professional vs Personal split
        professional = ['github', 'gitlab', 'linkedin']
        personal = ['instagram', 'facebook', 'twitter', 'reddit']
        
        prof_count = sum(1 for p in professional if results.get(p, {}).get('found'))
        pers_count = sum(1 for p in personal if results.get(p, {}).get('found'))
        
        if prof_count > 0 and pers_count == 0:
            patterns.append("💼 Professional-only presence - minimal personal exposure")
        elif pers_count > 0 and prof_count == 0:
            patterns.append("🎮 Personal-only presence - no professional footprint")
        
        # Pattern 4: Username consistency
        usernames = [
            v.get('profile', {}).get('username') 
            for v in results.values() if v.get('found')
        ]
        usernames = [u for u in usernames if u and u not in ['Unknown', None]]
        
        if len(set(usernames)) == 1 and len(usernames) >= 3:
            patterns.append(f"🎯 Consistent username '{usernames[0]}' across all platforms")
        elif len(set(usernames)) == len(usernames) and len(usernames) >= 3:
            patterns.append("🔀 Different username on each platform - compartmentalization strategy")
        
        return patterns
    
    def calculate_data_quality_score(self, results: Dict) -> Dict:
        """Calculate overall data quality and completeness"""
        total_platforms = len(results)
        found_platforms = sum(1 for v in results.values() if v.get('found'))
        
        if found_platforms == 0:
            return {
                'overall_score': 0,
                'platform_coverage': 0,
                'data_completeness': 0,
                'freshness_score': 0,
                'verification_score': 0,
                'grade': 'F'
            }
        
        # Data completeness per platform
        completeness_scores = []
        for platform, data in results.items():
            if data.get('found'):
                profile = data.get('profile', {})
                filled = sum(
                    1 for v in profile.values() 
                    if v and v not in ['Unknown', 'Not Available', 'No bio provided', 'Location not disclosed', 'Not public']
                )
                total = len(profile)
                if total > 0:
                    completeness_scores.append((filled / total) * 100)
        
        avg_completeness = sum(completeness_scores) / len(completeness_scores) if completeness_scores else 0
        
        # Calculate quality factors
        quality_factors = {
            'platform_coverage': (found_platforms / total_platforms) * 40,
            'data_completeness': (avg_completeness / 100) * 30,
            'freshness': 20,
            'verification': 10
        }
        
        # Adjust for stale data
        stale_count = sum(1 for v in results.values() if v.get('freshness') == 'STALE')
        if stale_count > 0:
            quality_factors['freshness'] -= (stale_count / found_platforms) * 15
        
        # Adjust for verification
        verified_count = sum(1 for v in results.values() if v.get('verification') == 'api_verified')
        if verified_count > 0:
            quality_factors['verification'] = (verified_count / found_platforms) * 10
        
        total_score = sum(quality_factors.values())
        
        return {
            'overall_score': round(min(total_score, 100), 1),
            'platform_coverage': round(quality_factors['platform_coverage'], 1),
            'data_completeness': round(avg_completeness, 1),
            'freshness_score': round(max(quality_factors['freshness'], 0), 1),
            'verification_score': round(quality_factors['verification'], 1),
            'grade': 'A' if total_score >= 80 else 'B' if total_score >= 60 else 'C' if total_score >= 40 else 'D'
        }
    
    def _extract_all_findings(self, results: Dict) -> List[Dict]:
        """Extract all findings from results for deduplication"""
        all_findings = []
        
        for platform, pf_data in results.items():
            if pf_data.get('found'):
                profile = pf_data.get('profile', {})
                for key, value in profile.items():
                    if value and value not in ['Unknown', 'Not Available', 'No bio provided', 'Location not disclosed', 'Not public']:
                        all_findings.append({
                            'type': key,
                            'value': str(value)[:100],
                            'platforms': platform,
                            'risk': 'MEDIUM'
                        })
        
        return all_findings