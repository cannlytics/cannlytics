/**
 * Payments JavaScript | Cannlytics Console
 * Created: 1/17/2021
 * Updated: 7/15/2021
 */

export const payments = {

  subscribe(subscription) {
    /*
     * Save account information,
     * then navigate to the confirmation page.
     */
    authRequest('/src/subscribe', subscription).then((response) => {
      if (response.success) {
        document.getElementById('pin_input').value = '';
        showNotification('Subscribed', response.message, { type: 'success' });
        window.location.href = '/';
      } else {
        showNotification('Unable to subscribe', response.message, { type: 'error' });
      }
    });
  },

};
