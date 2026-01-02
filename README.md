# CHAKRAVYUH 1.0 - OSINT Platform Setup Guide

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Node.js 16+
- npm or yarn

### 1. Setup

# Do Ctrl + ` To open Terminal
In Terminal Do: 
```bash
pip install -r requirements.txt
```

#### 2. Configure Environment Variables

Fill up `.env` file:

```bash
# AI Service API Keys (Add at least ONE)
# The system will automatically use the first available key

# Groq API (Recommended - Fast & Free)
# Get it from: https://console.groq.com/
GROQ_API_KEY=your_groq_api_key_here

# Google Gemini API (Free tier available)
# Get it from: https://ai.google.dev/
GEMINI_API_KEY=your_gemini_api_here

# Anthropic Claude API (Paid but powerful)
# Get it from: https://console.anthropic.com/
ANTHROPIC_API_KEY=your_anthropic_api_key_here

# Hugging Face API (Free)
# Get it from: https://huggingface.co/settings/tokens
HUGGINGFACE_API_KEY=your_huggingface_api_key_here

# GitHub Personal Access Token (Optional but recommended)
# Get it from: https://github.com/settings/tokens
GITHUB_TOKEN=your_github_token_here

# HaveIBeenPwned API Key (Required for breach checking)
# Get it from: https://haveibeenpwned.com/API/Key
HIBP_API_KEY=your_hibp_api_key_here
```

**How to get API keys:**

1. **AI API Key:**
   - Visit: https://console.anthropic.com/, https://console.groq.com/, https://ai.google.dev/, https://huggingface.co/settings/tokens
   - Sign up and generate an API key
   - This is REQUIRED for AI analysis
   - You can add one or all Ai api which will work first it will use that

2. **GitHub Token:**
   - Visit: https://github.com/settings/tokens
   - Generate a Personal Access Token
   - Select scopes: `public_repo`, `read:user`

3. **HaveIBeenPwned API Key:**
   - Visit: https://haveibeenpwned.com/API/Key
   - Purchase an API key (one-time fee)

#### 4. Start Backend Services

```bash
# Terminal 1 - Main OSINT API (port 5000)
python app.py
```

### 3. Frontend Setup

#### 1. Install Dependencies
```bash
# Optional if VS-CODE terminal have no access with CMD
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process
# Install npm packages
npm install lucide-react
npm install -D tailwindcss postcss autoprefixer
npx tailwindcss init -p
npm install react-icons
```

#### 2. Start Frontend
```bash
npm start
```

The application will open at `http://localhost:3000`

## 🧪 Testing the Application

### Test Multi-Modal OSINT Analysis

1. Enter a target (username or email): `torvalds` or `test@example.com`
2. Select platforms: GitHub, Twitter, LinkedIn, Reddit
3. Click "Analyze"
4. Watch real-time logs
5. View results with risk scores and findings

### Test Image Geolocation

1. Switch to "Visual Intelligence" tab
2. Click "Browse Files" or drag & drop an image
3. The service will:
   - Extract EXIF GPS data (if available)
   - Analyze visual features with Claude Vision
   - Identify landmarks and text
   - Provide location estimate with confidence

**Test with:**
- Photos with GPS data
- Street photos with signs
- Landmark photos
- Screenshots (no EXIF)

### Test API Endpoints Directly

**OSINT Analysis:**
```bash
curl -X POST http://localhost:5000/api/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "target": "torvalds",
    "platforms": ["github", "reddit"]
  }'
```

**Health Check:**
```bash
curl http://localhost:5000/api/health
curl http://localhost:5001/api/geolocation/health
```

**Image Geolocation:**
```bash
curl -X POST http://localhost:5001/api/geolocation/image \
  -F "file=@/path/to/image.jpg"
```

**Video Geolocation:**
```bash
curl -X POST http://localhost:5001/api/geolocation/video \
  -F "file=@/path/to/video.mp4" \
  -F "num_frames=5"
```

## 📁 Project Structure

