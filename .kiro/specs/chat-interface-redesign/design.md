# Design Document

## Overview

This design document outlines the technical approach for redesigning the chat interface to match the modern Stitch-generated design. The redesign will transform the current basic voice agent interface into a polished, professional chat application with a sidebar navigation, improved message display, and comprehensive dark mode support.

The design leverages Tailwind CSS for styling consistency and uses the Plus Jakarta Sans font family for modern typography. The interface will maintain the existing Flask backend integration while significantly enhancing the frontend user experience.

## Architecture

### Component Structure

```
Chat Interface
├── Sidebar Component
│   ├── Brand Header (Logo + Name)
│   ├── New Chat Button
│   ├── Recent Chats List
│   └── User Actions (Account, Settings)
├── Main Chat Panel
│   ├── Chat Header (Title + Status)
│   ├── Messages Container (Scrollable)
│   │   ├── Agent Message Bubbles
│   │   └── User Message Bubbles
│   └── Input Area
│       ├── Quick Action Buttons
│       └── Message Input + Send Button
└── Shared Utilities
    ├── Dark Mode Handler
    ├── WebSocket Manager (existing)
    └── LiveKit Integration (existing)
```

### Technology Stack

- **Frontend Framework**: Flask templates with Jinja2
- **CSS Framework**: Tailwind CSS (via CDN)
- **Typography**: Plus Jakarta Sans (Google Fonts)
- **Icons**: Material Symbols Outlined
- **Real-time Communication**: LiveKit (existing)
- **WebSocket**: FastAPI WebSocket (existing)
- **JavaScript**: Vanilla JS for interactions

### Integration Points

1. **Existing Voice Agent**: Maintain LiveKit integration for voice functionality
2. **WebSocket Transcripts**: Continue displaying transcripts in the new message bubble format
3. **User Authentication**: Integrate with existing Flask session management
4. **Chat History**: Connect to existing history endpoints for sidebar population

## Components and Interfaces

### 1. Sidebar Component

**Purpose**: Provide navigation and access to chat history

**Structure**:
```html
<aside class="sidebar">
  <div class="sidebar-header">
    <img src="logo" alt="Logo" />
    <div class="brand-info">
      <h1>WanderBot</h1>
      <p>AI Travel Agent</p>
    </div>
  </div>
  
  <button class="new-chat-btn">
    <icon>add</icon>
    <span>New Chat</span>
  </button>
  
  <div class="recent-chats">
    <p class="section-label">Recent Chats</p>
    <a href="#" class="chat-item">...</a>
  </div>
  
  <div class="user-actions">
    <a href="/profile">My Account</a>
    <a href="/settings">Settings</a>
  </div>
</aside>
```

**Styling**:
- Fixed width: 288px (18rem)
- Background: `bg-white/5 dark:bg-black/10`
- Full height with flex column layout
- Padding: 1rem (16px)

**Behavior**:
- Highlight active chat with `bg-primary/20` background
- Hover effects on chat items: `hover:bg-black/5 dark:hover:bg-white/5`
- Fetch chat history from `/api/history` endpoint
- New Chat button creates new session and redirects

### 2. Message Bubble Component

**Purpose**: Display individual chat messages with sender identification

**Agent Message Structure**:
```html
<div class="message-container agent">
  <img src="agent-avatar" class="avatar" />
  <div class="message-content">
    <p class="sender-name">WanderBot</p>
    <div class="message-bubble agent-bubble">
      <p>Message text...</p>
    </div>
  </div>
</div>
```

**User Message Structure**:
```html
<div class="message-container user">
  <div class="message-content">
    <p class="sender-name">You</p>
    <div class="message-bubble user-bubble">
      <p>Message text...</p>
    </div>
  </div>
  <img src="user-avatar" class="avatar" />
</div>
```

**Styling**:
- Avatar: 40px circular image
- Agent bubble: `bg-gray-200 dark:bg-[#233648]`, rounded-xl with `rounded-bl-none`
- User bubble: `bg-primary text-white`, rounded-xl with `rounded-br-none`
- Max width: 512px (32rem)
- Padding: 12px 16px
- Font size: 1rem (16px)
- Line height: 1.5 (relaxed)

