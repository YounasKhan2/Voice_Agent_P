/**
 * Toast Notification System
 * Displays temporary, non-intrusive messages to users
 */

class ToastNotification {
  constructor() {
    this.container = null;
    this.toasts = [];
    this.init();
  }

  /**
   * Initialize the toast container
   */
  init() {
    // Create container if it doesn't exist
    if (!document.getElementById('toast-container')) {
      this.container = document.createElement('div');
      this.container.id = 'toast-container';
      // Mobile: top-2.5 left-2.5 right-2.5, Desktop: top-5 right-5
      this.container.className = 'toast-container fixed top-2.5 left-2.5 right-2.5 sm:top-5 sm:right-5 sm:left-auto z-[9999] flex flex-col gap-3 pointer-events-none';
      document.body.appendChild(this.container);
    } else {
      this.container = document.getElementById('toast-container');
    }
  }

  /**
   * Show a toast notification
   * @param {string} message - The message to display
   * @param {string} type - The type of toast (success, error, info, warning)
   * @param {number} duration - Duration in milliseconds (minimum 3000ms)
   */
  show(message, type = 'info', duration = 3000) {
    // Ensure minimum duration of 3 seconds
    const displayDuration = Math.max(duration, 3000);

    // Create toast element with Tailwind classes and type-specific border
    const borderColors = {
      success: 'border-l-4 border-l-green-500',
      error: 'border-l-4 border-l-red-500',
      warning: 'border-l-4 border-l-yellow-500',
      info: 'border-l-4 border-l-blue-500'
    };
    
    const borderClass = borderColors[type] || borderColors.info;
    
    const toast = document.createElement('div');
    // Mobile: full width, Desktop: min-w-[300px] max-w-[400px]
    toast.className = `toast toast-${type} flex items-center justify-between w-full sm:min-w-[300px] sm:max-w-[400px] p-4 bg-slate-800 border border-slate-700 ${borderClass} rounded-lg shadow-xl pointer-events-auto opacity-0 translate-x-[400px] sm:translate-x-[400px] translate-y-[-100px] sm:translate-y-0 transition-all duration-300`;
    toast.setAttribute('role', type === 'error' ? 'alert' : 'status');
    toast.setAttribute('aria-live', type === 'error' ? 'assertive' : 'polite');
    
    // Create toast content
    const content = document.createElement('div');
    content.className = 'toast-content flex items-center gap-3 flex-1';
    
    // Add icon based on type
    const icon = document.createElement('span');
    icon.className = 'toast-icon flex-shrink-0 flex items-center justify-center';
    icon.innerHTML = this.getIcon(type);
    
    // Add message
    const messageEl = document.createElement('span');
    messageEl.className = 'toast-message flex-1 text-sm leading-normal text-white';
    messageEl.textContent = message;
    
    // Add dismiss button
    const dismissBtn = document.createElement('button');
    dismissBtn.className = 'toast-dismiss flex-shrink-0 w-6 h-6 flex items-center justify-center bg-transparent border-0 text-slate-400 text-2xl leading-none cursor-pointer rounded hover:bg-slate-700 hover:text-white transition-colors';
    dismissBtn.innerHTML = '&times;';
    dismissBtn.setAttribute('aria-label', 'Dismiss notification');
    dismissBtn.setAttribute('type', 'button');
    
    // Assemble toast
    content.appendChild(icon);
    content.appendChild(messageEl);
    toast.appendChild(content);
    toast.appendChild(dismissBtn);
    
    // Add to container
    this.container.appendChild(toast);
    this.toasts.push(toast);
    
    // Trigger slide-in animation (from right on desktop, from top on mobile)
    setTimeout(() => {
      toast.classList.remove('opacity-0', 'translate-x-[400px]', 'translate-y-[-100px]');
      toast.classList.add('toast-show', 'opacity-100', 'translate-x-0', 'translate-y-0');
    }, 10);
    
    // Set up dismiss handler
    dismissBtn.addEventListener('click', () => {
      this.dismiss(toast);
    });
    
    // Auto-dismiss after duration
    setTimeout(() => {
      this.dismiss(toast);
    }, displayDuration);
  }

