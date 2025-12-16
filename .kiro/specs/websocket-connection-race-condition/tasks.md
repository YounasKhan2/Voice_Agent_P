# Implementation Plan

- [x] 1. Convert openTranscriptWS to return a Promise
  - Modify the `openTranscriptWS` function in `flask_frontend/static/js/voice-agent.js` to return a Promise
  - Wrap WebSocket creation in a Promise that resolves on `ws.onopen` and rejects on error or timeout
  - Add a 3-second timeout for WebSocket connection establishment
  - Preserve existing message handling, keepalive ping, and cleanup logic
  - _Requirements: 1.1, 1.2, 1.3_

- [x] 2. Update connect function to await WebSocket connection
  - Modify the `connect()` function to await the `openTranscriptWS()` call
  - Add try-catch block around WebSocket connection to handle failures
  - Ensure proper error handling and cleanup if WebSocket connection fails
  - Maintain existing initialization timeout behavior
  - _Requirements: 1.1, 1.2, 1.4_

- [x] 3. Enhance error logging and user feedback
  - Add console logging for WebSocket connection lifecycle events (opening, connected, failed, timeout)
  - Update error messages to distinguish between WebSocket timeout and other connection failures
  - Ensure agent status updates reflect WebSocket connection state
  - Add detailed error information to console for debugging
  - _Requirements: 2.1, 2.2, 2.3, 2.4, 3.1, 3.2, 3.3, 3.4_

- [x] 4. Verify and test the fix
  - Test normal connection flow to ensure no error popup appears
  - Verify agent status shows "Ready" after successful connection
  - Test with network throttling to ensure proper waiting behavior
  - Verify error handling for WebSocket connection failures
  - Check console logs for proper debugging information
  - _Requirements: 1.4, 2.1, 2.2, 2.3, 3.4_
