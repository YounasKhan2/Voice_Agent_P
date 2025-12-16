# Implementation Plan

- [x] 1. Set up Tailwind CSS and dependencies
  - Add Tailwind CSS CDN to chat template
  - Add Google Fonts (Plus Jakarta Sans) link
  - Add Material Symbols Outlined icon font
  - Configure Tailwind dark mode with class strategy
  - _Requirements: 6.1, 7.1_

- [-] 2. Create new chat template structure
  - [x] 2.1 Create base HTML structure with sidebar and main panel layout
    - Implement flexbox container with full viewport height
    - Add sidebar with fixed 288px width
    - Add main chat panel with flex-1 to fill remaining space
    - _Requirements: 1.1, 1.5_
  
  - [x] 2.2 Build sidebar header component
    - Add logo/avatar placeholder (40px circular)
    - Add application name "WanderBot" with subtitle
    - Apply proper spacing and typography
    - _Requirements: 1.1, 7.1, 7.2_
  
  - [x] 2.3 Implement "New Chat" button in sidebar
    - Create button with icon and text
    - Apply primary blue background color
    - Add hover and focus states
    - _Requirements: 1.1, 7.4_
  
  - [x] 2.4 Create recent chats list section
    - Add "RECENT CHATS" section label with uppercase styling
    - Create chat item template with icon and title
    - Implement active state styling with primary color background
    - Add hover effects for non-active items
    - _Requirements: 1.2, 1.3, 7.4_
  
  - [x] 2.5 Add user actions section at sidebar bottom
    - Create "My Account" and "Settings" links
    - Add border-top separator
    - Apply proper spacing and hover states
    - Link to existing profile and settings routes
    - _Requirements: 1.4_

- [x] 3. Implement chat header component
  - [x] 3.1 Create header bar structure
    - Set fixed height of 64px
    - Add bottom border for separation
    - Apply proper padding (24px horizontal)
    - _Requirements: 3.1, 3.4, 3.5_
  
  - [x] 3.2 Add conversation title display
    - Display current room/session name
    - Use large font size and bold weight
    - Apply dark mode color variants
    - _Requirements: 3.1, 6.2_
  
  - [x] 3.3 Implement online status indicator
    - Add green dot (8px circular) for online status
    - Add "Online" text label
    - Position next to conversation title
    - _Requirements: 3.2_

- [x] 4. Build message bubble components
  - [x] 4.1 Create agent message bubble structure
    - Add left-aligned container with avatar
    - Create message content wrapper
    - Add sender name label above bubble
    - Implement rounded bubble with gray background
    - Apply rounded-bl-none for speech bubble effect
    - _Requirements: 2.1, 2.3, 2.4, 2.5_
  
  - [x] 4.2 Create user message bubble structure
    - Add right-aligned container with avatar
    - Create message content wrapper
    - Add sender name label above bubble
    - Implement rounded bubble with primary blue background
    - Apply rounded-br-none for speech bubble effect
    - _Requirements: 2.2, 2.3, 2.4, 2.5_
  
  - [x] 4.3 Style message bubble typography
    - Set font size to 1rem (16px)
    - Apply line-height of 1.5 for readability
    - Set max-width to 512px
    - Add proper padding (12px 16px)
    - _Requirements: 7.2, 7.3_
  
  - [x] 4.4 Implement avatar styling
    - Create 40px circular images
    - Add placeholder images for agent and user
    - Apply proper spacing between avatar and message
    - _Requirements: 2.5_

- [x] 5. Create scrollable messages container
  - [x] 5.1 Implement messages area layout
    - Create flex column container with gap spacing
    - Make container vertically scrollable
    - Set flex-1 to fill available space
    - Add padding around messages (24px)
    - _Requirements: 8.1, 8.2_
  
  - [x] 5.2 Hide scrollbars for clean appearance
    - Apply CSS to hide scrollbars while maintaining scroll functionality
    - Use webkit-scrollbar and scrollbar-width properties
    - _Requirements: 8.3_
  
  - [x] 5.3 Implement auto-scroll behavior
    - Add JavaScript to scroll to bottom on new messages
    - Detect manual scroll and preserve position
    - Only auto-scroll when user is at bottom
    - _Requirements: 8.4, 8.5_

- [ ] 6. Build input area with quick actions
  - [ ] 6.1 Create quick actions button row
    - Add container above input field
    - Create pill-shaped buttons with borders
    - Implement horizontal scroll for overflow
    - Add at least 3 sample action buttons
    - _Requirements: 4.1, 4.2, 4.4, 4.5_
  
  - [ ] 6.2 Style quick action buttons
    - Apply rounded-full border radius
    - Set border and background colors
    - Implement hover state color changes
    - Add proper padding and font sizing
    - _Requirements: 4.3, 7.4_
  
  - [ ] 6.3 Create message input textarea
    - Add textarea with rounded corners
    - Set placeholder text
    - Configure initial rows to 1
    - Apply border and background colors
    - _Requirements: 5.1, 5.3_
  
  - [ ] 6.4 Implement send button
    - Create circular button with send icon
    - Position absolute at bottom-right of input
    - Apply primary blue background
    - Add hover and focus states
    - _Requirements: 5.2, 5.5_
  
  - [ ] 6.5 Position input area at bottom
    - Fix input container to bottom of chat panel
    - Add proper padding around input area
    - Ensure it stays above viewport bottom
    - _Requirements: 5.4_