**Behavior**:
- Auto-scroll to latest message on new message arrival
- Maintain scroll position when user manually scrolls up
- Display timestamp on hover (optional enhancement)

### 3. Chat Header Component

**Purpose**: Display current conversation context and status

**Structure**:
```html
<header class="chat-header">
  <div class="header-content">
    <h2 class="conversation-title">Tokyo Flights</h2>
    <div class="status-indicator">
      <div class="status-dot online"></div>
      <p class="status-text">Online</p>
    </div>
  </div>
</header>
```

**Styling**:
- Height: 64px (4rem)
- Border bottom: `border-gray-200 dark:border-white/10`
- Padding: 0 24px
- Fixed position at top of main panel
- Background: inherits from main panel

**Behavior**:
- Display current room/session name
- Show online/offline status based on LiveKit connection
- Update title when switching conversations

### 4. Quick Actions Component

**Purpose**: Provide contextual action suggestions

**Structure**:
```html
<div class="quick-actions">
  <button class="action-btn">Show me flights</button>
  <button class="action-btn">Find activities</button>
  <button class="action-btn">I need a rental car</button>
</div>
```

**Styling**:
- Pill-shaped buttons: `rounded-full`
- Border: `border-gray-300 dark:border-gray-600`
- Background: `bg-background-light dark:bg-background-dark`
- Hover: `hover:bg-gray-100 dark:hover:bg-gray-800`
- Padding: 8px 16px
- Font size: 0.875rem (14px)
- Horizontal scroll if overflow

**Behavior**:
- Click action inserts text into input field
- Actions can be dynamically generated based on conversation context
- Smooth scroll animation for overflow

### 5. Message Input Component

**Purpose**: Allow users to compose and send messages

**Structure**:
```html
<div class="input-container">
  <div class="quick-actions">...</div>
  <div class="input-wrapper">
    <textarea 
      class="message-input"
      placeholder="Ask about your next trip..."
      rows="1"
    ></textarea>
    <button class="send-btn">
      <icon>send</icon>
    </button>
  </div>
</div>
```

**Styling**:
- Textarea: rounded-xl, border, auto-resize
- Background: `bg-white dark:bg-[#192633]`
- Border: `border-gray-300 dark:border-gray-600`
- Focus ring: `focus:ring-2 focus:ring-primary`
- Send button: circular, `bg-primary`, positioned absolute bottom-right
- Padding: 12px 48px 12px 16px (to accommodate send button)

**Behavior**:
- Auto-resize textarea based on content (max 5 rows)
- Enter key sends message (Shift+Enter for new line)
- Disable send button when input is empty
- Clear input after sending
- Integrate with existing LiveKit voice functionality

## Data Models

### Chat Message Model

```typescript
interface ChatMessage {
  id: string;
  sender: 'user' | 'agent';
  content: string;
  timestamp: Date;
  type: 'text' | 'voice' | 'system';
  metadata?: {
    duration?: number; // for voice messages
    confidence?: number; // for transcriptions
  };
}
```

### Chat Session Model

```typescript
interface ChatSession {
  id: string;
  title: string;
  lastMessage: string;
  lastActivity: Date;
  messageCount: number;
  isActive: boolean;
}
```

### User Preferences Model

```typescript
interface UserPreferences {
  darkMode: boolean;
  fontSize: 'small' | 'medium' | 'large';
  autoScroll: boolean;
  showTimestamps: boolean;
}
```

## Styling System

### Color Palette

```css
:root {
  /* Primary Colors */
  --color-primary: #137fec;
  --color-primary-hover: #0f6fd4;
  
  /* Background Colors */
  --bg-light: #f6f7f8;
  --bg-dark: #101922;
  
  /* Surface Colors */
  --surface-light: #ffffff;
  --surface-dark: #192633;
  
  /* Text Colors */
  --text-primary-light: #1a1a1a;
  --text-primary-dark: #eaeaea;
  --text-secondary-light: #666666;
  --text-secondary-dark: #92adc9;
  
  /* Border Colors */
  --border-light: #e5e7eb;
  --border-dark: rgba(255, 255, 255, 0.1);
  
  /* Message Bubble Colors */
  --bubble-agent-light: #e5e7eb;
  --bubble-agent-dark: #233648;
  --bubble-user: #137fec;
  
  /* Status Colors */
  --status-online: #10b981;
  --status-offline: #6b7280;
}
```

