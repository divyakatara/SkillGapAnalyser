/**
 * Content Script for SkillScope Chrome Extension
 * Extracts job information from job listing pages and displays skill gap analysis
 */

// Site-specific selectors for job information extraction
const SITE_SELECTORS = {
  linkedin: {
    title: '.top-card-layout__title, .job-details-jobs-unified-top-card__job-title',
    company: '.topcard__org-name-link, .job-details-jobs-unified-top-card__company-name',
    location: '.topcard__flavor--bullet, .job-details-jobs-unified-top-card__bullet',
    description: '.show-more-less-html__markup, .jobs-description__content'
  },
  indeed: {
    title: '.jobsearch-JobInfoHeader-title',
    company: '[data-company-name="true"], .jobsearch-InlineCompanyRating-companyHeader',
    location: '[data-testid="job-location"]',
    description: '#jobDescriptionText'
  },
  glassdoor: {
    title: '[data-test="job-title"]',
    company: '[data-test="employer-name"]',
    location: '[data-test="location"]',
    description: '.jobDescriptionContent'
  },
  naukri: {
    title: '.jd-header-title',
    company: '.jd-header-comp-name',
    location: '.jd-loc',
    description: '.job-desc'
  },
  prosple: {
    title: 'h1.job-title',
    company: '.company-name',
    location: '.job-location',
    description: '.job-description'
  }
};

let currentSite = null;
let analysisPanel = null;
let isAnalyzing = false;

// Initialize content script
(function initialize() {
  console.log('SkillScope: Content script loaded');
  
  // Detect current site
  currentSite = detectSite();
  
  if (currentSite) {
    console.log(`SkillScope: Detected site - ${currentSite}`);
    
    // Wait for page to fully load
    if (document.readyState === 'loading') {
      document.addEventListener('DOMContentLoaded', injectAnalysisButton);
    } else {
      injectAnalysisButton();
    }
    
    // Monitor for dynamic content changes (SPA navigation)
    observePageChanges();
  }
})();

/**
 * Detect which job site we're on
 */
function detectSite() {
  const hostname = window.location.hostname;
  
  if (hostname.includes('linkedin.com')) return 'linkedin';
  if (hostname.includes('indeed.com')) return 'indeed';
  if (hostname.includes('glassdoor.com')) return 'glassdoor';
  if (hostname.includes('naukri.com')) return 'naukri';
  if (hostname.includes('prosple.com')) return 'prosple';
  
  return null;
}

/**
 * Inject the "Analyze with SkillScope" button
 */
function injectAnalysisButton() {
  // Check if button already exists
  if (document.getElementById('skillscope-analyze-btn')) {
    return;
  }
  
  // Find a suitable location to inject the button
  const selectors = SITE_SELECTORS[currentSite];
  const titleElement = document.querySelector(selectors.title);
  
  if (!titleElement) {
    console.log('SkillScope: Job title element not found, will retry...');
    setTimeout(injectAnalysisButton, 1000);
    return;
  }
  
  // Create analyze button
  const button = document.createElement('button');
  button.id = 'skillscope-analyze-btn';
  button.className = 'skillscope-btn';
  button.innerHTML = `
    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
      <path d="M22 12h-4l-3 9L9 3l-3 9H2"/>
    </svg>
    <span>Analyze with SkillScope</span>
  `;
  
  button.addEventListener('click', handleAnalyzeClick);
  
  // Insert button near title
  titleElement.parentElement.insertBefore(button, titleElement.nextSibling);
  
  console.log('SkillScope: Analysis button injected');
}

/**
 * Handle analyze button click
 */
async function handleAnalyzeClick(e) {
  e.preventDefault();
  e.stopPropagation();
  
  if (isAnalyzing) return;
  
  const button = e.currentTarget;
  button.classList.add('analyzing');
  button.innerHTML = '<span class="spinner"></span> Analyzing...';
  isAnalyzing = true;
  
  try {
    // Extract job information
    const jobData = extractJobData();
    
    if (!jobData) {
      throw new Error('Could not extract job information');
    }
    
    console.log('Extracted job data:', jobData);
    
    // Send to background script for analysis
    chrome.runtime.sendMessage(
      { action: 'analyzeJob', data: jobData },
      (response) => {
        if (response.success) {
          displayAnalysisPanel(response.analysis, jobData);
        } else {
          if (response.error.includes('No resume uploaded')) {
            showUploadResumePrompt();
          } else {
            showError(response.error);
          }
        }
        
        resetButton(button);
        isAnalyzing = false;
      }
    );
  } catch (error) {
    console.error('Analysis error:', error);
    showError(error.message);
    resetButton(button);
    isAnalyzing = false;
  }
}

