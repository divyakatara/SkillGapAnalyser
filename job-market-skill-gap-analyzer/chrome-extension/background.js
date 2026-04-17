/**
 * Background Service Worker for SkillScope Chrome Extension
 * Handles API communication, resume storage, and message passing
 */

const API_BASE_URL = 'https://your-api-url.com'; // Will be replaced with actual deployment URL

// Initialize extension on install
chrome.runtime.onInstalled.addListener(() => {
  console.log('SkillScope extension installed');
  
  // Set default settings
  chrome.storage.sync.set({
    apiUrl: API_BASE_URL,
    autoAnalyze: true,
    showNotifications: true
  });
});

// Listen for messages from content scripts and popup
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  console.log('Background received message:', request.action);
  
  switch (request.action) {
    case 'uploadResume':
      handleResumeUpload(request.data, sendResponse);
      return true; // Keep channel open for async response
      
    case 'analyzeJob':
      handleJobAnalysis(request.data, sendResponse);
      return true;
      
    case 'getResumeStatus':
      getResumeStatus(sendResponse);
      return true;
      
    case 'getCourseRecommendations':
      getCourseRecommendations(request.data, sendResponse);
      return true;
      
    default:
      sendResponse({ error: 'Unknown action' });
  }
});

/**
 * Handle resume upload and parsing
 */
async function handleResumeUpload(data, sendResponse) {
  try {
    const { file, fileName } = data;
    
    // Get API URL from storage
    const settings = await chrome.storage.sync.get(['apiUrl']);
    const apiUrl = settings.apiUrl || API_BASE_URL;
    
    // Convert base64 to blob
    const blob = base64ToBlob(file);
    const formData = new FormData();
    formData.append('file', blob, fileName);
    
    // Send to API
    const response = await fetch(`${apiUrl}/api/resume/upload`, {
      method: 'POST',
      body: formData
    });
    
    if (!response.ok) {
      throw new Error(`API error: ${response.status}`);
    }
    
    const result = await response.json();
    
    // Store resume data and skills in chrome.storage
    await chrome.storage.local.set({
      resumeId: result.resume_id,
      userSkills: result.skills,
      lastUpdated: new Date().toISOString(),
      resumeAnalysis: result.analysis
    });
    
    sendResponse({ 
      success: true, 
      skills: result.skills,
      message: 'Resume uploaded and analyzed successfully'
    });
  } catch (error) {
    console.error('Resume upload error:', error);
    sendResponse({ 
      success: false, 
      error: error.message 
    });
  }
}

/**
 * Analyze job posting against user's resume
 */
async function handleJobAnalysis(jobData, sendResponse) {
  try {
    // Get user's resume data
    const stored = await chrome.storage.local.get(['resumeId', 'userSkills']);
    
    if (!stored.resumeId) {
      sendResponse({ 
        success: false, 
        error: 'No resume uploaded. Please upload your resume first.' 
      });
      return;
    }
    
    const settings = await chrome.storage.sync.get(['apiUrl']);
    const apiUrl = settings.apiUrl || API_BASE_URL;
    
    // Send job data to API for analysis
    const response = await fetch(`${apiUrl}/api/analyze/skill-gap`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        resume_id: stored.resumeId,
        job_title: jobData.title,
        job_description: jobData.description,
        company: jobData.company,
        location: jobData.location
      })
    });
    
    if (!response.ok) {
      throw new Error(`API error: ${response.status}`);
    }
    
    const analysis = await response.json();
    
    sendResponse({ 
      success: true, 
      analysis: analysis 
    });
  } catch (error) {
    console.error('Job analysis error:', error);
    sendResponse({ 
      success: false, 
      error: error.message 
    });
  }
}

/**
 * Get current resume status
 */
async function getResumeStatus(sendResponse) {
  try {
    const stored = await chrome.storage.local.get(['resumeId', 'userSkills', 'lastUpdated']);
    
    sendResponse({
      success: true,
      hasResume: !!stored.resumeId,
      skillCount: stored.userSkills ? stored.userSkills.length : 0,
      lastUpdated: stored.lastUpdated
    });
  } catch (error) {
    sendResponse({ 
      success: false, 
      error: error.message 
    });
  }
}

/**
 * Get course recommendations for missing skills
 */
async function getCourseRecommendations(skills, sendResponse) {
  try {
    const settings = await chrome.storage.sync.get(['apiUrl']);
    const apiUrl = settings.apiUrl || API_BASE_URL;
    
    const response = await fetch(`${apiUrl}/api/courses/recommend`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ skills })
    });
    
    if (!response.ok) {
      throw new Error(`API error: ${response.status}`);
    }
    
    const courses = await response.json();
    
    sendResponse({ 
      success: true, 
      courses: courses 
    });
  } catch (error) {
    console.error('Course recommendation error:', error);
    sendResponse({ 
      success: false, 
      error: error.message 
    });
  }
}

/**
 * Utility: Convert base64 to Blob
 */
function base64ToBlob(base64) {
  const parts = base64.split(';base64,');
  const contentType = parts[0].split(':')[1];
  const raw = window.atob(parts[1]);
  const rawLength = raw.length;
  const uInt8Array = new Uint8Array(rawLength);
  
  for (let i = 0; i < rawLength; ++i) {
    uInt8Array[i] = raw.charCodeAt(i);
  }
  
  return new Blob([uInt8Array], { type: contentType });
}
