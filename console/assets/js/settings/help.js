/**
 * Help Settings JavaScript | Cannlytics Console
 * Copyright (c) 2021-2022 Cannlytics
 * 
 * Authors: Keegan Skeate <keegan@cannlytics.com>
 * Created: 7/13/2021
 * Updated: 12/14/2021
 * License: MIT License <https://github.com/cannlytics/cannlytics-console/blob/main/LICENSE>
 */
import { APP_NAME, CONTACT_EMAIL } from '../constants.js';
import { auth } from '../firebase.js';
import { authRequest, showNotification } from '../utils.js';

export const helpSettings = {

  async inviteUser() {
    /**
     * Invite a user to the console, optionally specifying if the user
     * should be a team member of the user's current organization.
     */
    // FIXME: Ensure this works with appropriate messages.
    document.getElementById('action-button').classList.add('d-none');
    document.getElementById('action-button-loading').classList.remove('d-none');
    const user = auth.currentUser || {};
    const message = document.getElementById('feedback-message').value
    const timestamp = Date.now().toString(); // Optional: Specify time zone.
    const code = Math.random().toString(36).slice(-3);
    const name = user.displayName || 'Anonymous user';
    const data = {
      name,
      subject: `Invitation to the ${APP_NAME}`,
      message: message,
      email: user.email || 'No user',
      organization: user.organization || 'No organization',
      from: CONTACT_EMAIL,
      reply: CONTACT_EMAIL,
      recipients: [CONTACT_EMAIL],
      promo: code,
    };
    const response = await authRequest('/src/email/invite-user', { data });
    if (response.success) {
      const message = $`You have successfully invited ${name}.`;
      showNotification('Invitation sent sent', message, /* type = */ 'success');
      document.getElementById('feedback-message').value = '';
      document.getElementById('action-button').classList.remove('d-none');
      document.getElementById('action-button-loading').classList.add('d-none');
    } else {
      showNotification('Unable to send feedback', response.message, /* type = */ 'error');
    }
  },

  async sendFeedback() {
    /**
     * Send feedback through Firestore-triggered Google Cloud Function.
     */
    document.getElementById('send-feedback-button').classList.add('d-none');
    document.getElementById('send-feedback-button-loading').classList.remove('d-none');
    const user = auth.currentUser || {};
    const input = document.getElementById('feedback-message');
    const message = input.value
    const timestamp = Date.now().toString(); // Optional: Specify time zone.
    const code = Math.random().toString(36).slice(-3);
    const data = {
      name: user.displayName || 'Anonymous user',
      subject: `New ${APP_NAME} feedback!`,
      message: message,
      email: user.email || 'No user',
      organization: user.organization || 'No organization',
      from: CONTACT_EMAIL,
      reply: CONTACT_EMAIL,
      recipients: [CONTACT_EMAIL],
      promo: code,
    };
    const response = await authRequest('/src/email/send-message', { data });
    if (response.success) {
      const message = 'Thank you for your feedback, your feedback helps build the platform.';
      showNotification('Feedback sent', message, /* type = */ 'success');
      input.value = '';
      document.getElementById('send-feedback-button').classList.remove('d-none');
      document.getElementById('send-feedback-button-loading').classList.add('d-none');
    } else {
      showNotification('Unable to send feedback', response.message, /* type = */ 'error');
    }
  },

};
