import React, { useState } from 'react';
import { 
  Search, Upload, MapPin, AlertTriangle, Globe, Image, 
  FileText, Activity, Eye, XCircle, CheckCircle, MapPinned,
  Sparkles, Info, ExternalLink, Trash2
} from 'lucide-react';

export function VisualIntelligence({ backendStatus, BACKEND_URL }) {

  const renderSafe = (v) => {
    if (typeof v === "string") return v;
    if (typeof v === "object" && v !== null) {
      return v.pattern || v.type || JSON.stringify(v);
    }
    return "";
  };

  // Image/Video analysis state
  const [uploadedFile, setUploadedFile] = useState(null);
  const [previewUrl, setPreviewUrl] = useState(null);
  const [geoResults, setGeoResults] = useState(null);
  const [geoAnalyzing, setGeoAnalyzing] = useState(false);
  const [geoError, setGeoError] = useState(null);
  const [geoLogs, setGeoLogs] = useState([]);

  const addGeoLog = (message, type = 'info') => {
    const timestamp = new Date().toLocaleTimeString();
    setGeoLogs(prev => [...prev, { message, timestamp, type }]);
  };

  const handleFileUpload = (event) => {
    const files = event.target.files || (event.dataTransfer && event.dataTransfer.files);
    if (files && files.length > 0) {
      const file = files[0];
      
      // Validate file type
      const allowedExtensions = ['jpg', 'jpeg', 'png', 'gif', 'webp', 'mp4', 'mov'];
      const fileExtension = file.name.split('.').pop().toLowerCase();
      
      if (!allowedExtensions.includes(fileExtension)) {
        setGeoError(`Invalid file type: ${fileExtension}. Allowed: ${allowedExtensions.join(', ')}`);
        setUploadedFile(null);
        setPreviewUrl(null);
        addGeoLog(`Error: Invalid file type ${fileExtension}`, 'error');
        return;
      }
      
      // Create preview URL
      const preview = URL.createObjectURL(file);
      setPreviewUrl(preview);
      
      setGeoError(null);
      setUploadedFile(file);
      setGeoResults(null);
      addGeoLog(`✓ File selected: ${file.name}`);
    }
  };

  const handleClearFile = () => {
    if (previewUrl) {
      URL.revokeObjectURL(previewUrl);
    }
    setUploadedFile(null);
    setPreviewUrl(null);
    setGeoResults(null);
    setGeoError(null);
    setGeoLogs([]);
    addGeoLog('File cleared');
  };

  const handleVisualAnalyze = async () => {
    if (!uploadedFile) {
      addGeoLog('Please select an image or video file', 'error');
      setGeoError('No file selected');
      return;
    }

    if (!backendStatus || backendStatus.status === 'offline') {
      addGeoLog('Backend is offline. Please start the Flask server.', 'error');
      setGeoError('Backend offline');
      return;
    }

    setGeoAnalyzing(true);
    setGeoError(null);
    setGeoResults(null);
    setGeoLogs([]);

    const isVideo = uploadedFile.type.startsWith('video/');
    const endpoint = isVideo ? '/api/geolocation/video' : '/api/geolocation/image';

    addGeoLog(`Starting ${isVideo ? 'video' : 'image'} analysis...`);
    addGeoLog(`File: ${uploadedFile.name}`);
    addGeoLog(`Size: ${(uploadedFile.size / 1024 / 1024).toFixed(2)} MB`);

    try {
      const formData = new FormData();
      formData.append('file', uploadedFile);
      if (isVideo) {
        formData.append('num_frames', '5');
        addGeoLog('Video: Extracting 5 frames for analysis...');
      } else {
        addGeoLog('Image: Extracting EXIF metadata...');
      }

      addGeoLog('Uploading file to backend...');

      const response = await fetch(`${BACKEND_URL}${endpoint}`, {
        method: 'POST',
        body: formData
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.error || `HTTP ${response.status}`);
      }

      const data = await response.json();

      if (data.error) {
        throw new Error(data.error);
      }

      addGeoLog('✓ Analysis complete!', 'success');

      if (data.coordinate_source === 'exif') {
        addGeoLog('✓ GPS coordinates found in EXIF metadata', 'success');
        addGeoLog('Confidence: 100% (EXIF source)');
      } else if (data.coordinate_source === 'ai_estimation') {
        addGeoLog('✓ AI analysis completed', 'success');
        addGeoLog(`Confidence: ${data.confidence}%`);
      } else if (data.coordinate_source === 'ai_description_only') {
        addGeoLog('⚠ AI provided location description without coordinates');
      } else {
        addGeoLog('⚠ No location data found');
      }

      if (data.coordinates) {
        addGeoLog(`Location: ${data.coordinates.latitude}, ${data.coordinates.longitude}`);
      }

      setGeoResults(data);

    } catch (error) {
      const errorMsg = error.message || 'Unknown error occurred';
      console.error('Analysis error:', error);
      addGeoLog(`✗ Error: ${errorMsg}`, 'error');
      setGeoError(errorMsg);
    } finally {
      setGeoAnalyzing(false);
    }
  };

  const handleDragOver = (e) => {
    e.preventDefault();
    e.stopPropagation();
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    handleFileUpload(e);
  };

  const openInGoogleMaps = (lat, lon) => {
    window.open(`https://www.google.com/maps?q=${lat},${lon}`, '_blank');
  };

  return (
    <div className="min-h-screen bg-[#0a0a0a] text-white">
      {/* Grain overlay */}
      <div className="fixed inset-0 pointer-events-none opacity-[0.015]" style={{
        backgroundImage: `url("data:image/svg+xml,%3Csvg viewBox='0 0 400 400' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noiseFilter'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23noiseFilter)'/%3E%3C/svg%3E")`,
        backgroundRepeat: 'repeat'
      }}></div>

      {/* Visual Intelligence Section */}
      <div className="space-y-6 relative z-10 p-6">
        <div className="bg-black/50 backdrop-blur-sm border border-purple-500/20 rounded-xl p-6">
          <h2 className="text-2xl font-semibold mb-2 flex items-center gap-2">
            <Image className="w-6 h-6 text-purple-400" />
            Visual Intelligence & Geolocation Extraction
          </h2>
          <p className="text-sm text-gray-400 mb-6">
            Extract GPS coordinates from EXIF metadata or use AI to analyze landmarks and estimate location
          </p>

          {/* Error Alert */}
          {geoError && (
            <div className="mb-6 p-4 bg-red-500/20 border border-red-500/30 rounded-lg flex items-start gap-3">
              <AlertTriangle className="w-5 h-5 text-red-400 flex-shrink-0 mt-0.5" />
              <div className="flex-1">
                <p className="font-medium text-red-300">Analysis Error</p>
                <p className="text-sm text-red-200 mt-1">{geoError}</p>
              </div>
            </div>
          )}

          {/* Upload Zone */}
          <div
            className="border-2 border-dashed border-purple-500/30 rounded-lg p-12 text-center hover:border-purple-500/60 transition-all hover:bg-purple-500/5 cursor-pointer"
            onDragOver={handleDragOver}
            onDrop={handleDrop}
          >
            <Upload className="w-12 h-12 mx-auto mb-4 text-purple-400" />
            <p className="text-lg mb-2">Drop image or video here</p>
            <p className="text-sm text-gray-400 mb-4">
              Supports JPG, PNG, GIF, WebP, MP4, MOV • Max 50MB
            </p>

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
              <div className="mt-6 p-4 bg-green-500/20 border border-green-500/30 rounded-lg">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <CheckCircle className="w-5 h-5 text-green-400" />
                    <div className="text-left">
                      <p className="text-sm font-medium text-green-300">
                        {uploadedFile.name}
                      </p>
                      <p className="text-xs text-green-400/70 mt-0.5">
                        {(uploadedFile.size / 1024 / 1024).toFixed(2)} MB
                      </p>
                    </div>
                  </div>
                  <button
                    onClick={handleClearFile}
                    className="p-2 hover:bg-red-500/20 rounded-lg transition-colors"
                    title="Remove file"
                  >
                    <Trash2 className="w-4 h-4 text-red-400" />
                  </button>
                </div>

                {/* Preview */}
                {previewUrl && uploadedFile.type.startsWith('image/') && (
                  <div className="mt-4">
                    <img
                      src={previewUrl}
                      alt="Preview"
                      className="max-h-48 mx-auto rounded-lg border border-green-500/30"
                    />
                  </div>
                )}
              </div>
            )}
          </div>

          {/* Analyze Button */}
          {uploadedFile && (
            <button
              onClick={handleVisualAnalyze}
              disabled={geoAnalyzing || backendStatus?.status !== 'online'}
              className="mt-4 w-full px-6 py-3 bg-gradient-to-r from-purple-600 to-purple-700 hover:from-purple-700 hover:to-purple-800 disabled:from-gray-600 disabled:to-gray-700 disabled:cursor-not-allowed rounded-lg font-medium transition-all flex items-center justify-center gap-2 shadow-lg shadow-purple-500/20"
            >
              {geoAnalyzing ? (
                <>
                  <Activity className="w-5 h-5 animate-spin" />
                  Analyzing...
                </>
              ) : backendStatus?.status !== 'online' ? (
                <>
                  <XCircle className="w-5 h-5" />
                  Backend Offline - Check Server
                </>
              ) : (
                <>
                  <Sparkles className="w-5 h-5" />
                  Analyze for Geolocation
                </>
              )}
            </button>
          )}

          {/* Real-Time Logs */}
          {geoLogs.length > 0 && (
            <div className="mt-6 bg-black/70 border border-purple-500/20 rounded-lg p-4 font-mono">
              <div className="flex items-center justify-between mb-3">
                <h3 className="text-xs font-bold uppercase tracking-widest text-purple-400">
                  Real-time Analysis Log
                </h3>
                <Activity
                  className={`w-4 h-4 text-purple-400 ${
                    geoAnalyzing ? 'animate-pulse' : ''
                  }`}
                />
              </div>

              <div className="space-y-2 max-h-64 overflow-y-auto custom-scrollbar">
                {geoLogs.map((log, i) => (
                  <div key={i} className="text-[11px] flex gap-3">
                    <span className="text-purple-500/50 whitespace-nowrap">
                      [{log.timestamp}]
                    </span>
                    <span
                      className={
                        log.type === 'error'
                          ? 'text-red-400'
                          : log.type === 'success'
                          ? 'text-green-400'
                          : 'text-gray-300'
                      }
                    >
                      {log.message}
                    </span>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Geolocation Results */}
          {geoResults && !geoError && (
            <div className="mt-6 space-y-4">
              {/* Coordinates Card */}
              {geoResults.coordinates && (
                <div className="bg-gradient-to-br from-green-500/20 to-emerald-500/20 border border-green-500/30 rounded-lg p-5">
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <div className="flex items-center gap-2 mb-3">
                        <MapPin className="w-5 h-5 text-green-400" />
                        <h3 className="font-semibold text-green-300">GPS Coordinates Found</h3>
                      </div>
                      <div className="space-y-2">
                        <div className="flex items-center gap-2">
                          <span className="text-sm text-gray-400">Latitude:</span>
                          <span className="font-mono text-green-300">{geoResults.coordinates.latitude}</span>
                        </div>
                        <div className="flex items-center gap-2">
                          <span className="text-sm text-gray-400">Longitude:</span>
                          <span className="font-mono text-green-300">{geoResults.coordinates.longitude}</span>
                        </div>
                        <div className="flex items-center gap-2">
                          <span className="text-sm text-gray-400">Source:</span>
                          <span className="text-xs px-2 py-1 bg-green-500/30 text-green-300 rounded">
                            {geoResults.coordinate_source === 'exif' ? 'EXIF Metadata' : 'AI Estimation'}
                          </span>
                        </div>
                      </div>
                    </div>
                    <button
                      onClick={() => openInGoogleMaps(
                        geoResults.coordinates.latitude,
                        geoResults.coordinates.longitude
                      )}
                      className="px-4 py-2 bg-green-600 hover:bg-green-700 rounded-lg transition-colors flex items-center gap-2 text-sm"
                    >
                      <ExternalLink className="w-4 h-4" />
                      Open in Maps
                    </button>
                  </div>
                </div>
              )}

              {/* Confidence Meter */}
              <div className="bg-black/40 border border-purple-500/20 rounded-lg p-5">
                <div className="flex items-center justify-between mb-3">
                  <div className="flex items-center gap-2">
                    <Activity className="w-5 h-5 text-purple-400" />
                    <h3 className="font-semibold">Confidence Score</h3>
                  </div>
                  <span className="text-2xl font-bold text-purple-400">
                    {geoResults.confidence}%
                  </span>
                </div>
                <div className="w-full bg-gray-700 rounded-full h-3 overflow-hidden">
                  <div
                    className={`h-full transition-all duration-1000 ${
                      geoResults.confidence >= 80
                        ? 'bg-gradient-to-r from-green-500 to-emerald-500'
                        : geoResults.confidence >= 50
                        ? 'bg-gradient-to-r from-yellow-500 to-orange-500'
                        : 'bg-gradient-to-r from-red-500 to-orange-500'
                    }`}
                    style={{ width: `${geoResults.confidence}%` }}
                  ></div>
                </div>
                <p className="text-xs text-gray-400 mt-2">
                  {geoResults.confidence >= 80
                    ? '🎯 High confidence - Results are likely accurate'
                    : geoResults.confidence >= 50
                    ? '⚠️ Moderate confidence - Results may need verification'
                    : '⚠️ Low confidence - Results should be verified'}
                </p>
              </div>

              {/* Location Estimate */}
              {geoResults.location_estimate && (
                <div className="bg-black/40 border border-blue-500/20 rounded-lg p-5">
                  <div className="flex items-center gap-2 mb-3">
                    <Globe className="w-5 h-5 text-blue-400" />
                    <h3 className="font-semibold">Location Estimate</h3>
                  </div>
                  <p className="text-blue-300 text-lg whitespace-pre-wrap">{geoResults.location_estimate}</p>
                  {geoResults.analysis && geoResults.analysis !== 'Location analysis complete' && (
                    <div className="mt-4 p-3 bg-blue-500/10 border border-blue-500/20 rounded-lg">
                      <p className="text-sm text-gray-300 whitespace-pre-wrap">{geoResults.analysis}</p>
                    </div>
                  )}
                </div>
              )}

              {/* Visual Clues */}
              {geoResults.clues && geoResults.clues.length > 0 && (
                <div className="bg-black/40 border border-purple-500/20 rounded-lg p-5">
                  <div className="flex items-center gap-2 mb-3">
                    <Eye className="w-5 h-5 text-purple-400" />
                    <h3 className="font-semibold">Visual Clues Detected</h3>
                  </div>
                  <div className="space-y-2">
                    {geoResults.clues.map((clue, idx) => (
                      <div key={idx} className="flex items-start gap-2">
                        <span className="text-purple-400 mt-1">•</span>
                        <span className="text-gray-300">{renderSafe(clue)}</span>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Landmarks */}
              {geoResults.landmarks && geoResults.landmarks.length > 0 && (
                <div className="bg-black/40 border border-orange-500/20 rounded-lg p-5">
                  <div className="flex items-center gap-2 mb-3">
                    <MapPinned className="w-5 h-5 text-orange-400" />
                    <h3 className="font-semibold">Landmarks Identified</h3>
                  </div>
                  <div className="flex flex-wrap gap-2">
                    {geoResults.landmarks.map((landmark, idx) => (
                      <span
                        key={idx}
                        className="px-3 py-1.5 bg-orange-500/20 border border-orange-500/30 text-orange-300 rounded-full text-sm"
                      >
                        {renderSafe(landmark)}
                      </span>
                    ))}
                  </div>
                </div>
              )}

              {/* EXIF Data */}
              {geoResults.exif_data && geoResults.exif_data.has_exif && (
                <div className="bg-black/40 border border-cyan-500/20 rounded-lg p-5">
                  <div className="flex items-center gap-2 mb-3">
                    <FileText className="w-5 h-5 text-cyan-400" />
                    <h3 className="font-semibold">EXIF Metadata</h3>
                  </div>
                  <div className="space-y-2 text-sm">
                    <div className="flex justify-between">
                      <span className="text-gray-400">EXIF Data Present:</span>
                      <span className="text-green-400">✓ Yes</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-400">GPS Coordinates:</span>
                      <span className={geoResults.exif_data.coordinates ? 'text-green-400' : 'text-gray-500'}>
                        {geoResults.exif_data.coordinates ? '✓ Found' : '✗ Not found'}
                      </span>
                    </div>
                  </div>
                </div>
              )}

              {/* Metadata */}
              <div className="bg-black/40 border border-gray-500/20 rounded-lg p-4">
                <div className="flex items-center gap-2 mb-2">
                  <Info className="w-4 h-4 text-gray-400" />
                  <h3 className="text-sm font-medium text-gray-400">Analysis Metadata</h3>
                </div>
                <div className="grid grid-cols-2 gap-2 text-xs">
                  <div>
                    <span className="text-gray-500">AI Service:</span>
                    <span className="ml-2 text-gray-300">
                      {geoResults.ai_service_used || 'none'}
                    </span>
                  </div>
                  <div>
                    <span className="text-gray-500">Timestamp:</span>
                    <span className="ml-2 text-gray-300">
                      {new Date(geoResults.timestamp).toLocaleString()}
                    </span>
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Feature Overview */}
          <div className="mt-6 grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="bg-black/40 border border-purple-500/20 rounded-lg p-4">
              <h3 className="font-medium mb-3 flex items-center gap-2">
                <FileText className="w-5 h-5 text-purple-400" />
                EXIF Data Extraction
              </h3>
              <ul className="space-y-2 text-sm text-gray-300">
                <li className="flex items-center gap-2">
                  <MapPin className="w-4 h-4 text-green-400" />
                  GPS Coordinates (100% accurate)
                </li>
                <li className="flex items-center gap-2">
                  <Activity className="w-4 h-4 text-blue-400" />
                  Camera Model & Settings
                </li>
                <li className="flex items-center gap-2">
                  <FileText className="w-4 h-4 text-purple-400" />
                  Timestamp & Date Information
                </li>
              </ul>
            </div>

            <div className="bg-black/40 border border-purple-500/20 rounded-lg p-4">
              <h3 className="font-medium mb-3 flex items-center gap-2">
                <Sparkles className="w-5 h-5 text-purple-400" />
                AI Visual Analysis
              </h3>
              <ul className="space-y-2 text-sm text-gray-300">
                <li className="flex items-center gap-2">
                  <Eye className="w-4 h-4 text-purple-400" />
                  Landmark Recognition
                </li>
                <li className="flex items-center gap-2">
                  <Globe className="w-4 h-4 text-blue-400" />
                  Environmental Clues Analysis
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

      {/* Custom Scrollbar Styles */}
      <style jsx>{`
        .custom-scrollbar::-webkit-scrollbar {
          width: 6px;
        }
        .custom-scrollbar::-webkit-scrollbar-track {
          background: rgba(255, 255, 255, 0.05);
          border-radius: 3px;
        }
        .custom-scrollbar::-webkit-scrollbar-thumb {
          background: rgba(168, 85, 247, 0.5);
          border-radius: 3px;
        }
        .custom-scrollbar::-webkit-scrollbar-thumb:hover {
          background: rgba(168, 85, 247, 0.7);
        }
      `}</style>
    </div>
  );
}

export default VisualIntelligence;