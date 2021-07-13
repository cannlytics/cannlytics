/**
 * API Settings JavaScript | Cannlytics Console
 * Author: Keegan Skeate
 * Created: 7/13/2021
 * Updated: 7/13/2021
 */

import { apiRequest, deserializeForm, serializeForm, showNotification } from '../utils.js';
import { ui } from '../ui/ui.js';

export const apiSettings = {


  createAPIKey() {
    /* 
    * Create an API key.
    */
    const data = serializeForm('new-api-key-form');
    ui.showLoadingButton('create-api-key-button');
    apiRequest('/api/auth/create-key', data).then((response) => {
      // Optional: Add new key to the table and show the table without reloading!
      window.location.reload(); 
    }).finally(() => {
      ui.hideLoadingButton('create-api-key-button');
    });
  },


  deleteAPIKey() {
    /* 
    * Delete an API key.
    */
    // FIXME:
    const data = serializeForm('api-key-form');
    // ui.showLoadingButton('create-api-key-button');
    apiRequest('/api/auth/delete-key', data).then((response) => {
      if (response.error) {
        showNotification('Error deleting API key', response.message, { type: 'error' });
        return;
      }
      // Optional: Add new key to the table and show the table without reloading!
      window.location.reload(); 
    });
    // .finally(() => {
    //   ui.hideLoadingButton('create-api-key-button');
    // });
  },


  getAPIKeys(uid) {
    /* 
    * Get all of a user's API key information.
    */
    return new Promise((resolve, reject) => {
      apiRequest('/api/auth/get-keys').then((response) => {
        resolve(response['data']);
      });
    });
  },


  renderAPIKey(change) {
    /* 
    * Get all of a user's API key information.
    */
    if (change.type === 'added') {
      console.log('Add data to table:', change.doc);
    }
    else if (change.type === 'removed') {
      console.log('Remove row from table:', change.doc.id);
    }
  },


  viewAPIKey() {
    /*
     * Render a project's data when navigating to a project page.
     */
    const data = JSON.parse(localStorage.getItem('api-key'));
    deserializeForm(document.forms['api-key-form'], data);
  },


};
