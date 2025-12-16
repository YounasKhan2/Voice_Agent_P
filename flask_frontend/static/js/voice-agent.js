/* global LivekitClient */
(function () {
  const transcriptEl = document.getElementById('transcript');
  const btnConnect = document.getElementById('btn-connect');
  const btnStop = document.getElementById('btn-stop');
  const roomInput = document.getElementById('room');
  const nameInput = document.getElementById('name');

  let room = null;
  let localMicTrack = null;
  let sessionId = null;
  let ws = null;
  let wsPingInterval = null;
  let micReady = false;
  
  // Track interim messages for proper ordering
  let currentInterimMessages = {
    agent: { text: null, messageId: null },
    user: { text: null, messageId: null }
  };
  let messageSequence = [];
  let messageIdCounter = 0;
  let isProcessingNewChat = false; // Flag to prevent concurrent New Chat operations

  function readAppConfig() {
    const el = document.getElementById('app-config');
    if (!el) return { fastapiBaseUrl: 'http://127.0.0.1:8000', livekitUrl: 'http://127.0.0.1:7880' };
    try {
      return JSON.parse(el.textContent);
    } catch (e) {
      console.warn('Failed to parse app config, using defaults', e);
      return { fastapiBaseUrl: 'http://127.0.0.1:8000', livekitUrl: 'http://127.0.0.1:7880' };
    }
  }

  const APP_CONFIG = readAppConfig();

  async function saveCurrentSession() {
    // 6.1: Handle empty session (no messages)
    // Check messageSequence length before saving
    if (!sessionId || messageSequence.length === 0) {
      console.log('No session to save (no sessionId or no messages)');
      // Skip save operation if no messages exist
      // Don't show error for empty sessions
      return null;
    }
    
    try {
      console.log(`Saving session ${sessionId} with ${messageSequence.length} messages`);
      
      // 6.2: Handle network failures during save
      // Set timeout for save operation (10 seconds)
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 10000);
      
      const response = await fetch(`${APP_CONFIG.djangoApiUrl}/users/sessions/save`, {
        method: 'POST',
        credentials: 'include',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          session_id: sessionId,
          messages: messageSequence
        }),
        signal: controller.signal
      });
      
      clearTimeout(timeoutId);
      
      // 6.4: Handle session save failures
      // Check response status code
      if (!response.ok) {
        // Parse error messages from API
        const errorData = await response.json().catch(() => ({}));
        const errorMessage = errorData.detail || `Failed to save session: ${response.status}`;
        
        // Show specific error messages to user
        if (window.showToast) {
          if (response.status === 401) {
            window.showToast('Please log in to save your conversation', 'error');
          } else if (response.status === 403) {
            window.showToast('You do not have permission to save this session', 'error');
          } else if (response.status === 404) {
            window.showToast('Session not found. It may have expired.', 'error');
          } else {
            window.showToast(`Failed to save conversation: ${errorMessage}`, 'error');
          }
        }
        
        throw new Error(errorMessage);
      }
      
      const savedSession = await response.json();
      console.log('Session saved successfully:', savedSession);
      return savedSession;
    } catch (error) {
      // 6.2: Handle network failures during save
      // Catch fetch errors and network timeouts
      console.error('Failed to save session:', error);
      
      // Log errors for debugging
      console.error('Error details:', {
        name: error.name,
        message: error.message,
        stack: error.stack
      });
      
      // Show user-friendly error message
      if (window.showToast) {
        if (error.name === 'AbortError') {
          window.showToast('Save operation timed out. Please check your connection and try again.', 'error');
        } else if (error.message.includes('fetch') || error.message.includes('network')) {
          window.showToast('Network error. Please check your connection and try again.', 'error');
        } else if (!error.message.includes('Failed to save session')) {
          // Only show generic error if we haven't already shown a specific one
          window.showToast('Failed to save conversation. Please try again.', 'error');
        }
      }
      
      throw error;
    }
  }

  function updateAgentStatus(state, text) {
    const agentStatus = document.getElementById('agent-status');
    if (!agentStatus) return;
    
    const statusDot = agentStatus.querySelector('.w-2');
    const statusText = agentStatus.querySelector('span');
    
    if (statusDot) {
      // Update status dot color based on state
      switch (state) {
        case 'ready':
          statusDot.className = 'w-2 h-2 rounded-full bg-green-500';
          break;
        case 'initializing':
          statusDot.className = 'w-2 h-2 rounded-full bg-yellow-500 animate-pulse';
          break;
        case 'error':
          statusDot.className = 'w-2 h-2 rounded-full bg-red-500';
          break;
        case 'speaking':
          statusDot.className = 'w-2 h-2 rounded-full bg-primary';
          break;
        default:
          statusDot.className = 'w-2 h-2 rounded-full bg-gray-500';
      }
    }
    
    if (statusText) {
      statusText.textContent = text;
    }
  }

  function isAgentReady() {
    console.log('=== Agent Readiness Check ===');
    
    // Check room connection state
    console.log('Checking LiveKit room connection...');
    if (!room) {
      console.error('✗ Room object is null or undefined');
      console.error('  - LiveKit room was not created');
      updateAgentStatus('error', 'Room Not Created');
      return false;
    }
    console.log('  Room state:', room.state);
    if (room.state !== 'connected') {
      console.error('✗ Room is not in connected state');
      console.error('  - Current state:', room.state);
      console.error('  - Expected state: connected');
      updateAgentStatus('error', 'Room Not Connected');
      return false;
    }
    console.log('✓ LiveKit room is connected');
    
    // Verify WebSocket connection is established
    console.log('Checking WebSocket connection...');
    if (!ws) {
      console.error('✗ WebSocket object is null or undefined');
      console.error('  - WebSocket was not created');
      updateAgentStatus('error', 'WebSocket Not Created');
      return false;
    }
    console.log('  WebSocket readyState:', ws.readyState);
    const readyStateNames = ['CONNECTING', 'OPEN', 'CLOSING', 'CLOSED'];
    console.log('  WebSocket state name:', readyStateNames[ws.readyState] || 'UNKNOWN');
    if (ws.readyState !== WebSocket.OPEN) {
      console.error('✗ WebSocket is not in OPEN state');
      console.error('  - Current state:', ws.readyState, '(' + (readyStateNames[ws.readyState] || 'UNKNOWN') + ')');
      console.error('  - Expected state:', WebSocket.OPEN, '(OPEN)');
      updateAgentStatus('error', 'WebSocket Not Open');
      return false;
    }
    console.log('✓ WebSocket is open and ready');
    
    // Ensure sessionId is set
    console.log('Checking session ID...');
    if (!sessionId) {
      console.error('✗ Session ID is not set');
      console.error('  - Agent session was not created or ID was not returned');
      updateAgentStatus('error', 'No Session ID');
      return false;
    }
    console.log('✓ Session ID is set:', sessionId);
    
    console.log('=== ✓ All Readiness Checks Passed ===');
    console.log('Agent is ready for interaction');
    return true;
  }

  function addMsg(role, text, final = true) {
    if (!text || text.trim() === '') return;
    
    const isAgent = role === 'agent';
    console.log(`addMsg - Role: ${role}, Final: ${final}, Text: "${text.substring(0, 50)}..."`);
    
    // Track final messages in sequence (for all UI paths)
    if (final) {
      // Ensure timestamp is in milliseconds
      const timestamp = Date.now();
      messageSequence.push({ role, text, timestamp });
      console.log(`✓ Added to messageSequence: ${role} message (total: ${messageSequence.length})`);
    }
    
    // Use new chat UI if available
    if (window.chatUI) {
      if (final) {
        console.log(`✓ FINAL message for ${role}`);
        
        // Remove any interim message for this role
        if (currentInterimMessages[role].messageId) {
          console.log(`  Removing interim message ID ${currentInterimMessages[role].messageId}`);
          window.chatUI.removeInterimMessage(role, currentInterimMessages[role].messageId);
        }
        
        // ALWAYS add new final message (never replace)
        console.log(`  Adding NEW final message`);
        window.chatUI.addMessage(text, isAgent);
        
        // Clear the interim tracking for this role
        currentInterimMessages[role] = { text: null, messageId: null };
      } else {
        // Skip interim messages - only show final messages
        console.log(`⋯ INTERIM message for ${role} - SKIPPED (showing final only)`);
      }
      return;
    }
    
    // Fallback to old transcript element if it exists
    if (!transcriptEl) return;
    
    const div = document.createElement('div');
    div.className = `msg ${role}`;
    const roleSpan = document.createElement('span');
    roleSpan.className = 'role';
    roleSpan.textContent = role === 'agent' ? 'Agent:' : 'You:';
    const textSpan = document.createElement('span');
    textSpan.textContent = text;
    if (!final) {
      textSpan.classList.add('muted');
    }
    div.appendChild(roleSpan);
    div.appendChild(textSpan);
    transcriptEl.appendChild(div);
    transcriptEl.scrollTop = transcriptEl.scrollHeight;
  }

  function addEvent(role, event) {
    // Handle speaking events with animations
    if (window.chatUI) {
      const isAgent = role === 'agent';
      
      if (event === 'speech_started' || event === 'speaking_started') {
        window.chatUI.showSpeakingAnimation(isAgent);
      } else if (event === 'speech_ended' || event === 'speaking_ended') {
        window.chatUI.hideSpeakingAnimation();
      }
    }
    
    // Don't show event messages in the new UI
    if (window.chatUI) return;
    
    // Fallback for old UI
    const text = `${role} ${event.replace('_', ' ')}`;
    addMsg(role, `(${text})`, true);
  }

  async function fetchToken(room, identity, name) {
    const url = new URL(APP_CONFIG.fastapiBaseUrl + '/token');
    url.searchParams.set('room', room);
    url.searchParams.set('identity', identity);
    if (name) url.searchParams.set('name', name);
    const res = await fetch(url.toString(), { method: 'GET' });
    if (!res.ok) throw new Error('Failed to fetch token: ' + res.status);
    const data = await res.json();
    return data.token;
  }

  async function startAgent(roomName, identity) {
    const res = await fetch(APP_CONFIG.fastapiBaseUrl + '/session', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ room: roomName, identity, system_prompt: APP_CONFIG.systemPrompt || undefined })
    });
    if (!res.ok) throw new Error('Failed to start session: ' + res.status);
    const data = await res.json();
    return data.session_id;
  }

  async function stopAgent(sessId) {
    const res = await fetch(APP_CONFIG.fastapiBaseUrl + '/session/' + encodeURIComponent(sessId), {
      method: 'DELETE'
    });
    if (!res.ok) throw new Error('Failed to stop session: ' + res.status);
    return true;
  }

  function openTranscriptWS(sessId) {
    return new Promise((resolve, reject) => {
      console.log('=== WebSocket Connection Starting ===');
      console.log('Session ID:', sessId);
      
      const base = APP_CONFIG.fastapiBaseUrl;
      const isSecure = base.startsWith('https://');
      const url = base.replace(/^http(s)?:\/\//, isSecure ? 'wss://' : 'ws://') + '/ws/transcript/' + encodeURIComponent(sessId);
      console.log('WebSocket URL:', url);
      console.log('Connection protocol:', isSecure ? 'wss (secure)' : 'ws (insecure)');
      
      // Update agent status to show WebSocket connecting
      updateAgentStatus('initializing', 'Connecting WebSocket...');
      
      // Set up 3-second timeout for connection
      const connectionTimeout = setTimeout(() => {
        console.error('=== WebSocket Connection TIMEOUT ===');
        console.error('Failed to establish WebSocket connection within 3 seconds');
        console.error('Possible causes:');
        console.error('  - Backend server not responding');
        console.error('  - Network connectivity issues');
        console.error('  - Firewall blocking WebSocket connections');
        console.error('Session ID:', sessId);
        
        // Update agent status to show timeout
        updateAgentStatus('error', 'WebSocket Timeout');
        
        if (ws) {
          ws.close();
        }
        reject(new Error('WebSocket connection timed out after 3 seconds'));
      }, 3000);
      
      ws = new WebSocket(url);
      console.log('WebSocket object created, waiting for connection...');
      
      ws.onopen = () => {
        console.log('=== WebSocket Connection SUCCESSFUL ===');
        console.log('WebSocket readyState:', ws.readyState, '(OPEN)');
        console.log('Session ID:', sessId);
        clearTimeout(connectionTimeout);
        
        // Update agent status to show WebSocket connected
        updateAgentStatus('initializing', 'WebSocket Connected');
        
        // keepalive pings to satisfy server receive loop
        wsPingInterval = setInterval(() => {
          try { 
            ws.send('ping');
            console.log('WebSocket keepalive ping sent');
          } catch (e) {
            console.warn('Failed to send WebSocket keepalive ping:', e);
          }
        }, 20000);
        
        console.log('WebSocket keepalive interval started (20s)');
        
        // Resolve the promise now that connection is established
        resolve();
      };
      
      ws.onerror = (error) => {
        console.error('=== WebSocket Connection ERROR ===');
        console.error('WebSocket error event:', error);
        console.error('Error type:', error.type);
        console.error('Error target readyState:', error.target?.readyState);
        console.error('Session ID:', sessId);
        console.error('Possible causes:');
        console.error('  - Backend server not running or unreachable');
        console.error('  - Invalid WebSocket endpoint');
        console.error('  - CORS or security policy blocking connection');
        console.error('  - Network error or DNS resolution failure');
        
        // Update agent status to show connection error
        updateAgentStatus('error', 'WebSocket Error');
        
        clearTimeout(connectionTimeout);
        reject(new Error('WebSocket connection failed'));
      };
      
      ws.onmessage = (ev) => {
        try {
          const payload = JSON.parse(ev.data);
          
          // Determine if message is final
          // If 'final' field is explicitly set, use it
          // If 'final' field is undefined, treat as final (default behavior)
          const isFinal = payload.final !== false;
          
          console.log('WebSocket message received:', { 
            role: payload.role, 
            hasText: !!payload.text, 
            textLength: payload.text?.length,
            event: payload.event,
            final: payload.final,
            isFinal: isFinal
          });
          
          if (payload.text) {
            addMsg(payload.role || 'agent', payload.text, isFinal);
          } else if (payload.event) {
            addEvent(payload.role || 'agent', payload.event);
          }
        } catch (e) {
          console.warn('Failed to parse WebSocket message:', e);
          console.warn('Raw message data:', ev.data);
        }
      };
      
      ws.onclose = (event) => {
        console.log('=== WebSocket Connection CLOSED ===');
        console.log('Close code:', event.code);
        console.log('Close reason:', event.reason || '(no reason provided)');
        console.log('Clean close:', event.wasClean);
        console.log('Session ID:', sessId);
        
        if (wsPingInterval) { 
          clearInterval(wsPingInterval); 
          wsPingInterval = null;
          console.log('WebSocket keepalive interval cleared');
        }
        
        // Update agent status if connection was closed unexpectedly
        if (!event.wasClean && room && room.state === 'connected') {
          console.warn('WebSocket closed unexpectedly while room still connected');
          updateAgentStatus('error', 'WebSocket Disconnected');
        }
      };
    });
  }

  async function connect() {
    console.log('=== CONNECT FUNCTION STARTED ===');
    const voiceButton = document.getElementById('voice-button');
    const connectBtn = btnConnect || voiceButton;
    const agentStatus = document.getElementById('agent-status');
    
    // Update agent status to initializing
    updateAgentStatus('initializing', 'Initializing...');
    
    if (connectBtn) {
      connectBtn.setAttribute('aria-busy', 'true');
      connectBtn.disabled = true;
    }
    
    // Set up initialization timeout (5 seconds)
    const initTimeout = setTimeout(() => {
      console.error('Agent initialization timeout');
      updateAgentStatus('error', 'Timeout');
      throw new Error('Agent initialization timed out after 5 seconds');
    }, 5000);
    
    try {
      const roomName = (roomInput?.value?.trim() || APP_CONFIG.defaultRoom || 'quickstart');
      const displayName = (nameInput?.value?.trim() || APP_CONFIG.user?.display_name || 'Guest');
      const identity = displayName + '-' + Math.random().toString(36).slice(2, 8);
      
      console.log('Connection params:', { roomName, displayName, identity });
      console.log('FastAPI URL:', APP_CONFIG.fastapiBaseUrl);
      console.log('LiveKit URL:', APP_CONFIG.livekitUrl);

      // 1) Fetch client token from FastAPI
      console.log('Step 1: Fetching token...');
      const token = await fetchToken(roomName, identity, displayName);
      console.log('Token received:', token ? 'YES' : 'NO');

      // 2) Connect to LiveKit and publish microphone
      console.log('Step 2: Connecting to LiveKit...');
      console.log('LivekitClient available:', typeof LivekitClient !== 'undefined');
      const { Room, createLocalAudioTrack } = LivekitClient;
      room = new Room();
      await room.connect(APP_CONFIG.livekitUrl, token);
      console.log('LiveKit connected, room state:', room.state);

      // Attach remote audio tracks to hidden audio element for playback
      const agentAudioEl = document.getElementById('agent-audio');
      room.on('trackSubscribed', (track, publication, participant) => {
        if (track.kind === 'audio' && agentAudioEl) {
          try {
            // Preferred: use LiveKit helper to attach the track to element
            track.attach(agentAudioEl);
          } catch (_) {
            // Fallback: create a MediaStream
            try {
              const mediaStream = new MediaStream();
              mediaStream.addTrack(track.mediaStreamTrack);
              agentAudioEl.srcObject = mediaStream;
            } catch (e) {
              console.warn('Failed to bind remote audio track', e);
            }
          }
        }
      });

      // If pre-permission already granted, this should not reprompt
      console.log('Step 3: Creating local audio track...');
      localMicTrack = await createLocalAudioTrack({ echoCancellation: true, noiseSuppression: true });
      console.log('Local mic track created');
      await room.localParticipant.publishTrack(localMicTrack);
      console.log('Mic track published');

      // Attempt to start audio playback; browsers may require user gesture
      try { await room.startAudio(); } catch (_) {
        console.warn('room.startAudio() blocked until user gesture');
      }

      // 3) Start server-side agent session via FastAPI
      console.log('Step 4: Starting agent session...');
      sessionId = await startAgent(roomName, identity);
      console.log('Agent session started, ID:', sessionId);

      // 4) Open WS to receive transcripts and events
      console.log('Step 5: Opening WebSocket...');
      try {
        await openTranscriptWS(sessionId);
        console.log('✓ WebSocket connection established successfully');
      } catch (wsError) {
        console.error('=== WebSocket Connection Failed ===');
        console.error('Error message:', wsError.message);
        console.error('Error stack:', wsError.stack);
        
        // Determine error type for better user feedback
        const isTimeout = wsError.message.includes('timed out');
        const errorType = isTimeout ? 'TIMEOUT' : 'CONNECTION_FAILED';
        console.error('Error type:', errorType);
        
        if (isTimeout) {
          console.error('WebSocket connection timeout details:');
          console.error('  - Connection attempt exceeded 3 second limit');
          console.error('  - Backend may be slow to respond or unreachable');
          console.error('  - Check backend server status and network connectivity');
        } else {
          console.error('WebSocket connection failure details:');
          console.error('  - Connection was rejected or failed to establish');
          console.error('  - Backend server may not be running');
          console.error('  - WebSocket endpoint may be incorrect or blocked');
        }
        
        // Update agent status to show specific error
        updateAgentStatus('error', isTimeout ? 'WebSocket Timeout' : 'WebSocket Failed');
        
        // Clean up partial connections before throwing
        console.log('Cleaning up partial connections...');
        if (localMicTrack) {
          localMicTrack.stop();
          localMicTrack = null;
          console.log('  ✓ Microphone track stopped');
        }
        if (room) {
          await room.disconnect();
          room = null;
          console.log('  ✓ LiveKit room disconnected');
        }
        if (sessionId) {
          try { 
            await stopAgent(sessionId);
            console.log('  ✓ Agent session stopped');
          } catch (stopError) {
            console.warn('  ⚠ Failed to stop agent session:', stopError);
          }
          sessionId = null;
        }
        console.log('Cleanup complete');
        
        // Throw error with more specific message
        const userMessage = isTimeout 
          ? 'WebSocket connection timed out. The backend server may be slow or unreachable.'
          : 'WebSocket connection failed. Please check that the backend server is running.';
        throw new Error(userMessage);
      }

      // Clear initialization timeout
      clearTimeout(initTimeout);
      console.log('✓ Initialization timeout cleared');

      // Verify agent readiness before enabling UI
      console.log('Step 6: Verifying agent readiness...');
      if (!isAgentReady()) {
        throw new Error('Agent initialization incomplete');
      }
      console.log('✓ Agent readiness verified');

      if (btnStop) {
        btnStop.disabled = false;
        console.log('✓ Stop button enabled');
      }
      
      // Update voice button to show active state
      const voiceButton = document.getElementById('voice-button');
      if (voiceButton) {
        voiceButton.classList.add('bg-red-500', 'hover:bg-red-600');
        voiceButton.classList.remove('bg-primary', 'hover:bg-primary-hover');
        voiceButton.querySelector('.material-symbols-outlined').textContent = 'mic_off';
        voiceButton.setAttribute('aria-label', 'Stop voice conversation');
        console.log('✓ Voice button updated to active state');
      }
      
      // Update agent status to ready
      console.log('Updating agent status to Ready...');
      updateAgentStatus('ready', 'Ready');
      console.log('✓ Agent status updated to Ready');
      
      console.log('=== CONNECTION SUCCESSFUL ===');
      console.log('All systems ready:');
      console.log('  ✓ LiveKit room connected');
      console.log('  ✓ Microphone track published');
      console.log('  ✓ Agent session started');
      console.log('  ✓ WebSocket connection established');
      console.log('  ✓ Agent status: Ready');
      console.log('User can now start talking');
      
      addMsg('agent', 'Connected. You can start talking.');
    } catch (e) {
      // Clear initialization timeout
      clearTimeout(initTimeout);
      
      console.error('=== CONNECTION FAILED ===');
      console.error('Error type:', e.constructor.name);
      console.error('Error message:', e.message);
      console.error('Full error:', e);
      console.error('Stack:', e.stack);
      
      // Categorize error for better user feedback
      const errorMessage = (e && e.message || '').toLowerCase();
      let errorCategory = 'UNKNOWN';
      let userMessage = '';
      let statusText = 'Error';
      
      if (errorMessage.includes('failed to fetch')) {
        errorCategory = 'BACKEND_UNREACHABLE';
        statusText = 'Backend Unreachable';
        userMessage = 'Could not reach backend at ' + APP_CONFIG.fastapiBaseUrl + '. Is FastAPI running on port 8000?';
        console.error('Error category: Backend server unreachable');
        console.error('  - Check if FastAPI backend is running');
        console.error('  - Verify backend URL:', APP_CONFIG.fastapiBaseUrl);
        console.error('  - Check network connectivity');
      } else if (errorMessage.includes('websocket') && errorMessage.includes('timed out')) {
        errorCategory = 'WEBSOCKET_TIMEOUT';
        statusText = 'WebSocket Timeout';
        userMessage = 'WebSocket connection timed out. The backend server may be slow or unreachable. Please try again.';
        console.error('Error category: WebSocket connection timeout');
        console.error('  - WebSocket failed to connect within 3 seconds');
        console.error('  - Backend may be overloaded or network is slow');
        console.error('  - Try again or check backend server status');
      } else if (errorMessage.includes('websocket')) {
        errorCategory = 'WEBSOCKET_FAILED';
        statusText = 'WebSocket Failed';
        userMessage = 'WebSocket connection failed. Please check that the backend server is running and try again.';
        console.error('Error category: WebSocket connection failed');
        console.error('  - WebSocket connection was rejected or failed');
        console.error('  - Backend server may not be running');
        console.error('  - Check backend logs for errors');
      } else if (errorMessage.includes('timeout') || errorMessage.includes('timed out')) {
        errorCategory = 'INITIALIZATION_TIMEOUT';
        statusText = 'Initialization Timeout';
        userMessage = 'Agent initialization timed out after 5 seconds. Please try again.';
        console.error('Error category: General initialization timeout');
        console.error('  - Overall initialization exceeded 5 second limit');
        console.error('  - One or more connection steps took too long');
      } else if (errorMessage.includes('agent initialization incomplete')) {
        errorCategory = 'READINESS_CHECK_FAILED';
        statusText = 'Not Ready';
        userMessage = 'Agent initialization incomplete. One or more connections failed to establish properly.';
        console.error('Error category: Agent readiness check failed');
        console.error('  - Room state:', room?.state);
        console.error('  - WebSocket state:', ws?.readyState);
        console.error('  - Session ID:', sessionId);
      } else {
        errorCategory = 'UNKNOWN';
        statusText = 'Error';
        userMessage = 'Connection failed: ' + (e && e.message || e);
        console.error('Error category: Unknown error');
        console.error('  - Unexpected error during connection');
        console.error('  - See error details above');
      }
      
      console.error('Final error category:', errorCategory);
      
      // Update agent status with specific error
      updateAgentStatus('error', statusText);
      
      // Show user-friendly error message
      alert('Connect failed: ' + userMessage);
      
      const connectBtn = btnConnect || document.getElementById('voice-button');
      if (connectBtn) connectBtn.disabled = false;
      
      // Re-throw to allow caller to handle
      throw e;
    } finally {
      const connectBtn = btnConnect || document.getElementById('voice-button');
      if (connectBtn) connectBtn.removeAttribute('aria-busy');
    }
  }

  async function cleanup(saveSession = false) {
    // Save current session if requested
    if (saveSession) {
      try {
        await saveCurrentSession();
      } catch (error) {
        console.error('Error saving session during cleanup:', error);
        // Continue with cleanup even if save fails
      }
    }
    
    // Hide speaking animations
    if (window.chatUI) {
      window.chatUI.hideSpeakingAnimation();
      
      // Clear any interim messages
      if (currentInterimMessages.agent.messageId) {
        window.chatUI.removeInterimMessage('agent', currentInterimMessages.agent.messageId);
      }
      if (currentInterimMessages.user.messageId) {
        window.chatUI.removeInterimMessage('user', currentInterimMessages.user.messageId);
      }
    }
    
    // Reset interim tracking
    currentInterimMessages = {
      agent: { text: null, messageId: null },
      user: { text: null, messageId: null }
    };
    messageSequence = [];
    messageIdCounter = 0;
    
    // Close WS
    try { if (ws) ws.close(); } catch (_) {}
    ws = null;
    if (wsPingInterval) { clearInterval(wsPingInterval); wsPingInterval = null; }

    // Stop agent session
    if (sessionId) {
      try { await stopAgent(sessionId); } catch (_) {}
      sessionId = null;
    }

    // Unpublish and disconnect LiveKit
    try {
      if (localMicTrack) {
        localMicTrack.stop();
        localMicTrack = null;
      }
      if (room) {
        await room.disconnect();
        room = null;
      }
    } catch (_) {}

    // Reset voice button
    const voiceButton = document.getElementById('voice-button');
    if (voiceButton) {
      voiceButton.classList.remove('bg-red-500', 'hover:bg-red-600');
      voiceButton.classList.add('bg-primary', 'hover:bg-primary-hover');
      voiceButton.querySelector('.material-symbols-outlined').textContent = 'mic';
      voiceButton.setAttribute('aria-label', 'Start voice conversation');
      voiceButton.disabled = false;
    }
    
    if (btnStop) btnStop.disabled = true;
    if (btnConnect) btnConnect.disabled = false;
  }

  async function startNewChat() {
    // 6.3: Handle concurrent New Chat clicks
    // Ignore clicks while operation in progress
    if (isProcessingNewChat) {
      console.log('New chat operation already in progress, ignoring click');
      return;
    }
    
    // Use flag to track operation state
    isProcessingNewChat = true;
    
    // Disable button during processing
    const newChatBtn = document.getElementById('new-chat-btn') || document.getElementById('new-chat-button');
    const newChatIcon = document.getElementById('new-chat-icon');
    const newChatText = document.getElementById('new-chat-text');
    
    if (newChatBtn) {
      newChatBtn.disabled = true;
      newChatBtn.classList.add('opacity-75', 'cursor-not-allowed');
      
      // Update button text to show processing
      const originalText = newChatText ? newChatText.textContent : 'New Chat';
      if (newChatIcon) {
        newChatIcon.textContent = 'hourglass_empty';
        newChatIcon.classList.add('animate-spin');
      }
      if (newChatText) {
        newChatText.textContent = 'Saving...';
      }
      
      // Store original text for restoration
      newChatBtn.dataset.originalText = originalText;
    }
    
    console.log('Starting new chat...');
    
    try {
      // Update status to show processing
      updateAgentStatus('initializing', 'Saving...');
      
      // 6.1: Handle empty session (no messages)
      // Check if there are messages to save
      const hasMessages = messageSequence.length > 0;
      
      if (hasMessages) {
        // Save current session
        try {
          await saveCurrentSession();
          console.log('Session saved successfully');
        } catch (saveError) {
          // 6.4: Don't proceed with new chat if save fails
          console.error('Save failed, aborting new chat:', saveError);
          
          // Offer retry option
          if (window.showToast && confirm('Failed to save your conversation. Would you like to try again?')) {
            // Retry save operation
            try {
              await saveCurrentSession();
              console.log('Session saved successfully on retry');
            } catch (retryError) {
              console.error('Retry failed:', retryError);
              throw new Error('Failed to save conversation after retry');
            }
          } else {
            throw new Error('Save operation cancelled by user');
          }
        }
      } else {
        // 6.1: Proceed directly to cleanup and new session for empty sessions
        console.log('Empty session, skipping save');
      }
      
      // Cleanup current session
      await cleanup(false); // Don't save again, we already did it above
      
      // Clear message tracking
      messageSequence = [];
      messageIdCounter = 0;
      currentInterimMessages = {
        agent: { text: null, messageId: null },
        user: { text: null, messageId: null }
      };
      
      // Clear UI
      const messagesContainer = document.getElementById('messages-container');
      if (messagesContainer) {
        messagesContainer.innerHTML = '';
      }
      
      // Show empty state
      const emptyState = document.getElementById('empty-state');
      if (emptyState) {
        emptyState.style.display = 'flex';
      }
      
      // Update conversation title
      const titleEl = document.getElementById('conversation-title');
      if (titleEl) {
        titleEl.textContent = 'New Conversation';
      }
      
      // Update button text to show initialization
      if (newChatBtn) {
        const btnText = newChatBtn.querySelector('.btn-text');
        if (btnText) btnText.textContent = 'Initializing...';
      }
      
      // Update status to show initialization
      updateAgentStatus('initializing', 'Initializing...');
      
      // Initialize new agent session
      console.log('Initializing new agent session...');
      await connect();
      
      // Verify agent is ready
      if (!isAgentReady()) {
        throw new Error('Agent failed to initialize properly');
      }
      
      console.log('New chat started successfully');
      
      // Show success message
      if (window.showToast) {
        window.showToast('New conversation started', 'success');
      }
    } catch (error) {
      console.error('Failed to start new chat:', error);
      updateAgentStatus('error', 'Error');
      
      // Show error message if not already shown
      if (window.showToast && !error.message.includes('cancelled by user')) {
        window.showToast('Failed to start new conversation. Please try again.', 'error');
      }
      
      // Don't re-throw, just log the error
      console.error('New chat error details:', error);
    } finally {
      // 6.3: Re-enable button only after completion or error
      isProcessingNewChat = false;
      
      if (newChatBtn) {
        newChatBtn.disabled = false;
        newChatBtn.classList.remove('opacity-75', 'cursor-not-allowed');
        
        // Restore original button text
        if (newChatIcon) {
          newChatIcon.textContent = 'add';
          newChatIcon.classList.remove('animate-spin');
        }
        if (newChatText && newChatBtn.dataset.originalText) {
          newChatText.textContent = newChatBtn.dataset.originalText;
        }
      }
    }
  }

  // Expose startNewChat globally for button handler
  window.startNewChat = startNewChat;

  // Handle voice button click (toggle connect/disconnect)
  const voiceButton = document.getElementById('voice-button');
  if (voiceButton) {
    console.log('Voice button found, attaching click handler');
    voiceButton.addEventListener('click', () => {
      console.log('Voice button clicked!', { roomState: room?.state, connected: room && room.state === 'connected' });
      
      if (room && room.state === 'connected') {
        // Verify agent is ready before allowing disconnect
        if (!isAgentReady()) {
          console.warn('Agent not ready, preventing disconnect');
          updateAgentStatus('error', 'Not Ready');
          alert('Agent is not ready. Please wait for initialization to complete.');
          return;
        }
        
        // Disconnect
        console.log('Disconnecting...');
        voiceButton.setAttribute('aria-busy', 'true');
        cleanup().finally(() => voiceButton.removeAttribute('aria-busy'));
      } else {
        // Connect
        console.log('Connecting...');
        connect().catch(error => {
          console.error('Connection failed:', error);
          // Error already handled in connect() function
        });
      }
    });
  } else {
    console.error('Voice button not found!');
  }
  
  // Fallback for old UI buttons
  if (btnConnect) {
    btnConnect.addEventListener('click', () => {
      connect();
    });
  }

  if (btnStop) {
    btnStop.addEventListener('click', () => {
      btnStop.setAttribute('aria-busy', 'true');
      cleanup().finally(() => btnStop.removeAttribute('aria-busy'));
    });
  }

  // Request mic permission on page load and prefill defaults
  async function prewarmMic() {
    try {
      console.log('Prewarming microphone...');
      
      // Show defaults in the form if elements exist
      if (roomInput && (!roomInput.value || roomInput.value.trim() === '')) {
        roomInput.value = (APP_CONFIG.defaultRoom || 'quickstart');
      }
      if (nameInput && (!nameInput.value || nameInput.value.trim() === '')) {
        nameInput.value = APP_CONFIG.user?.display_name || 'Guest';
      }

      // Ask for mic permission early
      if (navigator?.mediaDevices?.getUserMedia) {
        const stream = await navigator.mediaDevices.getUserMedia({ audio: { echoCancellation: true } });
        // Immediately stop tracks; permission is cached by the browser
        stream.getTracks().forEach(t => t.stop());
        console.log('Microphone permission granted');
      }

      // Auto-connect for voice-only interface
      // For new UI with voice button, auto-connect on page load
      const voiceBtn = document.getElementById('voice-button');
      if (voiceBtn && !btnConnect) {
        console.log('Auto-connecting...');
        updateAgentStatus('initializing', 'Initializing...');
        
        try {
          await connect();
          
          // Verify agent is ready after connection
          if (!isAgentReady()) {
            console.warn('Agent not ready after auto-connect');
            updateAgentStatus('error', 'Not Ready');
          }
        } catch (error) {
          console.error('Auto-connect failed:', error);
          updateAgentStatus('error', 'Error');
          // Allow user to manually retry by clicking the button
        }
      }
    } catch (e) {
      console.warn('Mic permission prewarm failed or blocked:', e);
      updateAgentStatus('error', 'Mic Blocked');
      // Do not auto-connect if permission failed; let user click the button
    }
  }

  window.addEventListener('DOMContentLoaded', prewarmMic);
})();
