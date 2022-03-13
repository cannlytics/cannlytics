/**
 * Payments JavaScript | Cannlytics Console
 * Copyright (c) 2021-2022 Cannlytics
 * 
 * Authors: Keegan Skeate <keegan@cannlytics.com>
 * Created: 1/17/2021
 * Updated: 1/13/2022
 * License: MIT License <https://github.com/cannlytics/cannlytics-console/blob/main/LICENSE>
 */
import { CONTACT_EMAIL } from '../constants.js';
import { getCurrentUser, getDocument } from '../firebase.js';
import { authRequest, showNotification } from '../utils.js';

export const payments = {

  async initializeSupport() {
    /**
     * Select subscription, getting subscription plan ID and rendering a PayPal button.
     */
    document.getElementById('cancel-support-button').classList.remove('d-none');
    document.getElementById('finish-support-button').classList.add('d-none');
    const tier = document.getElementById('input_tier').value;
    if (tier === 'free') {
      document.getElementById('finish-support-loading-button').classList.remove('d-none');
    }
    try {
      this.showSubscription();
    } catch(error) {
      document.getElementById('finish-support-loading-button').classList.add('d-none');
      document.getElementById('finish-support-button').classList.remove('d-none');
    }
  },

  async showSubscription() {
    /*
     * Change subscription, getting subscription plan ID and rendering a PayPal button.
     */
    document.getElementById('paypal-button-container').innerHTML = '';
    const tier = document.getElementById('input_tier').value;
    if (!tier) {
      const message = 'Please choose a level of support. Free is an option.';
      showNotification('Select your level of support.', message, /* type = */ 'error');
      return;
    }
    if (tier === 'free') {
      document.getElementById('cancel-support-button').classList.add('d-none');
      const user = getCurrentUser();
      const details = { payer: { name: { given_name: user.displayName }, email_address: user.email } };
      submitSubscription(details, /* subscriptionId = */ null, tier);
      return;
    }
    const subscription = await this.getSubscription(tier);
    const planID = subscription.plan_id;
    const subscriptionName = subscription.id;
    paypal.Buttons({
      style: {
        shape: 'rect',
        color: 'silver',
        layout: 'horizontal',
        label: 'subscribe',
      },
      createSubscription: function(data, actions) {
        return actions.subscription.create({ 'plan_id': planID });
      },
      onApprove: function(data, actions) {
        try {
          const { subscriptionID } = data;
          return actions.order.capture().then(async function(details) {
            submitSubscription(details, subscriptionID, subscriptionName);
          });
        } catch(error) {
          reportError();
        }
      },
      onError: function (error) {
        alert(`Unknown error subscribing. Please contact ${CONTACT_EMAIL}. Thank you for your patience and we will deliver you support.`);
      },
    }).render('#paypal-button-container');
  },

  async getSubscription(name) {
    /**
     * Get a subscription given its name.
     * @param {String} name The name of the subscription plan.
     */
    return await getDocument(`public/subscriptions/subscription_plans/${name}`);
  },

  async getOrganizationSubscription() {
    /**
     * Get an organization's subscription data.
     */
    // TODO: Prefer to get this data through the API.
    const orgId = document.getElementById('organization_id').value;
    const data = await getDocument(`organizations/${orgId}/organization_settings/subscription`);
    return data;
  },

  async getUserSubscriptions() {
    /**
     * Get the current user's subscriptions.
     */
    const response = await authRequest('/src/payments/subscriptions');
    return response.data;
  },

  async subscribe(subscription) {
    /**
     * Save account information,
     * then navigate to the confirmation page.
     * @param {String} subscription A specific subscription for the user.
     */
    const response = await authRequest('/src/payments/subscribe', subscription);
    if (response.success) {
      document.getElementById('pin_input').value = '';
      showNotification('Subscribed', response.message, /* type = */ 'success');
      window.location.href = '/';
    } else {
      showNotification('Unable to subscribe', response.message, /* type = */ 'error');
    }
  },

};

const reportError = async () => {
  /**
   * Report a payment error so it can be corrected manually.
   */
  try {
    const data = {
      'name': 'CannBot',
      'subject': 'A PayPal payment error occurred!',
      'message': 'An unhandled error occurred during a PayPal payment. Please correct this matter manually.',
    };
    await authRequest('/src/email/send-message', data);
  } catch(error) {
    // Could not report error.
  }
}

const submitSubscription = async function(details, subscriptionId, planName) {
  /**
   * Submit a subscription through the API.
   */
  const name = details.payer.name.given_name;
  const email = details.payer.email_address;
  const postData = { name, email, id: subscriptionId, plan_name: planName }
  const response = await authRequest('/src/payments/subscribe', postData);
  if (response.success) {
    window.location.href = `${window.location.origin}?q=subscribed`;
  } else {
    const message = `An error occurred when subscribing to ${planName} subscription. Please try again later or email support.`;
    showNotification('Error Subscribing', response.message, /* type = */ 'error');
  }
}
