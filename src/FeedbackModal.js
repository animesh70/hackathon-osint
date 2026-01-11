import React, { useState } from 'react';
import { X, Upload, MessageSquare, Send, AlertCircle, CheckCircle, Image as ImageIcon, Video, File } from 'lucide-react';
import { useAuth } from './AuthContext';
import emailjs from 'emailjs-com';

export default function FeedbackModal({ isOpen, onClose }) {
  const { currentUser } = useAuth();
  const [formData, setFormData] = useState({
    title: '',
    type: 'bug',
    priority: 'medium',
    description: ''
  });
  const [files, setFiles] = useState([]);
  const [loading, setLoading] = useState(false);
  const [success, setSuccess] = useState(false);
  const [error, setError] = useState('');

  const feedbackTypes = [
    { value: 'bug', label: '🐛 Bug Report', color: 'red' },
    { value: 'feature', label: '✨ Feature Request', color: 'blue' },
    { value: 'improvement', label: '🚀 Improvement', color: 'purple' },
    { value: 'question', label: '❓ Question', color: 'yellow' },
    { value: 'other', label: '💬 Other', color: 'gray' }
  ];

  const priorityLevels = [
    { value: 'low', label: 'Low', color: 'green' },
    { value: 'medium', label: 'Medium', color: 'yellow' },
    { value: 'high', label: 'High', color: 'orange' },
    { value: 'critical', label: 'Critical', color: 'red' }
  ];

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };

  const handleFileChange = (e) => {
    const selectedFiles = Array.from(e.target.files);
    const validFiles = selectedFiles.filter(file => {
      const isImage = file.type.startsWith('image/');
      const isVideo = file.type.startsWith('video/');
      const isUnder10MB = file.size <= 10 * 1024 * 1024; // 10MB limit
      return (isImage || isVideo) && isUnder10MB;
    });

    if (validFiles.length < selectedFiles.length) {
      setError('Some files were skipped (only images/videos under 10MB)');
      setTimeout(() => setError(''), 3000);
    }

    setFiles([...files, ...validFiles].slice(0, 5)); // Max 5 files
  };

  const removeFile = (index) => {
    setFiles(files.filter((_, i) => i !== index));
  };

  const getFileIcon = (file) => {
    if (file.type.startsWith('image/')) return <ImageIcon className="w-4 h-4" />;
    if (file.type.startsWith('video/')) return <Video className="w-4 h-4" />;
    return <File className="w-4 h-4" />;
  };

  const convertFilesToBase64 = async (files) => {
    const promises = files.map(file => {
      return new Promise((resolve, reject) => {
        const reader = new FileReader();
        reader.onload = () => resolve({
          name: file.name,
          type: file.type,
          size: file.size,
          data: reader.result
        });
        reader.onerror = reject;
        reader.readAsDataURL(file);
      });
    });
    return Promise.all(promises);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!formData.title || !formData.description) {
      setError('Please fill in all required fields');
      return;
    }

    setLoading(true);
    setError('');

    try {
      let uploadedFiles = [];

      // Step 1: Upload files first
      if (files.length > 0) {
        const fileFormData = new FormData();
        files.forEach(file => {
          fileFormData.append('files', file);
        });

        const uploadResponse = await fetch('http://localhost:5000/api/upload-files', {
          method: 'POST',
          body: fileFormData
        });

        if (!uploadResponse.ok) {
          throw new Error('Failed to upload files');
        }

        const uploadData = await uploadResponse.json();
        uploadedFiles = uploadData.files;
        console.log('✅ Files uploaded:', uploadedFiles);
      }

      // Step 2: Prepare email with file info
      let fileDetails = 'No attachments';
      if (uploadedFiles.length > 0) {
        fileDetails = uploadedFiles.map(f => 
          `${f.original_name} (${(f.size / 1024).toFixed(1)}KB)`
        ).join(', ');
      }

      const templateParams = {
        feedback_title: formData.title || 'No Title',
        feedback_type: feedbackTypes.find(t => t.value === formData.type)?.label || formData.type,
        feedback_priority: priorityLevels.find(p => p.value === formData.priority)?.label || formData.priority,
        feedback_description: formData.description || 'No description provided',
        user_name: currentUser?.displayName || 'Anonymous',
        user_email: currentUser?.email || 'Not provided',
        submission_time: new Date().toLocaleString('en-US', { 
          dateStyle: 'medium', 
          timeStyle: 'short' 
        }),
        attachment_count: uploadedFiles.length.toString(),
        file_names: fileDetails,
        to_email: 'animeshmohanty59@gmail.com'
      };

      // Step 3: Send email notification
      await emailjs.send(
        process.env.REACT_APP_EMAILJS_SERVICE_ID,
        process.env.REACT_APP_EMAILJS_FEEDBACK_TEMPLATE_ID || 'feedback_template',
        templateParams,
        process.env.REACT_APP_EMAILJS_PUBLIC_KEY
      );

      console.log('✅ Email sent');

      // Step 4: Save feedback to database
      const response = await fetch('http://localhost:5000/api/feedback', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          email: currentUser?.email || 'Anonymous',
          title: formData.title,
          type: formData.type,
          priority: formData.priority,
          message: formData.description,
          uploaded_files: uploadedFiles
        })
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || 'Failed to save feedback');
      }

      console.log('✅ Feedback saved');

      setSuccess(true);
      setTimeout(() => {
        onClose();
        setSuccess(false);
        setFormData({ title: '', type: 'bug', priority: 'medium', description: '' });
        setFiles([]);
      }, 2000);

    } catch (err) {
      console.error('❌ Feedback submission error:', err);
      setError('Failed to submit feedback: ' + err.message);
    } finally {
      setLoading(false);
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black/80 backdrop-blur-sm flex items-center justify-center z-50 p-4">
      <div className="bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 border border-purple-500/30 rounded-2xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
        {/* Header */}
        <div className="sticky top-0 bg-black/50 backdrop-blur-sm border-b border-purple-500/20 p-6 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <MessageSquare className="w-6 h-6 text-purple-400" />
            <h2 className="text-2xl font-bold text-white">Send Feedback</h2>
          </div>
          <button
            onClick={onClose}
            className="p-2 hover:bg-white/10 rounded-lg transition-colors"
          >
            <X className="w-5 h-5 text-gray-400" />
          </button>
        </div>

        {/* Form */}
        <form onSubmit={handleSubmit} className="p-6 space-y-6">
          {/* Success Message */}
          {success && (
            <div className="p-4 bg-green-500/10 border border-green-500/30 rounded-lg flex items-center gap-3">
              <CheckCircle className="w-5 h-5 text-green-400" />
              <p className="text-green-300">Feedback submitted successfully! Thank you!</p>
            </div>
          )}

          {/* Error Message */}
          {error && (
            <div className="p-4 bg-red-500/10 border border-red-500/30 rounded-lg flex items-center gap-3">
              <AlertCircle className="w-5 h-5 text-red-400" />
              <p className="text-red-300">{error}</p>
            </div>
          )}

          {/* Title */}
          <div>
            <label className="block text-sm font-medium text-purple-300 mb-2">
              Title <span className="text-red-400">*</span>
            </label>
            <input
              type="text"
              name="title"
              value={formData.title}
              onChange={handleChange}
              className="w-full bg-black/60 text-white border border-purple-500/30 rounded-lg px-4 py-3 focus:outline-none focus:border-purple-500"
              placeholder="Brief summary of your feedback"
              required
            />
          </div>

          {/* Type and Priority */}
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-purple-300 mb-2">Type</label>
              <select
                name="type"
                value={formData.type}
                onChange={handleChange}
                className="w-full bg-black/60 text-white border border-purple-500/30 rounded-lg px-4 py-3 focus:outline-none focus:border-purple-500"
              >
                {feedbackTypes.map(type => (
                  <option key={type.value} value={type.value}>
                    {type.label}
                  </option>
                ))}
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-purple-300 mb-2">Priority</label>
              <select
                name="priority"
                value={formData.priority}
                onChange={handleChange}
                className="w-full bg-black/60 text-white border border-purple-500/30 rounded-lg px-4 py-3 focus:outline-none focus:border-purple-500"
              >
                {priorityLevels.map(priority => (
                  <option key={priority.value} value={priority.value}>
                    {priority.label}
                  </option>
                ))}
              </select>
            </div>
          </div>

          {/* Description */}
          <div>
            <label className="block text-sm font-medium text-purple-300 mb-2">
              Description <span className="text-red-400">*</span>
            </label>
            <textarea
              name="description"
              value={formData.description}
              onChange={handleChange}
              rows={6}
              className="w-full bg-black/60 text-white border border-purple-500/30 rounded-lg px-4 py-3 focus:outline-none focus:border-purple-500 resize-none"
              placeholder="Please provide detailed information about your feedback, bug, or suggestion..."
              required
            />
          </div>

          {/* File Upload */}
          <div>
            <label className="block text-sm font-medium text-purple-300 mb-2">
              Attachments (Optional)
            </label>
            <div className="border-2 border-dashed border-purple-500/30 rounded-lg p-6 text-center hover:border-purple-500/50 transition-colors">
              <input
                type="file"
                id="file-upload"
                multiple
                accept="image/*,video/*"
                onChange={handleFileChange}
                className="hidden"
                disabled={files.length >= 5}
              />
              <label htmlFor="file-upload" className="cursor-pointer">
                <Upload className="w-8 h-8 text-purple-400 mx-auto mb-2" />
                <p className="text-sm text-gray-300 mb-1">
                  Click to upload screenshots or videos
                </p>
                <p className="text-xs text-gray-500">
                  Max 5 files, 10MB each (Images/Videos only)
                </p>
              </label>
            </div>

            {/* File List */}
            {files.length > 0 && (
              <div className="mt-4 space-y-2">
                {files.map((file, index) => (
                  <div
                    key={index}
                    className="flex items-center justify-between bg-black/40 border border-purple-500/20 rounded-lg p-3"
                  >
                    <div className="flex items-center gap-3">
                      {getFileIcon(file)}
                      <div>
                        <p className="text-sm text-white">{file.name}</p>
                        <p className="text-xs text-gray-400">
                          {(file.size / 1024).toFixed(1)} KB
                        </p>
                      </div>
                    </div>
                    <button
                      type="button"
                      onClick={() => removeFile(index)}
                      className="p-1 hover:bg-red-500/20 rounded transition-colors"
                    >
                      <X className="w-4 h-4 text-red-400" />
                    </button>
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* User Info Display */}
          <div className="bg-black/40 border border-purple-500/20 rounded-lg p-4">
            <p className="text-xs text-gray-400 mb-2">Submitting as:</p>
            <div className="flex items-center gap-2">
              <div className="w-8 h-8 bg-purple-500/20 rounded-full flex items-center justify-center">
                <span className="text-sm font-medium text-purple-300">
                  {currentUser?.displayName?.charAt(0) || currentUser?.email?.charAt(0) || 'A'}
                </span>
              </div>
              <div>
                <p className="text-sm text-white">{currentUser?.displayName || 'Anonymous'}</p>
                <p className="text-xs text-gray-400">{currentUser?.email || 'Not logged in'}</p>
              </div>
            </div>
          </div>

          {/* Submit Button */}
          <button
            type="submit"
            disabled={loading || success}
            className="w-full bg-purple-600 hover:bg-purple-700 disabled:bg-gray-600 text-white py-3 rounded-lg font-medium transition-colors flex items-center justify-center gap-2"
          >
            {loading ? (
              <>
                <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin" />
                Sending...
              </>
            ) : success ? (
              <>
                <CheckCircle className="w-5 h-5" />
                Sent!
              </>
            ) : (
              <>
                <Send className="w-5 h-5" />
                Submit Feedback
              </>
            )}
          </button>
        </form>
      </div>
    </div>
  );
}