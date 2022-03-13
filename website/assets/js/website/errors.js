/**
 * Errors JavaScript | Cannlytics Website
 * Copyright (c) 2021-2022 Cannlytics
 * 
 * Authors: Keegan Skeate <keegan@cannlytics.com>
 * Created: 4/28/2021
 * Updated: 12/27/2021
 * License: MIT License <https://github.com/cannlytics/cannlytics-website/blob/main/LICENSE>
 */

import { authRequest } from '../utils.js';

export const errorSettings = {

  reportError(data) {
    /**
     * Reports an error to the back-end.
     * @param {Object} data Error data.
     */
    const randomInt = Math.floor(Math.random() * 99);
    data.math_input = randomInt;
    data.math_total = randomInt;
    try {
      authRequest('/src/email/send-message', data);
      const message = 'Thank you for reporting this error. We will try to address it as soon as possible.';
      showNotification('Error report sent', message, /* type = */ 'success');
    } catch(error) {
      const message = "We're sorry, your error report failed to send. We will still try to find the root cause if possible.";
      showNotification('Failed to send error report', message, /* type = */ 'error');
    }
  },

};
