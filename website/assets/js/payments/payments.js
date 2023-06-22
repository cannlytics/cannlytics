/**
 * Payment JavaScript | Cannlytics Website
 * Copyright (c) 2021-2023 Cannlytics
 * 
 * Authors: Keegan Skeate <https://github.com/keeganskeate>
 * Created: 1/17/2021
 * Updated: 6/21/2023
 * License: MIT License <https://github.com/cannlytics/cannlytics-website/blob/main/LICENSE>
 */
import { getDocument, onAuthChange } from '../firebase.js';
import { authRequest, getUrlParameter, showNotification, validateEmail } from '../utils.js';
import { hideLoadingButton, showLoadingButton } from '../ui/ui.js';

/**---------------------------------------------------------------------------
 * PayPal Subscriptions
 *--------------------------------------------------------------------------*/

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
    showNotification('Error Subscribing', message, /* type = */ 'error');
  }
}


const addPayPalButton = function(planId, planName) {
  /**
   * Create a PayPal button for a given subscription plan ID and name.
   */
  paypal.Buttons({
    intent: 'subscription',
    createSubscription: function(data, actions) {
      return actions.subscription.create({'plan_id': planId});
    },
    onApprove: function(data, actions) {
      try {
        const { subscriptionID } = data;
        return actions.order.capture().then(async function(details) {
          submitSubscription(details, subscriptionID, planName);
        });
      } catch(error) {
        reportError();
      }
    }
  }).render(`#paypal-${planName}`);
}


