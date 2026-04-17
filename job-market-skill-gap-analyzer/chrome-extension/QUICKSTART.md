# SkillScope Chrome Extension - Quick Start Guide

## 🚀 5-Minute Setup

### Step 1: Start the Backend API

Choose one option:

**Option A: Using Docker (Recommended)**
```bash
cd job-market-skill-gap-analyzer
docker-compose up -d
```

**Option B: Using Python**
```bash
cd job-market-skill-gap-analyzer/backend
uvicorn main:app --reload --port 8000
```

Verify API is running: http://localhost:8000/health

### Step 2: Load Chrome Extension

1. Open Chrome and go to `chrome://extensions/`
2. Enable "Developer mode" (toggle in top right)
3. Click "Load unpacked"
4. Navigate to and select: `job-market-skill-gap-analyzer/chrome-extension/`
5. Extension icon should appear in toolbar!

### Step 3: Configure API Endpoint

1. Click the SkillScope icon in Chrome toolbar
2. Scroll to Settings section
3. Enter API URL: `http://localhost:8000`
4. Click "Save Settings"

### Step 4: Upload Your Resume

1. Click SkillScope icon
2. Click "Upload Resume"
3. Select your PDF or Word resume
4. Wait for analysis (5-10 seconds)
5. See your skills count update!

### Step 5: Try It Out!

1. Visit any LinkedIn job posting: https://www.linkedin.com/jobs/
2. Open a job you're interested in
3. Look for the purple "Analyze with SkillScope" button
4. Click it and see your match score!

## ✅ Verification Checklist

- [ ] Backend API running (check http://localhost:8000/health)
- [ ] Extension loaded (icon visible in toolbar)
- [ ] API URL configured in settings
- [ ] Resume uploaded successfully
- [ ] Skill count shows in popup
- [ ] Analyze button appears on LinkedIn
- [ ] Match score appears when clicked

## 🐛 Troubleshooting

### Extension not loading?
- Make sure you selected the `chrome-extension` folder, not a subfolder
- Check Chrome console for errors (F12)
- Verify manifest.json exists in the selected folder

### API connection failed?
- Verify backend is running: `curl http://localhost:8000/health`
- Check API URL in extension settings
- Look for CORS errors in browser console
- Ensure port 8000 is not blocked by firewall

### Resume upload failing?
- File must be PDF, DOC, or DOCX
- File size must be under 5MB
- Check backend logs for errors
- Try a different resume file

### Button not appearing on job sites?
- Make sure you're on a supported site (LinkedIn, Indeed, etc.)
- Refresh the page after loading extension
- Check if content script loaded (inspect element → Sources → Content Scripts)
- Try reloading the extension

### No skills found in resume?
- Ensure resume has clear skill listings
- Try using a resume with technical skills
- Check backend logs for NLP processing errors

## 📱 Supported Job Sites

Current version works on:
- ✅ LinkedIn (linkedin.com/jobs/*)
- ✅ Indeed (indeed.com/viewjob*)
- ✅ Glassdoor (glassdoor.com/job-listing/*)
- ✅ Naukri (naukri.com/job-listings-*)
- ✅ Prosple (prosple.com/graduate-jobs/*)

## 💡 Tips for Best Results

1. **Resume Format**: Use a clear, well-formatted resume with distinct skill sections
2. **Keywords**: Include specific technologies (Python, React, AWS, etc.)
3. **Update Regularly**: Re-upload resume when you learn new skills
4. **Multiple Sites**: Try analyzing jobs on different platforms
5. **Compare Scores**: See how you match across different roles

## 🎯 What's Next?

Once everything works:
1. Deploy backend to cloud (see [DEPLOYMENT.md](DEPLOYMENT.md))
2. Update API URL to production endpoint
3. Create proper extension icons
4. Publish to Chrome Web Store
5. Share with friends!

## 📞 Need Help?

- Check [chrome-extension/README.md](chrome-extension/README.md) for detailed docs
- Review [CHROME_EXTENSION_SUMMARY.md](CHROME_EXTENSION_SUMMARY.md) for architecture
- Open GitHub issue if you find bugs
- Join community discussions

---

**Happy job hunting! 🎉**