/**
 * Extract job data from the page
 */
function extractJobData() {
  const selectors = SITE_SELECTORS[currentSite];
  
  const titleEl = document.querySelector(selectors.title);
  const companyEl = document.querySelector(selectors.company);
  const locationEl = document.querySelector(selectors.location);
  const descriptionEl = document.querySelector(selectors.description);
  
  if (!titleEl || !descriptionEl) {
    return null;
  }
  
  return {
    title: titleEl.textContent.trim(),
    company: companyEl ? companyEl.textContent.trim() : 'Unknown',
    location: locationEl ? locationEl.textContent.trim() : 'Unknown',
    description: descriptionEl.textContent.trim(),
    url: window.location.href
  };
}

/**
 * Display the analysis panel
 */
function displayAnalysisPanel(analysis, jobData) {
  // Remove existing panel if any
  if (analysisPanel) {
    analysisPanel.remove();
  }
  
  // Create panel
  analysisPanel = document.createElement('div');
  analysisPanel.id = 'skillscope-panel';
  analysisPanel.className = 'skillscope-panel';
  
  const matchScore = analysis.match_score || 0;
  const recommendation = getRecommendation(matchScore);
  
  analysisPanel.innerHTML = `
    <div class="skillscope-panel-header">
      <div class="skillscope-logo">
        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M22 12h-4l-3 9L9 3l-3 9H2"/>
        </svg>
        <span>SkillScope Analysis</span>
      </div>
      <button class="skillscope-close-btn" id="skillscope-close">×</button>
    </div>
    
    <div class="skillscope-panel-content">
      <div class="skillscope-job-info">
        <h3>${jobData.title}</h3>
        <p>${jobData.company} · ${jobData.location}</p>
      </div>
      
      <div class="skillscope-match-score">
        <div class="score-circle ${getScoreClass(matchScore)}">
          <span class="score-value">${matchScore}%</span>
          <span class="score-label">Match</span>
        </div>
        <div class="recommendation ${recommendation.class}">
          <strong>${recommendation.text}</strong>
          <p>${recommendation.description}</p>
        </div>
      </div>
      
      <div class="skillscope-skills">
        <div class="skill-section">
          <h4>✓ Matching Skills (${analysis.matching_skills ? analysis.matching_skills.length : 0})</h4>
          <div class="skill-tags">
            ${analysis.matching_skills ? analysis.matching_skills.map(skill => 
              `<span class="skill-tag match">${skill}</span>`
            ).join('') : '<p>No matching skills found</p>'}
          </div>
        </div>
        
        <div class="skill-section">
          <h4>⚠ Missing Skills (${analysis.missing_skills ? analysis.missing_skills.length : 0})</h4>
          <div class="skill-tags">
            ${analysis.missing_skills ? analysis.missing_skills.map(skill => 
              `<span class="skill-tag missing">${skill}</span>`
            ).join('') : '<p>You have all required skills!</p>'}
          </div>
        </div>
      </div>
      
      ${analysis.missing_skills && analysis.missing_skills.length > 0 ? `
        <div class="skillscope-courses">
          <h4>📚 Recommended Learning Paths</h4>
          <button class="skillscope-btn-secondary" id="skillscope-get-courses">
            Get Course Recommendations
          </button>
          <div id="course-recommendations"></div>
        </div>
      ` : ''}
      
      <div class="skillscope-insights">
        <h4>💡 Key Insights</h4>
        <ul>
          ${analysis.insights ? analysis.insights.map(insight => 
            `<li>${insight}</li>`
          ).join('') : '<li>Analysis complete</li>'}
        </ul>
      </div>
    </div>
  `;
  
  document.body.appendChild(analysisPanel);
  
  // Add event listeners
  document.getElementById('skillscope-close').addEventListener('click', () => {
    analysisPanel.remove();
  });
  
  const getCourseBtn = document.getElementById('skillscope-get-courses');
  if (getCourseBtn) {
    getCourseBtn.addEventListener('click', () => loadCourseRecommendations(analysis.missing_skills));
  }
  
  // Animate in
  setTimeout(() => {
    analysisPanel.classList.add('show');
  }, 10);
}

/**
 * Load course recommendations
 */
