# SkillScope - Smart Job Application Assistant

<div align="center">
  <img src="icons/icon128.png" alt="SkillScope Logo" width="128" height="128">
  
  <p><strong>AI-powered Chrome extension that analyzes your resume against job postings in real-time</strong></p>
  
  [![Chrome Web Store](https://img.shields.io/badge/Chrome-Web%20Store-blue)](https://chrome.google.com/webstore)
  [![Version](https://img.shields.io/badge/version-1.0.0-green)](https://github.com)
  [![License](https://img.shields.io/badge/license-MIT-blue)](LICENSE)
</div>

## 🎯 Features

- **📊 Real-time Skill Gap Analysis**: Instantly see how your skills match any job posting
- **🎓 Personalized Learning Paths**: Get course recommendations from Coursera, edX, Udemy, and more
- **✅ Smart Application Recommendations**: Know whether it's worth applying based on your profile
- **🔄 Dynamic Resume Updates**: Update your resume anytime and get fresh analysis
- **🌐 Multi-Site Support**: Works on LinkedIn, Indeed, Glassdoor, Naukri, Prosple, and more
- **🤖 AI-Powered**: Uses advanced NLP to understand skills and job requirements

## 📸 Screenshots

### Extension Popup
![Popup](docs/screenshots/popup.png)

### In-Page Analysis
![Analysis Panel](docs/screenshots/analysis-panel.png)

### Course Recommendations
![Courses](docs/screenshots/courses.png)

## 🚀 Installation

### From Chrome Web Store (Recommended)
1. Visit the [Chrome Web Store page](#) (coming soon)
2. Click "Add to Chrome"
3. Click "Add extension" in the confirmation dialog

### Manual Installation (Development)
1. Download or clone this repository
2. Open Chrome and navigate to `chrome://extensions/`
3. Enable "Developer mode" (toggle in top right)
4. Click "Load unpacked"
5. Select the `chrome-extension` folder
6. The extension is now installed!

## 📖 Usage

### 1. Upload Your Resume
1. Click the SkillScope icon in your browser toolbar
2. Click "Upload Resume" and select your PDF or Word document
3. Wait for the analysis to complete
4. Your skills are now saved and ready for job matching

### 2. Analyze Job Postings
1. Visit any supported job site (LinkedIn, Indeed, etc.)
2. Open a job posting
3. Click the "Analyze with SkillScope" button that appears
4. View your match score, skill gaps, and recommendations

### 3. Get Course Recommendations
- When viewing skill gaps, click "Get Course Recommendations"
- Browse personalized learning paths from top platforms
- Click course links to enroll and start learning

### 4. Update Your Resume
1. Click the extension icon
2. Click "Update Resume"
3. Upload your new resume
4. The extension will analyze and update your skill profile

## 🔧 Configuration

### API Endpoint
The extension requires a backend API server for analysis. You can:

**Option 1: Use Hosted Service** (Recommended)
- Default API URL is pre-configured
- No setup required

**Option 2: Self-Host**
1. Clone the main repository
2. Follow deployment instructions in [backend/README.md](../README.md)
3. Update API URL in extension settings

### Settings
Access settings by clicking the extension icon:
- **Auto-analyze**: Automatically analyze jobs when visiting job pages
- **Notifications**: Get notified when analysis completes
- **API Endpoint**: Custom backend API URL

## 🏗️ Supported Job Sites

| Site | Job Listings | Job Details | Auto-Detect |
|------|-------------|-------------|-------------|
| LinkedIn | ✅ | ✅ | ✅ |
| Indeed | ✅ | ✅ | ✅ |
| Glassdoor | ✅ | ✅ | ✅ |
| Naukri | ✅ | ✅ | ✅ |
| Prosple | ✅ | ✅ | ✅ |

*More sites coming soon! Submit requests via [GitHub Issues](https://github.com/your-repo/issues)*

## 🛠️ Technical Architecture

```
┌─────────────────┐
│  Chrome         │
│  Extension      │
│  (Frontend)     │
└────────┬────────┘
         │
         │ REST API
         │
┌────────▼────────┐
│  FastAPI        │
│  Backend        │
│  (Analysis)     │
└────────┬────────┘
         │
         │
┌────────▼────────┐
│  NLP Engine     │
│  (Skill         │
│  Extraction)    │
└─────────────────┘
```

### Components
- **Content Script**: Extracts job information from web pages
- **Background Worker**: Handles API communication and storage
- **Popup UI**: Resume management and settings
- **Backend API**: Skill extraction, gap analysis, course recommendations

## 🔒 Privacy & Security

- **Local Storage**: Your resume data is stored locally in Chrome
- **HTTPS Only**: All API communication is encrypted
- **No Tracking**: We don't track your browsing or job applications
- **Data Control**: Delete your data anytime from extension settings
- **Open Source**: Full transparency - review the code yourself

## 🧑‍💻 Development

### Prerequisites
- Node.js 18+ (for build tools)
- Chrome/Chromium browser
- Backend API running (see main README)

### Setup
```bash
# Clone repository
git clone https://github.com/your-repo/skillscope.git
cd skillscope/chrome-extension

# The extension is pure JavaScript - no build step required
# Load as unpacked extension in Chrome
```

### Project Structure
```
chrome-extension/
├── manifest.json          # Extension configuration
├── background.js          # Service worker
├── content/
│   ├── content.js        # Page content script
│   └── content.css       # Injected styles
├── popup/
│   ├── popup.html        # Extension popup
│   ├── popup.js          # Popup logic
│   └── popup.css         # Popup styles
└── icons/                # Extension icons
```

### Testing
```bash
# Run linter
npm run lint

# Test on local API
# 1. Update API URL in popup settings to http://localhost:8000
# 2. Start backend: cd ../backend && uvicorn main:app
# 3. Test extension on job sites
```

### Building for Production
```bash
# Create distribution package
cd chrome-extension
zip -r ../skillscope-extension.zip . -x "*.git*" -x "*node_modules*"

# The .zip file can be uploaded to Chrome Web Store
```

## 🤝 Contributing

We welcome contributions! Please see [CONTRIBUTING.md](../CONTRIBUTING.md) for guidelines.

### Areas for Contribution
- 🌐 Add support for more job sites
- 🎨 UI/UX improvements
- 🐛 Bug fixes and testing
- 📝 Documentation improvements
- 🌍 Internationalization (i18n)

## 📊 Roadmap

- [ ] Chrome Web Store publication
- [ ] Firefox extension port
- [ ] Safari extension port
- [ ] Batch job analysis
- [ ] Job tracking dashboard
- [ ] Salary insights
- [ ] Company reviews integration
- [ ] AI-powered cover letter generation

## 🆘 Support

- **Issues**: [GitHub Issues](https://github.com/your-repo/issues)
- **Discussions**: [GitHub Discussions](https://github.com/your-repo/discussions)
- **Email**: support@skillscope.app

## 📄 License

This project is licensed under the MIT License - see [LICENSE](../LICENSE) file for details.

## 🙏 Acknowledgments

- spaCy for NLP capabilities
- FastAPI for backend framework
- All our contributors and users

---

<div align="center">
  <p>Made with ❤️ for job seekers worldwide</p>
  <p>⭐ Star us on GitHub if this helps your job search!</p>
</div>
