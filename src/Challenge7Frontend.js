/**
 * Challenge 7: Real-World OSINT Robustness - Frontend Component
 * 
 * Usage in OSINTDashboard.js:
 * 
 * import Challenge7Frontend from './Challenge7Frontend';
 * 
 * // Inside your results display section:
 * {results && <Challenge7Frontend results={results} discoveredProfiles={discoveredProfiles} />}
 */

import React from 'react';
import { Activity, Target, CheckCircle, XCircle, AlertTriangle } from 'lucide-react';

const Challenge7Frontend = ({ results, discoveredProfiles, platformIcons }) => {
  
  if (!results) return null;

  return (
    <>
      {/* Data Quality Assessment Card */}
      {results.data_quality && (
        <div className="bg-gradient-to-br from-blue-500/10 to-cyan-500/10 border border-blue-500/30 rounded-xl p-5 mb-4 animate-slide-in">
          <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
            <Activity className="w-5 h-5 text-blue-400" />
            Data Quality Assessment
          </h3>

          {/* Metric Cards */}
          <div className="grid grid-cols-2 md:grid-cols-5 gap-3 mb-4">
            <div className="bg-black/40 rounded-lg p-3 text-center hover:bg-black/60 transition-colors">
              <p className="text-3xl font-bold text-blue-400">{results.data_quality.overall_score}</p>
              <p className="text-xs text-gray-400 mt-1">Overall Score</p>
            </div>
            <div className="bg-black/40 rounded-lg p-3 text-center hover:bg-black/60 transition-colors">
              <p className="text-2xl font-bold text-green-400">{results.data_quality.grade}</p>
              <p className="text-xs text-gray-400 mt-1">Grade</p>
            </div>
            <div className="bg-black/40 rounded-lg p-3 text-center hover:bg-black/60 transition-colors">
              <p className="text-sm font-bold text-purple-400">{results.data_quality.platform_coverage}%</p>
              <p className="text-xs text-gray-400 mt-1">Coverage</p>
            </div>
            <div className="bg-black/40 rounded-lg p-3 text-center hover:bg-black/60 transition-colors">
              <p className="text-sm font-bold text-orange-400">{results.data_quality.data_completeness}%</p>
              <p className="text-xs text-gray-400 mt-1">Completeness</p>
            </div>
            <div className="bg-black/40 rounded-lg p-3 text-center hover:bg-black/60 transition-colors">
              <p className="text-sm font-bold text-cyan-400">{results.data_quality.freshness_score}%</p>
              <p className="text-xs text-gray-400 mt-1">Freshness</p>
            </div>
          </div>

          {/* Progress Bars */}
          <div className="bg-black/40 rounded-lg p-4">
            <div className="space-y-2">
              <div className="flex items-center justify-between text-sm">
                <span className="text-gray-400">Platform Coverage</span>
                <div className="flex-1 mx-3 bg-black/30 rounded-full h-2">
                  <div 
                    className="bg-purple-500 h-2 rounded-full transition-all duration-1000"
                    style={{width: `${results.data_quality.platform_coverage}%`}}
                  />
                </div>
                <span className="font-medium">{results.data_quality.platform_coverage}%</span>
              </div>
              
              <div className="flex items-center justify-between text-sm">
                <span className="text-gray-400">Data Completeness</span>
                <div className="flex-1 mx-3 bg-black/30 rounded-full h-2">
                  <div 
                    className="bg-orange-500 h-2 rounded-full transition-all duration-1000"
                    style={{width: `${results.data_quality.data_completeness}%`}}
                  />
                </div>
                <span className="font-medium">{results.data_quality.data_completeness}%</span>
              </div>
              
              <div className="flex items-center justify-between text-sm">
                <span className="text-gray-400">Data Freshness</span>
                <div className="flex-1 mx-3 bg-black/30 rounded-full h-2">
                  <div 
                    className="bg-cyan-500 h-2 rounded-full transition-all duration-1000"
                    style={{width: `${results.data_quality.freshness_score}%`}}
                  />
                </div>
                <span className="font-medium">{results.data_quality.freshness_score}%</span>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Consolidated Intelligence Card */}
      {results.consolidated_intelligence && (
        <div className="bg-gradient-to-br from-green-500/10 to-emerald-500/10 border border-green-500/30 rounded-xl p-5 mb-4 animate-slide-in">
          <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
            <Target className="w-5 h-5 text-green-400" />
            Consolidated Intelligence
            <span className="text-xs bg-green-500/20 px-2 py-1 rounded-full ml-2">
              Merged from {discoveredProfiles?.length || 0} platforms
            </span>
          </h3>

          <div className="grid md:grid-cols-2 gap-4">
            {/* Emails */}
            {results.consolidated_intelligence.emails?.length > 0 && (
              <div className="bg-black/40 rounded-lg p-4 hover:bg-black/60 transition-colors">
                <p className="text-sm font-medium text-green-300 mb-2 flex items-center gap-2">
                  <span>📧</span> Email Addresses ({results.consolidated_intelligence.emails.length})
                </p>
                <div className="space-y-1">
                  {results.consolidated_intelligence.emails.map((email, idx) => (
                    <p key={idx} className="text-xs text-gray-300 font-mono">{email}</p>
                  ))}
                </div>
              </div>
            )}

            {/* Usernames */}
            {results.consolidated_intelligence.usernames?.length > 0 && (
              <div className="bg-black/40 rounded-lg p-4 hover:bg-black/60 transition-colors">
                <p className="text-sm font-medium text-green-300 mb-2 flex items-center gap-2">
                  <span>👤</span> Usernames ({results.consolidated_intelligence.usernames.length})
                </p>
                <div className="flex flex-wrap gap-2">
                  {results.consolidated_intelligence.usernames.map((username, idx) => (
                    <span key={idx} className="text-xs bg-green-500/20 text-green-300 px-2 py-1 rounded">
                      @{username}
                    </span>
                  ))}
                </div>
              </div>
            )}

            {/* Names */}
            {results.consolidated_intelligence.names?.length > 0 && (
              <div className="bg-black/40 rounded-lg p-4 hover:bg-black/60 transition-colors">
                <p className="text-sm font-medium text-green-300 mb-2 flex items-center gap-2">
                  <span>🏷️</span> Names ({results.consolidated_intelligence.names.length})
                </p>
                <div className="space-y-1">
                  {results.consolidated_intelligence.names.map((name, idx) => (
                    <p key={idx} className="text-xs text-gray-300">{name}</p>
                  ))}
                </div>
              </div>
            )}

            {/* Locations */}
            {results.consolidated_intelligence.locations?.length > 0 && (
              <div className="bg-black/40 rounded-lg p-4 hover:bg-black/60 transition-colors">
                <p className="text-sm font-medium text-green-300 mb-2 flex items-center gap-2">
                  <span>📍</span> Locations ({results.consolidated_intelligence.locations.length})
                </p>
                <div className="space-y-1">
                  {results.consolidated_intelligence.locations.map((loc, idx) => (
                    <p key={idx} className="text-xs text-gray-300">{loc}</p>
                  ))}
                </div>
              </div>
            )}

            {/* Companies */}
            {results.consolidated_intelligence.companies?.length > 0 && (
              <div className="bg-black/40 rounded-lg p-4 hover:bg-black/60 transition-colors">
                <p className="text-sm font-medium text-green-300 mb-2 flex items-center gap-2">
                  <span>🏢</span> Companies ({results.consolidated_intelligence.companies.length})
                </p>
                <div className="space-y-1">
                  {results.consolidated_intelligence.companies.map((company, idx) => (
                    <p key={idx} className="text-xs text-gray-300">{company}</p>
                  ))}
                </div>
              </div>
            )}

            {/* Links */}
            {results.consolidated_intelligence.links?.length > 0 && (
              <div className="bg-black/40 rounded-lg p-4 hover:bg-black/60 transition-colors">
                <p className="text-sm font-medium text-green-300 mb-2 flex items-center gap-2">
                  <span>🔗</span> Links ({results.consolidated_intelligence.links.length})
                </p>
                <div className="space-y-1">
                  {results.consolidated_intelligence.links.map((link, idx) => (
                    <a 
                      key={idx} 
                      href={link} 
                      target="_blank" 
                      rel="noopener noreferrer"
                      className="text-xs text-blue-400 hover:text-blue-300 block truncate"
                    >
                      {link}
                    </a>
                  ))}
                </div>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Behavioral Patterns Card */}
      {results.behavioral_patterns && results.behavioral_patterns.length > 0 && (
        <div className="bg-gradient-to-br from-purple-500/10 to-pink-500/10 border border-purple-500/30 rounded-xl p-5 mb-4 animate-slide-in">
          <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
            <Activity className="w-5 h-5 text-purple-400" />
            Behavioral Patterns Detected
            <span className="text-xs bg-purple-500/20 px-2 py-1 rounded-full ml-2">
              {results.behavioral_patterns.length} patterns
            </span>
          </h3>

          <div className="space-y-3">
            {results.behavioral_patterns.map((pattern, idx) => (
              <div key={idx} className="bg-black/40 rounded-lg p-4 hover:bg-black/60 transition-colors cursor-pointer">
                <p className="text-sm text-gray-300 flex items-start gap-3">
                  <span className="text-2xl">{pattern.split(' ')[0]}</span>
                  <span className="flex-1 mt-1">{pattern.substring(pattern.indexOf(' ') + 1)}</span>
                </p>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Enhanced Discovered Profiles with Quality Indicators */}
      {discoveredProfiles && discoveredProfiles.length > 0 && (
        <div className="mb-6 bg-black/50 border border-purple-500/30 rounded-lg p-4">
          <h3 className="font-semibold mb-3 text-purple-300 flex items-center justify-between">
            <span>Discovered Profiles</span>
            {results.duplicates_removed > 0 && (
              <span className="text-xs bg-orange-500/20 text-orange-300 px-2 py-1 rounded-full">
                {results.duplicates_removed} duplicates removed
              </span>
            )}
          </h3>

          <div className="space-y-2">
            {discoveredProfiles.map((profile, idx) => (
              <a
                key={idx}
                href={profile.profile_url}
                target="_blank"
                rel="noopener noreferrer"
                className="flex items-center justify-between p-3 rounded-lg bg-black/40 hover:bg-black/60 transition border border-purple-500/10 block"
              >
                <div className="flex-1">
                  <p className="text-sm font-medium text-purple-300 capitalize flex items-center gap-2">
                    {platformIcons && platformIcons[profile.platform_key] &&
                      React.createElement(
                        platformIcons[profile.platform_key],
                        { className: "w-4 h-4" }
                      )}
                    {profile.platform}
                  </p>
                  <p className="text-sm text-gray-300">@{profile.username}</p>
                  
                  {/* Data quality indicators */}
                  <div className="flex gap-2 mt-1">
                    {profile.data_completeness && (
                      <span className="text-xs text-gray-500">
                        {profile.data_completeness}% complete
                      </span>
                    )}
                    {profile.freshness && profile.freshness !== 'FRESH' && (
                      <span className={`text-xs flex items-center gap-1 ${
                        profile.freshness === 'STALE' ? 'text-red-400' : 'text-yellow-400'
                      }`}>
                        {profile.freshness === 'STALE' ? (
                          <><AlertTriangle className="w-3 h-3" /> Outdated</>
                        ) : (
                          <><AlertTriangle className="w-3 h-3" /> Aging</>
                        )}
                      </span>
                    )}
                  </div>
                </div>

                <span
                  className={`text-xs px-3 py-1 rounded-full flex items-center gap-1 ${
                    profile.verification === "api_verified"
                      ? "bg-green-500/20 text-green-300"
                      : "bg-yellow-500/20 text-yellow-300"
                  }`}
                >
                  {profile.verification === "api_verified" ? (
                    <><CheckCircle className="w-3 h-3" /> verified</>
                  ) : (
                    <><XCircle className="w-3 h-3" /> weak verified</>
                  )}
                </span>
              </a>
            ))}
          </div>
        </div>
      )}
    </>
  );
};

export default Challenge7Frontend;