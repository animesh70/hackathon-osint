
import React, { useState } from 'react';
import { Search, Upload, MapPin, Shield, AlertTriangle, Globe, Image, FileText, Activity, Eye, Target, Zap } from 'lucide-react';
import jsPDF from 'jspdf';

import {
  SiGithub,
  SiX,
  SiLinkedin,
  SiReddit,
  SiInstagram,
  SiFacebook,
  SiTiktok,
  SiYoutube
} from 'react-icons/si';
// ===== Fake Backend API =====
const fakeAnalyzeRiskAPI = (input) => {
  return new Promise((resolve) => {
    setTimeout(() => {
      resolve({
        summary: {
          critical: 2,
          medium: 2,
          low: 1
        },
        overallRisk: 7.5,
        findings: [
          {
            category: 'Credentials',
            item: 'Password found in data breach (2023)',
            risk: 'CRITICAL',
            score: 9.5,
            action: 'Change password immediately'
          },
          {
            category: 'Personal Identifiers',
            item: 'Full name + DOB on public profile',
            risk: 'CRITICAL',
            score: 8.5,
            action: 'Remove or restrict access'
          },
          {
            category: 'Contact Details',
            item: 'Email exposed on 3 platforms',
            risk: 'MEDIUM',
            score: 6.0,
            action: 'Monitor for spam/phishing'
          },
          {
            category: 'Behavioral Patterns',
            item: 'Consistent location patterns',
            risk: 'MEDIUM',
            score: 5.5,
            action: 'Disable location sharing'
          },
          {
            category: 'Organizational Links',
            item: 'Company affiliation visible',
            risk: 'LOW',
            score: 3.0,
            action: 'No immediate action needed'
          }
        ]
      });
    }, 2000); // simulate network + AI delay
  });
};