### Typography Scale

```css
/* Font Family */
font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;

/* Font Sizes */
--text-xs: 0.75rem;    /* 12px */
--text-sm: 0.875rem;   /* 14px */
--text-base: 1rem;     /* 16px */
--text-lg: 1.125rem;   /* 18px */
--text-xl: 1.25rem;    /* 20px */

/* Font Weights */
--font-normal: 400;
--font-medium: 500;
--font-semibold: 600;
--font-bold: 700;
--font-extrabold: 800;
```

### Spacing Scale

```css
/* Spacing (based on 4px base unit) */
--space-1: 0.25rem;   /* 4px */
--space-2: 0.5rem;    /* 8px */
--space-3: 0.75rem;   /* 12px */
--space-4: 1rem;      /* 16px */
--space-6: 1.5rem;    /* 24px */
--space-8: 2rem;      /* 32px */
```

### Border Radius

```css
--radius-sm: 0.25rem;   /* 4px */
--radius-md: 0.5rem;    /* 8px */
--radius-lg: 0.75rem;   /* 12px */
--radius-xl: 1rem;      /* 16px */
--radius-full: 9999px;  /* Circular */
```

## Dark Mode Implementation

### Strategy

Use Tailwind's dark mode with class-based toggling:

```html
<html class="dark">
  <!-- Dark mode active -->
</html>
```

### Toggle Mechanism

```javascript
function toggleDarkMode() {
  const html = document.documentElement;
  const isDark = html.classList.toggle('dark');
  localStorage.setItem('darkMode', isDark ? 'true' : 'false');
}

// Initialize on page load
function initDarkMode() {
  const savedMode = localStorage.getItem('darkMode');
  const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
  
  if (savedMode === 'true' || (!savedMode && prefersDark)) {
    document.documentElement.classList.add('dark');
  }
}
```

### Component Dark Mode Classes

All components use Tailwind's dark mode variants:

```html
<div class="bg-white dark:bg-gray-900 text-gray-900 dark:text-gray-100">
  <!-- Content adapts to dark mode -->
</div>
```

## Integration with Existing System

### LiveKit Voice Integration

Maintain existing LiveKit functionality while updating the UI:

```javascript
// Existing voice-agent.js integration
// Update transcript display to use new message bubble format
function displayTranscript(role, text) {
  const messageContainer = createMessageBubble(role, text);
  transcriptContainer.appendChild(messageContainer);
  scrollToBottom();
}
```

### WebSocket Connection

Keep existing WebSocket for real-time updates:

```javascript
// Existing WebSocket connection
// Update message handlers to use new UI components
ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  if (data.type === 'transcript') {
    displayTranscript(data.role, data.text);
  }
};
```

### Flask Route Integration

Update chat route to pass necessary data:

```python
@app.route('/chat')
@login_required
def chat():
    # Fetch user's recent chats for sidebar
    recent_chats = get_user_chat_history(current_user.id, limit=10)
    
    return render_template('chat.html',
        config={
            'user': {
                'display_name': current_user.display_name,
                'avatar_url': current_user.avatar_url
            },
            'recent_chats': recent_chats,
            'defaultRoom': 'quickstart',
            'livekit_url': os.getenv('LIVEKIT_URL'),
            'livekit_token': generate_livekit_token(current_user.id)
        }
    )
```

## Responsive Design

### Breakpoints

```css
/* Mobile: < 640px */
/* Tablet: 640px - 1024px */
/* Desktop: > 1024px */
```

### Mobile Adaptations

1. **Sidebar**: Convert to slide-out drawer with hamburger menu
2. **Message Bubbles**: Reduce max-width to 90% of viewport
3. **Quick Actions**: Enable horizontal scroll with scroll indicators
4. **Input Area**: Reduce padding, adjust button sizes
5. **Header**: Reduce height, smaller font sizes

