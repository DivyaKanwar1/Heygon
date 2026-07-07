let ws = null;
let isConnected = false;
let isRecording = false;
let stream = null;
let overlayTabId = null;
let currentScores = {
  eye_contact: 0,
  posture: 0,
  gestures: 0,
  overall: 0,
  timestamp: 0
};

function connectWebSocket() {
  const wsUrl = 'somethingparagaon.onrender.com';
  
  ws = new WebSocket(wsUrl);
  
  ws.onopen = () => {
    console.log('[Paragon IRIS] WebSocket connected');
    isConnected = true;
    updatePopupStatus('connected');
    setInterval(() => {
      if (ws && ws.readyState === WebSocket.OPEN) {
        ws.send(JSON.stringify({ type: 'ping' }));
      }
    }, 10000);
  };
  
  ws.onmessage = (event) => {
    try {
      const data = JSON.parse(event.data);
      if (data.type === 'scores') {
        currentScores = {
          eye_contact: data.eye_contact || 0,
          posture: data.posture || 0,
          gestures: data.gestures || 0,
          overall: data.overall || 0,
          timestamp: data.timestamp || Date.now()
        };
        updateOverlay(currentScores);
        updatePopupScores(currentScores);
      }
    } catch (e) {
      console.error('[Paragon IRIS] WebSocket message error:', e);
    }
  };
  
  ws.onclose = () => {
    console.log('[Paragon IRIS] WebSocket disconnected, reconnecting...');
    isConnected = false;
    updatePopupStatus('disconnected');
    setTimeout(connectWebSocket, 3000);
  };
  
  ws.onerror = (error) => {
    console.error('[Paragon IRIS] WebSocket error:', error);
  };
}

function updateOverlay(scores) {
  if (overlayTabId) {
    chrome.tabs.sendMessage(overlayTabId, {
      type: 'UPDATE_SCORES',
      payload: scores
    }).catch(() => {});
  }
}

function updatePopupScores(scores) {
  chrome.runtime.sendMessage({
    type: 'SCORES_UPDATE',
    payload: scores
  }).catch(() => {});
}

function updatePopupStatus(status) {
  chrome.runtime.sendMessage({
    type: 'STATUS_UPDATE',
    payload: { status, isConnected }
  }).catch(() => {});
}

function startRecording(tabId) {
  if (isRecording) return;
  
  chrome.tabCapture.capture({
    video: true,
    audio: true,
    videoConstraints: {
      mandatory: {
        minFrameRate: 15,
        maxFrameRate: 30
      }
    }
  }, (capturedStream) => {
    if (chrome.runtime.lastError) {
      console.error('[Paragon IRIS] Capture error:', chrome.runtime.lastError);
      return;
    }
    
    stream = capturedStream;
    isRecording = true;
    
    const videoTrack = stream.getVideoTracks()[0];
    const imageCapture = new ImageCapture(videoTrack);
    
    const sendFrame = async () => {
      if (!isRecording) return;
      
      try {
        const bitmap = await imageCapture.grabFrame();
        const canvas = document.createElement('canvas');
        canvas.width = bitmap.width;
        canvas.height = bitmap.height;
        const ctx = canvas.getContext('2d');
        ctx.drawImage(bitmap, 0, 0);
        
        const smallCanvas = document.createElement('canvas');
        smallCanvas.width = 320;
        smallCanvas.height = 240;
        const smallCtx = smallCanvas.getContext('2d');
        smallCtx.drawImage(canvas, 0, 0, 320, 240);
        
        const base64 = smallCanvas.toDataURL('image/jpeg', 0.6).split(',')[1];
        
        if (ws && ws.readyState === WebSocket.OPEN) {
          ws.send(JSON.stringify({
            type: 'frame',
            image: base64,
            timestamp: Date.now()
          }));
        }
      } catch (e) {}
      
      if (isRecording) {
        setTimeout(sendFrame, 200);
      }
    };
    
    sendFrame();
    openOverlay(tabId);
    updatePopupStatus('recording');
    console.log('[Paragon IRIS] Recording started');
  });
}

function stopRecording() {
  isRecording = false;
  if (stream) {
    stream.getTracks().forEach(track => track.stop());
    stream = null;
  }
  closeOverlay();
  updatePopupStatus('disconnected');
  console.log('[Paragon IRIS] Recording stopped');
}

function openOverlay(tabId) {
  chrome.scripting.executeScript({
    target: { tabId: tabId },
    files: ['content.js']
  }).then(() => {
    overlayTabId = tabId;
    chrome.tabs.sendMessage(tabId, {
      type: 'SHOW_OVERLAY',