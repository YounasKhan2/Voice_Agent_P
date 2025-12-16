# Design Document

## Overview

This design addresses the race condition in the voice agent initialization where the `isAgentReady()` check occurs before the WebSocket connection has fully established. The solution involves making the WebSocket connection establishment awaitable and ensuring proper sequencing of initialization steps.

## Architecture

The fix involves modifying the connection flow in `flask_frontend/static/js/voice-agent.js` to:

1. Convert the WebSocket connection function to return a Promise that resolves when the connection is open
2. Await the WebSocket connection before performing the readiness check
3. Maintain proper error handling and timeout behavior

### Current Flow (Problematic)

```
connect() called
  ↓
fetchToken()
  ↓
Connect to LiveKit
  ↓
startAgent()
  ↓
openTranscriptWS() ← Asynchronous, returns immediately
  ↓
isAgentReady() ← Checks WebSocket immediately (may not be open yet)
  ↓
Error: "Agent initialization incomplete"
```

### Proposed Flow (Fixed)

```
connect() called
  ↓
fetchToken()
  ↓
Connect to LiveKit
  ↓
startAgent()
  ↓
await openTranscriptWS() ← Wait for WebSocket to open
  ↓
isAgentReady() ← WebSocket is guaranteed to be open
  ↓
Success: Agent ready
```

## Components and Interfaces

### Modified Functions

#### `openTranscriptWS(sessId)`

**Current Signature:**
```javascript
function openTranscriptWS(sessId) { ... }
```

**New Signature:**
```javascript
async function openTranscriptWS(sessId) {
  return new Promise((resolve, reject) => { ... });
}
```

**Behavior:**
- Creates WebSocket connection
- Returns a Promise that:
  - Resolves when `ws.onopen` fires
  - Rejects if connection fails or times out
- Maintains existing message handling logic
- Preserves keepalive ping functionality

#### `connect()`

**Modification:**
- Change from: `openTranscriptWS(sessionId);`
- Change to: `await openTranscriptWS(sessionId);`
- Add try-catch around WebSocket connection to handle failures
- Maintain existing timeout and error handling

#### `isAgentReady()`

**No changes required** - This function will now be called after WebSocket is confirmed open, so its checks will pass correctly.

## Data Models

No data model changes required. The fix is purely behavioral.

## Error Handling

### WebSocket Connection Errors

1. **Connection Timeout**: If WebSocket doesn't open within a reasonable time (e.g., 3 seconds), reject the Promise with a timeout error
2. **Connection Failure**: If WebSocket `onerror` fires, reject the Promise with connection error details
3. **Connection Close**: If WebSocket closes unexpectedly during initialization, reject the Promise

### Error Messages

- **Timeout**: "WebSocket connection timed out after 3 seconds"
- **Connection Failed**: "WebSocket connection failed: [error details]"
- **Unexpected Close**: "WebSocket closed unexpectedly during initialization"

### Fallback Behavior

If WebSocket connection fails:
1. Log detailed error to console
2. Clean up partial connections (LiveKit room, agent session)
3. Display user-friendly error message
4. Re-enable connect button for retry

## Testing Strategy

### Manual Testing

1. **Normal Connection Flow**
   - Start voice conversation
   - Verify no error popup appears
   - Verify agent status shows "Ready"
   - Verify conversation works correctly

2. **Slow Network Simulation**
   - Throttle network in browser DevTools
   - Start voice conversation
   - Verify initialization waits for WebSocket
   - Verify no premature errors

3. **WebSocket Failure**
   - Block WebSocket port or endpoint
   - Start voice conversation
   - Verify appropriate error message
   - Verify cleanup occurs properly

4. **Timeout Scenario**
   - Simulate very slow WebSocket connection
   - Verify timeout error after 3 seconds
   - Verify cleanup and retry capability

### Console Logging

Add detailed logging at each step:
- "Opening WebSocket connection..."
- "WebSocket connected successfully"
- "WebSocket connection failed: [error]"
- "WebSocket connection timed out"

### Success Criteria

- No "Agent initialization incomplete" errors during normal operation
- WebSocket connection completes before readiness check
- Proper error messages for actual connection failures
- Agent status accurately reflects connection state
