/**
 * API Keys JavaScript | Cannlytics Website
 * Copyright (c) 2021-2023 Cannlytics
 * 
 * Authors: Keegan Skeate <https://github.com/keeganskeate>
 * Created: 7/13/2021
 * Updated: 6/22/2023
 * License: MIT License <https://github.com/cannlytics/cannlytics-console/blob/main/LICENSE>
 */
import { apiRequest, deserializeForm, serializeForm, showNotification } from '../utils.js';
import { showLoadingButton, hideLoadingButton } from '../ui/ui.js';

export const apiSettings = {

  async createAPIKey() {
    /** 
    * Create an API key.
    */
    const data = serializeForm('new-api-key-form');
    showLoadingButton('create-api-key-button');
    const response = await apiRequest('/api/auth/create-key', data);
    document.getElementById('new-key-card').classList.add('d-none');
    document.getElementById('key-created-card').classList.remove('d-none');
    document.getElementById('api-key').value = response.api_key;
    hideLoadingButton('create-api-key-button');
  },

  async deleteAPIKey() {
    /** 
    * Delete an API key.
    */
    const data = serializeForm('api-key-form');
    const response = await apiRequest('/api/auth/delete-key', data);
    if (!response.success) {
      showNotification('Error deleting API key', response.message, /* type = */ 'error');
      return;
    }
    // TODO: Reset the table without reloading the page?
    window.location.reload(); 
  },

  async getAPIKeys() {
    /** 
    * Get all of a user's API key information.
    */
    const response = await apiRequest('/api/auth/get-keys');
    return response['data'];
  },

  viewAPIKey() {
    /**
     * Render a project's data when navigating to a project page.
     */
    const data = JSON.parse(localStorage.getItem('api-key'));
    deserializeForm(document.forms['api-key-form'], data);
  },

};
