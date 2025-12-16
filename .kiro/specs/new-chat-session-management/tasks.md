# Implementation Plan

- [x] 1. Create Django API endpoint for saving sessions
  - [x] 1.1 Implement `save_session_view` function in `django_persistence/conversation/views.py`
    - Accept POST request with session_id and messages array
    - Validate session_id exists in database
    - Associate session with authenticated user via user_account FK
    - Set ended_at timestamp to mark session as complete
    - Create missing utterances from messages array using bulk_create
    - Return serialized session metadata
    - _Requirements: 1.1, 1.4, 2.1, 2.2, 2.3, 2.5, 3.1, 3.2_
  
  - [x] 1.2 Add URL route for save session endpoint
    - Add path to `django_persistence/conversation/urls.py`
    - Map to `save_session_view` function
    - Use path `users/sessions/save`
    - _Requirements: 1.1, 2.1_
  
  - [ ]* 1.3 Write unit tests for save session endpoint
    - Test successful session save with authentication
    - Test session association with correct user
    - Test rejection of unauthenticated requests (401)
    - Test prevention of cross-user session access (403)
    - Test handling of missing session_id (400)
    - Test handling of non-existent session (404)
    - _Requirements: 1.1, 2.1, 2.5_

- [x] 2. Implement frontend session save functionality
  - [x] 2.1 Add saveCurrentSession function to voice-agent.js
    - Check if sessionId exists and messageSequence has messages
    - Return null if nothing to save
    - Make POST request to Django API with session_id and messages
    - Include credentials for authentication
    - Handle response and errors
    - Return saved session data
    - _Requirements: 1.1, 2.1, 2.4, 3.2_
  
  - [x] 2.2 Enhance cleanup function in voice-agent.js
    - Add optional saveSession parameter (default false)
    - Call saveCurrentSession if saveSession is true
    - Maintain existing cleanup logic (hide animations, clear interim, close WS, stop agent, disconnect LiveKit)
    - Reset UI state (button, status indicators)
    - _Requirements: 1.1, 1.2, 1.3, 2.1_
  
  - [x] 2.3 Create startNewChat function in voice-agent.js
    - Call cleanup with saveSession=true to save current session
    - Clear messageSequence array
    - Reset messageIdCounter to 0
    - Reset currentInterimMessages tracking object
    - Clear messages container innerHTML
    - Show empty state element
    - Update conversation title to "New Conversation"
    - Call connect() to initialize new agent session
    - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.5, 5.1, 5.2, 5.3, 5.4_
  
  - [ ]* 2.4 Add error handling for session save operations
    - Wrap saveCurrentSession in try-catch
    - Log errors to console
    - Show user-friendly error toast message
    - Prevent proceeding with new chat if save fails
    - Add timeout handling (10 seconds)
    - Implement retry logic for network failures
    - _Requirements: 2.1, 4.3_

- [x] 3. Wire New Chat button to session management
  - [x] 3.1 Add click handler for New Chat button in chat.html
    - Find New Chat button element by class or ID
    - Attach click event listener
    - Call startNewChat function when clicked
    - Disable button during processing
    - Show loading indicator
    - Re-enable button after completion
    - _Requirements: 1.1, 1.2, 1.3, 4.1, 4.2, 5.5_
  
  - [x] 3.2 Add loading indicator for New Chat operation
    - Show spinner or loading text on button during save
    - Disable button to prevent double-clicks
    - Update button text to "Saving..." during operation
    - Restore original state after completion
    - _Requirements: 4.1, 4.2, 5.1_
  
  - [x] 3.3 Update UI to show session status
    - Update conversation title when new session starts
    - Show session ID or timestamp in UI (optional)
    - Update agent status indicator during transitions
    - Clear any error states from previous session
    - _Requirements: 5.1, 5.2, 5.3_

