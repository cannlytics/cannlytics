/**
 * Payment JavaScript | Cannlytics Website
 * Copyright (c) 2021-2023 Cannlytics
 * 
 * Authors: Keegan Skeate <https://github.com/keeganskeate>
 * Created: 1/17/2021
 * Updated: 6/23/2023
 * License: MIT License <https://github.com/cannlytics/cannlytics-website/blob/main/LICENSE>
 */
import { getDocument, onAuthChange } from '../firebase.js';
import { authRequest, getUrlParameter, showNotification, validateEmail } from '../utils.js';
import { hideLoadingButton, showLoadingButton } from '../ui/ui.js';

/**---------------------------------------------------------------------------
 * PayPal Payments
 *--------------------------------------------------------------------------*/

export const payments = {

  /**---------------------------------------------------------------------------
   * Setup Subscriptions
   *--------------------------------------------------------------------------*/

  async initializeSupport(tier) {
    /**
     * Initialize PayPal support subscription checkouts.
     * @param {String} tier The tier of subscription.
     */
    const subscriptionData = await this.getSubscription(tier);
    console.log('SUBSCRIPTION DATA:');
    console.log(subscriptionData);

    // Add PayPal button.
    const FUNDING_SOURCES = [
      paypal.FUNDING.PAYPAL,
      paypal.FUNDING.CARD
    ];
    FUNDING_SOURCES.forEach(fundingSource => {
      paypal.Buttons({
        fundingSource,

        // Style.
        style: {
          layout: 'vertical',
          shape: 'rect',
          color: (fundingSource == paypal.FUNDING.PAYLATER) ? 'gold' : '',
        },

        createSubscription: function(data, actions) {
          /* Create a subscription with PayPal. */
          return actions.subscription.create({
            plan_id: subscriptionData['plan_id'],
          });
        },

        onApprove: async (data, actions) => {
          /* Approve the subscription with the API. */
          try {
            // Make an approval request.
            const amount = document.getElementById('price').textContent;
            const body = { amount, 'subscription_id': subscriptionData.id };
            const url = `/src/payments/orders/${data.orderID}/capture`;
            const response = await authRequest(url, body);
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
            var msg = `You have successfully subscribed to Cannlytics AI! You can use your tokens to run AI-powered jobs in the app. Put your AI jobs to good use!`;
            showNotification('Cannlytics AI tokens purchased', msg, /* type = */ 'success', /* delay = */ 10000);

            // Show a success form to the user.
            document.getElementById('checkout').classList.add('d-none');
            document.getElementById('thank-you-message').classList.remove('d-none');

            // Update the user's token count.
            try {
              document.getElementById('current_tokens').textContent = details.tokens;
            } catch(error) {
              // No tokens displayed on the page.
            }

          } catch (error) {
            console.error(error);
            // Handle the error and display an appropriate error message to the user.
            const message = `An error occurred when approving your subscription. Please email dev@cannlytics.com for help.`;
            showNotification('Error approving your subscription', message, /* type = */ 'error');
          }
        },
      }).render("#paypal-button-container");
    });

    // Render the price.
    document.getElementById('rate').textContent = subscriptionData.price;
    document.getElementById('price').textContent = subscriptionData.price_now;
    document.getElementById('subscription_name').textContent = subscriptionData.id;

    // Render the attributes.
    let ul = document.getElementById('subscription-attributes');
    subscriptionData.attributes.forEach(attribute => {
      let li = document.createElement('li');
      li.className = "fs-6 mb-1";
      let small = document.createElement('small');
      small.className = "serif text-dark";
      small.textContent = attribute;
      li.appendChild(small);
      ul.appendChild(li);
    });
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
    try {
      // Update the user's newsletter subscription through the API.
      await authRequest('/api/users', { newsletter: true });
      window.location.href = `${window.location.origin}/account/subscriptions`;
    } catch(error) {
      const message = 'An error occurred when processing your subscription. Please contact dev@cannlytics.com for help.';
      showNotification('Error saving your account', message, /* type = */ 'error');
      hideLoadingButton(`${subscriptionType}-button`);
    }
  },

  /**---------------------------------------------------------------------------
   * Manage Subscriptions
   *--------------------------------------------------------------------------*/
  
  async initializeSubscriptions() {
    /**
     * Initialize the user's current subscriptions.
     */
  
    // Get the user's level of support.
    let userSubscription = await this.getUserSubscriptions();
    if (!userSubscription) userSubscription = { support: 'free' };
  
    // If no subscription, then show Upgrade on all and stop.
    const subscribeButtons = document.getElementsByClassName('subscribe-button');
    for (let button of subscribeButtons) {
      button.textContent = 'Subscribe';
    }
    if (!userSubscription.support || userSubscription.support == 'free') return;
  
    // If subscription, then show Cancel on current subscription and Change on others.
    // Add a selected border to the current user's subscription.
    const subscriptionButton = document.getElementById(`subscribe-button-${userSubscription.support}`);
    const cancelSubscriptionButton = document.getElementById(`cancel-button-${userSubscription.support}`);
    subscriptionButton.classList.add('d-none');
    cancelSubscriptionButton.classList.remove('d-none');
    for (let button of subscribeButtons) {
      button.textContent = 'Change';
    }
    const card = document.getElementById(`subscription-card-${userSubscription.support}`);
    card.classList.add('selected-subscription');

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

  async cancelSubscription() {
    /**
     * Cancel a user's PayPal subscription.
     */

    // Make cancel subscription request.
    const response = await authRequest('/api/payments/unsubscribe', { unsubscribe: true });
    if (response.success) {

      // Show a notification.
      const message = 'Successfully cancelled your Cannlytics AI subscription. You can subscribe again at any time.';
      showNotification('Subscription canceled', message, /* type = */ 'success');

      // Reset the subscription buttons and cards.
      const subscribeButtons = document.getElementsByClassName('subscribe-button');
      const cancelSubscribeButtons = document.getElementsByClassName('cancel-button');
      const subscribeCards = document.getElementsByClassName('subscription-card');
      for (let button of cancelSubscribeButtons) {
        button.classList.add('d-none');
      }
      for (let button of subscribeButtons) {
        button.textContent = 'Subscribe';
        button.classList.remove('d-none');
      }
      for (let card of subscribeCards) {
        card.classList.remove('selected-subscription');
      }
    } else {
      // Otherwise, show an error notification.
      const message = 'An error occurred when cancelling your subscription. Please email dev@cannlytics.com for help unsubscribing.';
      showNotification('Error cancelling subscription', message, /* type = */ 'error');
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
            return details.data.id;
          } catch (error) {
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

            // Show a success form to the user.
            document.getElementById('checkout').classList.add('d-none');
            document.getElementById('thank-you-message').classList.remove('d-none');

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
