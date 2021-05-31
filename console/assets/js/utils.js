/*
 * Utility JavaScript | Cannlytics Console
 * Author: Keegan Skeate <contact@cannlytics.com>
 * Created: 2/21/2021
 * Updated: 5/9/2021
 */

import { getUserToken } from './firebase.js';

/*---------------------------------------------------------------------
 Auth Helpers
 --------------------------------------------------------------------*/

export const authRequest = (endpoint, data, options) => new Promise((resolve, reject) => {
  /*
   * Make an authorized GET or POST request by
   * getting the user's ID token and exchanging it for a session cookie.
   */
  getUserToken().then((idToken) => {
    apiRequest(endpoint, data, options, idToken)
      .then((data) => {
        resolve(data);
      });
  }).catch((error) => {
    reject(error);
  });
});


export const apiRequest = (endpoint, data, options, idToken = null) => new Promise((resolve, reject) => {
  /*
   * Make a request to the Cannlytics API, with an ID token for authentication
   * or without ID token when the user already has an authenticated session.
   * CSRF protection is taken into account.
   */
  const csrftoken = getCookie('csrftoken');
  const headerAuth = new Headers({
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${idToken}`,
    'X-CSRFToken': csrftoken,
  });
  const headers = { headers: headerAuth, mode: 'same-origin', method: 'GET' };
  if (data) {
    headers.method = 'POST';
    headers.body = JSON.stringify(data);
  }
  if (options) {
    if (options.delete) {
      headers.method = 'DELETE';
    }
    if (options.params) {
      endpoint = new URL(endpoint)
      endpoint.search = new URLSearchParams(options.params).toString();
    }
  }
  fetch(endpoint, headers)
    .then(response => response.json())
    .then((data) => {
      resolve(data);
    })
    .catch((error) => {
      reject(error);
    });
});


export function getCookie(name) {
  /*
   * Get a cookie by name.
   */
  let cookieValue = null;
  if (document.cookie && document.cookie !== '') {
    const cookies = document.cookie.split(';');
    for (let i = 0; i < cookies.length; i++) {
      const cookie = cookies[i].trim();
      if (cookie.substring(0, name.length + 1) === (name + '=')) {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
        break;
      }
    }
  }
  return cookieValue;
}


export const Password = {
  /*
   * Class use to generate random passwords.
   * Usage: Password.generate(32)
   */
 
  _pattern : /[a-zA-Z0-9_\-\+\.]/,
  
  
  _getRandomByte : function() {
    // http://caniuse.com/#feat=getrandomvalues
    if (window.crypto && window.crypto.getRandomValues) {
      var result = new Uint8Array(1);
      window.crypto.getRandomValues(result);
      return result[0];
    }
    else if (window.msCrypto && window.msCrypto.getRandomValues)  {
      var result = new Uint8Array(1);
      window.msCrypto.getRandomValues(result);
      return result[0];
    }
    else {
      return Math.floor(Math.random() * 256);
    }
  },
  
  generate : function(length) {
    return Array.apply(null, {'length': length})
      .map(function() {
        var result;
        while(true)  {
          result = String.fromCharCode(this._getRandomByte());
          if (this._pattern.test(result)) {
            return result;
          }
        }        
      }, this)
      .join('');  
  }    
    
};


/*---------------------------------------------------------------------
 Form Helpers
 --------------------------------------------------------------------*/

 export function serializeForm(elementId, keepAll=false) {
  /*
   * Get a data object from a form, by default excluding empty fields.
   */
  const elements = document.getElementById(elementId).elements;
  const data = {};
  for (let i = 0 ; i < elements.length ; i++) {
    const item = elements.item(i);
    if (item.name || keepAll) data[item.name] = item.value;
  }
  return data
}


/*---------------------------------------------------------------------
 UI Helpers
 --------------------------------------------------------------------*/

export function hasClass(element, className) {
  /*
   * Check if an element has a class.
   */
  return (' ' + element.className + ' ').indexOf(' ' + className + ' ') > -1;
}


export function showNotification(title, message, options) {
  /*
   * Show an error notification.
   */
  const toastEl = document.getElementById('notification-toast');
  document.getElementById('notification-title').textContent = title;
  document.getElementById('notification-message').textContent = message;
  toastEl.classList.remove('d-none');
  if (options.type) {
    const types = ['error', 'success', 'wait'];
    types.forEach((type) => {
      if (type === options.type) {
        document.getElementById(`notification-${type}-icon`).classList.remove('d-none');
      } else {
        document.getElementById(`notification-${type}-icon`).classList.add('d-none');
      }
    });
  }
  const toast = new bootstrap.Toast(toastEl, { delay: options.delay || 4000 });
  toast.show()
}
