/**
 * Authentication JavaScript | Cannlytics Console
 * Copyright (c) 2021-2022 Cannlytics
 * 
 * Authors: Keegan Skeate <keegan@cannlytics.com>
 * Created: 12/4/2020
 * Updated: 1/7/2022
 * License: MIT License <https://github.com/cannlytics/cannlytics-website/blob/main/LICENSE>
 */
import { Modal } from 'bootstrap';
import {
  authErrors,
  confirmPasswordChange,
  createAccount,
  getCurrentUser,
  googleLogIn,
  logIn,
  logOut,
  onAuthChange,
  sendPasswordReset,
} from '../firebase.js';
import {
  apiRequest,
  authRequest,
  showNotification,
} from '../utils.js';

export const auth = {

  async loginWhenUserDetected() {
    /**
     * Trigger server login and navigation to the dashboard when a user is detected.
     * If it's the first time that the user has logged in, then their `email` and
     * `photo_url` are saved to their user data in Firestore.
     */
    onAuthChange(async (user) => {
      if (!user) return;
      await authRequest('/src/auth/login');
      if (user.metadata.createdAt === user.metadata.lastLoginAt) {
        const { email } = user;
        const defaultPhoto = `${window.location.origin}/robohash/${user.email}/?width=60&height=60`;
        const data = { email, photo_url: defaultPhoto };
        try {
          await apiRequest('/api/users', data);
        } catch(error) {
          showNotification('Login error', 'Authentication failed. Try again later.', /* type = */ 'error' );
          return;
        }
      }
      window.location.href = window.location.origin;
    });
  },

  async resetPassword() {
    /**
     * Reset a user's password.
     */
    const email = document.getElementById('sign-in-email').value;
    if (!email) {
      showNotification('Password reset error', 'Please enter your email to request a password reset.', /* type = */ 'error' );
      return;
    }
    document.getElementById('password-reset-button').classList.add('d-none');
    document.getElementById('password-reset-loading-button').classList.remove('d-none');
    try {
      await sendPasswordReset();
      window.location.href = `${window.location.origin}\\acount\\password-reset-done`;
    } catch(error) {
      document.getElementById('password-reset-button').classList.remove('d-none');
      document.getElementById('password-reset-loading-button').classList.add('d-none');
      showNotification('Password reset error', 'Password reset email failed to send. Try again later.', /* type = */ 'error' );
    }
  },

  resetPasswordCodeCheck() {
    /**
     * Check if the password reset code is valid.
     */
    const url = new URL(window.location.href);
    const code = url.searchParams.get('oobCode');
    verifyPasswordReset(code)
      .then((email) => {
        document.getElementById('sign-in-email').value = email;
      })
      .catch(()  => {
        const invalidMessage = document.getElementById('password-reset-code-invalid-message');
        const passwordResetForm = document.getElementById('password-reset-form');
        passwordResetForm.classList.add('d-none');
        invalidMessage.classList.remove('d-none');
      });
  },

  resetPasswordConfirm() {
    /**
     * Confirm a password reset.
     */
    const newPassword = document.getElementById('sign-in-password').value;
    const newPasswordConfirmation = document.getElementById('sign-in-password-confirmation').value;
    if (newPassword !== newPasswordConfirmation) {
      const message = 'The passwords you entered are not the same, please confirm your password.';
      showNotification('Passwords do not match', message, /* type = */ 'error');
      return;
    }
    const url = new URL(window.location.href);
    const code = url.searchParams.get('oobCode');
    confirmPasswordChange(code, newPassword)
      .then(() => {
        window.location.href = '/account/password-reset-complete';
      })
      .catch(() => {
        const message = 'The password reset link that you used is invalid. Please request a new password reset link.';
        showNotification('Password reset error', message, /* type = */ 'error');
      });
  },

  async signIn(event) {
    /**
     * Sign in with username and password.
     * @param {Event} event A user-driven event.
     */
    event.preventDefault();
    const email = document.getElementById('sign-in-email').value;
    const password = document.getElementById('sign-in-password').value;
    document.getElementById('sign-in-button').classList.add('d-none');
    document.getElementById('sign-in-loading-button').classList.remove('d-none');
    let persistence = true;
    try {
      persistence = document.getElementById('stay-signed-in').checked;
    } catch(error) { /* No persistence option. */ }
    try {
      await logIn(email, password, persistence);
    } catch(error) {
      const message = authErrors[error.code] || 'Unknown error encountered while signing in.';
      showNotification('Sign in error', message, /* type = */ 'error' );
    }
    document.getElementById('sign-in-button').classList.remove('d-none');
    document.getElementById('sign-in-loading-button').classList.add('d-none');
    try {
      const modal = Modal.getInstance(document.getElementById('sign-in-dialog'));
      modal.hide();
    } catch(error) { /* No login dialog. */ }
  },

  signInWithGoogle() {
    /**
     * Sign in with Google.
     */
    googleLogIn();
  },

  signUp,

  async signOut(redirect = true) {
    /**
     * Sign a user out of their account.
     */
    await logOut();
    await authRequest('/src/auth/logout');
    if (redirect) document.location.href = `${window.location.origin}/account/sign-out`;
  },
  
  verifyUser() {
    /**
     * Send a user a verification email.
     */
    const user = getCurrentUser();
    user.sendEmailVerification().then(() => {
      showNotification('Verification email sent', error.message, /* type = */ 'success');
    }).catch((error) => {
      showNotification('Verification error', error.message, /* type = */ 'error');
    });
  },

}

export async function signUp() {
  /**
   * Sign a user up for a Firebase account with a username and password.
   */
  const terms = document.getElementById('sign-up-terms-accepted');
  if (!terms.checked) {
    const message = 'Please agree with our terms of service and read our privacy policy to create an account.';
    showNotification('Terms not accepted', message, /* type = */ 'error');
    terms.classList.add('is-invalid');
    return;
  } else {
    terms.classList.remove('is-invalid');
  }
  const email = document.getElementById('sign-up-email').value;
  const password = document.getElementById('sign-up-password').value;
  document.getElementById('sign-up-button').classList.add('d-none');
  document.getElementById('sign-up-loading-button').classList.remove('d-none');
  try {
    await createAccount(email, password);
    const newsletter = document.getElementById('newsletter-signup');
    if (newsletter.checked) await cannlytics.payments.subscribe();
  } catch(error) {
    const message = authErrors[error.code] || 'Unknown error encountered while signing in.';
    document.getElementById('sign-up-button').classList.remove('d-none');
    document.getElementById('sign-up-loading-button').classList.add('d-none');
    showNotification('Sign up error', message, /* type = */ 'error');
    return;
  }
  document.getElementById('sign-up-button').classList.remove('d-none');
  document.getElementById('sign-up-loading-button').classList.add('d-none');
}