function loadCourseRecommendations(skills) {
  const btn = document.getElementById('skillscope-get-courses');
  const container = document.getElementById('course-recommendations');
  
  btn.textContent = 'Loading...';
  btn.disabled = true;
  
  chrome.runtime.sendMessage(
    { action: 'getCourseRecommendations', data: skills },
    (response) => {
      if (response.success && response.courses) {
        displayCourses(container, response.courses);
      } else {
        container.innerHTML = '<p class="error">Failed to load recommendations</p>';
      }
      btn.remove();
    }
  );
}

/**
 * Display course recommendations
 */
function displayCourses(container, courses) {
  container.innerHTML = courses.map(course => `
    <div class="course-card">
      <div class="course-provider">${course.provider}</div>
      <h5>${course.title}</h5>
      <p>${course.description}</p>
      <div class="course-meta">
        <span>${course.duration}</span>
        <span>${course.level}</span>
      </div>
      <a href="${course.url}" target="_blank" class="course-link">View Course →</a>
    </div>
  `).join('');
}

/**
 * Show upload resume prompt
 */
function showUploadResumePrompt() {
  if (analysisPanel) {
    analysisPanel.remove();
  }
  
  analysisPanel = document.createElement('div');
  analysisPanel.id = 'skillscope-panel';
  analysisPanel.className = 'skillscope-panel show';
  
  analysisPanel.innerHTML = `
    <div class="skillscope-panel-header">
      <div class="skillscope-logo">
        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M22 12h-4l-3 9L9 3l-3 9H2"/>
        </svg>
        <span>SkillScope</span>
      </div>
      <button class="skillscope-close-btn" id="skillscope-close">×</button>
    </div>
    
    <div class="skillscope-panel-content">
      <div class="skillscope-empty-state">
        <svg width="64" height="64" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
          <path d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"/>
        </svg>
        <h3>No Resume Uploaded</h3>
        <p>Upload your resume to get personalized skill gap analysis and job recommendations.</p>
        <button class="skillscope-btn-primary" id="open-extension">Upload Resume</button>
      </div>
    </div>
  `;
  
  document.body.appendChild(analysisPanel);
  
  document.getElementById('skillscope-close').addEventListener('click', () => {
    analysisPanel.remove();
  });
  
  document.getElementById('open-extension').addEventListener('click', () => {
    chrome.runtime.sendMessage({ action: 'openPopup' });
  });
}

/**
 * Show error message
 */
function showError(message) {
  const errorDiv = document.createElement('div');
  errorDiv.className = 'skillscope-error';
  errorDiv.textContent = message;
  document.body.appendChild(errorDiv);
  
  setTimeout(() => {
    errorDiv.remove();
  }, 5000);
}

/**
 * Reset analyze button
 */
function resetButton(button) {
  button.classList.remove('analyzing');
  button.innerHTML = `
    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
      <path d="M22 12h-4l-3 9L9 3l-3 9H2"/>
    </svg>
    <span>Analyze with SkillScope</span>
  `;
}

/**
 * Get recommendation based on match score
 */
function getRecommendation(score) {
  if (score >= 80) {
    return {
      text: '🎯 Strongly Recommended',
      description: 'You\'re an excellent match! Apply with confidence.',
      class: 'recommend-high'
    };
  } else if (score >= 60) {
    return {
      text: '✓ Worth Applying',
      description: 'Good match. Consider upskilling in missing areas.',
      class: 'recommend-medium'
    };
  } else if (score >= 40) {
    return {
      text: '⚠ Consider Carefully',
      description: 'Significant skill gaps. Focus on learning first.',
      class: 'recommend-low'
    };
  } else {
    return {
      text: '❌ Not Recommended',
      description: 'Major skill gaps. Build foundational skills first.',
      class: 'recommend-none'
    };
  }
}

/**
 * Get CSS class for score
 */
function getScoreClass(score) {
  if (score >= 80) return 'score-high';
  if (score >= 60) return 'score-medium';
  if (score >= 40) return 'score-low';
  return 'score-very-low';
}

/**
 * Observe page changes for SPAs
 */
function observePageChanges() {
  const observer = new MutationObserver((mutations) => {
    // Check if we're still on a job page
    const currentUrl = window.location.href;
    if (currentUrl.includes('/jobs/') || currentUrl.includes('/job-listings-') || currentUrl.includes('/viewjob')) {
      // Reinject button if it doesn't exist
      if (!document.getElementById('skillscope-analyze-btn')) {
        setTimeout(injectAnalysisButton, 500);
      }
    }
  });
  
  observer.observe(document.body, {
    childList: true,
    subtree: true
  });
}
