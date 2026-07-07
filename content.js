let overlayElement = null;
let overlayVisible = false;

chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request.type === 'SHOW_OVERLAY') {
    showOverlay(request.payload);
    sendResponse({ success: true });
  }
  
  if (request.type === 'HIDE_OVERLAY') {
    hideOverlay();
    sendResponse({ success: true });
  }
  
  if (request.type === 'UPDATE_SCORES') {
    updateOverlayScores(request.payload);
    sendResponse({ success: true });
  }
});

function showOverlay(payload) {
  if (overlayElement) {
    overlayElement.style.display = 'block';
    updateOverlayScores(payload.scores);
    return;
  }
  
  overlayElement = document.createElement('div');
  overlayElement.id = 'paragon-iris-overlay';
  overlayElement.style.cssText = `
    position: fixed;
    bottom: 20px;
    right: 20px;
    width: 280px;
    background: rgba(10, 10, 10, 0.92);
    backdrop-filter: blur(10px);
    border-radius: 16px;
    padding: 20px;
    z-index: 9999999;
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    color: white;
    border: 1px solid rgba(74, 144, 217, 0.3);
    box-shadow: 0 20px 60px rgba(0, 0, 0, 0.8);
    user-select: none;
  `;
  
  overlayElement.innerHTML = `
    <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 14px;">
      <div style="display: flex; align-items: center; gap: 10px;">
        <span style="font-size: 20px;">👁️</span>
        <span style="font-weight: 700; font-size: 14px; background: linear-gradient(135deg, #4A90D9, #6C2BD9); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">PARAGON IRIS</span>
      </div>
      <div style="display: flex; gap: 8px; align-items: center;">
        <span id="paragon-status-dot" style="display: inline-block; width: 8px; height: 8px; background: #2ECC71; border-radius: 50%;"></span>
        <button id="paragon-close-btn" style="background: none; border: none; color: #666; font-size: 18px; cursor: pointer; padding: 0 4px;">✕</button>
      </div>
    </div>
    
    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 10px; margin-bottom: 12px;">
      <div style="background: rgba(255,255,255,0.05); border-radius: 8px; padding: 10px; text-align: center;">
        <div style="font-size: 10px; color: #888; text-transform: uppercase; letter-spacing: 0.5px;">Eye Contact</div>
        <div id="paragon-eye-contact" style="font-size: 24px; font-weight: 700; color: #4A90D9;">0%</div>
      </div>
      <div style="background: rgba(255,255,255,0.05); border-radius: 8px; padding: 10px; text-align: center;">
        <div style="font-size: 10px; color: #888; text-transform: uppercase; letter-spacing: 0.5px;">Posture</div>
        <div id="paragon-posture" style="font-size: 24px; font-weight: 700; color: #6C2BD9;">0%</div>
      </div>
    </div>
    
    <div style="background: rgba(255,255,255,0.05); border-radius: 8px; padding: 12px; text-align: center;">
      <div style="font-size: 10px; color: #888; text-transform: uppercase; letter-spacing: 0.5px;">Overall Presence</div>
      <div id="paragon-overall" style="font-size: 32px; font-weight: 700; margin-top: 2px;">0</div>
    </div>
    
    <div style="display: flex; justify-content: space-between; margin-top: 12px; padding-top: 12px; border-top: 1px solid rgba(255,255,255,0.06);">
      <span style="font-size: 10px; color: #555;" id="paragon-timestamp">--:--:--</span>
      <span style="font-size: 10px; color: #555;">● Live</span>
    </div>
  `;
  
  document.body.appendChild(overlayElement);
  
  document.getElementById('paragon-close-btn').addEventListener('click', () => {
    hideOverlay();
    chrome.runtime.sendMessage({ type: 'STOP_RECORDING' });
  });
  
  if (payload && payload.scores) {
    updateOverlayScores(payload.scores);
  }
  
  overlayVisible = true;
  makeDraggable(overlayElement);
}

function updateOverlayScores(scores) {
  if (!overlayElement) return;
  
  const eyeContactEl = document.getElementById('paragon-eye-contact');
  const postureEl = document.getElementById('paragon-posture');
  const overallEl = document.getElementById('paragon-overall');
  const statusDot = document.getElementById('paragon-status-dot');
  const timestampEl = document.getElementById('paragon-timestamp');
  
  if (eyeContactEl) {
    const val = Math.round(scores.eye_contact || 0);
    eyeContactEl.textContent = val + '%';
    eyeContactEl.style.color = val >= 70 ? '#2ECC71' : (val >= 40 ? '#F39C12' : '#E74C3C');
  }
  
  if (postureEl) {
    const val = Math.round(scores.posture || 0);
    postureEl.textContent = val + '%';
    postureEl.style.color = val >= 70 ? '#2ECC71' : (val >= 40 ? '#F39C12' : '#E74C3C');
  }
  
  if (overallEl) {
    const val = Math.round(scores.overall || 0);
    overallEl.textContent = val;
    overallEl.style.color = val >= 70 ? '#2ECC71' : (val >= 40 ? '#F39C12' : '#E74C3C');
  }
  
  if (statusDot) {
    statusDot.style.background = '#2ECC71';
  }
  
  if (timestampEl) {
    const date = new Date(scores.timestamp || Date.now());
    timestampEl.textContent = date.toLocaleTimeString();
  }
}

function hideOverlay() {
  if (overlayElement) {
    overlayElement.style.display = 'none';
    overlayVisible = false;
  }
}

function makeDraggable(element) {
  let pos1 = 0, pos2 = 0, pos3 = 0, pos4 = 0;
  
  element.addEventListener('mousedown', (e) => {
    if (e.target.tagName === 'BUTTON') return;
    e.preventDefault();
    pos3 = e.clientX;
    pos4 = e.clientY;
    document.onmousemove = (event) => {
      event.preventDefault();
      pos1 = pos3 - event.clientX;
      pos2 = pos4 - event.clientY;
      pos3 = event.clientX;
      pos4 = event.clientY;
      element.style.top = (element.offsetTop - pos2) + 'px';
      element.style.left = (element.offsetLeft - pos1) + 'px';
      element.style.right = 'auto';
      element.style.bottom = 'auto';
    };
    document.onmouseup = () => {
      document.onmousemove = null;
      document.onmouseup = null;
    };
  });
}

console.log('[Paragon IRIS] Content script loaded');