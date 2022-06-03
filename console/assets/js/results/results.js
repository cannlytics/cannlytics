/**
 * Results JavaScript | Cannlytics Console
 * Copyright (c) 2021-2022 Cannlytics
 * 
 * Authors: Keegan Skeate <https://github.com/keeganskeate>
 * Created: 6/18/2020
 * Updated: 12/14/2021
 * License: MIT License <https://github.com/cannlytics/cannlytics-console/blob/main/LICENSE>
 */
import { getFileURL, setDocument, uploadFile } from '../firebase.js';
import { authRequest, showNotification } from '../utils.js';

export const results = {

  /*----------------------------------------------------------------------------
  Distributing results
  ----------------------------------------------------------------------------*/

  postResults() {
    /**
     * Post results to a given state traceability system.
     */
  },

  releaseResults() {
    /**
     * Release results, making them available to the client's contacts.
     */
  },

  sendResults() {
    /**
     * Send results to specific people.
     */
  },

  shareResults() {
    /**
     * Ability for result recipients to share their results with others.
     */
  },

  /*----------------------------------------------------------------------------
  CoA Generation and Review
  ----------------------------------------------------------------------------*/

  async generateCoA() {
    /**
     * Generate a CoA PDF.
     * @returns {Object} Returns data of the generated CoA or the error message.
     */
    // TODO: Implement.
    const data = {};
    const url = `/api/results/generate_coa?organization_id=${orgId}`;
    const response = await authRequest(url, data);
    if (!response.success) {
      showNotification('Error getting templates', response.message, /* type = */ 'error');
      return response.message;
    }
    return response.data;
  },

  reviewCoA() {
    /**
     * Review a CoA.
     */
  },

  approveCoA() {
    /**
     * Approve a CoA.
     */
  },

  /*----------------------------------------------------------------------------
  Templates
  ----------------------------------------------------------------------------*/

  async getCoATemplates(orgId) {
    /**
     * Get CoA templates.
     * @param {String} orgId A specific organization ID.
     * @returns {Object} Returns data of the template or the error message.
     */
    const url = `/api/templates?organization_id=${orgId}`;
    const response = await authRequest(url);
    if (!response.success) {
      showNotification('Error getting templates', response.message, /* type = */ 'error');
      return response.message;
    } else {
      return response.data;
    }
  },

  saveCoATemplate() {
    /**
     * Save CoA template data to Firestore.
     */
  },

  async uploadCoATemplate(event, orgId) {
    /**
     * Upload a CoA template to Firebase Storage.
     * @param {Event} event A user-driven event.
     * @param {String} orgId A specific organization ID.
     */
    if (event.target.files.length) {
      showNotification('Uploading template', 'Uploading your CoA template...', /* type = */ 'wait');
      const file = event.target.files[0];
      const [name] = file.name.split('.');
      const ref = `organizations/${orgId}/templates/${file.name}`;
      try {
        await uploadFile(ref, file);
        const url = await getFileURL(ref);
      } catch(error) {
        showNotification('Photo Change Error', 'Error uploading photo.', /* type = */ 'error')
      }
      try {
        // FIXME: Insufficient permissions. Post data to the API instead.
        const data = {
          photo_uploaded_at: new Date().toISOString(),
          photo_modified_at: file.lastModifiedDate,
          photo_size: file.size,
          photo_type: file.type,
          photo_ref: ref,
          photo_url: url,
        };
        await setDocument(`organizations/${orgId}/templates/${name}`, data);
        showNotification('Photo saved', 'Organization photo saved with your organization files.', /* type = */ 'success');
        document.getElementById('organization_photo_url').src = url;
      } catch(error) {
        showNotification('Photo Change Error', 'Error saving photo.', /* type = */ 'error')
      }
    }
  },

};
