/**
 * Dark Mode Management
 * Handles dark mode toggle with localStorage persistence
 */

/**
 * Initialize dark mode on page load
 * Checks localStorage for saved preference or falls back to system preference
 */
function initDarkMode() {
  const savedMode = localStorage.getItem('darkMode');
  const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
  
  if (savedMode === 'true' || (!savedMode && prefersDark)) {
    document.documentElement.classList.add('dark');
  } else {
    document.documentElement.classList.remove('dark');
  }
}

/**
 * Toggle dark mode on/off
 * Saves preference to localStorage
 * @returns {boolean} True if dark mode is now enabled, false otherwise
 */
function toggleDarkMode() {
  const html = document.documentElement;
  const isDark = html.classList.toggle('dark');
  localStorage.setItem('darkMode', isDark ? 'true' : 'false');
  return isDark;
}

/**
 * Set dark mode to a specific state
 * @param {boolean} enabled - Whether dark mode should be enabled
 */
function setDarkMode(enabled) {
  const html = document.documentElement;
  if (enabled) {
    html.classList.add('dark');
  } else {
    html.classList.remove('dark');
  }
  localStorage.setItem('darkMode', enabled ? 'true' : 'false');
}

/**
 * Get current dark mode state
 * @returns {boolean} True if dark mode is enabled, false otherwise
 */
function isDarkMode() {
  return document.documentElement.classList.contains('dark');
}

// Initialize dark mode when DOM is ready
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', initDarkMode);
} else {
  initDarkMode();
}