### Tablet Adaptations

1. **Sidebar**: Reduce width to 240px
2. **Message Bubbles**: Maintain desktop layout
3. **Font Sizes**: Slightly reduce for better fit

## Error Handling

### Connection Errors

```javascript
function handleConnectionError(error) {
  showToast('Connection lost. Attempting to reconnect...', 'error');
  // Existing reconnection logic
}
```

### Message Send Failures

```javascript
function handleSendError(error) {
  showToast('Failed to send message. Please try again.', 'error');
  // Re-enable input and send button
}
```

### Chat History Load Failures

```javascript
function handleHistoryError(error) {
  // Display empty state with error message
  sidebarChatList.innerHTML = `
    <div class="error-state">
      <p>Unable to load chat history</p>
      <button onclick="reloadHistory()">Retry</button>
    </div>
  `;
}
```

## Testing Strategy

### Unit Tests

1. **Message Bubble Rendering**: Test correct styling for user/agent messages
2. **Dark Mode Toggle**: Verify class application and localStorage persistence
3. **Input Validation**: Test empty message prevention, character limits
4. **Auto-scroll Logic**: Verify scroll behavior on new messages

### Integration Tests

1. **LiveKit Integration**: Verify voice functionality works with new UI
2. **WebSocket Messages**: Test real-time message display
3. **Chat History Loading**: Verify sidebar populates correctly
4. **Navigation**: Test switching between conversations

### Visual Regression Tests

1. **Component Snapshots**: Capture screenshots of all components in light/dark mode
2. **Responsive Views**: Test layouts at mobile, tablet, desktop breakpoints
3. **Interactive States**: Capture hover, focus, active states

### Accessibility Tests

1. **Keyboard Navigation**: Verify all interactive elements are keyboard accessible
2. **Screen Reader**: Test with NVDA/JAWS for proper announcements
3. **Color Contrast**: Verify WCAG AA compliance for all text
4. **Focus Indicators**: Ensure visible focus states on all interactive elements

## Performance Considerations

### Optimization Strategies

1. **Virtual Scrolling**: Implement for chat history with 100+ messages
2. **Lazy Loading**: Load chat history on demand as user scrolls
3. **Image Optimization**: Use appropriate avatar sizes, lazy load images
4. **CSS Optimization**: Use Tailwind's purge feature to remove unused styles
5. **JavaScript Bundling**: Minify and bundle JS files for production

### Performance Metrics

- **First Contentful Paint**: < 1.5s
- **Time to Interactive**: < 3s
- **Message Render Time**: < 50ms per message
- **Scroll Performance**: 60fps during scroll

## Migration Plan

### Phase 1: Template Structure (Day 1)

1. Create new `chat_v2.html` template with sidebar and main panel structure
2. Add Tailwind CSS CDN and Google Fonts
3. Implement basic layout without functionality

### Phase 2: Component Implementation (Day 2-3)

1. Build sidebar component with static data
2. Implement message bubble components
3. Create chat header with status indicator
4. Build input area with quick actions

### Phase 3: Integration (Day 4-5)

1. Connect sidebar to chat history API
2. Integrate message bubbles with WebSocket transcripts
3. Wire up input area to LiveKit functionality
4. Implement dark mode toggle

### Phase 4: Polish & Testing (Day 6-7)

1. Add animations and transitions
2. Implement responsive design
3. Conduct accessibility audit
4. Perform cross-browser testing
5. Fix bugs and refine UX

### Phase 5: Deployment

1. Replace old `chat.html` with new version
2. Monitor for issues
3. Gather user feedback
4. Iterate on improvements

## Future Enhancements

1. **Rich Message Types**: Support for images, files, carousels (as shown in Stitch design)
2. **Message Reactions**: Allow users to react to messages with emojis
3. **Search Functionality**: Search within conversation history
4. **Message Editing**: Allow users to edit sent messages
5. **Typing Indicators**: Show when agent is "thinking"
6. **Voice Waveform**: Visual representation of voice input/output
7. **Conversation Export**: Download conversation as PDF or text
8. **Custom Themes**: Allow users to customize color schemes
