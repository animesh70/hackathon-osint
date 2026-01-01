import React, { useState, useEffect, useRef } from 'react';
import { MessageCircle, X, Send, Minimize2, Maximize2, Settings, User } from 'lucide-react';

// HERE ADDED - Added backgroundTheme and setBackgroundTheme as props
const ChatAssistant = ({ backendStatus, currentTab, analysisResults, backgroundTheme, setBackgroundTheme }) => {
  const [isOpen, setIsOpen] = useState(false);
  const [isMinimized, setIsMinimized] = useState(false);
  const [messages, setMessages] = useState([]);
  const [inputValue, setInputValue] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const [selectedAssistant, setSelectedAssistant] = useState('sparke'); // 'sparke' or 'eve'
  const [showSettings, setShowSettings] = useState(false);
  const [unreadCount, setUnreadCount] = useState(0);
  // HERE REMOVED - Removed local backgroundTheme state (now using prop from parent)
  
  const messagesEndRef = useRef(null);
  const inputRef = useRef(null);

  const assistants = {
    sparke: {
      name: 'Sparke',
      avatar: '/assets/Sparke.jpeg',
      gender: 'male',
      greeting: 'Hi, I am Sparke! How can I help you today?',
      color: 'from-blue-500 to-cyan-500'
    },
    eve: {
      name: 'Eve',
      avatar: '/assets/Eve.jpeg',
      gender: 'female',
      greeting: 'Hi, I am Eve! How can I help you today?',
      color: 'from-purple-500 to-pink-500'
    }
  };

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

  const currentAssistant = assistants[selectedAssistant];

  // Knowledge Base - Professional responses
  const knowledgeBase = {
    greetings: [
      'hello', 'hi', 'hey', 'greetings', 'good morning', 'good afternoon', 'good evening'
    ],
    
    responses: {
      // Getting Started
      'how to analyze': {
        response: `To perform an OSINT analysis:

1. Navigate to the "Multi-Modal Fusion" tab
2. Enter your target identifier (username, email, or profile URL)
3. Select relevant platforms from the available options
4. Click the "Analyze" button to initiate the scan

The system will collect data from selected platforms and provide a comprehensive risk assessment.`,
        suggestions: ['What platforms should I choose?', 'How long does analysis take?', 'What is risk score?']
      },
      
      'platforms': {
        response: `Available OSINT platforms and their use cases:

• GitHub - Developer activity, code repositories, contribution patterns
• Twitter/X - Public posts, social connections, engagement metrics
• LinkedIn - Professional information, employment history, skills
• Reddit - Community participation, interests, posting patterns
• HaveIBeenPwned - Data breach verification, credential exposure

Select platforms based on your target's likely digital footprint.`,
        suggestions: ['How to analyze?', 'What is OSINT?', 'Understanding risk scores']
      },
      
      'risk score': {
        response: `Risk Score Classification:

CRITICAL (8.5-10.0):
- Immediate exploitation risk
- Exposed credentials or passwords
- Active data breaches
- Requires urgent action

HIGH (6.5-8.4):
- Significant exposure potential
- Personal identifiers exposed
- Multiple platform correlations

MEDIUM (4.0-6.4):
- Moderate privacy concerns
- Behavioral patterns identified
- Contact details visible

LOW (0-3.9):
- Minimal exposure
- Public information only
- Standard social media presence`,
        suggestions: ['How to reduce risk?', 'What is data breach?', 'Privacy protection']
      },
      
      'backend offline': {
        response: `Backend Connection Issue - Resolution Steps:

1. Open terminal in your project directory
2. Execute: python app.py
3. Wait for confirmation message: "Running on http://localhost:5000"
4. Refresh the browser page
5. Verify the status indicator shows "Backend Online"

If issues persist, verify:
- Python dependencies are installed (requirements.txt)
- Port 5000 is not in use by another application
- Flask server is running without errors`,
        suggestions: ['API key setup', 'How to analyze?', 'Technical support']
      },
      
      'osint': {
        response: `OSINT (Open Source Intelligence):

OSINT refers to the collection and analysis of publicly available information from various sources including:

• Social media platforms
• Public records and databases
• Search engines and web archives
• Government publications
• Academic resources
• News and media outlets

This platform automates OSINT collection and provides intelligent risk assessment of digital exposure.`,
        suggestions: ['Legal considerations', 'Privacy protection', 'How to analyze?']
      },
      
      'image analysis': {
        response: `Visual Intelligence Capabilities:

EXIF Metadata Extraction:
• GPS coordinates from geotagged images
• Camera make, model, and settings
• Timestamp and date information
• Software processing details

AI-Powered Analysis:
• Landmark recognition
• Environmental clue detection
• Text and sign extraction
• Shadow analysis for time estimation
• Architectural style identification

Upload images or videos in the "Visual Intelligence" tab for comprehensive geolocation analysis.`,
        suggestions: ['How to upload?', 'Supported formats', 'Geolocation accuracy']
      },
      
      'api keys': {
        response: `API Configuration:

Required API keys should be configured in the .env file:

GROQ_API_KEY - For Groq AI analysis
GEMINI_API_KEY - For Google Gemini AI
ANTHROPIC_API_KEY - For Claude AI
GITHUB_TOKEN - For GitHub data collection
HIBP_API_KEY - For HaveIBeenPwned breach checks

At least one AI service API key is recommended for enhanced analysis capabilities. The system will automatically select the available AI service.`,
        suggestions: ['Backend offline?', 'How to analyze?', 'Technical support']
      },
      
      'privacy': {
        response: `Privacy Protection Recommendations:

Immediate Actions:
1. Enable two-factor authentication on all accounts
2. Change passwords for any breached credentials
3. Review and restrict social media privacy settings
4. Disable location sharing on mobile devices
5. Use unique email addresses for different services

Long-term Strategies:
• Regular security audits of online presence
• Password manager for unique, strong passwords
• VPN usage for sensitive activities
• Periodic breach monitoring
• Minimize data sharing on public platforms`,
        suggestions: ['Risk score meaning', 'Data breaches', 'Security best practices']
      },
      
      'legal': {
        response: `Legal and Ethical Considerations:

OSINT analysis must comply with:

• Terms of Service of analyzed platforms
• Data protection regulations (GDPR, CCPA, etc.)
• Privacy laws in relevant jurisdictions
• Ethical guidelines for information gathering

Permissible Use Cases:
- Security assessment of personal digital footprint
- Authorized corporate security audits
- Research with proper consent
- Cybersecurity threat analysis

This tool is intended for legitimate security assessment and educational purposes only.`,
        suggestions: ['Privacy protection', 'What is OSINT?', 'Best practices']
      },
      
      'keyboard shortcuts': {
        response: `Keyboard Shortcuts:

Global:
• Ctrl/Cmd + K - Open command palette
• Escape - Close dialogs/panels
• Tab - Navigate between fields

Analysis:
• Enter - Execute analysis (when input focused)
• Ctrl/Cmd + R - Refresh results

Navigation:
• 1, 2, 3 - Switch between main tabs
• Ctrl/Cmd + / - Toggle this assistant

Additional shortcuts will be indicated throughout the interface.`,
        suggestions: ['How to analyze?', 'Features overview', 'Tips and tricks']
      }
    }
  };

  // Initialize with greeting
  useEffect(() => {
    if (messages.length === 0) {
      const greeting = {
        id: Date.now(),
        type: 'ai',
        content: currentAssistant.greeting,
        timestamp: new Date(),
        suggestions: ['How to analyze?', 'What is OSINT?', 'Show keyboard shortcuts', 'change Background colour']
      };
      setMessages([greeting]);
    }
  }, [selectedAssistant]);

  // Auto-scroll to bottom
  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // Track unread messages
  useEffect(() => {
    if (!isOpen && messages.length > 1) {
      setUnreadCount(prev => prev + 1);
    }
  }, [messages, isOpen]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const handleOpen = () => {
    setIsOpen(true);
    setUnreadCount(0);
    setTimeout(() => inputRef.current?.focus(), 100);
  };

  const handleClose = () => {
    setIsOpen(false);
  };

  const handleSendMessage = async () => {
    if (!inputValue.trim()) return;

    const userMessage = {
      id: Date.now(),
      type: 'user',
      content: inputValue,
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMessage]);
    setInputValue('');
    setIsTyping(true);

    // Simulate AI thinking time
    setTimeout(() => {
      const response = generateResponse(inputValue);
      const aiMessage = {
        id: Date.now() + 1,
        type: 'ai',
        content: response.content,
        timestamp: new Date(),
        suggestions: response.suggestions
      };
      setMessages(prev => [...prev, aiMessage]);
      setIsTyping(false);
    }, 1000 + Math.random() * 1000);
  };

  const generateResponse = (query) => {
    const lowerQuery = query.toLowerCase().trim();

    if (lowerQuery.includes('change background') || lowerQuery.includes('background')) {
      return {
        content: 'Sure! Please choose one of the following backgrounds:',
        suggestions: ['Dark Mode', 'Light Mode', 'Mint Breeze', 'Sunset Peach', 'Misty Blue', 'Desert Sand', 'Lavender Dream', 'Twilight', 'Aurora', 'Forest Night', 'Deep Night', 'Chocolate']
      };
    }

    // Context-aware responses
    if (backendStatus?.status === 'offline' && (lowerQuery.includes('not working') || lowerQuery.includes('offline') || lowerQuery.includes('error'))) {
      return knowledgeBase.responses['backend offline'];
    }

    // Check greetings
    if (knowledgeBase.greetings.some(greeting => lowerQuery.includes(greeting))) {
      return {
        content: `${currentAssistant.greeting}\n\nI can assist you with:
• Getting started with OSINT analysis
• Understanding risk assessments
• Platform selection guidance
• Image and video geolocation
• Troubleshooting and support

What would you like to know?`,
        suggestions: ['How to analyze?', 'What is OSINT?', 'Risk score meaning']
      };
    }

    // Match against knowledge base
    for (const [key, value] of Object.entries(knowledgeBase.responses)) {
      if (lowerQuery.includes(key) || lowerQuery.includes(key.replace(/\s+/g, ''))) {
        return {
          content: value.response,
          suggestions: value.suggestions
        };
      }
    }

    // Specific keyword matching
    if (lowerQuery.includes('upload') || lowerQuery.includes('image') || lowerQuery.includes('video')) {
      return knowledgeBase.responses['image analysis'];
    }

    if (lowerQuery.includes('breach') || lowerQuery.includes('pwned') || lowerQuery.includes('password')) {
      return {
        content: `Data Breach Assessment:

HaveIBeenPwned integration checks if your email appears in known data breaches. When breaches are detected:

1. Immediately change passwords for affected accounts
2. Enable two-factor authentication
3. Monitor for suspicious activity
4. Use unique passwords for each service
5. Consider using a password manager

Critical breaches require immediate action to prevent account takeover.`,
        suggestions: ['Privacy protection', 'Risk score meaning', 'How to reduce risk?']
      };
    }

    if (lowerQuery.includes('export') || lowerQuery.includes('save') || lowerQuery.includes('download')) {
      return {
        content: `Data Export Functionality:

Analysis results can be exported in multiple formats:

• JSON - Full structured data for programmatic use
• CSV - Tabular data for spreadsheet analysis
• PDF - Professional reports (coming soon)

Export options will be available in the results panel after completing an analysis.`,
        suggestions: ['How to analyze?', 'Understanding results', 'Features overview']
      };
    }

    // Default response with context
    let contextInfo = '';
    if (currentTab === 'visual') {
      contextInfo = '\n\nI notice you\'re in the Visual Intelligence section. You can upload images or videos for geolocation analysis.';
    } else if (currentTab === 'risk' && !analysisResults) {
      contextInfo = '\n\nI notice you\'re in the Risk Assessment section. Please perform an analysis first in the Multi-Modal Fusion tab.';
    }

    return {
      content: `I understand you're asking about "${query}".${contextInfo}

I can help you with:
• OSINT analysis procedures
• Platform selection guidance
• Risk assessment interpretation
• Image/video geolocation
• Troubleshooting technical issues
• Privacy and security recommendations

Could you please rephrase your question or select from the suggestions below?`,
      suggestions: ['How to analyze?', 'What is OSINT?', 'Risk score meaning', 'Backend offline?']
    };
  };

  // HERE ADDED - Using setBackgroundTheme from props to update parent state
  const handleSuggestionClick = (suggestion) => {
    if (backgrounds[suggestion]) {
      setBackgroundTheme(suggestion); // change background using parent's setState
      setMessages(prev => [...prev, {
        id: Date.now(),
        type: 'ai',
        content: `Background changed to ${suggestion}!`,
        timestamp: new Date()
      }]);
      return; // do not send as normal message
    }

    // Otherwise, treat as normal input
    setInputValue(suggestion);
    setTimeout(() => handleSendMessage(), 100);
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  const switchAssistant = (assistant) => {
    setSelectedAssistant(assistant);
    setShowSettings(false);
    setMessages([]);
  };

  const formatTime = (date) => {
  if (!date) return ''; // or return '--:--' if you want a placeholder
  return new Date(date).toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' });
};

  if (!isOpen) {
    return (
      <button
        onClick={handleOpen}
        className="fixed bottom-6 right-6 z-50 group"
        aria-label="Open chat assistant"
      >
        <div className="relative">
          {/* Glow effect */}
          <div className={`absolute inset-0 bg-gradient-to-r ${currentAssistant.color} rounded-full blur-xl opacity-50 group-hover:opacity-75 transition-opacity animate-pulse`}></div>
          
          {/* Button */}
          <div className={`relative w-16 h-16 bg-gradient-to-r ${currentAssistant.color} rounded-full flex items-center justify-center shadow-2xl group-hover:scale-110 transition-transform cursor-pointer`}>
            <MessageCircle className="w-8 h-8 text-white" />
          </div>

          {/* Unread badge */}
          {unreadCount > 0 && (
            <div className="absolute -top-1 -right-1 w-6 h-6 bg-red-500 rounded-full flex items-center justify-center text-xs font-bold text-white animate-bounce">
              {unreadCount}
            </div>
          )}
        </div>
      </button>
    );
  }

  return (
    <div className={`fixed ${isMinimized ? 'bottom-6 right-6' : 'bottom-6 right-6'} z-50 transition-all duration-300`}>
      <div className={`bg-black/95 backdrop-blur-xl border border-purple-500/30 rounded-2xl shadow-2xl overflow-hidden ${isMinimized ? 'w-80' : 'w-[400px] h-[600px]'} flex flex-col`}>
        
        {/* Header */}
        <div className={`bg-gradient-to-r ${currentAssistant.color} p-4 flex items-center justify-between`}>
          <div className="flex items-center gap-3">
            <div className="relative">
              <img 
                src={currentAssistant.avatar} 
                alt={currentAssistant.name}
                className="w-10 h-10 rounded-full border-2 border-white/30 object-cover"
                onError={(e) => {
                  e.target.src = `data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'%3E%3Crect fill='%23667' width='100' height='100'/%3E%3Ctext x='50' y='55' font-size='50' text-anchor='middle' fill='%23fff'%3E${currentAssistant.name[0]}%3C/text%3E%3C/svg%3E`;
                }}
              />
              <div className="absolute bottom-0 right-0 w-3 h-3 bg-green-400 rounded-full border-2 border-white"></div>
            </div>
            <div>
              <h3 className="font-semibold text-white">{currentAssistant.name}</h3>
              <p className="text-xs text-white/80">OSINT Assistant</p>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <button
              onClick={() => setShowSettings(!showSettings)}
              className="p-2 hover:bg-white/10 rounded-lg transition-colors"
              aria-label="Settings"
            >
              <Settings className="w-4 h-4 text-white" />
            </button>
            <button
              onClick={() => setIsMinimized(!isMinimized)}
              className="p-2 hover:bg-white/10 rounded-lg transition-colors"
              aria-label={isMinimized ? "Maximize" : "Minimize"}
            >
              {isMinimized ? <Maximize2 className="w-4 h-4 text-white" /> : <Minimize2 className="w-4 h-4 text-white" />}
            </button>
            <button
              onClick={handleClose}
              className="p-2 hover:bg-white/10 rounded-lg transition-colors"
              aria-label="Close"
            >
              <X className="w-4 h-4 text-white" />
            </button>
          </div>
        </div>

        {/* Settings Panel */}
        {showSettings && !isMinimized && (
          <div className="bg-purple-500/10 border-b border-purple-500/20 p-4">
            <p className="text-sm text-purple-300 mb-3 font-medium">Choose Your Assistant:</p>
            <div className="grid grid-cols-2 gap-3">
              <button
                onClick={() => switchAssistant('sparke')}
                className={`p-3 rounded-lg border-2 transition-all ${
                  selectedAssistant === 'sparke' 
                    ? 'border-blue-500 bg-blue-500/20' 
                    : 'border-white/10 bg-white/5 hover:bg-white/10'
                }`}
              >
                <img 
                  src={assistants.sparke.avatar} 
                  alt="Sparke"
                  className="w-12 h-12 rounded-full mx-auto mb-2 object-cover"
                  onError={(e) => {
                    e.target.src = `data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'%3E%3Crect fill='%233b82f6' width='100' height='100'/%3E%3Ctext x='50' y='55' font-size='50' text-anchor='middle' fill='%23fff'%3ES%3C/text%3E%3C/svg%3E`;
                  }}
                />
                <p className="text-sm font-medium text-white">Sparke</p>
                <p className="text-xs text-gray-400">Male Assistant</p>
              </button>
              <button
                onClick={() => switchAssistant('eve')}
                className={`p-3 rounded-lg border-2 transition-all ${
                  selectedAssistant === 'eve' 
                    ? 'border-purple-500 bg-purple-500/20' 
                    : 'border-white/10 bg-white/5 hover:bg-white/10'
                }`}
              >
                <img 
                  src={assistants.eve.avatar} 
                  alt="Eve"
                  className="w-12 h-12 rounded-full mx-auto mb-2 object-cover"
                  onError={(e) => {
                    e.target.src = `data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'%3E%3Crect fill='%23a855f7' width='100' height='100'/%3E%3Ctext x='50' y='55' font-size='50' text-anchor='middle' fill='%23fff'%3EE%3C/text%3E%3C/svg%3E`;
                  }}
                />
                <p className="text-sm font-medium text-white">Eve</p>
                <p className="text-xs text-gray-400">Female Assistant</p>
              </button>
            </div>
          </div>
        )}

        {!isMinimized && (
          <>
            {/* Messages */}
            <div className="flex-1 overflow-y-auto p-4 space-y-4 bg-gradient-to-b from-black/50 to-black/30">
              {messages.map((message) => (
                <div key={message.id} className={`flex ${message.type === 'user' ? 'justify-end' : 'justify-start'} animate-in fade-in slide-in-from-bottom-2`}>
                  <div className={`flex gap-2 max-w-[85%] ${message.type === 'user' ? 'flex-row-reverse' : 'flex-row'}`}>
                    {message.type === 'ai' && (
                      <img 
                        src={currentAssistant.avatar} 
                        alt={currentAssistant.name}
                        className="w-8 h-8 rounded-full flex-shrink-0 object-cover"
                        onError={(e) => {
                          e.target.src = `data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'%3E%3Crect fill='%23667' width='100' height='100'/%3E%3Ctext x='50' y='55' font-size='50' text-anchor='middle' fill='%23fff'%3E${currentAssistant.name[0]}%3C/text%3E%3C/svg%3E`;
                        }}
                      />
                    )}
                    {message.type === 'user' && (
                      <div className="w-8 h-8 rounded-full bg-purple-600 flex items-center justify-center flex-shrink-0">
                        <User className="w-5 h-5 text-white" />
                      </div>
                    )}
                    <div>
                      <div className={`rounded-2xl px-4 py-3 ${
                        message.type === 'user' 
                          ? 'bg-gradient-to-r from-purple-600 to-blue-600 text-white' 
                          : 'bg-white/5 border border-purple-500/20 text-gray-100'
                      }`}>
                        <p className="text-sm whitespace-pre-line leading-relaxed">{message.content}</p>
                      </div>
                      <p className="text-xs text-gray-500 mt-1 px-1">{formatTime(message.timestamp)}</p>
                      
                      {/* Suggestions */}
                      {message.type === 'ai' && message.suggestions && (
                        <div className="flex flex-wrap gap-2 mt-3">
                          {message.suggestions.map((suggestion, idx) => (
                            <button
                              key={idx}
                              onClick={() => handleSuggestionClick(suggestion)}
                              className="px-3 py-1.5 bg-purple-500/20 hover:bg-purple-500/30 border border-purple-500/30 rounded-full text-xs text-purple-300 transition-colors"
                            >
                              {suggestion}
                            </button>
                          ))}
                        </div>
                      )}
                    </div>
                  </div>
                </div>
              ))}

              {/* Typing indicator */}
              {isTyping && (
                <div className="flex justify-start animate-in fade-in">
                  <div className="flex gap-2 items-end">
                    <img 
                      src={currentAssistant.avatar} 
                      alt={currentAssistant.name}
                      className="w-8 h-8 rounded-full object-cover"
                      onError={(e) => {
                        e.target.src = `data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'%3E%3Crect fill='%23667' width='100' height='100'/%3E%3Ctext x='50' y='55' font-size='50' text-anchor='middle' fill='%23fff'%3E${currentAssistant.name[0]}%3C/text%3E%3C/svg%3E`;
                      }}
                    />
                    <div className="bg-white/5 border border-purple-500/20 rounded-2xl px-4 py-3">
                      <div className="flex gap-1">
                        <div className="w-2 h-2 bg-purple-400 rounded-full animate-bounce" style={{ animationDelay: '0ms' }}></div>
                        <div className="w-2 h-2 bg-purple-400 rounded-full animate-bounce" style={{ animationDelay: '150ms' }}></div>
                        <div className="w-2 h-2 bg-purple-400 rounded-full animate-bounce" style={{ animationDelay: '300ms' }}></div>
                      </div>
                    </div>
                  </div>
                </div>
              )}

              <div ref={messagesEndRef} />
            </div>

            {/* Input */}
            <div className="border-t border-purple-500/20 p-4 bg-black/50">
              <div className="flex gap-2">
                <input
                  ref={inputRef}
                  type="text"
                  value={inputValue}
                  onChange={(e) => setInputValue(e.target.value)}
                  onKeyPress={handleKeyPress}
                  placeholder="Type your question..."
                  className="flex-1 bg-white/5 border border-purple-500/30 rounded-lg px-4 py-3 text-sm focus:outline-none focus:border-purple-500 placeholder-gray-500"
                />
                <button
                  onClick={handleSendMessage}
                  disabled={!inputValue.trim() || isTyping}
                  className={`p-3 rounded-lg transition-all ${
                    inputValue.trim() && !isTyping
                      ? `bg-gradient-to-r ${currentAssistant.color} hover:opacity-90 shadow-lg`
                      : 'bg-gray-700 cursor-not-allowed'
                  }`}
                  aria-label="Send message"
                >
                  <Send className="w-5 h-5 text-white" />
                </button>
              </div>
              <p className="text-xs text-gray-500 mt-2 text-center">
                Press Enter to send • {currentAssistant.name} is here to help
              </p>
            </div>
          </>
        )}

        {isMinimized && (
          <div className="p-4 text-center">
            <p className="text-sm text-gray-400">Chat minimized</p>
            <button
              onClick={() => setIsMinimized(false)}
              className="text-xs text-purple-400 hover:text-purple-300 mt-2"
            >
              Click to expand
            </button>
          </div>
        )}
      </div>
    </div>
  );
};

export default ChatAssistant;