export default function OSINTDashboard() {
 const [activeTab, setActiveTab] = useState('risk');
  const [targetInput, setTargetInput] = useState('');
  const [analyzing, setAnalyzing] = useState(false);
  const [results, setResults] = useState(null);
  const [logs, setLogs] = useState([]);
const [riskData, setRiskData] = useState(null);

  const challenges = [
    { id: 'multi-modal', name: 'Multi-Modal Fusion', icon: Globe },
    { id: 'visual', name: 'Visual Intelligence', icon: Image },
    { id: 'risk', name: 'Risk Assessment', icon: Shield }
  ];

  const handleAnalyze = async () => {
    setAnalyzing(true);
    setResults(null);
    setLogs([]);
    
    const steps = [
      'Initializing OSINT core...',
      'Resolving target identifiers...',
      'Querying open-source platforms...',
      'Scraping public repositories...',
      'Extracting metadata...',
      'Running correlation analysis...',
      'Calculating exposure risk...',
      'Finalizing intelligence report...'
    ];
    
    steps.forEach((step, index) => {
      setTimeout(() => {
        setLogs(prev => [...prev, step]);
      }, index * 700);
    });
    
    setTimeout(() => {
      setResults({
        risk: 7.5,
        exposures: 12,
        platforms: 5,
        critical: 2
      });
      setAnalyzing(false);
    }, steps.length * 700 + 500);
  };

  const handleVisualAnalyze = () => {
    setLogs([]);
    const steps = [
      'Loading image file...',
      'Extracting EXIF metadata...',
      'Scanning for GPS coordinates...',
      'Analyzing visual features...',
      'Detecting landmarks and text...',
      'Running AI geolocation inference...',
      'Cross-referencing environmental clues...',
      'Generating location estimate...'
    ];
    
    steps.forEach((step, index) => {
      setTimeout(() => {
        setLogs(prev => [...prev, step]);
      }, index * 600);
    });
  };
const downloadReport = () => {
  if (!riskData) return;

  const doc = new jsPDF();
  let y = 20;

  doc.setFontSize(18);
  doc.text('OSINT Intelligence Report', 20, y);
  y += 10;

  doc.setFontSize(12);
  doc.text(`Target: ${targetInput || 'N/A'}`, 20, y);
  y += 8;

  doc.text(`Overall Risk Score: ${riskData.overallRisk}/10`, 20, y);
  y += 12;

  doc.setFontSize(14);
  doc.text('Risk Findings:', 20, y);
  y += 8;

  riskData.findings.forEach((item, index) => {
    doc.setFontSize(11);
    doc.text(
      `${index + 1}. [${item.risk}] ${item.category} - ${item.item}`,
      20,
      y
    );
    y += 7;

    doc.text(`   Recommendation: ${item.action}`, 20, y);
    y += 8;

    if (y > 270) {
      doc.addPage();
      y = 20;
    }
  });

  doc.save('OSINT_Intelligence_Report.pdf');
};

  return (
    <div className="min-h-screen bg-[#0a0a0a] text-white">
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
                <h1 className="text-2xl font-bold">CHAKRAVYUH 1.0</h1>
                <p className="text-sm text-purple-300">OSINT Intelligence Platform</p>
              </div>
            </div>
            <div className="flex items-center gap-4">
              <span className="text-sm text-purple-300">GITA Autonomous College</span>
              <div className="w-2 h-2 rounded-full bg-green-400 animate-pulse"></div>
              <span className="text-sm">System Active</span>
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
            <div className="bg-black/50 backdrop-blur-sm border border-purple-500/20 rounded-xl p-6">
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
                      className="flex-1 bg-black/60 border border-purple-500/30 rounded-lg px-4 py-3 focus:outline-none focus:border-purple-500 placeholder-gray-500"
                    />
                    <button
                      onClick={handleAnalyze}
                      disabled={analyzing || !targetInput}
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
                    { name: 'GitHub', icon: SiGithub },
                    { name: 'Twitter/X', icon: SiX },
                    { name: 'LinkedIn', icon: SiLinkedin },
                    { name: 'Reddit', icon: SiReddit },
                    { name: 'Instagram', icon: SiInstagram },
                    { name: 'Facebook', icon: SiFacebook },
                    { name: 'TikTok', icon: SiTiktok },
                    { name: 'YouTube', icon: SiYoutube }
                  ].map((platform) => {
                    const Icon = platform.icon;
                    return (
                      <label key={platform.name} className="flex items-center gap-2 bg-black/40 p-3 rounded-lg cursor-pointer hover:bg-black/60 transition-colors group">
                        <input type="checkbox" defaultChecked className="rounded border-purple-500" />
                        <Icon className="w-4 h-4 text-purple-400 group-hover:text-purple-300 transition-colors" />
                        <span className="text-sm">{platform.name}</span>
                      </label>
                    );
                  })}
                </div>
              </div>

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
                        [{new Date().toLocaleTimeString()}]
                      </span>
                      <span className="text-gray-300">{log}</span>
                    </div>
                  ))}
                  {logs.length === 0 && (
                    <p className="text-xs text-gray-500 italic">
                      Awaiting command…
                    </p>
                  )}
                </div>
              </div>

              {/* Results */}
              {results && (
                <div className="mt-6 space-y-4">
                  <div className="grid grid-cols-4 gap-4">
                    <div className="bg-gradient-to-br from-red-500/20 to-red-600/10 border border-red-500/30 rounded-lg p-4">
                      <div className="flex items-center justify-between mb-2">
                        <AlertTriangle className="w-5 h-5 text-red-400" />
                        <span className="text-2xl font-bold">{results.risk}</span>
                      </div>
                      <p className="text-sm text-red-300">Risk Score</p>
                    </div>
                    <div className="bg-gradient-to-br from-blue-500/20 to-blue-600/10 border border-blue-500/30 rounded-lg p-4">
                      <div className="flex items-center justify-between mb-2">
                        <Eye className="w-5 h-5 text-blue-400" />
                        <span className="text-2xl font-bold">{results.exposures}</span>
                      </div>
                      <p className="text-sm text-blue-300">Exposures Found</p>
                    </div>
                    <div className="bg-gradient-to-br from-purple-500/20 to-purple-600/10 border border-purple-500/30 rounded-lg p-4">
                      <div className="flex items-center justify-between mb-2">
                        <Globe className="w-5 h-5 text-purple-400" />
                        <span className="text-2xl font-bold">{results.platforms}</span>
                      </div>
                      <p className="text-sm text-purple-300">Platforms</p>
                    </div>
                    <div className="bg-gradient-to-br from-orange-500/20 to-orange-600/10 border border-orange-500/30 rounded-lg p-4">
                      <div className="flex items-center justify-between mb-2">
                        <Zap className="w-5 h-5 text-orange-400" />
                        <span className="text-2xl font-bold">{results.critical}</span>
                      </div>
                      <p className="text-sm text-orange-300">Critical Issues</p>
                    </div>
                  </div>

                  {/* Detailed Findings */}
                  <div className="bg-black/60 border border-purple-500/20 rounded-lg p-4">
                    <h3 className="font-semibold mb-3 flex items-center gap-2">
                      <FileText className="w-4 h-4 text-purple-400" />
                      Discovered Intelligence
                    </h3>
                    <div className="space-y-2">
                      {[
                        { type: 'Email', value: 'john.doe@example.com', risk: 'MEDIUM', platforms: 'GitHub, LinkedIn' },
                        { type: 'Username', value: 'johndoe123', risk: 'LOW', platforms: 'Twitter, Reddit, GitHub' },
                        { type: 'Credential', value: 'Found in breach database', risk: 'CRITICAL', platforms: 'HaveIBeenPwned' },
                        { type: 'Location', value: 'Bhubaneswar, India', risk: 'MEDIUM', platforms: 'Instagram, Twitter' }
                      ].map((finding, idx) => (
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
                </div>
              )}
            </div>
          </div>
        )}

        {/* Visual Intelligence */}
        {activeTab === 'visual' && (
          <div className="space-y-6">
            <div className="bg-black/50 backdrop-blur-sm border border-purple-500/20 rounded-xl p-6">
              <h2 className="text-xl font-semibold mb-4 flex items-center gap-2">
                <Image className="w-5 h-5 text-purple-400" />
                Visual Intelligence & Geolocation Extraction
              </h2>
              
              {/* Upload Zone */}
              <div className="border-2 border-dashed border-purple-500/30 rounded-lg p-12 text-center hover:border-purple-500/60 transition-colors cursor-pointer bg-black/30">
                <Upload className="w-12 h-12 mx-auto mb-4 text-purple-400" />
                <p className="text-lg mb-2">Drop image or video here</p>
                <p className="text-sm text-gray-400">Supports JPG, PNG, MP4, MOV</p>
                <button 
                  onClick={handleVisualAnalyze}
                  className="mt-4 px-6 py-2 bg-purple-600 hover:bg-purple-700 rounded-lg transition-colors"
                >
                  Browse Files
                </button>
              </div>

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
                        [{new Date().toLocaleTimeString()}]
                      </span>
                      <span className="text-gray-300">{log}</span>
                    </div>
                  ))}
                  {logs.length === 0 && (
                    <p className="text-xs text-gray-500 italic">
                      Awaiting command…
                    </p>
                  )}
                </div>
              </div>

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

              {/* Sample Result */}
              <div className="mt-6 bg-gradient-to-br from-purple-500/10 to-blue-500/10 border border-purple-500/30 rounded-lg p-4">
                <h3 className="font-medium mb-3 flex items-center gap-2">
                  <MapPin className="w-4 h-4 text-green-400" />
                  Geolocation Estimate
                </h3>
                <div className="grid md:grid-cols-2 gap-4">
                  <div>
                    <p className="text-sm text-gray-300 mb-2">Coordinates:</p>
                    <p className="font-mono text-green-400">20.2961° N, 85.8245° E</p>
                  </div>
                  <div>
                    <p className="text-sm text-gray-300 mb-2">Confidence:</p>
                    <div className="flex items-center gap-2">
                      <div className="flex-1 bg-black/30 rounded-full h-2">
                        <div className="bg-green-400 h-2 rounded-full" style={{width: '85%'}}></div>
                      </div>
                      <span className="text-sm font-medium">85%</span>
                    </div>
                  </div>
                </div>
                <p className="text-sm text-gray-300 mt-4">
                  <span className="font-medium">Analysis:</span> Image shows distinctive architecture consistent with Bhubaneswar region. 
                  Shadow angle suggests afternoon timing. Vegetation indicates tropical climate.
                </p>
              </div>
            </div>
          </div>
        )}

        {/* Risk Assessment */}
        {activeTab === 'risk' && (
          <div className="space-y-6">
            <div className="bg-black/50 backdrop-blur-sm border border-purple-500/20 rounded-xl p-6">
              <h2 className="text-xl font-semibold mb-4 flex items-center gap-2">
  <Shield className="w-5 h-5 text-purple-400" />

  <span>Exposure Classification & Risk Assessment</span>

  <span className="ml-2 text-xs bg-purple-500/20 text-purple-300 px-2 py-1 rounded">
    AI Powered
  </span>
</h2>
<button
  onClick={async () => {
    setRiskData(null);
    const response = await fakeAnalyzeRiskAPI(targetInput);
    setRiskData(response);
  }}
  className="mb-6 px-4 py-2 bg-purple-600 hover:bg-purple-700 rounded-lg text-sm"
>
  Run AI Risk Analysis
</button>

<button
  onClick={downloadReport}
  disabled={!riskData}
  className="mb-6 ml-3 px-4 py-2 bg-green-600 hover:bg-green-700 disabled:bg-gray-600 rounded-lg text-sm"
>
  Download Intelligence Report
</button>


              {/* Risk Overview */}
              {/* Risk Score Explanation */}
<div className="mb-6 bg-black/40 border border-purple-500/20 rounded-lg p-4">
  <h4 className="text-sm font-semibold text-purple-300 mb-2">
    How Risk Score is Calculated
  </h4>
  <p className="text-xs text-gray-300 leading-relaxed">
    Each exposed data point is classified by severity using AI reasoning.
    Critical exposures carry higher weight due to exploitability and impact.
  </p>

  <ul className="mt-2 text-xs text-gray-400 space-y-1">
    <li>• CRITICAL exposure = 4 points</li>
    <li>• MEDIUM exposure = 2 points</li>
    <li>• LOW exposure = 1 point</li>
    <li>• Final score normalized to a 0–10 scale</li>
  </ul>
</div>

              <div className="grid md:grid-cols-3 gap-4 mb-6">
                <div className="bg-gradient-to-br from-red-500/20 to-red-600/10 border border-red-500/30 rounded-lg p-6 text-center">
                  <AlertTriangle className="w-8 h-8 mx-auto mb-3 text-red-400" />
                  <p className="text-3xl font-bold mb-2">4</p>
                  <p className="text-sm text-red-300">Critical Exposures</p>
                </div>
                <div className="bg-gradient-to-br from-orange-500/20 to-orange-600/10 border border-orange-500/30 rounded-lg p-6 text-center">
                  <AlertTriangle className="w-8 h-8 mx-auto mb-3 text-orange-400" />
                  <p className="text-3xl font-bold mb-2">2</p>
                  <p className="text-sm text-orange-300">Medium Risk</p>
                </div>
                <div className="bg-gradient-to-br from-green-500/20 to-green-600/10 border border-green-500/30 rounded-lg p-6 text-center">
                  <Shield className="w-8 h-8 mx-auto mb-3 text-green-400" />
                  <p className="text-3xl font-bold mb-2">1</p>
                  <p className="text-sm text-green-300">Low Risk</p>
                </div>
              </div>

              {/* Detailed Risk Breakdown */}
              <div className="space-y-3">
                 {riskData?.findings.map((item, idx) => (
    <div
      key={idx}
      className="bg-black/40 border border-purple-500/20 rounded-lg p-4 hover:bg-black/60 transition-colors"
    >
      <div className="flex items-start justify-between mb-2">
        <div className="flex-1">
          <div className="flex items-center gap-3 mb-1">
            <span className="text-xs font-medium text-purple-400 bg-purple-500/20 px-2 py-1 rounded">
              {item.category}
            </span>

            <span
              className={`text-xs font-medium px-2 py-1 rounded ${
                item.risk === 'CRITICAL'
                  ? 'bg-red-500/20 text-red-300'
                  : item.risk === 'MEDIUM'
                  ? 'bg-orange-500/20 text-orange-300'
                  : 'bg-green-500/20 text-green-300'
              }`}
            >
              {item.risk}
            </span>

            <span className="text-sm font-bold text-white">
              {item.score}/10
            </span>
          </div>

          <p className="text-sm mb-2">{item.item}</p>

          <p className="text-xs text-purple-300">
            <span className="font-medium">Recommended Action:</span>{' '}
            {item.action}
          </p>
        </div>
      </div>

      <div className="mt-3">
        <div className="bg-black/30 rounded-full h-2">
          <div
            className={`h-2 rounded-full ${
              item.risk === 'CRITICAL'
                ? 'bg-red-500'
                : item.risk === 'MEDIUM'
                ? 'bg-orange-500'
                : 'bg-green-500'
            }`}
            style={{ width: `${item.score * 10}%` }}
          ></div>
        </div>
      </div>
    </div>
  ))}

              </div>

              {/* AI Recommendations */}
              <div className="mt-6 bg-gradient-to-br from-purple-500/10 to-blue-500/10 border border-purple-500/30 rounded-lg p-4">
                <h3 className="font-medium mb-3 flex items-center gap-2">
                  <Zap className="w-4 h-4 text-purple-400" />
                  AI-Generated Recommendations
                </h3>
                <ul className="space-y-2 text-sm text-gray-300">
                  <li className="flex items-start gap-2">
                    <span className="text-purple-400 mt-1">•</span>
                    <span>Enable 2FA on all accounts where credentials were exposed</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <span className="text-purple-400 mt-1">•</span>
                    <span>Review privacy settings on social media platforms</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <span className="text-purple-400 mt-1">•</span>
                    <span>Consider using unique usernames across platforms to reduce correlation</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <span className="text-purple-400 mt-1">•</span>
                    <span>Monitor HaveIBeenPwned for future breaches involving your email</span>
                  </li>
                </ul>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Footer */}
      <footer className="relative mt-12 border-t border-purple-500/20 bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 backdrop-blur-sm py-6">
        <div className="max-w-7xl mx-auto px-6 text-center text-sm text-purple-300">
          <p>Built for CHAKRAVYUH 1.0 Hackathon | GITA Autonomous College, Bhubaneswar</p>
          <p className="mt-1">Problem Statement ID: GITACVPS001</p>
        </div>
      </footer>
    </div>
  );
}