- [ ] 7. Implement dark mode functionality
  - [ ] 7.1 Create dark mode toggle mechanism
    - Add JavaScript function to toggle 'dark' class on html element
    - Store preference in localStorage
    - Initialize dark mode on page load based on saved preference
    - _Requirements: 6.1_
  
  - [ ] 7.2 Apply dark mode color variants to all components
    - Update sidebar background colors
    - Update message bubble backgrounds
    - Update input area colors
    - Update text colors for readability
    - Update border colors
    - _Requirements: 6.2, 6.4_
  
  - [ ] 7.3 Ensure proper contrast ratios
    - Verify text readability in dark mode
    - Test all interactive elements
    - Validate against WCAG AA standards
    - _Requirements: 6.3_
  
  - [ ] 7.4 Maintain visual hierarchy in dark mode
    - Ensure component distinction is clear
    - Verify hover and focus states are visible
    - Test status indicators and icons
    - _Requirements: 6.5_

- [ ] 8. Integrate with existing LiveKit functionality
  - [ ] 8.1 Update transcript display to use new message bubbles
    - Modify voice-agent.js to create message bubble HTML
    - Map transcript roles to agent/user message types
    - Append new messages to messages container
    - _Requirements: 2.1, 2.2_
  
  - [ ] 8.2 Connect WebSocket messages to UI
    - Update WebSocket message handlers
    - Display incoming transcripts as message bubbles
    - Trigger auto-scroll on new messages
    - _Requirements: 8.4_
  
  - [ ] 8.3 Wire up send button to LiveKit
    - Connect send button click to existing send logic
    - Clear input after sending
    - Disable button when input is empty
    - _Requirements: 5.2_
  
  - [ ] 8.4 Maintain existing voice functionality
    - Ensure LiveKit connection still works
    - Verify audio playback continues to function
    - Test room joining and agent spawning
    - _Requirements: All_

- [ ] 9. Populate sidebar with chat history
  - [ ] 9.1 Fetch chat history from backend
    - Call existing history API endpoint
    - Parse response data
    - Handle loading and error states
    - _Requirements: 1.2_
  
  - [ ] 9.2 Render chat items dynamically
    - Create chat item elements from data
    - Add click handlers for navigation
    - Highlight current active chat
    - _Requirements: 1.2, 1.3_
  
  - [ ] 9.3 Implement "New Chat" functionality
    - Add click handler to create new session
    - Clear current messages
    - Update URL or session state
    - _Requirements: 1.1_

- [ ] 10. Add responsive design for mobile
  - [ ] 10.1 Implement mobile sidebar toggle
    - Convert sidebar to slide-out drawer on mobile
    - Add hamburger menu button in header
    - Implement overlay when sidebar is open
    - _Requirements: 1.5_
  
  - [ ] 10.2 Adjust message bubbles for mobile
    - Reduce max-width to 90% of viewport
    - Adjust padding and font sizes
    - Ensure avatars scale appropriately
    - _Requirements: 2.4, 7.2_
  
  - [ ] 10.3 Optimize input area for mobile
    - Reduce padding around input
    - Adjust button sizes for touch targets
    - Ensure quick actions scroll smoothly
    - _Requirements: 4.5, 5.4_
  
  - [ ] 10.4 Test at mobile breakpoint (< 640px)
    - Verify layout doesn't break
    - Test all interactive elements
    - Ensure text remains readable
    - _Requirements: All_

- [ ] 11. Implement smooth transitions and animations
  - [ ] 11.1 Add hover transitions to interactive elements
    - Apply transition properties to buttons
    - Add smooth color changes on hover
    - Implement focus ring animations
    - _Requirements: 7.4_
  
  - [ ] 11.2 Add message appearance animations
    - Fade in new messages
    - Slide in from appropriate side
    - Keep animations subtle and fast
    - _Requirements: 7.4_
  
  - [ ]* 11.3 Add sidebar slide animation for mobile
    - Smooth slide-in/out transition
    - Fade overlay in/out
    - _Requirements: 7.4_

- [ ] 12. Implement accessibility features
  - [ ] 12.1 Add ARIA labels and roles
    - Label sidebar navigation
    - Add aria-live to messages container
    - Label all interactive buttons
    - _Requirements: All_
  
  - [ ] 12.2 Ensure keyboard navigation
    - Test tab order through all elements
    - Add keyboard shortcuts for common actions
    - Ensure focus is visible
    - _Requirements: All_
  
  - [ ] 12.3 Add focus indicators
    - Apply visible focus rings to all interactive elements
    - Use primary color for focus states
    - Ensure 2px outline with offset
    - _Requirements: 7.4_
  
  - [ ]* 12.4 Test with screen readers
    - Verify proper announcements for new messages
    - Test navigation with NVDA/JAWS
    - Ensure all content is accessible
    - _Requirements: All_

- [ ] 13. Polish and final touches
  - [ ] 13.1 Add loading states
    - Show skeleton loaders for chat history
    - Display loading indicator when fetching messages
    - Add spinner for send button during transmission
    - _Requirements: All_
  
  - [ ] 13.2 Implement error handling UI
    - Display toast notifications for errors
    - Show retry buttons for failed operations
    - Add empty states for no chat history
    - _Requirements: All_
  
  - [ ] 13.3 Optimize performance
    - Minimize CSS by removing unused Tailwind classes
    - Lazy load chat history as user scrolls
    - Debounce scroll events
    - _Requirements: 8.1, 8.2_
  
  - [ ]* 13.4 Cross-browser testing
    - Test in Chrome, Firefox, Safari, Edge
    - Verify dark mode works in all browsers
    - Check for layout inconsistencies
    - _Requirements: All_
  
  - [ ]* 13.5 Final visual polish
    - Adjust spacing for pixel-perfect alignment
    - Verify all colors match design
    - Test all hover and focus states
    - Ensure consistent typography
    - _Requirements: 7.1, 7.2, 7.3, 7.4_
