let currentStatus = 'disconnected';
let currentScores = { eye_contact: 0, posture: 0, overall: 0 };

const startBtn = document.getElementById('start-btn');
const stopBtn = document.getElementById('stop-btn');
const statusDot = document.getElementById('status-dot');
const statusText = document.getElementById('status-text');
const previewEye = document.getElementById('preview-eye');
const previewPosture = document.getElementById('preview-posture');
const previewOverall = document.getElementById('preview-overall');

function updateStatus(status, scores) {
  currentStatus = status;
  
  if (scores) {
    currentScores = scores;
  }
  
  statusDot.className = 'status-dot';
  if (status === 'connected' || status === 'recording') {
    statusDot.classList.add('connected');
    statusText.textContent = status === 'recording' ? 'Recording...' : 'Connected';
  } else {
    statusDot.classList.add('disconnected');
    statusText.textContent = 'Disconnected';
  }
  
  if (status === 'recording') {
    startBtn.style.display = 'none';
    stopBtn.style.display = 'block';
    stopBtn.disabled = false;
  } else {
    startBtn.style.display = 'block';
    startBtn.disabled = false;
    stopBtn.style.display = 'none';
  }
  
  if (currentScores.eye_contact > 0 || currentScores.overall > 0) {
    const eye = Math.round(currentScores.eye_contact || 0);
    const posture = Math.round(currentScores.posture || 0);
    const overall = Math.round(currentScores.overall || 0);
    
    previewEye.textContent = eye + '%';
    previewEye.style.color = eye >= 70 ? '#2ECC71' : (eye >= 40 ? '#F39C12' : '#E74C3C');
    
    previewPosture.textContent = posture + '%';
    previewPosture.style.color = posture >= 70 ? '#2ECC71' : (posture >= 40 ? '#F39C12' : '#E74C3C');
    
    previewOverall.textContent = overall;
    previewOverall.style.color = overall >= 70 ? '#2ECC71' : (overall >= 40 ? '#F39C12' : '#E74C3C');
  }
}

function getStatus() {
  chrome.runtime.sendMessage({ type: 'GET_STATUS' }, (response) => {
    if (response) {
      updateStatus(response.status || 'disconnected', currentScores);
    }
  });
}

function startRecording() {
  startBtn.disabled = true;
  startBtn.textContent = 'Starting...';
  
  chrome.runtime.sendMessage({ type: 'START_RECORDING' }, (response) => {
    if (response && response.success) {
      updateStatus('recording', currentScores);
    } else {
      startBtn.disabled = false;
      startBtn.textContent = '🎯 Start Analysis';
      alert('Failed to start recording. Make sure you are on a video call page.');
    }
  });
}

function stopRecording() {
  stopBtn.disabled = true;
  stopBtn.textContent = 'Stopping...';
  
  chrome.runtime.sendMessage({ type: 'STOP_RECORDING' }, (response) => {
    stopBtn.disabled = false;
    stopBtn.textContent = '⏹ Stop Analysis';
    getStatus();
  });
}

chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request.type === 'STATUS_UPDATE') {
    updateStatus(request.payload.status, currentScores);
  }
  
  if (request.type === 'SCORES_UPDATE') {
    updateStatus(currentStatus, request.payload);
  }
});

startBtn.addEventListener('click', startRecording);
stopBtn.addEventListener('click', stopRecording);

getStatus();
setInterval(getStatus, 5000);

console.log('[Paragon IRIS Popup] Loaded');