  /**
   * Dismiss a toast notification
   * @param {HTMLElement} toast - The toast element to dismiss
   */
  dismiss(toast) {
    if (!toast || !toast.classList.contains('toast-show')) {
      return;
    }
    
    // Trigger slide-out animation (to right on desktop, to top on mobile)
    toast.classList.remove('toast-show', 'opacity-100', 'translate-x-0', 'translate-y-0');
    toast.classList.add('toast-hide', 'opacity-0', 'translate-x-[400px]', 'sm:translate-x-[400px]', 'translate-y-[-100px]', 'sm:translate-y-0');
    
    // Remove from DOM after animation
    setTimeout(() => {
      if (toast.parentNode) {
        toast.parentNode.removeChild(toast);
      }
      
      // Remove from toasts array
      const index = this.toasts.indexOf(toast);
      if (index > -1) {
        this.toasts.splice(index, 1);
      }
    }, 300);
  }

  /**
   * Get icon HTML for toast type with VoyageAI colors
   * @param {string} type - The toast type
   * @returns {string} SVG icon HTML with appropriate color class
   */
  getIcon(type) {
    const colorClasses = {
      success: 'text-green-500',
      error: 'text-red-500',
      warning: 'text-yellow-500',
      info: 'text-blue-500'
    };
    
    const colorClass = colorClasses[type] || colorClasses.info;
    
    const icons = {
      success: `<svg class="${colorClass}" width="20" height="20" viewBox="0 0 20 20" fill="none" xmlns="http://www.w3.org/2000/svg">
        <path d="M10 0C4.48 0 0 4.48 0 10C0 15.52 4.48 20 10 20C15.52 20 20 15.52 20 10C20 4.48 15.52 0 10 0ZM8 15L3 10L4.41 8.59L8 12.17L15.59 4.58L17 6L8 15Z" fill="currentColor"/>
      </svg>`,
      error: `<svg class="${colorClass}" width="20" height="20" viewBox="0 0 20 20" fill="none" xmlns="http://www.w3.org/2000/svg">
        <path d="M10 0C4.48 0 0 4.48 0 10C0 15.52 4.48 20 10 20C15.52 20 20 15.52 20 10C20 4.48 15.52 0 10 0ZM11 15H9V13H11V15ZM11 11H9V5H11V11Z" fill="currentColor"/>
      </svg>`,
      warning: `<svg class="${colorClass}" width="20" height="20" viewBox="0 0 20 20" fill="none" xmlns="http://www.w3.org/2000/svg">
        <path d="M1 17H19L10 2L1 17ZM11 14H9V12H11V14ZM11 10H9V6H11V10Z" fill="currentColor"/>
      </svg>`,
      info: `<svg class="${colorClass}" width="20" height="20" viewBox="0 0 20 20" fill="none" xmlns="http://www.w3.org/2000/svg">
        <path d="M10 0C4.48 0 0 4.48 0 10C0 15.52 4.48 20 10 20C15.52 20 20 15.52 20 10C20 4.48 15.52 0 10 0ZM11 15H9V9H11V15ZM11 7H9V5H11V7Z" fill="currentColor"/>
      </svg>`
    };
    
    return icons[type] || icons.info;
  }

  /**
   * Show a success toast
   * @param {string} message - The message to display
   * @param {number} duration - Duration in milliseconds
   */
  success(message, duration = 3000) {
    this.show(message, 'success', duration);
  }

  /**
   * Show an error toast
   * @param {string} message - The message to display
   * @param {number} duration - Duration in milliseconds
   */
  error(message, duration = 3000) {
    this.show(message, 'error', duration);
  }

  /**
   * Show a warning toast
   * @param {string} message - The message to display
   * @param {number} duration - Duration in milliseconds
   */
  warning(message, duration = 3000) {
    this.show(message, 'warning', duration);
  }

  /**
   * Show an info toast
   * @param {string} message - The message to display
   * @param {number} duration - Duration in milliseconds
   */
  info(message, duration = 3000) {
    this.show(message, 'info', duration);
  }
}

// Create global instance
window.toast = new ToastNotification();
