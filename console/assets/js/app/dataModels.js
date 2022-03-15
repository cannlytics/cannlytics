/**
 * App JavaScript | Cannlytics Console
 * Copyright (c) 2021-2022 Cannlytics
 * 
 * Authors: Keegan Skeate <keegan@cannlytics.com>
 * Created: 12/7/2020
 * Updated: 1/13/2022
 * License: MIT License <https://github.com/cannlytics/cannlytics-console/blob/main/LICENSE>
 */
import { getDocument } from '../firebase.js';
import { authRequest, serializeForm, showNotification } from '../utils.js';

export const dataModels = {

  async get(model, id = null, options = {}) {
    /**
     * Retrieve data from the database, either an array of data objects or a
     * single object if an ID is specified. You can pass params in `options` to
     * filter the data.
     * @param {String} model The name of a given data model.
     * @param {String} id A specific observation ID.
     */
    // const modelType = model.replace(/^./, string[0].toUpperCase());
    if (id) return await authRequest(`/api/${model}/${id}`);
    return await authRequest(`/api/${model}`, null, options);
  },

  startDelete() {
    /**
     * Begin the deletion process by showing a text area for deletion reason.
     */
    document.getElementById('deletion-reason').classList.remove('d-none');
  },

  cancelDelete() {
    /**
     * Cancel the deletion process by hiding the text area for deletion reason.
     */
    document.getElementById('deletion-reason').classList.add('d-none');
  },

  async delete(model, id) {
    /** Delete an entry from the database, passing the whole object as context
     * if available in a form, otherwise just pass the ID.
     * @param {String} model The name of a given data model.
     * @param {String} id A specific observation ID.
     */
    const orgId = document.getElementById('organization_id').value;
    const deletionReason = document.getElementById('deletion_reason_input').value;
    const data = { deletion_reason: deletionReason };
    try {
      const url = `/api/${model}/${id}?organization_id=${orgId}`;
      await authRequest(url, data, { delete: true });
      window.location.href = `/${model}`;
    } catch(error) {
      showNotification('Error deleting data', error.message, /* type = */ 'error');
    }
  },

  async save(model, modelSingular, abbreviation, buttonId = 'form-save') {
    /** Create an entry in the database if it does not exist, otherwise
     * update the entry.
     * @param {String} model The name of a given data model.
     * @param {String} modelSingular The name of a singular observation.
     * @param {String} abbreviation The abbreviation for the data model.
     * @param {String} buttonId The element ID of the button in the uesr interface.
     */
    // FIXME: Delete old entry if ID changes.
    const orgId = document.getElementById('organization_id').value;
    document.getElementById(`${buttonId}-button`).classList.add('d-none');
    document.getElementById(`${buttonId}-loading-button`).classList.remove('d-none');
    let id = document.getElementById(`input_${modelSingular}_id`).value;
    if (!id) id = await this.createID(model, modelSingular, orgId, abbreviation);
    const data = serializeForm(`${modelSingular}-form`);
    const url = `/api/${model}/${id}?organization_id=${orgId}`;
    try {
      const response = await authRequest(url, data);
      const message = 'Data saved. You can safely navigate pages.'
      showNotification('Data saved', message, /* type = */ 'success');
      document.getElementById('form-save-loading-button').classList.add('d-none');
      document.getElementById('form-save-button').classList.remove('d-none');
      return response;
    } catch(error) {
      showNotification('Error saving data', error.message, /* type = */ 'error');
      document.getElementById('form-save-loading-button').classList.add('d-none');
      document.getElementById('form-save-button').classList.remove('d-none');
      return error;
    }
  },

  async getDataModel(orgId, model) {
    /**
     * Get a specific data model for a given organization.
     * @param {String} orgId The ID for a specific organization.
     * @param {String} model The name of a given data model.
     * @returns {Object} Returns data about the data model.
     */
    return await getDocument(`organizations/${orgId}/data_models/${model}`);
  },

}
