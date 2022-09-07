/**
 * Data JavaScript | Cannlytics Website
 * Copyright (c) 2021-2022 Cannlytics
 * 
 * Authors: Keegan Skeate <https://github.com/keeganskeate>
 * Created: 8/21/2021
 * Updated: 7/20/2022
 * License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>
 */
import { reportError } from '../payments/payments.js';
import { authRequest } from '../utils.js';
import { CoADoc } from './coas.js';
import { dataTables } from './dataTables.js';

export const data = {

  coas: CoADoc,
  ...dataTables,

  /**---------------------------------------------------------------------------
   * Payment
   *--------------------------------------------------------------------------*/

  initializePayPalPayment() {
    /**
     * Initialize PayPal payment option.
     */

    // Get the product description.
    const orderDescription = document.getElementById('dataset_description').value;

    paypal.Buttons({
      style: {
        shape: 'pill',
        color: 'gold',
        layout: 'vertical',
        label: 'buynow',
        
      },
      createOrder: function(data, actions) {

        // Allow the user to choose business or student price.
        let priceTotal = 499;
        if (document.getElementById('student-price').checked) {
          priceTotal = document.getElementById('dataset_student_price').value;
        } else {
          priceTotal = document.getElementById('dataset_business_price').value;
        }
        priceTotal = parseFloat(priceTotal.replace('$', ''));

        // Optional: Allow for other currencies.
        return actions.order.create({
          purchase_units: [{
            description: orderDescription,
            amount: {
              currency_code: 'USD',
              value: priceTotal,
              breakdown: {
                item_total: {
                  currency_code: 'USD',
                  value: itemTotalValue,
                },
                shipping: {
                  currency_code: 'USD',
                  value: 0,
                },
                tax_total: {
                  currency_code: 'USD',
                  value: 0,
                }
              }
            },
            items: [{
              name: orderDescription,
              unit_amount: {
                currency_code: 'USD',
                value: priceTotal,
              },
              quantity: 1
            }]
          }]
        });
      },
      onApprove: function(data, actions) {
        return actions.order.capture().then(async function(details) {
          
          // Capture payment details.
          const name = details.payer.name.given_name;
          const email = details.payer.email_address;
          const paymentId = details.id;
          const postData = {
            name,
            email,
            payer_id: details.payer.payer_id,
            payment_id: paymentId,
            payment_link: details.links[0].href,
            order_json: JSON.stringify(details),
          };

          // Get dataset file ordered.
          postData.dataset = {
            file_name: document.getElementById('dataset_file_name').value,
            file_ref: document.getElementById('dataset_file_ref').value,
          };

          // Trigger download, double-checking the payment in the API.
          const response = await authRequest('/src/market/buy-data', postData);
          if (response.success) {

            // Report payment.
            await reportSubscription(email, name, paymentId);

            // Show a success / thank you message.
            const element = document.getElementById('paypal-button-container');
            element.innerHTML = '';
            document.getElementById('thank-you-message').classList.remove('d-none');

          } else {
            const message = 'An error occurred when buying data. Please try again later or email support.';
            showNotification('Error Subscribing', message, /* type = */ 'error');
          }

        });
      },
      onError: function(error) {
        const message = 'A payment error occurred. Please try again later or email support.';
        showNotification('Payment Error', message, /* type = */ 'error');
        reportError();
      },
    }).render('#paypal-button-container');
  },

  /**---------------------------------------------------------------------------
   * Market
   * TODO: Finish blockchain market functionality.
   *--------------------------------------------------------------------------*/

  async getDataset(id) {
    /**
     * Get metadata about a given dataset.
     * @param {String} id A dataset ID.
     */
    return await authRequest(`/api/datasets/${id}`);
  },

  async getDataMarketStats() {
    /**
     * Get metadata about the data market.
     */
    return await authRequest('/api/market');
  },

  async getStateData(id) {
    /**
     * Get metadata about a given state's data.
     * @param {String} id A state ID. Typically the lowercase state abbreviation.
     *    e.g. `nc` for North Carolina.
     */
    if (id) return await authRequest(`/api/data/state/${id}`);
    return await authRequest('/api/data/state');
  },

  downloadDataset() {
    /**
     * Download a given dataset.
     */
    authRequest('/api/market/download-lab-data');
  },

  async publishDataset() {
    /**
     * Publish a given dataset on the data market.
     */
    const response = authRequest('/api/market/download-lab-data');
    if (response.success) {
      const message = 'Your dataset has been published.';
      showNotification('Data Published', message, /* type = */ 'success');
    } else {
      const message = 'An error occurred when saving your account.';
      showNotification('Error Publishing Data', message, /* type = */ 'error');
    }
  },

  sellDataset() {
    /**
     * Sell a given dataset on the data market.
     */
    // TODO: Get dataset details from the UI.
    const dataset = {};
    const response = authRequest('/api/market/sell', dataset);
    if (response.success) {
      const message = 'Your dataset is now for sale.';
      showNotification('Data Listed for Sale', message, /* type = */ 'success');
    } else {
      const message = 'An error occurred when listing your data for sale.';
      showNotification('Error Listing Data for Sale', message, /* type = */ 'error');
    }
  },

  buyDataset() {
    /**
     * Buy a given dataset on the data market.
     */
    // TODO: Get dataset details from the UI.
    const dataset = {};
    const response = authRequest('/api/market/buy', dataset);
    if (response.success) {
      const message = 'Your have successfully bought a dataset.';
      showNotification('Data Purchased', message, /* type = */ 'success');
    } else {
      const message = 'An error occurred when purchasing this dataset.';
      showNotification('Error Purchasing Data', message, /* type = */ 'error');
    }
  },

};
