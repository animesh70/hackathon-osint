
import React, { useState, useEffect } from 'react';
import { Search, Upload, MapPin, Shield, AlertTriangle, Globe, Image, FileText, Activity, Eye, Target, Zap, CheckCircle, XCircle } from 'lucide-react';
import SkeletonCard from "./SkeletonCard";
import SnowEffect from './SnowEffect';
import { Snowflake } from 'lucide-react'; 

import {
   SiGithub,
   SiGitlab,
   SiX,
   SiInstagram,
   SiYoutube,
   SiFacebook,
   SiLinkedin,
   SiReddit
} from 'react-icons/si';

import ChatAssistant from './ChatAssistant';

export default function OSINTDashboard() {
  const [viewMode, setViewMode] = useState("user");
  const [activeTab, setActiveTab] = useState('multi-modal');
  const [targetInput, setTargetInput] = useState('');
  const [analyzing, setAnalyzing] = useState(false);
  const [results, setResults] = useState(null);
  const [logs, setLogs] = useState([]);
  const [backendStatus, setBackendStatus] = useState(null);
  const [selectedPlatforms, setSelectedPlatforms] = useState({
     github: true,
     gitlab: true,
     reddit: true,
     instagram: true,
     youtube: true,
     facebook: true,
     linkedin: true,
     twitter: true
  });

  const [backgroundTheme, setBackgroundTheme] = useState('Dark Mode');
  const [snowEnabled, setSnowEnabled] = useState(true);

const backgrounds = {
  'Dark Mode': 'from-black/50 to-black/30',
  'Light Mode': 'from-white/80 to-gray-200/100',
  'Mint Breeze': 'from-green-200 via-blue-200 to-green-300',
  'Sunset Peach': 'from-orange-200 via-pink-200 to-yellow-200',
  'Misty Blue': 'from-blue-300 via-purple-200 to-blue-400',
  'Desert Sand': 'from-pink-200 via-yellow-200 to-green-200',
  'Lavender Dream': 'from-purple-200 via-blue-100 to-pink-200',
  'Twilight': 'from-purple-900 via-orange-800 to-yellow-700',
  'Aurora': 'from-purple-600 via-blue-500 to-cyan-400',
  'Forest Night': 'from-gray-900 via-green-900 to-gray-800',
  'Deep Night': 'from-indigo-950 via-purple-950 to-black',
  'Chocolate': 'from-amber-900 via-red-900 to-stone-900'
};




  // 🔗 Platform icon mapping for fusion UI
const platformIcons = {
  github: SiGithub,
  gitlab: SiGitlab,
  reddit: SiReddit,
  instagram: SiInstagram,
  youtube: SiYoutube,
  facebook: SiFacebook,
  linkedin: SiLinkedin,
  twitter: SiX
};

  // Image/Video analysis state
  const [uploadedFile, setUploadedFile] = useState(null);
  const [geoResults, setGeoResults] = useState(null);
  const [geoAnalyzing, setGeoAnalyzing] = useState(false);

  const BACKEND_URL = 'http://localhost:5000';

  const challenges = [
    { id: 'multi-modal', name: 'Multi-Modal Fusion', icon: Globe },
    { id: 'visual', name: 'Visual Intelligence', icon: Image },
    { id: 'risk', name: 'Risk Assessment', icon: Shield }
  ];

  // Check backend health on mount
  useEffect(() => {
    checkBackendHealth();
  }, []);

  const checkBackendHealth = async () => {
    try {
      const response = await fetch(`${BACKEND_URL}/api/health`);
      const data = await response.json();
      setBackendStatus(data);
      addLog('Backend connected successfully', 'success');
    } catch (error) {
      setBackendStatus({ status: 'offline', error: error.message });
      addLog('Backend connection failed. Make sure Flask server is running on port 5000', 'error');
    }
  };

  const addLog = (message, type = 'info') => {
    const timestamp = new Date().toLocaleTimeString();
    setLogs(prev => [...prev, { message, timestamp, type }]);
  };

 const togglePlatform = (platform) => {
  setSelectedPlatforms(prev => ({
    ...prev,
    [platform]: !prev[platform]
  }));

  // 🔒 Prevent stale results from previous selections
  setResults(null);
};


  const handleAnalyze = async () => {
    if (!targetInput.trim()) {
      addLog('Please enter a target identifier', 'error');
      return;
    }

    if (!backendStatus || backendStatus.status === 'offline') {
      addLog('Backend is offline. Please start the Flask server.', 'error');
      return;
    }

    setAnalyzing(true);
    setResults(null);
    setLogs([]);
    
    addLog('Initializing OSINT analysis...');
    addLog(`Target: ${targetInput}`);
    
    const enabledPlatforms = Object.keys(selectedPlatforms).filter(p => selectedPlatforms[p]);
    addLog(`Platforms selected: ${enabledPlatforms.join(', ')}`);

    try {
      addLog('Sending request to backend...');
      
      const response = await fetch(`${BACKEND_URL}/api/analyze`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          target: targetInput,
          platforms: enabledPlatforms
        })
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      
      addLog('Analysis complete!');
      addLog(`AI Service: ${data.ai_service_used || 'none'}`);
      addLog(`Platforms found: ${data?.risk_score?.platforms ?? 0}`);
addLog(`Risk level: ${data?.risk_score?.level ?? 'UNKNOWN'}`);

      
      setResults(data);
      
    } catch (error) {
      addLog(`Error: ${error.message}`, 'error');
      console.error('Analysis error:', error);
    } finally {
      setAnalyzing(false);
    }
  };

  const handleFileUpload = (event) => {
    const file = event.target.files[0];
    if (file) {
      setUploadedFile(file);
      addLog(`File selected: ${file.name}`);
    }
  };

  const handleVisualAnalyze = async () => {
    if (!uploadedFile) {
      addLog('Please select an image or video file', 'error');
      return;
    }

    if (!backendStatus || backendStatus.status === 'offline') {
      addLog('Backend is offline. Please start the Flask server.', 'error');
      return;
    }

    setGeoAnalyzing(true);
    setGeoResults(null);
    setLogs([]);

    const isVideo = uploadedFile.type.startsWith('video/');
    const endpoint = isVideo ? '/api/geolocation/video' : '/api/geolocation/image';

    addLog(`Analyzing ${isVideo ? 'video' : 'image'}: ${uploadedFile.name}`);
    addLog('Uploading file to backend...');

    try {
      const formData = new FormData();
      formData.append('file', uploadedFile);
      if (isVideo) {
        formData.append('num_frames', '5');
      }

      addLog('Processing file...');
      if (isVideo) {
        addLog('Extracting frames from video...');
      } else {
        addLog('Extracting EXIF metadata...');
      }

      const response = await fetch(`${BACKEND_URL}${endpoint}`, {
        method: 'POST',
        body: formData
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      
      addLog('Analysis complete!');
      addLog(`Coordinate source: ${data.coordinate_source}`);
      addLog(`Confidence: ${data.confidence}%`);
      if (data.coordinates) {
        addLog(`Location: ${data.coordinates.latitude}, ${data.coordinates.longitude}`);
      }
      
      setGeoResults(data);
      
    } catch (error) {
      addLog(`Error: ${error.message}`, 'error');
      console.error('Visual analysis error:', error);
    } finally {
      setGeoAnalyzing(false);
    }
  };
// --- Attacker View sorting logic ---
const exploitabilityWeight = (risk) => {
  switch (risk) {
    case "CRITICAL":
      return 3;
    case "MEDIUM":
      return 2;
    case "LOW":
      return 1;
    default:
      return 0;
  }
};

// ✅ Canonical Discovered Profiles (single source of truth)
const discoveredProfiles = (results?.profiles || []).filter(
  profile =>
    profile.exists === true &&
    selectedPlatforms[profile.platform_key] &&
    (
      profile.verification === "api_verified" ||
      profile.verification === "weak_verified"
    )
);

const fusion = results?.multi_modal_fusion
  ? {
      ...results.multi_modal_fusion,
      verified_platforms: results.multi_modal_fusion.verified_platforms.filter(
        p =>
          selectedPlatforms[p] &&
          discoveredProfiles.some(dp => dp.platform_key === p)
      ),
      heuristic_platforms: results.multi_modal_fusion.heuristic_platforms.filter(
        p =>
          selectedPlatforms[p] &&
          !discoveredProfiles.some(dp => dp.platform_key === p)
      )
    }
  : {
      identity_confidence: 0,
      confidence_level: "WEAK",
      verified_platforms: [],
      heuristic_platforms: [],
      key_findings: []
    };


// ✅ Platforms confirmed via canonical profiles (SINGLE SOURCE OF TRUTH)
const allowedPlatforms = new Set(
  (results?.profiles || [])
    .filter(p => p.exists === true)
    .map(p => p.platform_key)
);

const displayFindings = (() => {
  if (!results?.findings) return [];

 // ✅ Keep findings ONLY if at least one platform is confirmed
  const filtered = results.findings.filter(finding => {
    if (!finding.platforms) return false;

    return finding.platforms
      .split(",")
      .some(p =>
        allowedPlatforms.has(p.trim().toLowerCase())
      );
  });

    // ✅ Deduplicate (platform + type + value)
  const uniqueMap = new Map();
  filtered.forEach(f => {
    const key = `${f.platforms}-${f.type}-${f.value}`;
    if (!uniqueMap.has(key)) {
      uniqueMap.set(key, f);
    }
  });
  const deduped = Array.from(uniqueMap.values());

    
  
  if (viewMode === "user") {
    return deduped;
  }

  // Attacker view → most exploitable first
  return [...deduped].sort(
    (a, b) => exploitabilityWeight(b.risk) - exploitabilityWeight(a.risk)
  );
})();
 

// Attacker wording helper (frontend-only)
const attackerNarrative = (finding) => {
  if (finding.risk === "CRITICAL") {
    return "High-value attack surface. Immediate exploitation possible.";
  }

  if (finding.risk === "MEDIUM") {
    return "Useful for reconnaissance or social engineering.";
  }

  return "Low direct impact, but contributes to profiling.";
};

const exploitTags = (finding) => {
  if (finding.risk === "CRITICAL") {
    return ["ACCOUNT TAKEOVER", "PHISHING"];
  }

  if (finding.risk === "MEDIUM") {
    return ["RECON", "SOCIAL ENGINEERING"];
  }

  return ["PROFILING"];
};


 // ================= NORMALIZED RISK SCORE =================
const riskScore = results?.risk_assessment?.risk_score
  ? {
      risk: results.risk_assessment.risk_score.risk ?? 0,
      exposures: results.risk_assessment.risk_score.exposures ?? 0,
      platforms: results.risk_assessment.risk_score.platforms ?? 0,
      critical:
        results.risk_assessment.risk_breakdown?.critical ??
        results.findings?.filter(f => f.risk === "CRITICAL").length ??
        0,
      factors: results.risk_assessment.risk_score.factors ?? []
    }
  : {
      risk: 0,
      exposures: 0,
      platforms: 0,
      critical: 0,
      factors: []
    };

  return (
   <div
  className={`min-h-screen bg-gradient-to-br ${backgrounds[backgroundTheme]} text-white transition-colors duration-500`}
>
      {/* Snow Effect */}
      <SnowEffect intensity={25} enabled={snowEnabled} />

      {/* Grain overlay */}
      <div className="fixed inset-0 pointer-events-none opacity-[0.015]" style={{
        backgroundImage: `url("data:image/svg+xml,%3Csvg viewBox='0 0 400 400' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noiseFilter'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23noiseFilter)'/%3E%3C/svg%3E")`,
        backgroundRepeat: 'repeat'
      }}></div>

      {/* Header */}
      <header className="relative border-b border-purple-500/20 bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 backdrop-blur-sm">
        <div className="max-w-7xl mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <Target className="w-8 h-8 text-purple-400" />
              <div>
                <h1 className="text-2xl font-bold text-white">
  CHAKRAVYUH 1.0
</h1>
<p className="text-sm text-white/80">
  OSINT Intelligence Platform
</p>

              </div>
            </div>
            <div className="flex items-center gap-4">
              <span className="text-sm text-purple-300">GITA Autonomous College</span>
              <div className={`w-2 h-2 rounded-full ${backendStatus?.status === 'online' ? 'bg-green-400' : 'bg-red-400'} animate-pulse`}></div>
              <span className="text-sm text-white">{backendStatus?.status === 'online' ? 'Backend Online' : 'Backend Offline'}</span>
              {backendStatus?.ai_service && (
                <span className="text-xs bg-purple-500/20 px-2 py-1 rounded">AI: {backendStatus.ai_service}</span>
              )}
            </div>
          </div>
        </div>
      </header>

      <div className="relative max-w-7xl mx-auto px-6 py-8">
        {/* Challenge Tabs */}
        <div className="flex gap-4 mb-8">
          {challenges.map((challenge) => {
            const Icon = challenge.icon;
            return (
              <button
                key={challenge.id}
                onClick={() => setActiveTab(challenge.id)}
                className={`flex-1 p-4 rounded-lg transition-all ${
                  activeTab === challenge.id
                    ? 'bg-purple-600 shadow-lg shadow-purple-500/50'
                    : 'bg-white/5 hover:bg-white/10'
                }`}
              >
                <Icon className="w-6 h-6 mx-auto mb-2" />
                <p className="text-sm font-medium">{challenge.name}</p>
              </button>
            );
          })}
        </div>

        {/* Multi-Modal Fusion */}
        {activeTab === 'multi-modal' && (
          <div className="space-y-6">
           <div className="
  bg-black/50
  backdrop-blur-sm 
  border border-purple-500/20 
  rounded-xl p-6
">

              <h2 className="text-xl font-semibold mb-4 flex items-center gap-2">
                <Globe className="w-5 h-5 text-purple-400" />
                Multi-Modal OSINT Fusion Engine
              </h2>
              
              {/* Input Section */}
              <div className="space-y-4">
                <div>
                  <label className="block text-sm text-purple-300 mb-2">Target Identifier</label>
                  <div className="flex gap-3">
                    <input
                      type="text"
                      value={targetInput}
                      onChange={(e) => setTargetInput(e.target.value)}
                      placeholder="Enter username, email, or profile URL..."
                     className="
  flex-1 
  bg-black/60 text-white
  border border-purple-500/30 
  rounded-lg px-4 py-3 
  focus:outline-none focus:border-purple-500 
  placeholder-gray-500
"

                      onKeyPress={(e) => e.key === 'Enter' && handleAnalyze()}
                    />
                    <button
                      onClick={handleAnalyze}
                      disabled={analyzing || !targetInput || backendStatus?.status !== 'online'}
                      className="px-6 py-3 bg-purple-600 hover:bg-purple-700 disabled:bg-gray-600 disabled:cursor-not-allowed rounded-lg font-medium transition-colors flex items-center gap-2"
                    >
                      {analyzing ? (
                        <>
                          <Activity className="w-4 h-4 animate-spin" />
                          Analyzing...
                        </>
                      ) : (
                        <>
                          <Search className="w-4 h-4" />
                          Analyze
                        </>
                      )}
                    </button>
                  </div>
                </div>

                {/* Data Sources */}
                <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                  {[
                     { name: 'GitHub', icon: SiGithub, key: 'github' },
                     { name: 'GitLab', icon: SiGitlab, key: 'gitlab' },
                     { name: 'Reddit', icon: SiReddit, key: 'reddit' },
                     { name: 'Instagram', icon: SiInstagram, key: 'instagram' },
                     { name: 'YouTube', icon: SiYoutube, key: 'youtube' },
                     { name: 'Facebook', icon: SiFacebook, key: 'facebook' },
                     { name: 'LinkedIn', icon: SiLinkedin, key: 'linkedin' },
                     { name: 'Twitter', icon: SiX, key: 'twitter' }
                  ].map((platform) => {
                    const Icon = platform.icon;
                    return (
               <label
  key={platform.name}
  className="
    flex items-center gap-2 
    bg-black/40 hover:bg-black/60
    p-3 rounded-lg cursor-pointer transition-colors group
  "
>

                        <input 
                          type="checkbox" 
                          checked={selectedPlatforms[platform.key]}
                          onChange={() => togglePlatform(platform.key)}
                          className="rounded border-purple-500" 
                        />
                        <Icon className="w-4 h-4 text-purple-400 group-hover:text-purple-300 transition-colors" />
                        <span className="text-sm">{platform.name}</span>
                      </label>
                    );
                  })}
                </div>
              </div>

              {/* Real-Time Logs */}
             <div className="
  mt-6 
  bg-black/70
  border border-purple-500/20 
  rounded-lg p-4 font-mono
">

                <div className="flex items-center justify-between mb-3">
                  <h3 className="text-xs font-bold uppercase tracking-widest text-purple-400">
                    Real-time Logs
                  </h3>
                  <Activity className={`w-4 h-4 text-purple-400 ${logs.length > 0 ? 'animate-pulse' : ''}`} />
                </div>
                <div className="space-y-2 max-h-40 overflow-y-auto">
                  {logs.map((log, i) => (
                    <div key={i} className="text-[11px] flex gap-3 animate-in fade-in slide-in-from-left-2">
                      <span className="text-purple-500/50">
                        [{log.timestamp}]
                      </span>
                      <span className={log.type === 'error' ? 'text-red-400' : log.type === 'success' ? 'text-green-400' : 'text-gray-300'}>
                        {log.message}
                      </span>
                    </div>
                  ))}
                  {logs.length === 0 && (
                    <p className="text-xs text-gray-500 italic">
                      Awaiting command...
                    </p>
                  )}
                </div>
              </div>

              {/* Results */}
             {analyzing && (
  <div className="mt-6 grid grid-cols-1 md:grid-cols-2 gap-4">
    <SkeletonCard />
    <SkeletonCard />
    <SkeletonCard />
    <SkeletonCard />
  </div>
)}

{!analyzing && results && (
  <div className="mt-6 space-y-4">
 
 {/* 🔗 Multi-Modal Fusion Card */}
{results?.multi_modal_fusion && (
  <div className="bg-gradient-to-br from-indigo-500/10 to-purple-600/10 border border-purple-500/30 rounded-xl p-5">
    
    <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
      <Zap className="w-5 h-5 text-purple-400" />
      Multi-Modal OSINT Fusion
    </h3>

    {/* Identity Confidence */}
    <div className="mb-4">
      <p className="text-sm text-gray-400 mb-1">Identity Confidence</p>
      <div className="w-full bg-black/30 rounded-full h-3">
        <div
          className="h-3 rounded-full bg-purple-500 transition-all"
          style={{ width: `${fusion.identity_confidence}%` }}

        />
      </div>
      <p className="text-xs text-gray-400 mt-1">
       {fusion.identity_confidence}% confidence this identity belongs to the same person

      </p>
    </div>

  

{/* Verified Platforms */}
<div className="mb-4">
  <p className="text-sm text-gray-400 mb-1">Verified Platforms</p>
  <div className="flex flex-wrap gap-3">
    {fusion.verified_platforms.length > 0 ? (
      fusion.verified_platforms.map((platform, idx) => {
        const Icon = platformIcons[platform];
        return (
          <div
            key={idx}
            className="flex items-center gap-2 px-3 py-1 bg-green-500/20 text-green-300 rounded-full text-xs"
          >
            {Icon && <Icon className="w-4 h-4" />}
            <span className="capitalize">{platform}</span>
          </div>
        );
      })
    ) : (
      <span className="text-xs text-gray-500">No verified platforms</span>
    )}
  </div>
</div>

{/* Heuristic Platforms */}
<div className="mb-4">
  <p className="text-sm text-gray-400 mb-1">Unverified Signals</p>
  <div className="flex flex-wrap gap-3">
    {fusion.heuristic_platforms.length > 0 ? (
      fusion.heuristic_platforms.map((platform, idx) => {
        const Icon = platformIcons[platform];
        return (
          <div
            key={idx}
            className="flex items-center gap-2 px-3 py-1 bg-yellow-500/20 text-yellow-300 rounded-full text-xs"
          >
            {Icon && <Icon className="w-4 h-4" />}
            <span className="capitalize">{platform}</span>
          </div>
        );
      })
    ) : (
      <span className="text-xs text-gray-500">No unverified signals</span>
    )}
  </div>
</div>


    {/* Key Findings */}
    <div>
      <p className="text-sm text-gray-400 mb-1">Key Fusion Findings</p>
      <ul className="list-disc list-inside text-sm text-gray-300 space-y-1">
  {fusion.key_findings.length > 0 &&
    fusion.key_findings.map((finding, idx) => (
      <li key={idx}>{finding}</li>
    ))
  }
</ul>

    </div>

  </div>
)}

                  <div className="grid grid-cols-2 md:grid-cols-4 gap-4">

                    <div className="bg-gradient-to-br from-red-500/20 to-red-600/10 border border-red-500/30 rounded-lg p-4">
                      <div className="flex items-center justify-between mb-2">
                        <AlertTriangle className="w-5 h-5 text-red-400" />
                        <span className="text-2xl font-bold">{riskScore.risk}</span>
                      </div>
                      <p className="text-sm text-red-300">Risk Score</p>
                    </div>
                    <div className="bg-gradient-to-br from-blue-500/20 to-blue-600/10 border border-blue-500/30 rounded-lg p-4">
                      <div className="flex items-center justify-between mb-2">
                        <Eye className="w-5 h-5 text-blue-400" />
                        <span className="text-2xl font-bold">{riskScore.exposures}</span>
                      </div>
                      <p className="text-sm text-blue-300">Exposures Found</p>
                    </div>
                    <div className="bg-gradient-to-br from-purple-500/20 to-purple-600/10 border border-purple-500/30 rounded-lg p-4">
                      <div className="flex items-center justify-between mb-2">
                        <Globe className="w-5 h-5 text-purple-400" />
                        <span className="text-2xl font-bold">{riskScore.platforms}
</span>
                      </div>
                      <p className="text-sm text-purple-300">Platforms</p>
                    </div>
                    <div className="bg-gradient-to-br from-orange-500/20 to-orange-600/10 border border-orange-500/30 rounded-lg p-4">
                      <div className="flex items-center justify-between mb-2">
                        <Zap className="w-5 h-5 text-orange-400" />
                        <span className="text-2xl font-bold">{riskScore.critical}</span>
                      </div>
                      <p className="text-sm text-orange-300">Critical Issues</p>
                    </div>
                  </div>

                

                    {discoveredProfiles.length > 0 && (
  <div className="mb-6 bg-black/50 border border-purple-500/30 rounded-lg p-4">
    <h3 className="font-semibold mb-3 text-purple-300">
      Discovered Profiles
    </h3>

    <div className="space-y-2">
      {discoveredProfiles.map((profile, idx) => (
        <a
          key={idx}
          href={profile.profile_url}
          target="_blank"
          rel="noopener noreferrer"
          className="flex items-center justify-between p-3 rounded-lg bg-black/40 hover:bg-black/60 transition border border-purple-500/10"
        >
          <div>
            <p className="text-sm font-medium text-purple-300 capitalize flex items-center gap-2">
              {platformIcons[profile.platform_key] &&
                React.createElement(
                  platformIcons[profile.platform_key],
                  { className: "w-4 h-4" }
                )}
              {profile.platform}
            </p>
            <p className="text-sm text-gray-300">
              @{profile.username}
            </p>
          </div>

          {/* ✅ Verified badge (canonical only) */}
          <span
  className={`text-xs px-3 py-1 rounded-full ${
    profile.verification === "api_verified"
      ? "bg-green-500/20 text-green-300"
      : "bg-yellow-500/20 text-yellow-300"
  }`}
>
  {profile.verification === "api_verified" ? "verified" : "weak verified"}
</span>

        </a>
      ))}
    </div>
  </div>
)}



                  {/* Detailed Findings */}
                  <div className="bg-black/60 border border-purple-500/20 rounded-lg p-4">
                    <h3 className="font-semibold mb-3 flex items-center gap-2">
                      <FileText className="w-4 h-4 text-purple-400" />
                      Discovered Intelligence
                    </h3>
                    <div className="space-y-2">
                    {displayFindings.map((finding, idx) => (


                        <div key={idx} className="flex items-center justify-between p-3 bg-black/40 rounded-lg hover:bg-black/60 transition-colors">
                          <div className="flex-1">
                            <div className="flex items-center gap-3">
                              <span className="text-sm font-medium text-purple-300">{finding.type}</span>
                              <span className="text-sm">{finding.value}</span>
                            </div>
                            <p className="text-xs text-gray-400 mt-1">Found on: {finding.platforms}</p>
                          </div>
                          <span className={`px-3 py-1 rounded-full text-xs font-medium ${
                            finding.risk === 'CRITICAL' ? 'bg-red-500/20 text-red-300' :
                            finding.risk === 'MEDIUM' ? 'bg-orange-500/20 text-orange-300' :
                            'bg-green-500/20 text-green-300'
                          }`}>
                            {finding.risk}
                          </span>
                        </div>
                      ))}
                    </div>
                  </div>

{/* AI Analysis Summary */}
{results?.ai_analysis && (
  <div className="bg-gradient-to-br from-purple-500/10 to-blue-500/10 border border-purple-500/30 rounded-lg p-4 mt-4">
    <h3 className="font-medium mb-3 flex items-center gap-2">
      <Zap className="w-4 h-4 text-purple-400" />
      AI Analysis Summary
    </h3>

    <p className="text-sm text-gray-300 leading-relaxed">
      {results.ai_analysis.summary || "AI analysis completed. See detailed findings below."}
    </p>

    {results.ai_analysis.risk_assessment && (
      <div className="mt-3 p-3 bg-black/40 rounded-lg">
        <div className="grid grid-cols-2 gap-3">
          <div>
            <p className="text-xs text-purple-300 mb-1">Risk Level</p>
            <p className="font-bold text-white">{results.ai_analysis.risk_assessment.level}</p>
          </div>
          <div>
            <p className="text-xs text-purple-300 mb-1">Risk Score</p>
            <p className="font-bold text-white">{results.ai_analysis.risk_assessment.score}/10</p>
          </div>
        </div>
        
        {results.ai_analysis.risk_assessment.factors && 
         results.ai_analysis.risk_assessment.factors.length > 0 && (
          <div className="mt-3">
            <p className="text-xs text-purple-300 mb-2">Key Risk Factors:</p>
            <ul className="space-y-1">
              {results.ai_analysis.risk_assessment.factors.slice(0, 3).map((factor, idx) => (
                <li key={idx} className="text-xs text-gray-400 flex items-start gap-2">
                  <span className="text-purple-400">•</span>
                  <span>{factor}</span>
                </li>
              ))}
            </ul>
          </div>
        )}
      </div>
    )}

    {/* Show info if no AI service configured */}
    {(!results.ai_service_used || results.ai_service_used === 'none') && (
      <div className="mt-3 p-3 bg-yellow-500/10 border border-yellow-500/30 rounded-lg">
        <p className="text-xs text-yellow-300 flex items-center gap-2">
          <AlertTriangle className="w-3 h-3" />
          💡 Add an AI API key (GROQ_API_KEY, GEMINI_API_KEY, or ANTHROPIC_API_KEY) to your .env file for enhanced semantic analysis with entity extraction, behavioral patterns, and intelligent correlations.
        </p>
      </div>
    )}

    {/* Show entities if available */}
    {results.ai_analysis.entities && 
     Object.keys(results.ai_analysis.entities).length > 0 && (
      <div className="mt-3 p-3 bg-black/40 rounded-lg">
        <p className="text-xs text-purple-300 mb-2">🎯 Extracted Entities:</p>
        <div className="flex flex-wrap gap-2">
          {Object.entries(results.ai_analysis.entities).map(([type, values]) => (
            Array.isArray(values) && values.length > 0 && (
              <span key={type} className="text-xs bg-purple-500/20 text-purple-300 px-2 py-1 rounded capitalize">
                {type}: {values.length}
              </span>
            )
          ))}
        </div>
      </div>
    )}

    {/* Show patterns if available */}
    {results.ai_analysis.patterns && 
     results.ai_analysis.patterns.length > 0 && (
      <div className="mt-3 p-3 bg-black/40 rounded-lg">
        <p className="text-xs text-purple-300 mb-2">📊 Behavioral Patterns:</p>
        <ul className="space-y-1">
          {results.ai_analysis.patterns.slice(0, 3).map((pattern, idx) => (
            <li key={idx} className="text-xs text-gray-400 flex items-start gap-2">
              <span className="text-blue-400">▸</span>
              <span>{pattern}</span>
            </li>
          ))}
        </ul>
      </div>
    )}

    {/* Show correlations if available */}
    {results.ai_analysis.correlations && 
     results.ai_analysis.correlations.length > 0 && (
      <div className="mt-3 p-3 bg-black/40 rounded-lg">
        <p className="text-xs text-purple-300 mb-2">🔗 Cross-Platform Correlations:</p>
        <ul className="space-y-1">
          {results.ai_analysis.correlations.slice(0, 3).map((correlation, idx) => (
            <li key={idx} className="text-xs text-gray-400 flex items-start gap-2">
              <span className="text-green-400">✓</span>
              <span>{correlation}</span>
            </li>
          ))}
        </ul>
      </div>
    )}
  </div>
)}
  

                </div>
              )}
            </div>
          </div>
        )}

        {/* Visual Intelligence */}
        {activeTab === 'visual' && (
          <div className="space-y-6">
            <div className="
  bg-black/50
  backdrop-blur-sm 
  border border-purple-500/20 
  rounded-xl p-6
">

              <h2 className="text-xl font-semibold mb-4 flex items-center gap-2">
                <Image className="w-5 h-5 text-purple-400" />
                Visual Intelligence & Geolocation Extraction
              </h2>
              
              {/* Upload Zone */}
              <div className="border-2 border-dashed border-purple-500/30 rounded-lg p-12 text-center hover:border-purple-500/60 transition-colors">
                <Upload className="w-12 h-12 mx-auto mb-4 text-purple-400" />
                <p className="text-lg mb-2">Drop image or video here</p>
                <p className="text-sm text-gray-400 mb-4">Supports JPG, PNG, MP4, MOV</p>
                <input
                  type="file"
                  accept="image/*,video/*"
                  onChange={handleFileUpload}
                  className="hidden"
                  id="file-upload"
                />
                <label htmlFor="file-upload" className="cursor-pointer">
                  <span className="inline-block px-6 py-2 bg-purple-600 hover:bg-purple-700 rounded-lg transition-colors">
                    Browse Files
                  </span>
                </label>
                {uploadedFile && (
                  <p className="mt-4 text-sm text-green-400">Selected: {uploadedFile.name}</p>
                )}
              </div>

              {uploadedFile && (
                <button
                  onClick={handleVisualAnalyze}
                  disabled={geoAnalyzing || backendStatus?.status !== 'online'}
                  className="mt-4 w-full px-6 py-3 bg-purple-600 hover:bg-purple-700 disabled:bg-gray-600 disabled:cursor-not-allowed rounded-lg font-medium transition-colors flex items-center justify-center gap-2"
                >
                  {geoAnalyzing ? (
                    <>
                      <Activity className="w-4 h-4 animate-spin" />
                      Analyzing...
                    </>
                  ) : (
                    <>
                      <Search className="w-4 h-4" />
                      Analyze for Geolocation
                    </>
                  )}
                </button>
              )}

              {/* Real-Time Logs */}
              <div className="mt-6 bg-black/70 border border-purple-500/20 rounded-lg p-4 font-mono">
                <div className="flex items-center justify-between mb-3">
                  <h3 className="text-xs font-bold uppercase tracking-widest text-purple-400">
                    Real-time Logs
                  </h3>
                  <Activity className={`w-4 h-4 text-purple-400 ${logs.length > 0 ? 'animate-pulse' : ''}`} />
                </div>
                <div className="space-y-2 max-h-40 overflow-y-auto">
                  {logs.map((log, i) => (
                    <div key={i} className="text-[11px] flex gap-3 animate-in fade-in slide-in-from-left-2">
                      <span className="text-purple-500/50">
                        [{log.timestamp}]
                      </span>
                      <span className={log.type === 'error' ? 'text-red-400' : log.type === 'success' ? 'text-green-400' : 'text-gray-300'}>
                        {log.message}
                      </span>
                    </div>
                  ))}
                  {logs.length === 0 && (
                    <p className="text-xs text-gray-500 italic">
                      Awaiting command...
                    </p>
                  )}
                </div>
              </div>

              {/* Geolocation Results */}
              {geoResults && (
                <div className="mt-6 space-y-4">
                  {geoResults.coordinates && (
                    <div className="bg-gradient-to-br from-green-500/10 to-green-600/10 border border-green-500/30 rounded-lg p-4">
                      <h3 className="font-medium mb-3 flex items-center gap-2">
                        <MapPin className="w-4 h-4 text-green-400" />
                        Coordinates Extracted
                      </h3>
                      <div className="grid md:grid-cols-2 gap-4">
                        <div>
                          <p className="text-sm text-gray-300 mb-2">Latitude:</p>
                          <p className="font-mono text-green-400">{geoResults.coordinates.latitude}°</p>
                        </div>
                        <div>
                          <p className="text-sm text-gray-300 mb-2">Longitude:</p>
                          <p className="font-mono text-green-400">{geoResults.coordinates.longitude}°</p>
                        </div>
                      </div>
                      <div className="mt-4">
                        <p className="text-sm text-gray-300 mb-2">Source: <span className="font-medium text-purple-400">{geoResults.coordinate_source}</span></p>
                        <p className="text-sm text-gray-300 mb-2">Confidence:</p>
                        <div className="flex items-center gap-2">
                          <div className="flex-1 bg-black/30 rounded-full h-2">
                            <div className="bg-green-400 h-2 rounded-full" style={{width: `${geoResults.confidence}%`}}></div>
                          </div>
                          <span className="text-sm font-medium">{geoResults.confidence}%</span>
                        </div>
                      </div>
                    </div>
                  )}

                  {geoResults.location_estimate && (
                    <div className="bg-black/60 border border-purple-500/20 rounded-lg p-4">
                      <h3 className="font-semibold mb-3">Location Estimate</h3>
                      <p className="text-lg text-purple-300 mb-4">{geoResults.location_estimate}</p>
                      
                      {geoResults.analysis && (
                        <div className="mt-4 p-3 bg-black/40 rounded">
                          <p className="text-sm text-gray-300">{geoResults.analysis}</p>
                        </div>
                      )}

                      {geoResults.clues && geoResults.clues.length > 0 && (
                        <div className="mt-4">
                          <p className="text-sm font-medium text-purple-300 mb-2">Key Clues:</p>
                          <ul className="space-y-1">
                            {geoResults.clues.map((clue, idx) => (
                              <li key={idx} className="text-xs text-gray-400 flex items-start gap-2">
                                <span className="text-purple-400">•</span>
                                <span>{clue}</span>
                              </li>
                            ))}
                          </ul>
                        </div>
                      )}

                      {geoResults.landmarks && geoResults.landmarks.length > 0 && (
                        <div className="mt-4">
                          <p className="text-sm font-medium text-purple-300 mb-2">Landmarks Identified:</p>
                          <div className="flex flex-wrap gap-2">
                            {geoResults.landmarks.map((landmark, idx) => (
                              <span key={idx} className="text-xs bg-purple-500/20 text-purple-300 px-2 py-1 rounded">
                                {landmark}
                              </span>
                            ))}
                          </div>
                        </div>
                      )}
                    </div>
                  )}

                  {geoResults.exif_data && geoResults.exif_data.has_exif && (
                    <div className="bg-black/60 border border-purple-500/20 rounded-lg p-4">
                      <h3 className="font-semibold mb-3">EXIF Metadata</h3>
                      <div className="grid md:grid-cols-2 gap-4 text-sm">
                        <div>
                          <p className="text-purple-300 mb-1">Camera:</p>
                          <p className="text-gray-300">{geoResults.exif_data.camera.make} {geoResults.exif_data.camera.model}</p>
                        </div>
                        <div>
                          <p className="text-purple-300 mb-1">Date Taken:</p>
                          <p className="text-gray-300">{geoResults.exif_data.datetime.original}</p>
                        </div>
                      </div>
                    </div>
                  )}
                </div>
              )}

              {/* Analysis Options */}
              <div className="mt-6 grid grid-cols-2 gap-4">
                <div className="bg-black/40 border border-purple-500/20 rounded-lg p-4">
                  <h3 className="font-medium mb-3">EXIF Data Extraction</h3>
                  <ul className="space-y-2 text-sm text-gray-300">
                    <li className="flex items-center gap-2">
                      <MapPin className="w-4 h-4 text-green-400" />
                      GPS Coordinates
                    </li>
                    <li className="flex items-center gap-2">
                      <Activity className="w-4 h-4 text-blue-400" />
                      Camera Model & Settings
                    </li>
                    <li className="flex items-center gap-2">
                      <FileText className="w-4 h-4 text-purple-400" />
                      Timestamp & Date
                    </li>
                  </ul>
                </div>
                <div className="bg-black/40 border border-purple-500/20 rounded-lg p-4">
                  <h3 className="font-medium mb-3">AI Visual Analysis</h3>
                  <ul className="space-y-2 text-sm text-gray-300">
                    <li className="flex items-center gap-2">
                      <Eye className="w-4 h-4 text-purple-400" />
                      Landmark Recognition
                    </li>
                    <li className="flex items-center gap-2">
                      <Globe className="w-4 h-4 text-blue-400" />
                      Environmental Clues
                    </li>
                    <li className="flex items-center gap-2">
                      <Search className="w-4 h-4 text-green-400" />
                      Text & Sign Detection
                    </li>
                  </ul>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Risk Assessment */}
        {activeTab === 'risk' && results && (
          <div className="space-y-6">
           <div className="
  bg-black/50
  backdrop-blur-sm 
  border border-purple-500/20 
  rounded-xl p-6
">

           <div className="flex items-center justify-between mb-4">
  <h2 className="text-xl font-semibold flex items-center gap-2">
    <Shield className="w-5 h-5 text-purple-400" />
    Exposure Classification & Risk Assessment
  </h2>

  {/* View Mode Toggle */}
  <div className="flex bg-black/40 border border-purple-500/30 rounded-lg overflow-hidden">
    <button
      onClick={() => setViewMode("user")}
      className={`px-4 py-1 text-sm transition ${
        viewMode === "user"
          ? "bg-purple-600 text-white"
          : "text-gray-300 hover:bg-black/30"
      }`}
    >
      User View
    </button>

    <button
      onClick={() => setViewMode("attacker")}
      className={`px-4 py-1 text-sm transition ${
        viewMode === "attacker"
          ? "bg-red-600 text-white"
          : "text-gray-300 hover:bg-black/30"
      }`}
    >
      Attacker View
    </button>
  </div>
</div>
{/* Attacker recon notice (ONLY when no CRITICAL exists) */}
{viewMode === "attacker" &&
  !results.findings.some(f => f.risk === "CRITICAL") && (
    <div className="mb-4 bg-yellow-500/10 border border-yellow-500/30 rounded-lg p-3">
      <p className="text-sm text-yellow-300">
        No immediate critical exploits detected. Target is suitable for
        reconnaissance, profiling, and future social engineering.
      </p>
    </div>
)}

<div className="bg-black/60 border border-purple-500/20 rounded-lg p-4 mt-4">
 <h3 className="text-sm font-semibold mb-1">
  Exposure Severity (Heuristic)
</h3>

<p className="text-xs text-gray-400 mb-3">
  Severity based on discovered signals. May include unverified platforms.
</p>

  <div className="w-full bg-gray-700 rounded-full h-3">
    <div
      className={`h-3 rounded-full transition-all ${
        riskScore.risk >= 7
          ? "bg-red-500"
          : riskScore.risk >= 4
          ? "bg-orange-500"
          : "bg-green-500"
      }`}
      style={{ width: `${riskScore.risk * 10}%` }}
    />
  </div>

  <p className="text-xs text-gray-400 mt-2">
    Risk Score: {riskScore.risk} / 10
  </p>
</div>

              {/* Risk Overview */}
              <div className="grid md:grid-cols-3 gap-4 mb-6">
                <div className="bg-gradient-to-br from-red-500/20 to-red-600/10 border border-red-500/30 rounded-lg p-6 text-center">
                  <AlertTriangle className="w-8 h-8 mx-auto mb-3 text-red-400" />
                 <p className="text-3xl font-bold mb-2">{results.risk_assessment.risk_breakdown.critical}</p>

                  <p className="text-sm text-red-300">Critical Exposures</p>
                </div>
                <div className="bg-gradient-to-br from-orange-500/20 to-orange-600/10 border border-orange-500/30 rounded-lg p-6 text-center">
                  <AlertTriangle className="w-8 h-8 mx-auto mb-3 text-orange-400" />
                  <p className="text-3xl font-bold mb-2">{results.risk_assessment.risk_breakdown.medium}</p>
                  <p className="text-sm text-orange-300">Medium Risk</p>
                </div>
                <div className="bg-gradient-to-br from-green-500/20 to-green-600/10 border border-green-500/30 rounded-lg p-6 text-center">
                  <Shield className="w-8 h-8 mx-auto mb-3 text-green-400" />
                  <p className="text-3xl font-bold mb-2">{results.risk_assessment.risk_breakdown.low}</p>
                  <p className="text-sm text-green-300">Low Risk</p>
                </div>
              </div>

              {/* Risk Factors */}
              <div className="bg-black/60 border border-purple-500/20 rounded-lg p-4 mb-6">
                <h3 className="font-semibold mb-3">Risk Factors</h3>
                <ul className="space-y-2">
                 {Array.isArray(riskScore.factors) &&
                  riskScore.factors.map((factor, idx) => (


                    <li key={idx} className="text-sm text-gray-300 flex items-start gap-2">
                      <AlertTriangle className="w-4 h-4 text-orange-400 mt-0.5 flex-shrink-0" />
                      <span>{factor}</span>
                    </li>
                  ))}
                </ul>
              </div>

              {/* Detailed Risk Breakdown */}
              <div className="space-y-3">
                {displayFindings.map((item, idx) => {

                  const riskScore = item.risk === 'CRITICAL' ? 9.5 : item.risk === 'MEDIUM' ? 6.0 : 3.0;
                  return (
                    <div key={idx} className="bg-black/40 border border-purple-500/20 rounded-lg p-4 hover:bg-black/60 transition-colors">
                      <div className="flex items-start justify-between mb-2">
                        <div className="flex-1">
                          <div className="flex items-center gap-3 mb-1">
                            <span className="text-xs font-medium text-purple-400 bg-purple-500/20 px-2 py-1 rounded">
                              {item.type}
                            </span>
                            <span className={`text-xs font-medium px-2 py-1 rounded ${
                              item.risk === 'CRITICAL' ? 'bg-red-500/20 text-red-300' :
                              item.risk === 'MEDIUM' ? 'bg-orange-500/20 text-orange-300' :
                              'bg-green-500/20 text-green-300'
                            }`}>
                              {item.risk}
                            </span>
                            <span className="text-sm font-bold text-white">{riskScore}/10</span>
                          </div>
                          <p className="text-sm mb-2">
  {viewMode === "user"
    ? item.value
    : attackerNarrative(item)}
</p>

                        <p className="text-xs text-gray-400">
  Found on: {item.platforms}
  {item.platforms?.toLowerCase().includes("twitter") && (
    <span className="ml-2 text-yellow-400 text-[10px]">(unverified)</span>
  )}
</p>

                        </div>
                      </div>
                      <div className="mt-3">
                        <div className="bg-black/30 rounded-full h-2">
                          <div 
                            className={`h-2 rounded-full ${
                              item.risk === 'CRITICAL' ? 'bg-red-500' :
                              item.risk === 'MEDIUM' ? 'bg-orange-500' :
                              'bg-green-500'
                            }`}
                            style={{width: `${riskScore * 10}%`}}
                          ></div>
                        </div>
                      </div>
                    </div>
                  );
                })}
              </div>

              {/* AI Recommendations */}
              {results.ai_analysis && results.ai_analysis.risk_assessment && (
                <div className="mt-6 bg-gradient-to-br from-purple-500/10 to-blue-500/10 border border-purple-500/30 rounded-lg p-4">
                  <h3 className="font-medium mb-3 flex items-center gap-2">
                    <Zap className="w-4 h-4 text-purple-400" />
                    AI Risk Assessment
                  </h3>
                  <div className="mb-4">
                    <p className="text-sm text-purple-300">Overall Risk Level: <span className="font-bold text-lg">{results.ai_analysis.risk_assessment.level}</span></p>
                    <p className="text-sm text-purple-300">AI Risk Score: <span className="font-bold">{results.ai_analysis.risk_assessment.score}/10</span></p>
                  </div>
                  {results.ai_analysis.risk_assessment.factors && results.ai_analysis.risk_assessment.factors.length > 0 && (
                    <ul className="space-y-2 text-sm text-gray-300">
                      {results.ai_analysis.risk_assessment.factors.map((factor, idx) => (
                        <li key={idx} className="flex items-start gap-2">
                          <span className="text-purple-400 mt-1">•</span>
                          <span>{factor}</span>
                        </li>
                      ))}
                    </ul>
                  )}
                </div>
              )}
            </div>
          </div>
        )}

        {/* No results in risk tab */}
        {activeTab === 'risk' && !results && (
          <div className="bg-black/50 backdrop-blur-sm border border-purple-500/20 rounded-xl p-12 text-center">
            <Shield className="w-16 h-16 mx-auto mb-4 text-purple-400" />
            <h3 className="text-xl font-semibold mb-2">No Analysis Data</h3>
            <p className="text-gray-400 mb-6">Run an analysis in the Multi-Modal Fusion tab first to see risk assessment.</p>
            <button
              onClick={() => setActiveTab('multi-modal')}
              className="px-6 py-3 bg-purple-600 hover:bg-purple-700 rounded-lg font-medium transition-colors"
            >
              Go to Analysis Tab
            </button>
          </div>
        )}
      </div>

        {/* Chat Assistant - Add this right before the Footer */}
        <ChatAssistant 
            backendStatus={backendStatus}
            currentTab={activeTab}
            analysisResults={results}
            backgroundTheme={backgroundTheme}
            setBackgroundTheme={setBackgroundTheme}
/>


      {/* Footer */}
      <footer className="relative mt-12 border-t border-purple-500/20 bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 backdrop-blur-sm py-6">
        <div className="max-w-7xl mx-auto px-6 text-center text-sm text-purple-300">
          <p>Built for CHAKRAVYUH 1.0 Hackathon | GITA Autonomous College, Bhubaneswar</p>
          <p className="mt-1">Problem Statement ID: GITACVPS001</p>
          {backendStatus && (
            <div className="mt-3 flex items-center justify-center gap-4 text-xs">
              <span>Backend: {backendStatus.status === 'online' ? '✓ Online' : '✗ Offline'}</span>
              {backendStatus.services && (
                <>
                  <span>|</span>
                  <span>GitHub API: {backendStatus.services.github ? '✓' : '✗'}</span>
                  <span>AI Service: {backendStatus.ai_service || 'none'}</span>
                  <span>Image Analysis: {backendStatus.services.image_geolocation ? '✓' : '✗'}</span>
                </>
              )}
            </div>
          )}
        </div>
      </footer>
    </div>
  );
}
