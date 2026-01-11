import React, { useState, useEffect } from 'react';
import { useAuth } from './AuthContext';
import { useNavigate } from 'react-router-dom';
import { Shield, Users, MessageSquare, LogOut, ArrowLeft, Trash2, ChevronDown, ChevronUp, Calendar, Paperclip } from 'lucide-react';

export default function AdminPanel() {
  const [feedback, setFeedback] = useState([]);
  const [expandedId, setExpandedId] = useState(null);
  const [stats, setStats] = useState({
    totalUsers: 0,
    totalFeedback: 0,
    pendingFeedback: 0
  });
  const [loading, setLoading] = useState(true);
  const { currentUser, logout } = useAuth();
  const navigate = useNavigate();

  const BACKEND_URL = 'http://localhost:5000';

  useEffect(() => {
    fetchFeedback();
    fetchStats();
  }, []);

  const fetchFeedback = async () => {
    try {
      const response = await fetch(`${BACKEND_URL}/api/admin/feedback`, {
        headers: {
          'Authorization': `Bearer ${await currentUser.getIdToken()}`
        }
      });
      const data = await response.json();
      console.log('📥 Fetched feedback:', data.feedback); // Debug
      setFeedback(data.feedback || []);
      setLoading(false);
    } catch (error) {
      console.error('Failed to fetch feedback:', error);
      setLoading(false);
    }
  };

  const fetchStats = async () => {
    try {
      const response = await fetch(`${BACKEND_URL}/api/admin/stats`, {
        headers: {
          'Authorization': `Bearer ${await currentUser.getIdToken()}`
        }
      });
      const data = await response.json();
      setStats(data.stats || stats);
    } catch (error) {
      console.error('Failed to fetch stats:', error);
    }
  };

  const handleDelete = async (id) => {
    if (!window.confirm('Are you sure you want to delete this feedback?')) return;

    try {
      const response = await fetch(`${BACKEND_URL}/api/admin/feedback/${id}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${await currentUser.getIdToken()}`
        }
      });

      if (response.ok) {
        setFeedback(feedback.filter(f => f.id !== id));
        fetchStats();
      }
    } catch (error) {
      console.error('Failed to delete feedback:', error);
    }
  };

  const handleLogout = async () => {
    try {
      await logout();
      navigate('/login');
    } catch (error) {
      console.error('Failed to logout:', error);
    }
  };

  const toggleExpand = (id) => {
    setExpandedId(expandedId === id ? null : id);
  };

  const formatDate = (timestamp) => {
    if (!timestamp) return 'No date';
    try {
      const date = new Date(timestamp);
      return date.toLocaleString('en-US', {
        month: 'short',
        day: 'numeric',
        year: 'numeric',
        hour: 'numeric',
        minute: '2-digit',
        hour12: true
      });
    } catch (e) {
      return 'Invalid date';
    }
  };

  const getTypeColor = (type) => {
    const colors = {
      'bug': 'bg-red-500/20 text-red-300 border-red-500/30',
      'feature': 'bg-blue-500/20 text-blue-300 border-blue-500/30',
      'improvement': 'bg-purple-500/20 text-purple-300 border-purple-500/30',
      'question': 'bg-yellow-500/20 text-yellow-300 border-yellow-500/30',
      'other': 'bg-gray-500/20 text-gray-300 border-gray-500/30'
    };
    return colors[type] || colors['other'];
  };

  const getPriorityColor = (priority) => {
    const colors = {
      'critical': 'bg-red-600/30 text-red-200 border-red-600/40',
      'high': 'bg-orange-500/30 text-orange-200 border-orange-500/40',
      'medium': 'bg-yellow-500/30 text-yellow-200 border-yellow-500/40',
      'low': 'bg-green-500/30 text-green-200 border-green-500/40'
    };
    return colors[priority] || colors['medium'];
  };

  const getTypeEmoji = (type) => {
    const emojis = {
      'bug': '🐛',
      'feature': '✨',
      'improvement': '🚀',
      'question': '❓',
      'other': '💬'
    };
    return emojis[type] || '💬';
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900">
      {/* Header */}
      <header className="border-b border-purple-500/20 bg-black/50 backdrop-blur-sm">
        <div className="max-w-7xl mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <button
                onClick={() => navigate('/dashboard')}
                className="p-2 hover:bg-purple-500/20 rounded-lg transition-colors"
              >
                <ArrowLeft className="w-5 h-5 text-purple-400" />
              </button>
              <Shield className="w-8 h-8 text-purple-400" />
              <div>
                <h1 className="text-xl font-bold text-white">Admin Panel</h1>
                <p className="text-xs text-purple-300">CHAKRAVYUH 1.0</p>
              </div>
            </div>
            <div className="flex items-center gap-4">
              <span className="text-sm text-purple-300">{currentUser?.email}</span>
              <button
                onClick={handleLogout}
                className="flex items-center gap-2 px-4 py-2 bg-red-500/20 hover:bg-red-500/30 text-red-300 rounded-lg transition-colors"
              >
                <LogOut className="w-4 h-4" />
                Logout
              </button>
            </div>
          </div>
        </div>
      </header>

      <div className="max-w-7xl mx-auto px-6 py-8">
        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          <div className="bg-black/50 border border-purple-500/20 rounded-xl p-6">
            <Users className="w-8 h-8 text-purple-400 mb-3" />
            <p className="text-3xl font-bold text-white mb-1">{stats.totalUsers}</p>
            <p className="text-sm text-purple-300">Total Users</p>
          </div>

          <div className="bg-black/50 border border-purple-500/20 rounded-xl p-6">
            <MessageSquare className="w-8 h-8 text-blue-400 mb-3" />
            <p className="text-3xl font-bold text-white mb-1">{stats.totalFeedback}</p>
            <p className="text-sm text-blue-300">Total Feedback</p>
          </div>

          <div className="bg-black/50 border border-purple-500/20 rounded-xl p-6">
            <Shield className="w-8 h-8 text-green-400 mb-3" />
            <p className="text-3xl font-bold text-white mb-1">{stats.pendingFeedback}</p>
            <p className="text-sm text-green-300">Pending Review</p>
          </div>
        </div>

        {/* Feedback List */}
        <div className="bg-black/50 border border-purple-500/20 rounded-xl p-6">
          <h2 className="text-xl font-semibold text-white mb-6 flex items-center gap-2">
            <MessageSquare className="w-5 h-5 text-purple-400" />
            User Feedback
          </h2>

          {loading ? (
            <div className="text-center py-12">
              <div className="w-12 h-12 border-4 border-purple-500 border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
              <p className="text-gray-400">Loading feedback...</p>
            </div>
          ) : feedback.length === 0 ? (
            <div className="text-center py-12">
              <MessageSquare className="w-16 h-16 text-gray-600 mx-auto mb-4" />
              <p className="text-gray-400">No feedback yet</p>
            </div>
          ) : (
            <div className="space-y-4">
              {feedback.map((item) => (
                <div
                  key={item.id}
                  className="bg-black/40 border border-purple-500/20 rounded-lg overflow-hidden hover:border-purple-500/40 transition-all"
                >
                  {/* Collapsed View */}
                  <div 
                    className="p-4 cursor-pointer"
                    onClick={() => toggleExpand(item.id)}
                  >
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        {/* Title and Badges */}
                        <div className="flex items-center gap-3 mb-2 flex-wrap">
                          <h4 className="text-lg font-semibold text-white">
                            {item.title || 'No Title'}
                          </h4>
                          
                          {item.feedback_type && (
                            <span className={`text-xs px-2 py-1 rounded-full border ${getTypeColor(item.feedback_type)}`}>
                              {getTypeEmoji(item.feedback_type)} {item.feedback_type}
                            </span>
                          )}
                          
                          {item.priority && (
                            <span className={`text-xs px-2 py-1 rounded-full border ${getPriorityColor(item.priority)}`}>
                              {item.priority.toUpperCase()}
                            </span>
                          )}
                        </div>
                        
                        {/* User and Date Info */}
                        <div className="flex items-center gap-3 mb-2 flex-wrap text-sm">
                          <span className="text-purple-300 font-medium">
                            {item.email || 'Anonymous'}
                          </span>
                          <span className="text-gray-500 flex items-center gap-1">
                            <Calendar className="w-3 h-3" />
                            {formatDate(item.timestamp)}
                          </span>
                          {item.file_count > 0 && (
                            <span className="text-blue-300 flex items-center gap-1 bg-blue-500/10 px-2 py-0.5 rounded">
                              <Paperclip className="w-3 h-3" />
                              {item.file_count} file(s)
                            </span>
                          )}
                        </div>
                        
                        {/* Preview of message */}
                        <p className="text-gray-400 text-sm line-clamp-2">
                          {item.message || 'No message'}
                        </p>
                      </div>
                      
                      <div className="flex items-center gap-2 ml-4">
                        <button
                          onClick={(e) => {
                            e.stopPropagation();
                            handleDelete(item.id);
                          }}
                          className="p-2 hover:bg-red-500/20 rounded-lg transition-colors"
                        >
                          <Trash2 className="w-4 h-4 text-red-400" />
                        </button>
                        {expandedId === item.id ? (
                          <ChevronUp className="w-5 h-5 text-purple-400" />
                        ) : (
                          <ChevronDown className="w-5 h-5 text-purple-400" />
                        )}
                      </div>
                    </div>
                  </div>

                  {/* Expanded View */}
                  {expandedId === item.id && (
                    <div className="border-t border-purple-500/20 bg-black/20 p-4">
                      <div className="space-y-4">
                        {/* Full Message */}
                        <div>
                          <h5 className="text-sm font-semibold text-purple-300 mb-2">Full Description:</h5>
                          <p className="text-gray-300 whitespace-pre-wrap bg-black/40 p-3 rounded">
                            {item.message || 'No description provided'}
                          </p>
                        </div>

                        {/* User Details */}
                        <div className="grid grid-cols-2 gap-4">
                          <div>
                            <h5 className="text-sm font-semibold text-purple-300 mb-1">Submitted By:</h5>
                            <p className="text-gray-300">{item.email || 'Anonymous'}</p>
                          </div>
                          <div>
                            <h5 className="text-sm font-semibold text-purple-300 mb-1">Submission Time:</h5>
                            <p className="text-gray-300">{formatDate(item.timestamp)}</p>
                          </div>
                        </div>

                        {/* Attachments with Preview */}
{item.file_paths && item.file_paths.length > 0 ? (
  <div>
    <h5 className="text-sm font-semibold text-purple-300 mb-2">Attachments ({item.file_paths.length}):</h5>
    <div className="grid grid-cols-2 gap-3">
      {item.file_paths.map((file, idx) => {
        // ✅ Use file.filename (the one with timestamp) for the URL
        const fileUrl = `${BACKEND_URL}/api/uploads/${file.filename}`;
        
        // Debug logs
        console.log('🔍 File object:', file);
        console.log('🌐 Requesting URL:', fileUrl);
        
        const isImage = /\.(jpg|jpeg|png|gif|webp)$/i.test(file.filename);
        const isVideo = /\.(mp4|mov|avi|webm)$/i.test(file.filename);

        return (
          <div key={idx} className="bg-black/40 border border-purple-500/20 rounded-lg p-3">
            {isImage && (
              <div className="mb-2">
                <img 
                  src={fileUrl} 
                  alt={file.original_name}
                  className="w-full h-40 object-cover rounded cursor-pointer hover:opacity-80 transition"
                  onClick={() => window.open(fileUrl, '_blank')}
                  onError={(e) => {
                    console.error('❌ Image load failed');
                    console.error('URL:', fileUrl);
                    console.error('File object:', file);
                    e.target.style.display = 'none';
                    e.target.nextSibling.style.display = 'flex';
                  }}
                />
                <div 
                  className="hidden items-center justify-center h-40 bg-red-500/10 border border-red-500/30 rounded text-red-300 text-xs"
                >
                  Failed to load image
                </div>
              </div>
            )}
            
            {isVideo && (
              <div className="mb-2">
                <video 
                  src={fileUrl}
                  controls
                  className="w-full h-40 rounded"
                  onError={(e) => {
                    console.error('❌ Video load failed:', fileUrl);
                  }}
                />
              </div>
            )}

            <div className="flex items-center justify-between">
  <div className="flex-1 min-w-0">
    <p className="text-xs text-gray-300 truncate" title={file.original_name}>
      {file.original_name}
    </p>
    <p className="text-xs text-gray-500">
      {(file.size / 1024).toFixed(1)} KB
    </p>
    {/* Debug info - remove after fixing */}
    <p className="text-[10px] text-purple-400 mt-1">
      Stored as: {file.filename}
    </p>
  </div>
  
  <a 
    href={fileUrl}
    download={file.original_name}
    className="ml-2 p-1.5 bg-blue-500/20 hover:bg-blue-500/30 rounded transition text-blue-300"
                title="Download"
              >
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
                </svg>
              </a>
            </div>
          </div>
        );
      })}
    </div>
  </div>
) : (
  <div>
    <h5 className="text-sm font-semibold text-purple-300 mb-1">Attachments:</h5>
    <p className="text-gray-400 text-sm">No files attached</p>
  </div>
)}
                        {/* Rating */}
                        {item.rating && (
                          <div>
                            <h5 className="text-sm font-semibold text-purple-300 mb-1">Rating:</h5>
                            <div className="flex items-center gap-1">
                              {[...Array(5)].map((_, i) => (
                                <span
                                  key={i}
                                  className={`text-xl ${i < item.rating ? 'text-yellow-400' : 'text-gray-600'}`}
                                >
                                  ★
                                </span>
                              ))}
                            </div>
                          </div>
                        )}
                      </div>
                    </div>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}