export const payments = {

  /**---------------------------------------------------------------------------
   * Setup Subscriptions
   *--------------------------------------------------------------------------*/

  async initializeSupport() {
    /**
     * Initialize PayPal support subscription checkouts.
     */
    const enterpriseSubscription = await this.getSubscription('enterprise');
    const proSubscription = await this.getSubscription('pro');
    const premiumSubscription = await this.getSubscription('premium');
    addPayPalButton(enterpriseSubscription.plan_id, 'enterprise');
    addPayPalButton(proSubscription.plan_id, 'pro');
    addPayPalButton(premiumSubscription.plan_id, 'premium');
  },

  async initializePremiumSubscription() {
    /**
     * Initialize premium PayPal subscription checkout.
      */
    const premiumSubscription = await this.getSubscription('premium');
    addPayPalButton(premiumSubscription.plan_id, 'premium');
  },

  async subscribe(subscription, subscriptionType = 'subscribe') {
    /**
     * Subscribe email, then navigate to the confirmation page.
     * @param {Object} subscription An object with subscription data.
     * @param {String} subscriptionType The type of subscription.
     */
    let data;
    const form = document.getElementById('account-information');
    showLoadingButton(`${subscriptionType}-button`);
    if (form) {
      data = Object.fromEntries(new FormData(form).entries());
      data = { ...data, ...subscription };
    } else {
      const userEmail = document.getElementById(`${subscriptionType}-email`).value;
      if (!validateEmail(userEmail)) {
        const message = 'Please provide a valid email.'
        showNotification('Invalid email', message, /* type = */ 'error');
        hideLoadingButton(`${subscriptionType}-button`);
        return;
      }
      data = { email: userEmail, plan_name: 'newsletter' };
    }
    const response = await authRequest('/src/payments/subscribe', data);
    if (response.success) {
      window.location.href = `${window.location.origin}/subscriptions/subscribed`;
    } else {
      const message = 'An error occurred when processing your subscription. Please contact dev@cannlytics.com for help.';
      showNotification('Error saving your account', message, /* type = */ 'error');
      hideLoadingButton(`${subscriptionType}-button`);
    }
  },

  /**---------------------------------------------------------------------------
   * Manage Subscriptions
   *--------------------------------------------------------------------------*/

  initializeSubscriptions() {
    /**
     * Initialize the user's current subscriptions.
     */

    // Get the user's level of support.
    const support = JSON.parse(document.getElementById('user_support').textContent);
    console.log('Users level of support:');
    console.log(support);

    // TODO: If no subscription, then show Upgrade on all.

    // TODO: If subscription, then show Cancel on current subscription and Change on others.


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

  async changeSupportSubscription() {
    /**
     * Change the user's level of support.
     */
    const newSupport = this.id.replace('support-option-', '');
    const currentSupport = JSON.parse(document.getElementById('user_support').textContent);
    document.getElementById('checkout-enterprise-button').classList.add('d-none');
    document.getElementById('checkout-pro-button').classList.add('d-none');
    document.getElementById('checkout-premium-button').classList.add('d-none');
    if (newSupport === currentSupport) {
      cannlytics.payments.cancelChangeSupportSubscription();
    }
    else {
      if (newSupport === 'no-support' && currentSupport) {
        document.getElementById('save-support-button').classList.remove('d-none');
        document.getElementById('cancel-support-button').classList.remove('d-none');
        document.getElementById('checkout-enterprise-button').classList.add('d-none');
        document.getElementById('checkout-pro-button').classList.add('d-none');
        document.getElementById('checkout-premium-button').classList.add('d-none');
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
    document.getElementById('checkout-premium-button').classList.add('d-none');
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

  /**---------------------------------------------------------------------------
   * Subscription Plans
   *--------------------------------------------------------------------------*/

  async initializeFreeNewsletter() {
    /** 
     * Initialize the user's free newsletter subscription.
     */
    onAuthChange(async (user) => {
      if (!user) return;
        const userData = await authRequest('/api/users');
        console.log('USER DATA:');
        console.log(userData);
        document.getElementById('free-newsletter-checkbox').checked = userData.data.newsletter;
    });
  },

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
    // FIXME: Popup is not working properly (double popup).
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

  /**---------------------------------------------------------------------------
   * Tokens
   *--------------------------------------------------------------------------*/

  navigateToBuyTokens() {
    /** Navigate the user to the buy tokens page. */
    const tokens = document.getElementById('tokenSlider').value;
    
  },

  async getUserTokens() {
    /**
     * Get the current user's subscriptions.
     */
    const response = await authRequest('/src/payments/subscriptions');
    if (response.data) {
      console.log('DATA:');
      console.log(response.data);
      document.getElementById('current_tokens').textContent = response.data.tokens ?? 0;
      document.getElementById('price_per_token').textContent = (response.data.price_per_token ?? 0.05) * 100;
    }
    try {
      // Get the number of tokens from the URL.
      const urlParams = new URLSearchParams(window.location.search);
      const tokens = urlParams.get('tokens');
      document.getElementById('tokens').textContent = tokens.toString();

      // Get the price per token.
      const pricePerTokenElement = document.getElementById('price_per_token');
      const pricePerToken = parseFloat(pricePerTokenElement.textContent);

      // Calculate the total price.
      const totalPrice = tokens * pricePerToken / 100;

      // Now you can use totalPrice wherever you need it.
      // For example, to display it in an element with id "totalPrice":
      const totalPriceElement = document.getElementById('price');
      totalPriceElement.textContent = `$${totalPrice.toFixed(2)}`;
    } catch(error) {
      // No price to calculate.
    }
    return response.data;
  },

  renderBuyTokensButton() {
    /**
     * Show a PayPal button that the user can use to purchase tokens.
     * @param {String} buttonId PayPal's hosted button ID.
     */
    const button = document.getElementById('paypal-order-tokens-button');
    button.innerHTML = '';
    button.classList.remove('d-none');

    // Render the PayPal button.
    const FUNDING_SOURCES = [
      // FUNDING SOURCES
      paypal.FUNDING.PAYPAL,
      paypal.FUNDING.CARD,
    ];
    FUNDING_SOURCES.forEach(fundingSource => {
      paypal.Buttons({
        fundingSource,

        // Style.
        style: {
          color: 'silver',
          layout: 'horizontal',
          shape: 'rect',
          color: (fundingSource == paypal.FUNDING.PAYLATER) ? 'gold' : '',
        },

        createOrder: async (data, actions) => {
          /* Create an order for tokens. */
          try {
            // Make an orders request.
            const tokens = document.getElementById('tokenSlider').value;
            const details = await authRequest('/src/payments/orders', { tokens });
            console.log('DETAILS:');
            console.log(details);
            return details.data.id;
          } catch (error) {
            console.error(error);
            const message = `An error occurred when buying tokens. Please email dev@cannlytics.com for help.`;
            showNotification('Error buying tokens', message, /* type = */ 'error');
            return null;
          }
        },

        onApprove: async (data, actions) => {
          /* Handle approved transactions. */
          try {
            // Make an approval request.
            const tokens = document.getElementById('tokenSlider').value;
            const url = `/src/payments/orders/${data.orderID}/capture`;
            const response = await authRequest(url, { tokens });
            const details = response.data;
            console.log('DETAILS:');
            console.log(details);

            // Three cases to handle:
            //   (1) Recoverable INSTRUMENT_DECLINED -> call actions.restart()
            //   (2) Other non-recoverable errors -> Show a failure message
            //   (3) Successful transaction -> Show confirmation or thank you message
            // This example reads a v2/checkout/orders capture response, propagated from the server
            // You could use a different API or structure for your 'orderData'
            // See: https://developer.paypal.com/docs/checkout/integration-features/funding-failure/
            var errorDetail = false;
            try {
              errorDetail = Array.isArray(details.details) && details.details[0];
              if (errorDetail && errorDetail.issue === 'INSTRUMENT_DECLINED') {
                return actions.restart();
              }
            } catch(error) {
              // No error to handle.
            }

            // Show an error notification if the transaction failed.
            if (errorDetail) {
              let msg = 'Sorry, your transaction could not be processed.';
              msg += errorDetail.description ? ' ' + errorDetail.description : '';
              msg += details.debug_id ? ' (' + details.debug_id + ')' : '';
              showNotification('Error buying tokens', msg, /* type = */ 'error');
              return;
            }

            // Successful transaction.
            var msg = `You have successfully purchased ${tokens} Cannlytics AI tokens! You can use your tokens to run AI-powered jobs in the app. Put your AI jobs to good use!`;
            showNotification('Cannlytics AI tokens purchased', msg, /* type = */ 'success', /* delay = */ 10000);

            // TODO: Show a success form to the user.

            // Update the user's token count.
            document.getElementById('current_tokens').textContent = details.tokens;

          } catch (error) {
            console.error(error);
            // Handle the error and display an appropriate error message to the user.
            const message = `An error occurred when approving your purchase of tokens. Please email dev@cannlytics.com for help.`;
            showNotification('Error approving your purchase', message, /* type = */ 'error');
          }
        },
      }).render('#paypal-order-tokens-button');
    });
  },


  /**---------------------------------------------------------------------------
   * Misc
   *--------------------------------------------------------------------------*/

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

/**---------------------------------------------------------------------------
 * Notifications
 *--------------------------------------------------------------------------*/

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
