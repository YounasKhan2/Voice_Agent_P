# Branding Assets

This directory contains all visual assets for the ChatAI application.

## Files

### Logo
- **logo.svg** - Main application logo with chat bubble icon and "ChatAI" text
  - Used in: Landing page, authentication pages
  - Format: SVG (scalable, optimized for web)
  - Colors: Gradient from #6366f1 (indigo) to #8b5cf6 (purple)

### Favicon
- **favicon.svg** - Browser tab icon
  - Used in: All pages (via base.html)
  - Format: SVG (32x32 viewBox)
  - Colors: Gradient background with white chat bubble

### Illustrations
- **landing-hero.svg** - Hero section illustration for landing page
  - Shows animated chat interface mockup
  - Format: SVG with CSS animations
  - Size: 800x600 viewBox
  - Features: Floating elements, sparkle effects, message animations

- **auth-illustration.svg** - Background illustration for login/signup pages
  - Abstract shapes and chat bubbles
  - Format: SVG with CSS animations
  - Size: 600x800 viewBox
  - Features: Animated floating elements, gradient shapes

### Feature Icons
- **icon-chat.svg** - Natural conversations feature icon
  - Chat bubble with dots
  - Size: 48x48 viewBox
  - Color: Indigo to purple gradient

- **icon-fast.svg** - Lightning fast feature icon
  - Lightning bolt with speed lines
  - Size: 48x48 viewBox
  - Color: Amber gradient

- **icon-smart.svg** - Intelligent responses feature icon
  - Brain/head with circuit pattern
  - Size: 48x48 viewBox
  - Color: Blue gradient

- **icon-secure.svg** - Security feature icon
  - Shield with checkmark
  - Size: 48x48 viewBox
  - Color: Green gradient

### Patterns
- **pattern-dots.svg** - Subtle dot pattern for backgrounds
  - Repeating dot pattern
  - Size: 100x100 viewBox
  - Color: Dark slate with low opacity

## Technical Details

### Format
All assets are in SVG format for the following benefits:
- Scalable to any size without quality loss
- Small file size (typically < 5KB each)
- Crisp display on all screen resolutions
- Support for CSS animations
- Easy to modify colors and styles

### Optimization
- All SVGs are hand-coded for minimal file size
- No external dependencies or fonts
- Inline gradients and animations
- Optimized viewBox dimensions

### Color Palette
Assets use the application's design system colors:
- Primary: #6366f1 (Indigo)
- Secondary: #8b5cf6 (Purple)
- Accent: #ec4899 (Pink)
- Success: #10b981 (Green)
- Warning: #f59e0b (Amber)
- Info: #3b82f6 (Blue)

### Accessibility
- All images include descriptive alt text in templates
- SVGs use semantic structure
- Color contrast meets WCAG 2.1 AA standards
- Animations respect prefers-reduced-motion

## Usage

### In HTML Templates
```html
<!-- Logo -->
<img src="{{ url_for('static', filename='images/logo.svg') }}" alt="ChatAI Logo" width="200" height="60" />

<!-- Feature Icon -->
<img src="{{ url_for('static', filename='images/icon-chat.svg') }}" alt="Chat Icon" width="48" height="48" />

<!-- Hero Illustration -->
<img src="{{ url_for('static', filename='images/landing-hero.svg') }}" alt="AI Chat Interface" class="hero-illustration" />
```

### In CSS
```css
/* Background pattern */
.element {
  background-image: url('/static/images/pattern-dots.svg');
  background-repeat: repeat;
}
```

## Future Enhancements

Potential additions for future iterations:
- PNG/WebP fallbacks for older browsers
- Dark/light mode variants
- Additional icon set for more features
- Animated logo variants
- Social media preview images
- Email template graphics
