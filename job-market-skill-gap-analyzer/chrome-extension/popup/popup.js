/**
 * Popup Script for SkillScope Chrome Extension
 */

// DOM Elements
const uploadBtn = document.getElementById('upload-btn');
const updateResumeBtn = document.getElementById('update-resume-btn');
const resumeFileInput = document.getElementById('resume-file');
const noResumeSection = document.getElementById('no-resume');
const resumeInfoSection = document.getElementById('resume-info');
const uploadProgress = document.getElementById('upload-progress');
const viewSkillsBtn = document.getElementById('view-skills-btn');
const skillsModal = document.getElementById('skills-modal');
const closeSkillsModal = document.getElementById('close-skills-modal');
const saveSettingsBtn = document.getElementById('save-settings-btn');

// Initialize popup
document.addEventListener('DOMContentLoaded', async () => {
  await loadResumeStatus();
  await loadSettings();
  attachEventListeners();
});

/**
 * Load resume status
 */
async function loadResumeStatus() {
  chrome.runtime.sendMessage({ action: 'getResumeStatus' }, (response) => {
    if (response.success) {
      updateResumeUI(response);
    }
  });
}

/**
 * Update resume UI based on status
 */
function updateResumeUI(status) {
  const resumeStatusBadge = document.getElementById('resume-status');
  const lastUpdatedEl = document.getElementById('last-updated');
  const skillCountEl = document.getElementById('skill-count');

  if (status.hasResume) {
    noResumeSection.style.display = 'none';
    resumeInfoSection.style.display = 'block';
    resumeStatusBadge.textContent = 'Active';
    resumeStatusBadge.className = 'status-badge active';
    
    // Format date
    const date = new Date(status.lastUpdated);
    lastUpdatedEl.textContent = date.toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric'
    });
    
    skillCountEl.textContent = status.skillCount;
  } else {
    noResumeSection.style.display = 'flex';
    resumeInfoSection.style.display = 'none';
    resumeStatusBadge.textContent = 'Not uploaded';
    resumeStatusBadge.className = 'status-badge';
  }
}

/**
 * Load settings from storage
 */
async function loadSettings() {
  chrome.storage.sync.get(['apiUrl', 'autoAnalyze', 'showNotifications'], (settings) => {
    document.getElementById('api-url').value = settings.apiUrl || '';
    document.getElementById('auto-analyze').checked = settings.autoAnalyze !== false;
    document.getElementById('show-notifications').checked = settings.showNotifications !== false;
  });
}

/**
 * Attach event listeners
 */
function attachEventListeners() {
  // Upload buttons
  uploadBtn.addEventListener('click', () => resumeFileInput.click());
  updateResumeBtn.addEventListener('click', () => resumeFileInput.click());
  resumeFileInput.addEventListener('change', handleFileSelect);

  // View skills
  viewSkillsBtn.addEventListener('click', showSkillsModal);
  closeSkillsModal.addEventListener('click', hideSkillsModal);

  // Settings
  saveSettingsBtn.addEventListener('click', saveSettings);

  // Click outside modal to close
  skillsModal.addEventListener('click', (e) => {
    if (e.target === skillsModal) {
      hideSkillsModal();
    }
  });
}

/**
 * Handle file selection
 */
async function handleFileSelect(e) {
  const file = e.target.files[0];
  
  if (!file) return;

  // Validate file type
  const validTypes = ['application/pdf', 'application/msword', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'];
  if (!validTypes.includes(file.type)) {
    showNotification('Please upload a PDF or Word document', 'error');
    return;
  }

  // Validate file size (max 5MB)
  if (file.size > 5 * 1024 * 1024) {
    showNotification('File size must be less than 5MB', 'error');
    return;
  }

  // Show progress
  noResumeSection.style.display = 'none';
  resumeInfoSection.style.display = 'none';
  uploadProgress.style.display = 'block';

  try {
    // Convert file to base64
    const base64 = await fileToBase64(file);

    // Send to background script
    chrome.runtime.sendMessage(
      {
        action: 'uploadResume',
        data: {
          file: base64,
          fileName: file.name
        }
      },
      (response) => {
        uploadProgress.style.display = 'none';

        if (response.success) {
          showNotification('Resume uploaded successfully!', 'success');
          loadResumeStatus();
        } else {
          showNotification(`Upload failed: ${response.error}`, 'error');
          noResumeSection.style.display = 'flex';
        }
      }
    );
  } catch (error) {
    console.error('File upload error:', error);
    showNotification('Failed to upload resume', 'error');
    uploadProgress.style.display = 'none';
    noResumeSection.style.display = 'flex';
  }

  // Reset file input
  resumeFileInput.value = '';
}

/**
 * Convert file to base64
 */
function fileToBase64(file) {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onload = () => resolve(reader.result);
    reader.onerror = reject;
    reader.readAsDataURL(file);
  });
}

/**
 * Show skills modal
 */
async function showSkillsModal() {
  const stored = await chrome.storage.local.get(['userSkills']);
  const skills = stored.userSkills || [];

  const skillsList = document.getElementById('skills-list');
  
  if (skills.length === 0) {
    skillsList.innerHTML = '<p class="empty-message">No skills found</p>';
  } else {
    skillsList.innerHTML = skills
      .map(skill => `<span class="skill-badge">${skill}</span>`)
      .join('');
  }

  skillsModal.style.display = 'flex';
}

/**
 * Hide skills modal
 */
function hideSkillsModal() {
  skillsModal.style.display = 'none';
}

/**
 * Save settings
 */
async function saveSettings() {
  const apiUrl = document.getElementById('api-url').value;
  const autoAnalyze = document.getElementById('auto-analyze').checked;
  const showNotifications = document.getElementById('show-notifications').checked;

  // Validate API URL if provided
  if (apiUrl && !isValidUrl(apiUrl)) {
    showNotification('Please enter a valid URL', 'error');
    return;
  }

  chrome.storage.sync.set(
    {
      apiUrl,
      autoAnalyze,
      showNotifications
    },
    () => {
      showNotification('Settings saved successfully!', 'success');
    }
  );
}

/**
 * Validate URL
 */
function isValidUrl(string) {
  try {
    const url = new URL(string);
    return url.protocol === 'http:' || url.protocol === 'https:';
  } catch (_) {
    return false;
  }
}

/**
 * Show notification
 */
function showNotification(message, type = 'info') {
  const notification = document.createElement('div');
  notification.className = `notification ${type}`;
  notification.textContent = message;

  document.body.appendChild(notification);

  // Animate in
  setTimeout(() => {
    notification.classList.add('show');
  }, 10);

  // Remove after 3 seconds
  setTimeout(() => {
    notification.classList.remove('show');
    setTimeout(() => {
      notification.remove();
    }, 300);
  }, 3000);
}
