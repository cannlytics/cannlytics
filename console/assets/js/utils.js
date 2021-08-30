/*
 * Utility JavaScript | Cannlytics Console
 * Author: Keegan Skeate <contact@cannlytics.com>
 * Created: 2/21/2021
 * Updated: 6/21/2021
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
  getUserToken()
    .then((idToken) => {
      apiRequest(endpoint, data, options, idToken)
        .then((data) => resolve(data))
        .catch((error) => reject(error));
    })
    .catch((error) => reject(error));
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
  const init = {
    headers: headerAuth,
    // credentials: 'include',
    // mode: 'same-origin',
    method: 'GET',
  };
  if (data) {
    init.method = 'POST';
    init.body = JSON.stringify(data);
  }
  if (options) {
    if (options.delete) {
      init.method = 'DELETE';
    }
    if (options.params) {
      endpoint = new URL(endpoint)
      endpoint.search = new URLSearchParams(options.params).toString();
    }
  }
  fetch(window.location.origin + endpoint, init)
    .then(response => {
      try {
        return response.json();
      } catch(error) {
        return response;
      }
      // return response.json();
    })
    .catch((error) => reject(error))
    .then((data) => resolve(data))
    .catch((error) => reject(error));
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
  let form;
  if (typeof elementId === 'string') {
    form = document.getElementById(elementId);
  }
  else {
    form = elementId;
  }
  const elements = form.elements;
  const data = {};
  for (let i = 0 ; i < elements.length ; i++) {
    const item = elements.item(i);
    if (item.name || keepAll) data[item.name] = item.value;
  }
  return data
}


export function deserializeForm(form, data) {
  /*
   * Populate a form given data.
   */
  const entries = (new URLSearchParams(data)).entries();
  for (const [key, val] of entries) {
      const input = form.elements[key];
      if (input) {
        switch(input.type) {
          case 'checkbox': input.checked = !!val; break;
          default: input.value = val; break;
        }
      }
  }
}

export function parameterizeForm(form) {
  /*
   * Get data from a form into a query string.
   * https://stackoverflow.com/a/44033425/1869660
   */
  const data = new FormData(form);
  return new URLSearchParams(data).toString();
}


// Format file size as bytes.
// https://stackoverflow.com/questions/15900485/correct-way-to-convert-size-in-bytes-to-kb-mb-gb-in-javascript
export function formatBytes(a,b=2){if(0===a)return"0 Bytes";const c=0>b?0:b,d=Math.floor(Math.log(a)/Math.log(1024));return parseFloat((a/Math.pow(1024,d)).toFixed(c))+" "+["Bytes","KB","MB","GB","TB","PB","EB","ZB","YB"][d]};


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

/*---------------------------------------------------------------------
 Text Helpers
 --------------------------------------------------------------------*/

export function capitalize(string) {
  /*
   * Capitalize the first letter of a given string.
   * Reference: https://www.geeksforgeeks.org/how-to-make-first-letter-of-a-string-uppercase-in-javascript/
   */
  return string.replace(/^./, string[0].toUpperCase());
}


export function slugify(text) {
  /*
   * Turn a string to a slug.
   * Reference: https://stackoverflow.com/questions/1053902/how-to-convert-a-title-to-a-url-slug-in-jquery
   */
  return text
    .toLowerCase()
    .replace(/[^\w ]+/g,'')
    .replace(/ +/g,'-');
}
