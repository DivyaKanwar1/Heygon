let socket = null;
let reconnectAttempts = 0;
const maxReconnectAttempts = 10;

const eyeContactEl = document.getElementById('eye-contact');
const postureEl = document.getElementById('posture');
const overallEl = document.getElementById('overall');
const statusDot = document.getElementById('status-dot');
const timestampEl = document.getElementById('timestamp');
const closeBtn = document.getElementById('close-btn');

function connect() {
  const wsUrl = 'somethingparagon.onrender.com';
  
  socket = new WebSocket(wsUrl);
  
  socket.onopen = function() {
    console.log('[Paragon IRIS Overlay] Connected');
    statusDot.style.background = '#2ECC71';
    reconnectAttempts = 0;
  };
  
  socket.onmessage = function(event) {
    try {
      const data = JSON.parse(event.data);
      if (data.type === 'scores') {
        updateScores(data);
      }
    } catch (e) {
      console.error('[Paragon IRIS Overlay] Parse error:', e);
    }
  };
  
  socket.onclose = function() {
    console.log('[Paragon IRIS Overlay] Disconnected');
    statusDot.style.background = '#E74C3C';
    reconnect();
  };
  
  socket.onerror = function(error) {
    console.error('[Paragon IRIS Overlay] Error:', error);
  };
}

function reconnect() {
  if (reconnectAttempts >= maxReconnectAttempts) {
    console.log('[Paragon IRIS Overlay] Max reconnect attempts reached');
    return;
  }
  
  const delay = Math.min(1000 * Math.pow(2, reconnectAttempts), 30000);
  reconnectAttempts++;
  
  setTimeout(() => {
    console.log(`[Paragon IRIS Overlay] Reconnecting (attempt ${reconnectAttempts})`);
    connect();
  }, delay);
}

function updateScores(data) {
  const eyeContact = Math.round(data.eye_contact || 0);
  const posture = Math.round(data.posture || 0);
  const overall = Math.round(data.overall || 0);
  const timestamp = data.timestamp || Date.now();
  
  if (eyeContactEl) {
    eyeContactEl.textContent = eyeContact + '%';
    eyeContactEl.style.color = eyeContact >= 70 ? '#2ECC71' : (eyeContact >= 40 ? '#F39C12' : '#E74C3C');
  }
  
  if (postureEl) {
    postureEl.textContent = posture + '%';
    postureEl.style.color = posture >= 70 ? '#2ECC71' : (posture >= 40 ? '#F39C12' : '#E74C3C');
  }
  
  if (overallEl) {
    overallEl.textContent = overall;
    overallEl.style.color = overall >= 70 ? '#2ECC71' : (overall >= 40 ? '#F39C12' : '#E74C3C');
  }
  
  if (timestampEl) {
    const date = new Date(timestamp);
    timestampEl.textContent = date.toLocaleTimeString();
  }
  
  if (statusDot) {
    statusDot.style.background = '#2ECC71';
  }
}

if (closeBtn) {
  closeBtn.addEventListener('click', function() {
    if (chrome && chrome.runtime) {
      chrome.runtime.sendMessage({ type: 'STOP_RECORDING' });
    }
    const container = document.getElementById('overlay-container');
    if (container) {
      container.style.display = 'none';
    }
  });
}

connect();
console.log('[Paragon IRIS Overlay] Loaded');