- [x] 4. Implement message sequence tracking
  - [x] 4.1 Update addMsg function to track final messages
    - When final=true, append message to messageSequence array
    - Include role, text, and timestamp in message object
    - Ensure timestamp is in milliseconds
    - Maintain chronological order
    - _Requirements: 1.4, 1.5, 3.2, 3.5_
  
  - [x] 4.2 Ensure interim messages are also saved to sequence
    - track all messages
    - Interim messages should update UI and be saved
    - Verify finalizeInterimMessage properly marks messages as final
    - _Requirements: 1.4, 3.2_

- [x] 5. Update session initialization flow
  - [x] 5.1 Ensure agent initializes before UI is ready
    - Wait for connect() promise to resolve
    - Show loading indicator during initialization
    - Display error if initialization fails
    - Update agent status indicator when ready
    - _Requirements: 4.1, 4.2, 4.3, 4.4_
  
  - [x] 5.2 Add agent readiness verification
    - Check room connection state before accepting input
    - Verify WebSocket connection is established
    - Ensure sessionId is set before allowing interaction
    - Display appropriate status messages
    - _Requirements: 4.2, 4.3_
  
  - [x] 5.3 Implement initialization timeout handling
    - Set 5-second timeout for agent initialization
    - Show error message if timeout occurs
    - Allow user to retry initialization
    - Log timeout events for monitoring
    - _Requirements: 4.4_

- [x] 6. Handle edge cases and error scenarios
  - [x] 6.1 Handle empty session (no messages)
    - Check messageSequence length before saving
    - Skip save operation if no messages exist
    - Proceed directly to cleanup and new session
    - Don't show error for empty sessions
    - _Requirements: 2.4_
  
  - [x] 6.2 Handle network failures during save
    - Catch fetch errors and network timeouts
    - Show user-friendly error message
    - Offer retry option
    - Log errors for debugging
    - _Requirements: 2.1, 4.3_
  
  - [x] 6.3 Handle concurrent New Chat clicks
    - Disable button during processing
    - Ignore clicks while operation in progress
    - Use flag to track operation state
    - Re-enable button only after completion or error
    - _Requirements: 1.1, 4.1_
  
  - [x] 6.4 Handle session save failures
    - Check response status code
    - Parse error messages from API
    - Show specific error messages to user
    - Don't proceed with new chat if save fails
    - _Requirements: 2.1, 4.3_

- [x] 7. Verify history integration
  - [x] 7.1 Test saved sessions appear in history list
    - Navigate to history page after saving session
    - Verify session appears in list
    - Check session metadata (timestamp, message count)
    - Verify sessions are ordered by most recent first
    - _Requirements: 3.1, 3.3, 3.4_
  
  - [x] 7.2 Test session detail view shows saved messages
    - Click on saved session in history
    - Verify all messages are displayed
    - Check message order is preserved
    - Verify transcriptions are included
    - _Requirements: 3.2, 3.5_
  
  - [x] 7.3 Verify session ownership and access control
    - Test that users can only see their own sessions
    - Verify cross-user access is prevented
    - Test unauthenticated access is blocked
    - _Requirements: 2.5, 3.1_

- [ ]* 8. Add integration tests for complete flow
  - [ ]* 8.1 Test end-to-end new chat flow
    - Start voice conversation
    - Send multiple messages
    - Click New Chat button
    - Verify session saved to history
    - Verify UI cleared
    - Verify new session initialized
    - Verify new session has different ID
    - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.5, 2.1, 2.2, 2.3, 2.4, 2.5, 3.1, 3.2, 3.3, 3.4, 3.5, 4.1, 4.2, 4.3, 4.4, 5.1, 5.2, 5.3, 5.4, 5.5_
  
  - [ ]* 8.2 Test multiple consecutive new chats
    - Create first conversation
    - Click New Chat
    - Create second conversation
    - Click New Chat
    - Create third conversation
    - Verify all three sessions in history
    - Verify each session has correct messages
    - _Requirements: 1.1, 2.1, 3.1, 3.4_
  
  - [ ]* 8.3 Test error recovery scenarios
    - Simulate network failure during save
    - Verify error message displayed
    - Verify retry functionality works
    - Verify session not lost on error
    - _Requirements: 2.1, 4.3_