```
hackathon-osint/
├── cursors/
│   ├── appstarting-ezgif.com-ani-to-gif-converter.gif
│   ├── ImageToStl.com_arrow.png
│   ├── ImageToStl.com_crosshair.png
│   ├── ImageToStl.com_hand.png
│   ├── ImageToStl.com_help.png
│   ├── ImageToStl.com_ibeam.png
│   ├── ImageToStl.com_no.png
│   ├── nwpen.png
│   ├── person.png
│   ├── pin.png
│   ├── sizeall.png
│   ├── sizenesw.png
│   ├── sizens.png
│   ├── sizenwse.png
│   ├── sizewe.png
│   ├── uparrow.png
│   └── wait-ezgif.com-ani-to-gif-converter.gif
├── src/
│   ├── App.css                    
│   ├── App.js
│   ├── App.test.js
│   ├── ChatAssistant.js 
│   ├── index.css
│   ├── index.js
│   ├── logo.svg
│   ├── OSINTDashboard.js
│   ├── reportWebVitals.js                       
│   ├── setupTests.js
│   ├── SkeletonCard
│   ├── SnowEffect.js
│   └── VisualIntelligence.js
│   ├── SkeletonCard.js
├── .env
├── app.py
├── visual.py
├── package-lock.json
├── package.json
├── postcssconfig.js
├── README.md
├── requirements.txt
└── tailwind.config.js
```

## 🔧 Troubleshooting

### Backend Issues

**Error: "Module not found"**
```bash
# Make sure virtual environment is activated
source venv/bin/activate  # macOS/Linux
venv\Scripts\activate     # Windows

# Reinstall dependencies
pip install -r requirements.txt
```

**Error: "API key not configured"**
- Check your `.env` file exists in the backend directory
- Verify the API key format is correct
- Restart the Python servers after adding keys

**CORS Errors:**
- Ensure `flask-cors` is installed
- Check that both services are running
- Frontend should be on port 3000, backends on 5000 and 5001

### Frontend Issues

**Custom cursors not showing:**
- Verify files are in `public/cursors/`
- Check browser console for 404 errors
- Clear browser cache
- Check file names match exactly (case-sensitive)

**API connection failed:**
- Ensure backend services are running
- Check `API_BASE_URL` in `OSINTDashboard.js` matches your setup
- Check browser console for CORS errors

## 🎯 Features Overview

### Multi-Modal OSINT Fusion
- Collects data from multiple platforms simultaneously
- GitHub: repos, commits, profile data
- Reddit: user karma, post history
- Twitter/X: profile information
- HaveIBeenPwned: breach checking
- AI-powered analysis and correlation
- Real-time logging of collection process

### Visual Intelligence
- EXIF metadata extraction
- GPS coordinate parsing
- Claude Vision API analysis
- Landmark recognition
- Text detection (signs, plates)
- Shadow and environmental analysis
- Video frame extraction and analysis

### Risk Assessment
- Automated risk scoring (0-10)
- Exposure classification (Critical/High/Medium/Low)
- Cross-platform correlation
- AI-generated recommendations
- Detailed finding breakdown

## 🚨 Important Notes

1. **API Rate Limits:** Be mindful of API rate limits, especially for GitHub and HaveIBeenPwned
2. **Costs:** Anthropic Claude API is pay-per-use. Monitor your usage.
3. **Legal:** Only use for legitimate OSINT research and with proper authorization
4. **Privacy:** Handle collected data responsibly and securely
5. **Twitter/X:** Full functionality requires Twitter API access (not included in basic setup)

## 📝 Demo Data

For testing without real API calls, the frontend has mock data built-in. Simply run analysis without backend services to see the UI in action.

## 🎓 Hackathon Presentation Tips

1. **Start with GitHub analysis** - Shows immediate results
2. **Demonstrate image geolocation** - Most impressive feature
3. **Show real-time logs** - Demonstrates processing flow
4. **Highlight AI analysis** - Key differentiator
5. **Show risk assessment** - Practical application

## 🆘 Support

For issues during the hackathon:
1. Check this guide first
2. Review error messages in browser console and terminal
3. Verify all dependencies are installed
4. Ensure API keys are configured correctly

Good luck with CHAKRAVYUH 1.0! 🎯
