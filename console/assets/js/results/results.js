/**
 * Results JavaScript | Cannlytics Console
 * Author: Keegan Skeate
 * Created: 6/18/2020
 * Updated: 8/2/2021
 */

import {
  getDownloadURL,
  updateDocument,
  uploadFile,
} from '../firebase.js';

import {
  authRequest,
  showNotification,
} from '../utils.js';

export const results = {

  /*----------------------------------------------------------------------------
  Distributing results
  ----------------------------------------------------------------------------*/

  postResults() {
    /*
     * Post results to a given state traceability system.
     */
    console.log('Reviewing CoA...');
  },


  releaseResults() {
    /*
     * Release results, making them available to the client's contacts.
     */
    console.log('Reviewing CoA...');
  },


  sendResults() {
    /*
     * Send results to specific people.
     */
    console.log('Reviewing CoA...');
  },


  shareResults() {
    /*
     * Ability for result recipients to share their results with others.
     */
    console.log('Sharing results...');
  },

  /*----------------------------------------------------------------------------
  CoA Generation and Review
  ----------------------------------------------------------------------------*/

  generateCoA() {
    /*
     * Generate a CoA PDF.
     */
    console.log('Generating CoA...');
  },


  reviewCoA() {
    /*
     * Review a CoA.
     */
    console.log('Reviewing CoA...');
  },


  approveCoA() {
    /*
     * Approve a CoA.
     */
    console.log('Reviewing CoA...');
  },


  /*----------------------------------------------------------------------------
  Templates
  ----------------------------------------------------------------------------*/


  getCoATemplates(orgId) {
    /*
     * Get CoA templates.
     */
    console.log('Getting CoA templates:', orgId);
    return new Promise((resolve, reject) => {
      authRequest(`/api/templates?organization_id=${orgId}`).then((response) => {
        if (response.error) {
          showNotification('Error getting templates', response.message, { type: 'error' });
          reject(response.error);
        } else {
          resolve(response.data);
        }
      });
    });
  },


  saveCoATemplate() {
    /*
     * Save CoA template data to Firestore.
     */
    console.log('Saving CoA template...');
  },


  uploadCoATemplate(event, orgId) {
    /*
     * Upload a CoA template to Firebase Storage.
     */
    console.log('Uploading CoA template...', event);
    if (event.target.files.length) {
      showNotification('Uploading template', 'Uploading your CoA template...', { type: 'wait' });
      const file = event.target.files[0];
      const [name] = file.name.split('.');
      const ref = `organizations/${orgId}/templates/${file.name}`;
      uploadFile(ref, file).then((snapshot) => {
        getDownloadURL(ref).then((url) => {
          // FIXME: Insufficient permissions. Post data to the API instead.
          updateDocument(`organizations/${orgId}/templates/{name}`, {
            photo_uploaded_at: new Date().toISOString(),
            photo_modified_at: file.lastModifiedDate,
            photo_size: file.size,
            photo_type: file.type,
            photo_ref: ref,
            photo_url: url,
          }).then(() => {
            showNotification('Photo saved', 'Organization photo saved with your organization files.', { type: 'success' });
            document.getElementById('organization_photo_url').src = url;
          })
          .catch((error) => showNotification('Photo Change Error', 'Error saving photo.', { type: 'error' }));
        }).catch((error) => showNotification('Photo Change Error', 'Error uploading photo.', { type: 'error' }));
      });
    }
  },


};
