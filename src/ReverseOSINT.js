import React, { useState } from 'react';
import { 
  Eye, Shield, AlertTriangle, Activity, Target, Search, 
  Database, Globe, Skull, Radio, ExternalLink, CheckCircle,
  XCircle, Info, Zap, Lock, Unlock
} from 'lucide-react';

export default function ReverseOSINT({ backendStatus, BACKEND_URL }) {
  const [targetInput, setTargetInput] = useState('');
  const [analyzing, setAnalyzing] = useState(false);
  const [results, setResults] = useState(null);
  const [selectedPlatforms, setSelectedPlatforms] = useState({
    github: true,
    gitlab: true,
    twitter: true,
    linkedin: true,
    instagram: true,
    reddit: true,
    facebook: true,
    youtube: true
  });

  const handleAnalyze = async () => {
    if (!targetInput.trim()) {
      alert('Please enter a target identifier');
      return;
    }

    setAnalyzing(true);
    setResults(null);

    try {
      const enabledPlatforms = Object.keys(selectedPlatforms).filter(
        p => selectedPlatforms[p]
      );

      const response = await fetch(`${BACKEND_URL}/api/reverse-osint/analyze`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          target: targetInput,
          platforms: enabledPlatforms
        })
      });

      if (!response.ok) throw new Error(`HTTP ${response.status}`);

      const data = await response.json();
      setResults(data);
    } catch (error) {
      alert(`Analysis failed: ${error.message}`);
      console.error(error);
    } finally {
      setAnalyzing(false);
    }
  };

  const togglePlatform = (platform) => {
    setSelectedPlatforms(prev => ({
      ...prev,
      [platform]: !prev[platform]
    }));
  };

  const getRiskColor = (risk) => {
    switch (risk) {
      case 'CRITICAL': return 'text-red-400 bg-red-500/20 border-red-500/30';
      case 'HIGH': return 'text-orange-400 bg-orange-500/20 border-orange-500/30';
      case 'MEDIUM': return 'text-yellow-400 bg-yellow-500/20 border-yellow-500/30';
      case 'LOW': return 'text-green-400 bg-green-500/20 border-green-500/30';
      default: return 'text-gray-400 bg-gray-500/20 border-gray-500/30';
    }
  };

  const getRiskIcon = (risk) => {
    switch (risk) {
      case 'CRITICAL': return <Skull className="w-5 h-5" />;
      case 'HIGH': return <AlertTriangle className="w-5 h-5" />;
      case 'MEDIUM': return <Info className="w-5 h-5" />;
      case 'LOW': return <Shield className="w-5 h-5" />;
      default: return <Eye className="w-5 h-5" />;
    }
  };

  return (
    <div className="space-y-6">
      {/* Header Card */}
      <div className="bg-black/50 backdrop-blur-sm border border-purple-500/20 rounded-xl p-6">
        <div className="flex items-center gap-3 mb-4">
          <Eye className="w-6 h-6 text-purple-400" />
          <div>
            <h2 className="text-xl font-semibold">Reverse OSINT</h2>
            <p className="text-sm text-gray-400">Detect who's tracking your online presence</p>
          </div>
        </div>

        {/* Input Section */}
        <div className="space-y-4">
          <div>
            <label className="block text-sm text-purple-300 mb-2">Target Identifier</label>
            <div className="flex gap-3">
              <input
                type="text"
                value={targetInput}
                onChange={(e) => setTargetInput(e.target.value)}
                placeholder="Enter username or email..."
                className="flex-1 bg-black/60 text-white border border-purple-500/30 rounded-lg px-4 py-3 focus:outline-none focus:border-purple-500 placeholder-gray-500"
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
                    Scanning...
                  </>
                ) : (
                  <>
                    <Search className="w-4 h-4" />
                    Scan for Trackers
                  </>
                )}
              </button>
            </div>
          </div>

          {/* Platform Selection */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
            {Object.keys(selectedPlatforms).map((platform) => (
              <label
                key={platform}
                className="flex items-center gap-2 bg-black/40 hover:bg-black/60 p-3 rounded-lg cursor-pointer transition-colors"
              >
                <input
                  type="checkbox"
                  checked={selectedPlatforms[platform]}
                  onChange={() => togglePlatform(platform)}
                  className="rounded border-purple-500"
                />
                <span className="text-sm capitalize">{platform}</span>
              </label>
            ))}
          </div>
        </div>

        {/* Info Banner */}
        <div className="mt-4 bg-blue-500/10 border border-blue-500/30 rounded-lg p-3">
          <p className="text-xs text-blue-300 flex items-center gap-2">
            <Info className="w-4 h-4" />
            This tool detects trackers, scrapers, data brokers, and surveillance indicators targeting your online profiles.
          </p>
        </div>
      </div>

      {/* Results Section */}
      {analyzing && (
        <div className="bg-black/50 border border-purple-500/20 rounded-xl p-12 text-center">
          <Activity className="w-16 h-16 mx-auto mb-4 text-purple-400 animate-spin" />
          <h3 className="text-xl font-semibold mb-2">Scanning for Trackers...</h3>
          <p className="text-gray-400">Analyzing tracking patterns across platforms</p>
        </div>
      )}

      {!analyzing && results && (
        <div className="space-y-6">
          {/* Risk Overview */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div className={`rounded-xl p-5 border ${getRiskColor(results.risk_level)}`}>
              <div className="flex items-center justify-between mb-2">
                {getRiskIcon(results.risk_level)}
                <span className="text-2xl font-bold">{results.summary?.risk_score || 0}</span>
              </div>
              <p className="text-sm">Risk Score</p>
              <p className="text-xs mt-1 opacity-80">{results.risk_level} THREAT</p>
            </div>

            <div className="bg-gradient-to-br from-red-500/20 to-red-600/10 border border-red-500/30 rounded-xl p-5">
              <div className="flex items-center justify-between mb-2">
                <Radio className="w-5 h-5 text-red-400" />
                <span className="text-2xl font-bold">{results.trackers?.length || 0}</span>
              </div>
              <p className="text-sm text-red-300">Active Trackers</p>
            </div>

            <div className="bg-gradient-to-br from-orange-500/20 to-orange-600/10 border border-orange-500/30 rounded-xl p-5">
              <div className="flex items-center justify-between mb-2">
                <Database className="w-5 h-5 text-orange-400" />
                <span className="text-2xl font-bold">{results.data_brokers?.length || 0}</span>
              </div>
              <p className="text-sm text-orange-300">Data Brokers</p>
            </div>

            <div className="bg-gradient-to-br from-purple-500/20 to-purple-600/10 border border-purple-500/30 rounded-xl p-5">
              <div className="flex items-center justify-between mb-2">
                <Eye className="w-5 h-5 text-purple-400" />
                <span className="text-2xl font-bold">{results.surveillance_indicators?.length || 0}</span>
              </div>
              <p className="text-sm text-purple-300">Surveillance Signs</p>
            </div>
          </div>

          {/* Tracking Status Alert */}
          {results.tracking_detected && (
            <div className="bg-red-500/10 border border-red-500/30 rounded-xl p-4">
              <div className="flex items-center gap-3">
                <AlertTriangle className="w-6 h-6 text-red-400" />
                <div>
                  <h3 className="font-semibold text-red-300">Active Tracking Detected</h3>
                  <p className="text-sm text-red-200/80 mt-1">
                    Multiple entities are monitoring your online presence. Review findings below.
                  </p>
                </div>
              </div>
            </div>
          )}

          {/* Web Trackers */}
          {results.trackers && results.trackers.length > 0 && (
            <div className="bg-black/50 border border-purple-500/20 rounded-xl p-6">
              <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
                <Radio className="w-5 h-5 text-red-400" />
                Web Trackers Detected ({results.trackers.length})
              </h3>
              <div className="space-y-3">
                {results.trackers.map((tracker, idx) => (
                  <div key={idx} className="bg-black/40 border border-red-500/20 rounded-lg p-4 hover:bg-black/60 transition">
                    <div className="flex items-start justify-between mb-2">
                      <div className="flex-1">
                        <div className="flex items-center gap-3 mb-2">
                          <span className="font-medium text-red-300">{tracker.name}</span>
                          <span className={`text-xs px-2 py-1 rounded-full ${getRiskColor(tracker.risk)}`}>
                            {tracker.risk}
                          </span>
                        </div>
                        <p className="text-sm text-gray-300 mb-1">{tracker.description}</p>
                        <p className="text-xs text-gray-500">Platform: {tracker.platform}</p>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Scrapers */}
          {results.scrapers && results.scrapers.length > 0 && (
            <div className="bg-black/50 border border-purple-500/20 rounded-xl p-6">
              <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
                <Target className="w-5 h-5 text-orange-400" />
                Potential Scrapers ({results.scrapers.length})
              </h3>
              <div className="space-y-3">
                {results.scrapers.map((scraper, idx) => (
                  <div key={idx} className="bg-black/40 border border-orange-500/20 rounded-lg p-4">
                    <div className="flex items-start justify-between mb-2">
                      <div className="flex-1">
                        <div className="flex items-center gap-3 mb-2">
                          <span className="font-medium text-orange-300">{scraper.name}</span>
                          <span className={`text-xs px-2 py-1 rounded-full ${getRiskColor(scraper.risk)}`}>
                            {scraper.risk}
                          </span>
                          <span className="text-xs text-gray-500">Likelihood: {scraper.likelihood}</span>
                        </div>
                        <p className="text-sm text-gray-300">{scraper.description}</p>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Data Brokers */}
          {results.data_brokers && results.data_brokers.length > 0 && (
            <div className="bg-black/50 border border-purple-500/20 rounded-xl p-6">
              <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
                <Database className="w-5 h-5 text-yellow-400" />
                Data Broker Exposure ({results.data_brokers.length})
              </h3>
              <div className="space-y-3">
                {results.data_brokers.map((broker, idx) => (
                  <div key={idx} className="bg-black/40 border border-yellow-500/20 rounded-lg p-4">
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <div className="flex items-center gap-3 mb-2">
                          <span className="font-medium text-yellow-300">{broker.name}</span>
                          <span className={`text-xs px-2 py-1 rounded-full ${getRiskColor(broker.risk)}`}>
                            {broker.risk}
                          </span>
                        </div>
                        <p className="text-sm text-gray-300 mb-2">{broker.description}</p>
                        <div className="flex gap-3">
                          <a
                            href={broker.url}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="text-xs text-blue-400 hover:text-blue-300 flex items-center gap-1"
                          >
                            <ExternalLink className="w-3 h-3" />
                            Visit Site
                          </a>
                          <a
                            href={broker.removal_link}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="text-xs text-green-400 hover:text-green-300 flex items-center gap-1"
                          >
                            <Lock className="w-3 h-3" />
                            Request Removal
                          </a>
                        </div>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Surveillance Indicators */}
          {results.surveillance_indicators && results.surveillance_indicators.length > 0 && (
            <div className="bg-black/50 border border-purple-500/20 rounded-xl p-6">
              <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
                <Eye className="w-5 h-5 text-purple-400" />
                Surveillance Indicators ({results.surveillance_indicators.length})
              </h3>
              <div className="space-y-3">
                {results.surveillance_indicators.map((indicator, idx) => (
                  <div key={idx} className="bg-black/40 border border-purple-500/20 rounded-lg p-4">
                    <div className="flex items-start justify-between mb-2">
                      <div className="flex-1">
                        <div className="flex items-center gap-3 mb-2">
                          <span className="font-medium text-purple-300">{indicator.pattern}</span>
                          <span className={`text-xs px-2 py-1 rounded-full ${getRiskColor(indicator.risk)}`}>
                            {indicator.risk}
                          </span>
                        </div>
                        <p className="text-sm text-gray-300 mb-1">{indicator.description}</p>
                        <p className="text-xs text-gray-500 mb-2">Indicator: {indicator.indicator}</p>
                        <p className="text-xs text-blue-400">💡 {indicator.recommendation}</p>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Dark Web Mentions */}
          {results.dark_web_mentions && results.dark_web_mentions.length > 0 && (
            <div className="bg-black/50 border border-red-500/30 rounded-xl p-6">
              <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
                <Skull className="w-5 h-5 text-red-400" />
                Dark Web Intelligence ({results.dark_web_mentions.length})
              </h3>
              <div className="space-y-3">
                {results.dark_web_mentions.map((mention, idx) => (
                  <div key={idx} className="bg-red-500/10 border border-red-500/30 rounded-lg p-4">
                    <div className="flex items-start justify-between mb-2">
                      <div className="flex-1">
                        <div className="flex items-center gap-3 mb-2">
                          <span className="font-medium text-red-300">{mention.source}</span>
                          <span className={`text-xs px-2 py-1 rounded-full ${getRiskColor(mention.risk)}`}>
                            {mention.risk}
                          </span>
                          <span className="text-xs text-gray-500">Confidence: {mention.confidence}</span>
                        </div>
                        <p className="text-sm text-gray-300 mb-2">{mention.description}</p>
                        <p className="text-xs text-yellow-400">⚠️ {mention.recommendation}</p>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Indexer Exposure */}
          {results.exposure_on_indexers && results.exposure_on_indexers.length > 0 && (
            <div className="bg-black/50 border border-purple-500/20 rounded-xl p-6">
              <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
                <Globe className="w-5 h-5 text-blue-400" />
                Search Engine & Archive Exposure ({results.exposure_on_indexers.length})
              </h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                {results.exposure_on_indexers.map((indexer, idx) => (
                  <div key={idx} className="bg-black/40 border border-blue-500/20 rounded-lg p-3">
                    <div className="flex items-center gap-2 mb-1">
                      <span className="text-sm font-medium text-blue-300">{indexer.name}</span>
                      <span className="text-xs text-gray-500">({indexer.type})</span>
                    </div>
                    <p className="text-xs text-gray-400">{indexer.description}</p>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Recommendations */}
          {results.recommendations && results.recommendations.length > 0 && (
            <div className="bg-gradient-to-br from-green-500/10 to-blue-500/10 border border-green-500/30 rounded-xl p-6">
              <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
                <Shield className="w-5 h-5 text-green-400" />
                Security Recommendations
              </h3>
              <ul className="space-y-2">
                {results.recommendations.map((rec, idx) => (
                  <li key={idx} className="text-sm text-gray-300 flex items-start gap-2">
                    <CheckCircle className="w-4 h-4 text-green-400 mt-0.5 flex-shrink-0" />
                    <span>{rec}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}

      {/* No Results State */}
      {!analyzing && !results && (
        <div className="bg-black/50 border border-purple-500/20 rounded-xl p-12 text-center">
          <Eye className="w-16 h-16 mx-auto mb-4 text-purple-400 opacity-50" />
          <h3 className="text-xl font-semibold mb-2">No Analysis Yet</h3>
          <p className="text-gray-400">Enter a target and click "Scan for Trackers" to begin</p>
        </div>
      )}
    </div>
  );
}