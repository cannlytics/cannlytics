/**
 * Waste JavaScript | Cannlytics Console
 * Copyright (c) 2021 Cannlytics
 * 
 * Authors: Keegan Skeate
 * Created: 2/6/2022
 * Updated: 2/16/2022
 * License: MIT License <https://github.com/cannlytics/cannlytics-console/blob/main/LICENSE>
 */
import { authRequest, deserializeForm, serializeForm, showNotification } from '../utils.js';

export const waste = {

  initialize() {
    /**
     * Initialize waste.
     */
  },

  getWaste() {
    /**
     * Get waste through the API.
     */
    const form = document.getElementById('waste-form');
    const data = serializeForm(form);
    authRequest('/api/waste', data).then((response) => {
      if (response.error) {
        showNotification('Error getting waste', response.message, { type: 'error' });
      } else {
        // TODO: Render the analytics in the user interface.
        document.getElementById('output').classList.remove('d-none');
        document.getElementById('output-message').textContent = JSON.stringify(response.data);
      }
    });
  },

  getWasteAreas() {
    /**
     * Get areas used for waste.
     * @returns {Array}
     */
  },

  getSampleAmount(sampleId) {
    /**
     * Get the current expected amount of a given sample.
     * @param {String} sampleId The ID for a given sample.
     * @returns {Number}
     */
    // TODO: Get and return the expected amount for a given sample from the database.
  },

  getSampleOriginalAmount(sampleId) {
    /**
     * Get the original amount of the sample.
     * @param {String} sampleId The ID for a given sample.
     * @returns {Number}
     */
    // TODO: Get and return the original amount for a given sample from the database.
  },

  getWarningLimit() {
    /**
     * Get the limit at which the staff is warned about weight out-of-specification.
     */
    // TODO: Get and return the waste warning limit from the database.
  },

  calculatePercentUsed() {
    /**
     * Calculate the percent used as the sample amount divided by the original
     * sample amount time 100.
     */
    const sampleAmount = this.getSampleAmount();
    const originalSampleAmount = this.getSampleOriginalAmount();
    return sampleAmount / originalSampleAmount * 100;
  },

  calculatePercentDifference(currentSampleAmount) {
    /**
     * Calculated the percent difference as the current sample amount minus the
     * sample amount divided by the sample_amount times 100.
     */
    const sampleAmount = this.getSampleAmount();
    return (currentSampleAmount - sampleAmount) / sampleAmount * 100;
  },

  raiseCorrectiveAction() {
    /**
     * Raise corrective_action if the percent difference is above the warning limit.
     */
    // TODO: Create a corrective action database entry and document (using template).
    // TODO: Send corrective action notification to the staff.
  },

  reconcileWasteItem() {
    /**
     * Reconcile a given waste item.
     */
    const currentSampleAmount = 0; // TODO: Get from the user interface.
    const warningLimit = this.getWarningLimit();
    this.calculatePercentDifference(currentSampleAmount);
    if (percent_difference > warningLimit) this.raiseCorrectiveAction();
  },

}
