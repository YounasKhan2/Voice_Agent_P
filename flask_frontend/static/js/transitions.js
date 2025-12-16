/**
 * Page Transition Animation System
 * Provides smooth animations when navigating between pages
 */

class PageTransitions {
    constructor() {
        this.transitionDuration = 400; // Maximum duration in ms
        this.isTransitioning = false;
    }

    /**
     * Navigate to a URL with a fade transition animation
     * @param {string} targetUrl - The URL to navigate to
     * @param {number} duration - Animation duration in ms (default: 300ms)
     */
    fadeTransition(targetUrl, duration = 300) {
        if (this.isTransitioning) return;
        this.isTransitioning = true;

        // Add fade-out class to body
        document.body.classList.add('page-transition-fade');
        
        // Navigate after animation completes
        setTimeout(() => {
            window.location.href = targetUrl;
        }, duration);
    }

    /**
     * Navigate to a URL with a slide transition animation
     * @param {string} targetUrl - The URL to navigate to
     * @param {number} duration - Animation duration in ms (default: 400ms)
     */
    slideTransition(targetUrl, duration = 400) {
        if (this.isTransitioning) return;
        this.isTransitioning = true;

        // Add slide-out class to body
        document.body.classList.add('page-transition-slide');
        
        // Navigate after animation completes
        setTimeout(() => {
            window.location.href = targetUrl;
        }, duration);
    }

    /**
     * Navigate with animation based on context
     * Uses slide transition for login/signup navigation
     * @param {string} targetUrl - The URL to navigate to
     * @param {string} transitionType - Type of transition ('fade' or 'slide')
     */
    navigateWithAnimation(targetUrl, transitionType = 'slide') {
        if (transitionType === 'fade') {
            this.fadeTransition(targetUrl, 300);
        } else {
            this.slideTransition(targetUrl, 400);
        }
    }
}

// Create global instance
const pageTransitions = new PageTransitions();

/**
 * Helper function for easy access
 * @param {string} targetUrl - The URL to navigate to
 * @param {string} transitionType - Type of transition ('fade' or 'slide')
 */
function navigateWithAnimation(targetUrl, transitionType = 'slide') {
    pageTransitions.navigateWithAnimation(targetUrl, transitionType);
}

// Handle page load fade-in
document.addEventListener('DOMContentLoaded', () => {
    // Remove any transition classes that might persist
    document.body.classList.remove('page-transition-fade', 'page-transition-slide');
    
    // Add fade-in class for smooth entry
    document.body.classList.add('page-loaded');
});
