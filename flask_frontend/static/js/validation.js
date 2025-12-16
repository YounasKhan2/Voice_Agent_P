/**
 * Client-side form validation for authentication forms
 */

class FormValidator {
  constructor(formElement) {
    this.form = formElement;
    this.errors = {};
  }

  /**
   * Validate email format
   */
  validateEmail(email) {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!email || email.trim() === '') {
      return 'Email is required';
    }
    if (!emailRegex.test(email)) {
      return 'Please enter a valid email address';
    }
    return null;
  }

  /**
   * Validate password length (minimum 8 characters only)
   */
  validatePassword(password) {
    if (!password || password.trim() === '') {
      return 'Password is required';
    }
    if (password.length < 8) {
      return 'Password must be at least 8 characters';
    }
    // No other password requirements - let users choose their password
    return null;
  }

  /**
   * Validate password confirmation
   */
  validatePasswordConfirmation(password, confirmPassword) {
    if (!confirmPassword || confirmPassword.trim() === '') {
      return 'Please confirm your password';
    }
    if (password !== confirmPassword) {
      return 'Passwords do not match';
    }
    return null;
  }

  /**
   * Validate display name
   */
  validateDisplayName(displayName) {
    if (!displayName || displayName.trim() === '') {
      return 'Display name is required';
    }
    const trimmedName = displayName.trim();
    if (trimmedName.length < 2) {
      return 'Display name must be at least 2 characters';
    }
    if (trimmedName.length > 100) {
      return 'Display name must not exceed 100 characters';
    }
    return null;
  }

  /**
   * Display error message below a form field
   */
  showError(fieldId, errorMessage) {
    const field = document.getElementById(fieldId);
    if (!field) return;

    // Remove any existing error message
    this.clearError(fieldId);

    // Add Tailwind error classes to input
    field.classList.add('border-red-500');
    field.classList.remove('border-green-500', 'border-slate-300', 'border-slate-700');
    
    // For dark mode support
    if (document.documentElement.classList.contains('dark')) {
      field.classList.add('dark:border-red-500');
    }

    // Create and insert error message with Tailwind styling
    const errorDiv = document.createElement('div');
    errorDiv.className = 'text-sm text-red-500 mt-1';
    errorDiv.id = `${fieldId}-error`;
    errorDiv.textContent = errorMessage;
    
    // Insert after the input field or its parent container
    const container = field.closest('.flex.flex-col') || field.parentNode;
    container.appendChild(errorDiv);
  }

  /**
   * Clear error message for a field
   */
  clearError(fieldId) {
    const field = document.getElementById(fieldId);
    if (!field) return;

    // Remove Tailwind error classes
    field.classList.remove('border-red-500', 'dark:border-red-500');
    
    // Restore default border classes if not in success state
    if (!field.classList.contains('border-green-500')) {
      field.classList.add('border-slate-300');
      if (document.documentElement.classList.contains('dark')) {
        field.classList.add('dark:border-slate-700');
      }
    }

    // Remove error message
    const errorDiv = document.getElementById(`${fieldId}-error`);
    if (errorDiv) {
      errorDiv.remove();
    }
  }

  /**
   * Show success state for a field
   */
  showSuccess(fieldId) {
    const field = document.getElementById(fieldId);
    if (!field) return;

    // Remove error classes
    field.classList.remove('border-red-500', 'dark:border-red-500', 'border-slate-300', 'border-slate-700');
    
    // Add Tailwind success classes
    field.classList.add('border-green-500');
    
    // For dark mode support
    if (document.documentElement.classList.contains('dark')) {
      field.classList.add('dark:border-green-500');
    }

    // Remove any error message
    const errorDiv = document.getElementById(`${fieldId}-error`);
    if (errorDiv) {
      errorDiv.remove();
    }
  }

  /**
   * Clear success state for a field
   */
  clearSuccess(fieldId) {
    const field = document.getElementById(fieldId);
    if (!field) return;

    // Remove success classes
    field.classList.remove('border-green-500', 'dark:border-green-500');
    
    // Restore default border classes
    field.classList.add('border-slate-300');
    if (document.documentElement.classList.contains('dark')) {
      field.classList.add('dark:border-slate-700');
    }
  }

  /**
   * Clear all errors
   */
  clearAllErrors() {
    // Remove all error messages (Tailwind styled)
    const errorMessages = this.form.querySelectorAll('[id$="-error"]');
    errorMessages.forEach(msg => msg.remove());

    // Remove Tailwind error classes from all inputs
    const errorInputs = this.form.querySelectorAll('.border-red-500');
    errorInputs.forEach(input => {
      input.classList.remove('border-red-500', 'dark:border-red-500');
      // Restore default border classes if not in success state
      if (!input.classList.contains('border-green-500')) {
        input.classList.add('border-slate-300');
        if (document.documentElement.classList.contains('dark')) {
          input.classList.add('dark:border-slate-700');
        }
      }
    });

    this.errors = {};
  }

  /**
   * Validate login form
   */
  validateLoginForm() {
    this.clearAllErrors();
    let isValid = true;

    const email = document.getElementById('email').value;
    const password = document.getElementById('password').value;

    // Validate email
    const emailError = this.validateEmail(email);
    if (emailError) {
      this.showError('email', emailError);
      this.errors.email = emailError;
      isValid = false;
    }

    // Validate password
    const passwordError = this.validatePassword(password);
    if (passwordError) {
      this.showError('password', passwordError);
      this.errors.password = passwordError;
      isValid = false;
    }

    return isValid;
  }

  /**
   * Validate signup form
   */
  validateSignupForm() {
    this.clearAllErrors();
    let isValid = true;

    const email = document.getElementById('email').value;
    const displayName = document.getElementById('display_name').value;
    const password = document.getElementById('password').value;
    const confirmPassword = document.getElementById('confirm_password').value;

    // Validate email
    const emailError = this.validateEmail(email);
    if (emailError) {
      this.showError('email', emailError);
      this.errors.email = emailError;
      isValid = false;
    }

    // Validate display name
    const displayNameError = this.validateDisplayName(displayName);
    if (displayNameError) {
      this.showError('display_name', displayNameError);
      this.errors.display_name = displayNameError;
      isValid = false;
    }

    // Validate password
    const passwordError = this.validatePassword(password);
    if (passwordError) {
      this.showError('password', passwordError);
      this.errors.password = passwordError;
      isValid = false;
    }

    // Validate password confirmation
    const confirmError = this.validatePasswordConfirmation(password, confirmPassword);
    if (confirmError) {
      this.showError('confirm_password', confirmError);
      this.errors.confirm_password = confirmError;
      isValid = false;
    }

    return isValid;
  }

  /**
   * Add real-time validation on blur
   */
  addBlurValidation(fieldId, validationFn, showSuccessState = false) {
    const field = document.getElementById(fieldId);
    if (!field) return;

    field.addEventListener('blur', () => {
      const value = field.value;
      // Only validate if field has content
      if (value && value.trim() !== '') {
        const error = validationFn(value);
        if (error) {
          this.showError(fieldId, error);
        } else {
          this.clearError(fieldId);
          // Optionally show success state for valid fields
          if (showSuccessState) {
            this.showSuccess(fieldId);
          }
        }
      }
    });

    // Clear error/success on input
    field.addEventListener('input', () => {
      if (field.classList.contains('border-red-500')) {
        this.clearError(fieldId);
      }
      if (field.classList.contains('border-green-500')) {
        this.clearSuccess(fieldId);
      }
    });
  }
}

// Export for use in templates
window.FormValidator = FormValidator;
