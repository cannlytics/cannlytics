/**
 * Utility JavaScript | Cannlytics Console
 * Copyright (c) 2021-2022 Cannlytics
 * 
 * Authors: Keegan Skeate <https://github.com/keeganskeate>
 * Created: 2/21/2021
 * Updated: 1/13/2022
 * License: MIT License <https://github.com/cannlytics/cannlytics-console/blob/main/LICENSE>
 */
import { Toast } from 'bootstrap';
import { getUserToken } from './firebase.js';

/*------------------------------------------------------------------------------
 * Authentication Helpers
 *----------------------------------------------------------------------------*/

export const authRequest = async (endpoint, data, options) => {
  /**
   * Make an authorized GET or POST request by
   * getting the user's ID token and exchanging it for a session cookie.
   * @param {String} endpoint The API endpoint to which to make an authenticated request.
   * @param {Object} data Any data posted to the API.
   * @param {Object} options Any request options: `delete` (bool) or `params` (Object).
   */
  try {
    const idToken = await getUserToken();
    return await apiRequest(endpoint, data, options, idToken);
  } catch(error) {
    return error;
  }
};

export const apiRequest = async (endpoint, data, options, idToken = null) => {
  /**
   * Make a request to the Cannlytics API, with an ID token for authentication
   * or without ID token when the user already has an authenticated session.
   * CSRF protection is taken into account.
   * @param {String} endpoint The API endpoint to which to make an authenticated request.
   * @param {Object} data Any data posted to the API.
   * @param {Object} options Any request options: `delete` (bool) or `params` (Object).
   * @param {String} idToken = null
   */
  const csrftoken = getCookie('csrftoken');
  const headerAuth = new Headers({
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${idToken}`,
    'X-CSRFToken': csrftoken,
  });
  const init = {
    headers: headerAuth,
    // mode: 'no-cors',
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
  const url = endpoint.startsWith('https') ? endpoint : window.location.origin + endpoint;
  const response = await fetch(url, init);
  try {
    return response.json();
  } catch(error) {
    return response;
  }
};

export function getCookie(name) {
  /**
   * Get a cookie by name.
   * @param {string} name The name of the cookie to retrieve.
   * @returns {string}
   */
  let cookieValue = '';
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
  /**
   * Class use to generate random passwords.
   * @Usage Password.generate(32)
   */
 
  _pattern : /[a-zA-Z0-9_\-\+\.]/,
  
  _getRandomByte : function() {
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

/*------------------------------------------------------------------------------
 * Form Helpers
 *----------------------------------------------------------------------------*/

 export function serializeForm(elementId, keepAll = false) {
  /**
   * Get a data object from a form, by default excluding empty fields.
   * @param {string} elementId The ID of the form element.
   * @param {bool} keepAll Whether or not to keep all the null fields,
   *    `false` by default.
   * @returns {Map}
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
  /**
   * Populate a form given data.
   * @param {Element} form The form to which to populate data.
   * @param {Object} data The data to populate into a form.
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
  /**
   * Get data from a form into a query string.
   * Credit: https://stackoverflow.com/a/44033425/1869660
   * @param {Element} form The form to which to populate data.
   * @returns {String}
   */
  const data = new FormData(form);
  return new URLSearchParams(data).toString();
}

/**
 * Format file size as bytes.
 * Credit: https://stackoverflow.com/questions/15900485/correct-way-to-convert-size-in-bytes-to-kb-mb-gb-in-javascript
 */
export function formatBytes(a,b=2){if(0===a)return"0 Bytes";const c=0>b?0:b,d=Math.floor(Math.log(a)/Math.log(1024));return parseFloat((a/Math.pow(1024,d)).toFixed(c))+" "+["Bytes","KB","MB","GB","TB","PB","EB","ZB","YB"][d]};

/*------------------------------------------------------------------------------
 * UI Helpers
 *----------------------------------------------------------------------------*/

export function hasClass(element, className) {
  /**
   * Check if an element has a class.
   * @param {Element} element An element to check for a certain class.
   * @param {String} className The class string to check for in an element.
   */
  return (' ' + element.className + ' ').indexOf(' ' + className + ' ') > -1;
}

export function showNotification(title, message, type, delay = 3500) {
  /**
   * Show an error notification.
   * @param {String} title The title for the notification.
   * @param {String} message The message to display in the notification.
   * @param {String} type The type of message: `error`, `success`, or `wait`.
   * @param {Number} delay The time to show the notification, 3500 milliseconds by default.
   */
  const toastEl = document.getElementById('notification-toast');
  document.getElementById('notification-title').textContent = title;
  document.getElementById('notification-message').textContent = message;
  toastEl.classList.remove('d-none');
  if (type) {
    const types = ['error', 'success', 'wait'];
    document.getElementById(`notification-error-icon`).classList.add('d-none');
    document.getElementById(`notification-success-icon`).classList.add('d-none');
    document.getElementById(`notification-wait-icon`).classList.add('d-none');
    types.forEach((t) => {
      if (type === t) document.getElementById(`notification-${type}-icon`).classList.remove('d-none');
    });
  }
  const toast = new Toast(toastEl, { delay });
  toast.show()
}

/*------------------------------------------------------------------------------
 * Text Helpers
 *----------------------------------------------------------------------------*/

export function getUrlParameter(name) {
  /** Get a specific parameter from the URL.
   * @param {String} name The name of the parameter.
   * @returns {String} Returns the parameter value if it is in the URL.
  */
  name = name.replace(/[\[]/, '\\[').replace(/[\]]/, '\\]');
  var regex = new RegExp('[\\?&]' + name + '=([^&#]*)');
  var results = regex.exec(location.search);
  return results === null ? '' : decodeURIComponent(results[1].replace(/\+/g, ' '));
}

export function capitalize(text) {
  /**
   * Capitalize the first letter of given text.
   * Reference: https://www.geeksforgeeks.org/how-to-make-first-letter-of-a-string-uppercase-in-javascript/
   * @param {String} text The text to capitalize.
   */
  return text.replace(/^./, text[0].toUpperCase());
}

export function slugify(text) {
  /**
   * Turn text to a slug.
   * Reference: https://stackoverflow.com/questions/1053902/how-to-convert-a-title-to-a-url-slug-in-jquery
   * @param {String} text The text to capitalize.
   */
  return text
    .toLowerCase()
    .replace(/[^\w ]+/g,'')
    .replace(/ +/g,'-');
}

/*------------------------------------------------------------------------------
 * URL Helpers
 *----------------------------------------------------------------------------*/

export function setURLParameter(paramName, paramValue) {
  /**
   * Add query parameter to the URL.
   * @param {String} paramName The key of the parameter.
   * @param {String} paramValue The value for the parameter.
   */
  let url = window.location.href;
  const hash = location.hash;
  url = url.replace(hash, '');
  if (url.indexOf(paramName + '=') >= 0) {
    const prefix = url.substring(0, url.indexOf(paramName + '=')); 
    let suffix = url.substring(url.indexOf(paramName + '='));
    suffix = suffix.substring(suffix.indexOf('=') + 1);
    suffix = (suffix.indexOf('&') >= 0) ? suffix.substring(suffix.indexOf('&')) : '';
    url = `${prefix}${paramName}=${paramValue}${suffix}`;
  }
  else {
    if (url.indexOf('?') < 0) url = `${url}?${paramName}=${paramValue}`;
    else url = `${url}&${paramName}=${paramValue}`;
  }
  window.location.href = `\\search\\${url}${hash}`;
}


export const utils = {
  apiRequest,
  authRequest,
  capitalize,
  deserializeForm,
  getCookie,
  getUrlParameter,
  hasClass,
  parameterizeForm,
  setURLParameter,
  serializeForm,
  slugify,
  showNotification,
}
