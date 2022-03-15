/**
 * Payment JavaScript | Cannlytics Website
 * Copyright (c) 2021-2022 Cannlytics
 * 
 * Authors: Keegan Skeate <keegan@cannlytics.com>
 * Created: 1/17/2021
 * Updated: 1/11/2022
 * License: MIT License <https://github.com/cannlytics/cannlytics-website/blob/main/LICENSE>
 */
import { getDocument } from '../firebase.js';
import { authRequest, getUrlParameter, showNotification, validateEmail } from '../utils.js';
import { hideLoadingButton, showLoadingButton } from '../ui/ui.js';

const submitSubscription = async function(details, subscriptionID, planName) {
  /**
   * Submit a subscription through the API.
   */
  const name = details.payer.name.given_name;
  const email = details.payer.email_address;
  const postData = { name, email, id: subscriptionID, plan_name: planName }
  const response = await authRequest('/src/payments/subscribe', postData);
  if (response.success) {
    window.location.href = `${window.location.origin}/subscriptions/subscribed`;
  } else {
    const message = `An error occurred when subscribing to ${planName} subscription. Please try again later or email support.`;
    showNotification('Error Subscribing', response.message, /* type = */ 'error');
  }
}

export const payments = {

  /**---------------------------------------------------------------------------
   * Setup Subscriptions
   *--------------------------------------------------------------------------*/

  async initializePremiumSubscription() {
    /**
     * Initialize premium PayPal subscription checkout.
      */
    const subscription = await this.getSubscription('premium');
    paypal.Buttons({
      createSubscription: function(data, actions) {
        return actions.subscription.create({
          'plan_id': subscription.plan_id,
        });
      },
      onApprove: function(data, actions) {
        try {
          const { subscriptionID } = data;
          return actions.order.capture().then(async function(details) {
            submitSubscription(details, subscriptionID, 'premium');
          });
        } catch(error) {
          reportError();
        }
      }
    }).render('#paypal-premium');
  },

  async initializeSupport() {
    /**
     * Initialize PayPal support subscription checkouts.
     */
    const enterpriseSubscription = await this.getSubscription('enterprise');
    const proSubscription = await this.getSubscription('pro');
    paypal.Buttons({
      createSubscription: function(data, actions) {
        return actions.subscription.create({
          'plan_id': enterpriseSubscription.plan_id,
        });
      },
      onApprove: function(data, actions) {
        try {
          const { subscriptionID } = data;
          return actions.order.capture().then(async function(details) {
            submitSubscription(details, subscriptionID, 'enterprise');
          });
        } catch(error) {
          reportError();
        }
      }
    }).render('#paypal-enterprise');
    paypal.Buttons({
      createSubscription: function(data, actions) {
        return actions.subscription.create({
          'plan_id': proSubscription.plan_id,
        });
      },
      onApprove: function(data, actions) {
        try {
          const { subscriptionID } = data;
          return actions.order.capture().then(async function(details) {
            submitSubscription(details, subscriptionID, 'pro');
          });
        } catch(error) {
          reportError();
        }
      }
    }).render('#paypal-pro');
  },

  /**---------------------------------------------------------------------------
   * Manage Subscriptions
   *--------------------------------------------------------------------------*/

  initializeSubscriptions() {
    /**
     * Initialize the user's current subscriptions.
     */

    // Setup the user interface.
    const newsletter = JSON.parse(document.getElementById('user_newsletter').textContent);
    const premium = JSON.parse(document.getElementById('user_premium').textContent);
    const support = JSON.parse(document.getElementById('user_support').textContent);
    const newsletterCheckbox = document.getElementById('free-newsletter-checkbox');
    const premiumCheckbox = document.getElementById('premium-material-checkbox');
    if (newsletter) newsletterCheckbox.checked = true;
    if (premium) premiumCheckbox.checked = true;
    if (support) {
      document.getElementById(`support-option-${support}`).checked = true;
      document.getElementById('support-option-no-support').checked = false;
    }
    
    // Attach functionality.
    newsletterCheckbox.addEventListener('click', this.subscribeToFreeNewsletter);
    premiumCheckbox.addEventListener('click', this.subscribeToPremium);
    document.getElementById('save-premium-button').addEventListener('click', this.savePremiumSubscription);
    document.getElementById('cancel-premium-button').addEventListener('click', this.cancelSubscribeToPremium);
    document.getElementById('support-option-enterprise').addEventListener('click', this.changeSupportSubscription);
    document.getElementById('support-option-pro').addEventListener('click', this.changeSupportSubscription);
    document.getElementById('support-option-no-support').addEventListener('click', this.changeSupportSubscription);
    document.getElementById('save-support-button').addEventListener('click', this.saveSupportSubscription);
    document.getElementById('cancel-support-button').addEventListener('click', this.cancelChangeSupportSubscription);
    
    // Initialize subscriptions.
    this.initializePremiumSubscription();
    this.initializeSupport();
  },

  async changeSupportSubscription() {
    /**
     * Change the user's level of support.
     */
    const newSupport = this.id.replace('support-option-', '');
    const currentSupport = JSON.parse(document.getElementById('user_support').textContent);
    if (newSupport === currentSupport) {
      cannlytics.payments.cancelChangeSupportSubscription();
    }
    else {
      if (newSupport === 'no-support' && currentSupport) {
        document.getElementById('save-support-button').classList.remove('d-none');
        document.getElementById('cancel-support-button').classList.remove('d-none');
        document.getElementById('checkout-enterprise-button').classList.add('d-none');
        document.getElementById('checkout-pro-button').classList.add('d-none');
      } else {
        document.getElementById('save-support-button').classList.add('d-none');
        document.getElementById('cancel-support-button').classList.remove('d-none');
        const checkoutButton = document.getElementById(`checkout-${newSupport}-button`);
        checkoutButton.classList.remove('d-none');
      }
    }
  },

  cancelChangeSupportSubscription() {
    /**
     * Cancel the new support choice and return to the user's current level of support.
     */
    document.getElementById('save-support-button').classList.add('d-none');
    document.getElementById('cancel-support-button').classList.add('d-none');
    document.getElementById('checkout-enterprise-button').classList.add('d-none');
    document.getElementById('checkout-pro-button').classList.add('d-none');
    const support = JSON.parse(document.getElementById('user_support').textContent);
    if (support) {
      const supportId = support.toLowerCase();
      document.getElementById(`support-option-${supportId}`).checked = true;
      document.getElementById('support-option-no-support').checked = false;
    }
    else document.getElementById('support-option-no-support').checked = true;
  },

  async saveSupportSubscription() {
    /**
     * Save the user's decision about their support subscription.
     */
    const currentSupport = JSON.parse(document.getElementById('user_support').textContent);
    await cancelSubscription(currentSupport);
    await authRequest('/api/users', { support: 'no-support' });
    const message = `You have been unsubscribed from ${currentSupport} support.`;
    showNotification('Unsubscribed', message, /* type = */ 'success');
    document.getElementById('save-support-button').classList.add('d-none');
    document.getElementById('cancel-support-button').classList.add('d-none');
  },

  /**---------------------------------------------------------------------------
   * Newsletter
   *--------------------------------------------------------------------------*/

  async subscribeToFreeNewsletter() {
    /**
     * Subscribe the user to the free newsletter.
     */
    const newsletterCheckbox = document.getElementById('free-newsletter-checkbox');
    if (newsletterCheckbox.checked) {
      await authRequest('/api/users', { newsletter: true });
      const message = 'You are now subscribed to the free newsletter.'
      showNotification('Subscribed', message, /* type = */ 'success');
    } else {
      await authRequest('/api/users', { newsletter: false });
      const message = 'You have been unsubscribed from the free newsletter.'
      showNotification('Unsubscribed', message, /* type = */ 'success');
    }
  },

  /**---------------------------------------------------------------------------
   * Premium
   *--------------------------------------------------------------------------*/

  async subscribeToPremium() {
    /**
     * Subscribe the user to the free newsletter.
     */
    const premium = JSON.parse(document.getElementById('user_premium').textContent);
    const premiumCheckbox = document.getElementById('premium-material-checkbox');
    if (premiumCheckbox.checked) {
      document.getElementById('cancel-premium-button').classList.remove('d-none');
      document.getElementById('checkout-premium-button').classList.remove('d-none');
    } else {
      if (premium) {
        document.getElementById('checkout-premium-button').classList.add('d-none');
        document.getElementById('save-premium-button').classList.remove('d-none');
        document.getElementById('cancel-premium-button').classList.remove('d-none');
      }
      else cannlytics.payments.cancelSubscribeToPremium();
    }
  },

  cancelSubscribeToPremium() {
    /**
     * Cancel the option to subscribe to premium.
     */
    document.getElementById('save-premium-button').classList.add('d-none');
    document.getElementById('cancel-premium-button').classList.add('d-none');
    document.getElementById('checkout-premium-button').classList.add('d-none');
    document.getElementById('premium-material-checkbox').checked = false;
  },

  async savePremiumSubscription() {
    /**
     * Save the user's decision about their premium subscription.
     */
    const premiumCheckbox = document.getElementById('premium-material-checkbox');
    if (premiumCheckbox.checked) {
      await authRequest('/api/users', { premium: true });
      const message = 'You are now subscribed to premium material.'
      showNotification('Subscribed', message, /* type = */ 'success');
    } else {
      await cancelSubscription('premium');
      await authRequest('/api/users', { premium: false });
      const message = 'You have been unsubscribed from premium material.'
      showNotification('Unsubscribed', message, /* type = */ 'success');
    }
    document.getElementById('save-premium-button').classList.add('d-none');
    document.getElementById('cancel-premium-button').classList.add('d-none');
  },

  /**---------------------------------------------------------------------------
   * Sponsorships
   *--------------------------------------------------------------------------*/

   getSponsorshipTiers() {
    /**
     * Get sponsorship tiers loaded into a UI script from Django.
     * @returns {Array} An array of sponsorship tier IDs.
     */
    const sponsorships = JSON.parse(
      document.getElementById('sponsorships').textContent
    );
    return sponsorships.map(x => x.id);
  },

  initializeSponsorships() {
    /**
     * Initialize the user's current sponsorship tiers.
     */
    const sponsorshipTiers = this.getSponsorshipTiers();
    const userSponsorships = JSON.parse(
      document.getElementById('user_sponsorships').textContent
    );
    sponsorshipTiers.forEach(id => {
      const tierInput = document.getElementById(`sponsor-tier-${id}`);
      if (userSponsorships.includes(id)) tierInput.checked = true;
      // TODO: Prefer to assign onchange from JavaScript file.
      // tierInput.onchange = this.toggleSponsorCheckout;
    });
    document.getElementById('select-all-tiers-button').addEventListener('click', this.selectAllSponsorshipTiers);
    document.getElementById('save-button').addEventListener('click', this.saveSponsorshipTiers);
    document.getElementById('cancel-button').addEventListener('click', this.cancelNewSponsorships);
  },

  cancelNewSponsorships() {
    /**
     * Cancels a user's newly selected sponsorships.
     */
    document.getElementById('donate-button').classList.add('d-none');
    document.getElementById('save-button').classList.add('d-none');
    document.getElementById('cancel-button').classList.add('d-none');
    const sponsorshipTiers = cannlytics.payments.getSponsorshipTiers();
    const userSponsorships = JSON.parse(document.getElementById('user_sponsorships').textContent);
    sponsorshipTiers.forEach(id => {
      const tierInput = document.getElementById(`sponsor-tier-${id}`);
      if (userSponsorships.includes(id)) tierInput.checked = true;
      else tierInput.checked = false;
    });
  },

  async saveSponsorshipTiers() {
    /**
     * Save the user's sponsorship tiers.
     */
    const sponsorships = [];
    const sponsorshipTiers = cannlytics.payments.getSponsorshipTiers();
    sponsorshipTiers.forEach(id => {
      const tierInput = document.getElementById(`sponsor-tier-${id}`);
      if (tierInput.checked) sponsorships.push(id);
    });
    try {
      await authRequest('/api/users', { sponsorships });
      // FIXME: Cancel a user's PayPal recurring donation through the API.
      const randomInt = Math.floor(Math.random() * 99);
      const staffMessage = {
        name: 'CannBot',
        subject: 'PayPal Recurring Donation Needs to be Canceled',
        message: "A user has canceled a recurring PayPal donation. Please manually ensure the user's recurring donation is canceled.",
        math_input: randomInt,
        math_total: randomInt,
      };
      await authRequest('/src/email/send-message', staffMessage);
    } catch(error) {
      const message = 'An error occurred while changing your sponsorships. Please try again later or email support.';
      showNotification('Error Saving Sponsorships', message, /* type = */ 'error');
    }
  },

  selectAllSponsorshipTiers() {
    /**
     * Select all sponsorship tiers.
     */
    const sponsorshipTiers = cannlytics.payments.getSponsorshipTiers();
    sponsorshipTiers.forEach(function(id) {
      document.getElementById(`sponsor-tier-${id}`).checked = true;
    });
    document.getElementById('cancel-button').classList.remove('d-none');
    cannlytics.payments.showDonateButton(sponsorshipTiers[0]);
  },

  showDonateButton(buttonId) {
    /**
     * Show a PayPal donation button.
     * @param {String} buttonId PayPal's hosted button ID.
     */
    const button = document.getElementById('donate-button');
    button.innerHTML = '';
    button.classList.remove('d-none');
    PayPal.Donation.Button({
      env:'production',
      hosted_button_id: buttonId,
      image: {
        src:'https://www.paypalobjects.com/en_US/i/btn/btn_donate_LG.gif',
        alt:'Donate with PayPal button',
        title:'PayPal - The safer, easier way to pay online!',
      },
      onApprove: function(data, actions) {
        // Save user's new subscription to Firestore and notify staff.
        try {
          const { subscriptionID } = data;
          return actions.order.capture().then(async function(details) {
            const name = details.payer.name.given_name;
            const email = details.payer.email_address;
            const sponsorships = JSON.parse(
              document.getElementById('user_sponsorships').textContent
            ) || [];
            sponsorships.push(subscriptionID);
            try {
              await authRequest('/api/users', { sponsorships });
            } catch(error) { /* User may not be signed in. */ }
            await reportSubscription(email, name, subscriptionID);
          });
        } catch(error) {
          reportError();
        }
      },
      onCancel: function (data) {
        const message = 'You have canceled your payment. You can always do so later.';
        showNotification('Payment Canceled', message, /* type = */ 'error');
      },
      onError: function (error) {
        const message = 'A payment error occurred. Please try again later or email support.';
        showNotification('Payment Error', message, /* type = */ 'error');
        reportError();
      },
    }).render('#donate-button');
  },

  toggleSponsorCheckout(input) {
    /**
     * Show checkout if a user is selecting new sponsorship options,
     * show save if a user deselects a current sponsorship, and
     * hide the checkout button if the user returns to their original tiers.
     */
    const tier = input.id.replace('sponsor-tier-', '');
    const userSponsorships = JSON.parse(
      document.getElementById('user_sponsorships').textContent
    ) || [];
    if (input.checked) {
      if (!userSponsorships.includes(tier)) {
        const newTiers = JSON.parse(
          localStorage.getItem('cannlytics_new_sponsor_tiers'
        )) || userSponsorships;
        newTiers.push(tier);
        localStorage.setItem('cannlytics_new_sponsor_tiers', JSON.stringify(newTiers));
        document.getElementById('cancel-button').classList.remove('d-none');
        this.showDonateButton(tier);
      }
    } else {
      let newTiers = JSON.parse(
        localStorage.getItem('cannlytics_new_sponsor_tiers'
      )) || userSponsorships;
      newTiers = newTiers.filter(item => item !== tier)
      localStorage.setItem('cannlytics_new_sponsor_tiers', JSON.stringify(newTiers));
      if (newTiers.length !== userSponsorships.length) {
        if (userSponsorships.length) {
          document.getElementById('save-button').classList.remove('d-none');
        }
        document.getElementById('cancel-button').classList.remove('d-none');
      } else {
        document.getElementById('donate-button').classList.add('d-none');
        document.getElementById('save-button').classList.add('d-none');
        document.getElementById('cancel-button').classList.add('d-none');
      }
    }
  },

  /**---------------------------------------------------------------------------
   * Checkout
   *--------------------------------------------------------------------------*/

  async initializeCheckout() {
    
    // Get subscription data.
    const planName = JSON.parse(document.getElementById('plan_name').textContent);
    const subscriptionData = await this.getSubscription(planName);
    const planID = subscriptionData['plan_id'];

    // Fill-in the template.
    document.getElementById('subscription-title').textContent = planName;
    document.getElementById('subscription-description').textContent = subscriptionData.plan_description;
    document.getElementById('subscription-price').textContent = subscriptionData.price;
    document.getElementById('subscription-price-now').textContent = `${subscriptionData.price_now} now`;

    // Initialize PayPal buttons.
    // FIXME: Display is not working properly.
    paypal.Buttons({
      style: {
          shape: 'rect',
          color: 'silver',
          layout: 'horizontal',
          label: 'subscribe',
      },
      createSubscription: function(data, actions) {
        // Optional: Validate the form.
        return actions.subscription.create({ 'plan_id': planID });
      },
      onApprove: function(data, actions) {
        const subscription = { ...data, ...{ 'plan_id': planID, 'plan_name': planName } };
        cannlytics.payments.subscribe(subscription);
      },
      onError: function (error) {
        alert('Unknown error subscribing, please contact support. Thank you for your patience and we will deliver you support.');
      },
    }).render('#paypal-button-container');

  },

  async subscribe(subscription) {
    /**
     * Subscribe email, then navigate to the confirmation page.
     * @param {Object} subscription An object with subscription data.
     */
    const form = document.getElementById('account-information');
    let data;
    showLoadingButton('subscribe-button');
    if (form) {
      data = Object.fromEntries(new FormData(form).entries());
      data = { ...data, ...subscription };
    } else {
      const userEmail = document.getElementById('sign-up-email').value;
      if (!validateEmail(userEmail)) {
        const message = 'Please provide a valid email.'
        showNotification('Invalid email', message, /* type = */ 'error');
        hideLoadingButton('subscribe-button');
        return;
      }
      data = { email: userEmail, plan_name: 'newsletter' };
    }
    const response = await authRequest('/src/payments/subscribe', data);
    if (response.success) {
      window.location.href = `${window.location.origin}/subscriptions/subscribed`;
    } else {
      const message = 'An error occurred when saving your account.';
      showNotification('Error saving your account', response.message, /* type = */ 'error');
      hideLoadingButton('subscribe-button');
    }
  },

  /**---------------------------------------------------------------------------
   * Misc
   *--------------------------------------------------------------------------*/

  async cancelSubscription(planName) {
    /**
     * Cancel a PayPal subscription for a user.
     * @param {String} planName The name of the subscription to cancel.
     */
    await authRequest('/api/payments/unsubscribe', { plan_name: planName });
    if (response.success) {
      const message = 'An error occurred when saving your account.';
      showNotification('Subscription canceled', message, /* type = */ 'success');
    } else {
      const message = 'An error occurred when canceling your subscription. Please email support.';
      showNotification('Error Canceling Subscription', message, /* type = */ 'error');
    }
  },

  async getSubscription(name) {
    /**
     * Get a subscription given its name.
     * @param {String} name The name of the subscription plan.
     */
    return await getDocument(`public/subscriptions/subscription_plans/${name}`);
  },

  async getUserSubscriptions() {
    /**
     * Get the current user's subscriptions.
     */
    const response = await authRequest('/src/payments/subscriptions');
    return response.data;
  },

  async logPromo() {
    /**
     * Log a promotional event.
     */
    const code = getUrlParameter('source');
    if (!code) return;
    const data = { 'promo_code': code };
    await authRequest('/src/market/promotions', data);
  },

};

export const reportError = async () => {
  /**
   * Report a payment error so it can be corrected manually.
   */
  try {
    const randomInt = Math.floor(Math.random() * 99);
    const data = {
      name: 'CannBot',
      subject: 'A PayPal payment error occurred!',
      message: 'An unhandled error occurred during a PayPal payment. Please correct this matter manually.',
      math_input: randomInt,
      math_total: randomInt,
    };
    await authRequest('/src/email/send-message', data);
  } catch(error) {
    // Could not report error.
  }
}

export const reportSubscription = async (email, name, id) => {
  /**
   * Report a new subscription to the staff.
   */
  try {
    const randomInt = Math.floor(Math.random() * 99);
    const data = {
      name: 'CannBot',
      subject: 'New PayPal Payment!',
      message: `Payment by:\n\nEmail: ${email}\nName: ${name}\nPayPal ID: ${id}`,
      math_input: randomInt,
      math_total: randomInt,
    };
    await authRequest('/src/email/send-message', data);
  } catch(error) {
    // Could not report subscription.
  }
}
