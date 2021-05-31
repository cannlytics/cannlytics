/**
 * Errors JavaScript | Cannlytics Console
 * Licensed under GPLv3 (https://github.com/cannlytics/cannlytics_console/blob/main/LICENSE)
 * Author: Keegan Skeate
 * Created: 4/28/2021
 */

import { authRequest } from '../utils.js';

export const errorSettings = {


  reportError(data) {
    /*
     * Reports an error to the back-end.
     */
    authRequest('/api/errors', data).then(() => {
      const message = 'Thank you for reporting this error. We will try to address it as soon as possible.';
      showNotification('Error report sent', message, { type: 'success' });
    }).catch((error) => {
      const message = "We're sorry, your error report failed to send. We will still try to find the root cause if possible.";
      showNotification('Failed to send error report', message, { type: 'error' });
    });
  },

};
