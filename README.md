<<<<<<< HEAD
# 🧸 OSINT Location Visualizer - Magic Map

An ethical OSINT (Open Source Intelligence) tool for visualizing publicly available location data from social media posts. This tool helps users understand their digital footprint and location exposure.

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![Flask](https://img.shields.io/badge/Flask-3.0-green.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

## 🎯 Features

### Four Core Visualizations

- 🔴 **Exact Pin Locations** - Posts with GPS metadata (High Confidence)
- 🟡 **Approximate Regions** - Locations inferred from image content (Medium/Low Confidence)
- 🟢 **Activity Clusters** - Multiple posts from the same geographic area
- ➖ **Movement Paths** - Inferred travel patterns between posts over time

### Additional Features

- 📅 **Timeline View** - Chronological visualization of all posts
- 💾 **Data Export** - Export analysis results as JSON
- 📊 **Statistics Dashboard** - Summary of analysis metrics
- 🗺️ **Interactive Map** - Zoom, pan, and click for details
- 🎨 **Responsive Design** - Works on desktop, tablet, and mobile

## 📋 Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- Modern web browser (Chrome, Firefox, Safari, Edge)

## 🚀 Quick Start

### 1. Clone or Download the Project
```bash
git clone https://github.com/yourusername/osint-location-visualizer.git
cd osint-location-visualizer
```

Or download and extract the ZIP file.

### 2. Create Virtual Environment
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate

# On macOS/Linux:
source venv/bin/activate
```

### 3. Install Dependencies
=======
# CHAKRAVYUH 1.0 - OSINT Platform Setup Guide

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Node.js 16+
- npm or yarn

### 1. Setup

# Do Ctrl + ` To open Terminal
In Terminal Do: 
>>>>>>> d46736adb11c5fcbcb2b72c57efef6f8ae7f0354
```bash
pip install -r requirements.txt
```

<<<<<<< HEAD
### 4. Set Up Configuration (Optional)
```bash
# Copy example environment file
cp .env.example .env

# Edit .env with your preferred settings (optional for demo mode)
```

### 5. Run the Application
```bash
python app.py
```

### 6. Open in Browser

Navigate to: `http://localhost:5000`

You should see the Magic Map interface!

## 📁 Project Structure
```
osint-location-visualizer/
│
├── app.py                          # Main Flask application
├── config.py                       # Configuration settings
├── requirements.txt                # Python dependencies
├── README.md                       # This file
├── .env.example                    # Environment variables template
├── .gitignore                      # Git ignore rules
│
├── models/                         # Data models
│   ├── __init__.py
│   ├── post.py                     # Post data model
│   └── location.py                 # Location data model
│
├── services/                       # Business logic
│   ├── __init__.py
│   ├── instagram_analyzer.py      # Instagram data analysis
│   ├── location_inference.py      # AI location inference
│   └── geo_utils.py                # Geographic utilities
│
├── api/                            # API endpoints
│   ├── __init__.py
│   └── routes.py                   # RESTful API routes
│
├── static/                         # Frontend assets
│   ├── css/
│   │   ├── style.css               # Main styles
│   │   └── responsive.css          # Responsive styles
│   ├── js/
│   │   ├── map.js                  # Map functionality
│   │   ├── markers.js              # Marker management
│   │   ├── ui.js                   # UI interactions
│   │   └── api-client.js           # API communication
│   └── images/
│       └── logo.png                # Project logo (optional)
│
├── templates/                      # HTML templates
│   ├── base.html                   # Base template
│   └── index.html                  # Main page
│
├── data/                           # Data storage
│   ├── demo_posts.json             # Demo data
│   └── analysis_results/           # Saved analysis results
│
├── tests/                          # Unit tests
│   ├── __init__.py
│   ├── test_services.py
│   └── test_api.py
│
└── docs/                           # Documentation
    ├── API_DOCS.md                 # API documentation
    ├── SETUP.md                    # Detailed setup guide
    └── ETHICS.md                   # Ethical guidelines
```

## 🔧 Configuration

### Environment Variables (.env)
```bash
# Flask Configuration
SECRET_KEY=your-secret-key-here
DEBUG=True
HOST=0.0.0.0
PORT=5000

# Instagram API (for future integration)
INSTAGRAM_CLIENT_ID=your-client-id
INSTAGRAM_CLIENT_SECRET=your-client-secret
```

### config.py Settings

Key configuration options:

- `MAX_POSTS_TO_ANALYZE` - Maximum number of posts to process
- `DEFAULT_CONFIDENCE_THRESHOLD` - Minimum confidence for results
- `EXACT_GPS_CONFIDENCE` - Confidence level for GPS data (0.95)
- `VISUAL_INFERENCE_CONFIDENCE` - Confidence for image analysis (0.60)

## 📊 API Endpoints

### POST /api/analyze
Analyze user posts for location data

**Request:**
```json
{
  "username": "demo_user",
  "platform": "instagram"
}
```

**Response:**
```json
{
  "success": true,
  "username": "demo_user",
  "posts": [...],
  "statistics": {
    "total": 5,
    "exact": 2,
    "approx": 2,
    "clusters": 1,
    "time_span": "16 days"
  }
}
```

### GET /api/demo-data
Get demo data for testing

### POST /api/calculate-distance
Calculate distance between two coordinates

**Request:**
```json
{
  "lat1": 28.6139,
  "lng1": 77.2090,
  "lat2": 19.0760,
  "lng2": 72.8777
}
```

### POST /api/export
Export analysis results as JSON file

### GET /api/health
Health check endpoint

## 🎓 How It Works

### 1. Data Collection
- Currently uses demo data
- In production: Would connect to Instagram Basic Display API
- Only accesses publicly available posts

### 2. Location Analysis
Three methods for determining location:

**Exact Location (🔴 High Confidence)**
- GPS metadata embedded in photos
- Confidence: 95%

**Visual Inference (🟡 Medium Confidence)**
- AI image analysis identifies landmarks, scenes
- Text recognition from signs and billboards
- Confidence: 40-70%

**Text Analysis (🟡 Low Confidence)**
- Natural Language Processing on captions
- Location keywords extraction
- Confidence: 30-60%

### 3. Clustering
- Groups posts within 10km radius
- Identifies areas of repeated activity
- Creates cluster markers (🟢)

### 4. Movement Inference
- Connects posts chronologically
- Shows inferred travel patterns
- Does NOT show actual routes or methods

## ⚖️ Ethical Guidelines

### ✅ Designed For:

- **Security Awareness** - Help users understand their digital footprint
- **Privacy Education** - Demonstrate location exposure risks
- **Research** - Academic study of OSINT techniques
- **Self-Assessment** - Analyze your own location data

### ❌ NOT For:

- **Stalking or Harassment** - Strictly prohibited
- **Unauthorized Surveillance** - Privacy violation
- **Doxxing** - Exposing private information
- **Malicious Purposes** - Any harmful intent

### Our Approach:

1. **Transparency** - All confidence levels clearly displayed
2. **Public Data Only** - No private or restricted content
3. **Educational Focus** - Emphasis on awareness and prevention
4. **No Real-Time Tracking** - Historical data only
5. **User Consent** - Designed for self-analysis first

## 🛠️ Development

### Running Tests
```bash
# Install test dependencies
pip install pytest pytest-cov

# Run tests
pytest

# Run with coverage
pytest --cov=. --cov-report=html
```

### Code Style
```bash
# Install linting tools
pip install flake8 black

# Format code
black .

# Lint code
flake8 .
```

## 🚀 Future Enhancements

- [ ] Real Instagram API integration
- [ ] AI-powered image recognition for landmarks
- [ ] Support for Twitter, Facebook, TikTok
- [ ] Advanced clustering algorithms (DBSCAN, K-means)
- [ ] Heat map visualization
- [ ] Multi-user comparison
- [ ] Privacy score calculation
- [ ] Browser extension
- [ ] Mobile app

## 🐛 Troubleshooting

### Common Issues

**Port already in use:**
```bash
# Change port in .env file or:
python app.py --port 8000
```

**Dependencies not installing:**
```bash
# Upgrade pip
pip install --upgrade pip

# Install with verbose output
pip install -v -r requirements.txt
```

**Map not loading:**
- Check internet connection (requires Leaflet.js CDN)
- Disable browser ad-blockers
- Clear browser cache

## 📝 License

MIT License

Copyright (c) 2026 [Your Name]

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

[Full MIT License text...]

## 👥 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

Please read [CONTRIBUTING.md](CONTRIBUTING.md) for details on our code of conduct.

## 🏆 Hackathon Information

This project is **hackathon-ready** with:

- ✅ Complete documentation
- ✅ Demo mode for immediate testing
- ✅ Clear ethical guidelines
- ✅ Modular, extensible architecture
- ✅ RESTful API
- ✅ Responsive UI
- ✅ Example data included

### Presentation Tips:

1. **Start with the problem** - Digital footprint awareness
2. **Demo the tool** - Show all four visualization types
3. **Emphasize ethics** - Responsible OSINT practices
4. **Discuss tech stack** - Flask, Leaflet.js, Python
5. **Show future roadmap** - AI integration, multi-platform

## 📞 Contact & Support

- **Issues**: [GitHub Issues](https://github.com/yourusername/osint-location-visualizer/issues)
- **Email**: your.email@example.com
- **Twitter**: @yourusername

## 🙏 Acknowledgments

- [Leaflet.js](https://leafletjs.com/) - Interactive maps
- [OpenStreetMap](https://www.openstreetmap.org/) - Map data
- [Flask](https://flask.palletsprojects.com/) - Web framework
- Inspired by privacy awareness and ethical hacking communities

---

**⚠️ Disclaimer**: This tool is for educational and awareness purposes only. Users are responsible for ensuring their use complies with all applicable laws and respects individual privacy. The creators assume no liability for misuse.

**Remember**: Use responsibly and ethically! 🌟
=======
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
│   ├── ReverseOSINT.js                    
│   ├── setupTests.js
│   ├── SkeletonCard
│   ├── SnowEffect.js
│   └── VisualIntelligence.js
├── .env
├── app.py
├── visual.py
├── reverse_osint.py
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
>>>>>>> d46736adb11c5fcbcb2b72c57efef6f8ae7f0354
