/**
 * Certificates JavaScript | Cannlytics Console
 * Author: Keegan Skeate
 * Created: 8/9/2021
 * Updated: 8/9/2021
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


export const certificates = {


  async streamCertificates(status, start='', end='', orderBy='updated_at') {
    /*
     * Stream certificates, listening for any changes.
     */
    // TODO: Get all samples by `certificate_status`
    if (!start) start = new Date(new Date().setDate(new Date().getDate()-1)).toISOString().substring(0, 10);
    if (!end) {
      end = new Date()
      end.setUTCHours(23, 59, 59, 999);
      end = end.toISOString();
    }
    // const dataModel = await getDocument(`organizations/${orgId}/data_models/logs`);
    // dataModel.fields = dataModel.fields.filter(function(obj) {
    //   return !(['log_id', 'changes', 'user'].includes(obj.key));
    // });
    console.log('Start:', start);
    console.log('End:', end);
    db.collection('organizations').doc(orgId).collection('samples')
      .where('certificate_status', '==', status)
      .where(orderBy, '>=', start)
      .where(orderBy, '<=', end)
      .orderBy(orderBy, 'desc')
      // .limit(this.logLimit) // TODO: Is limit necessary?
      .onSnapshot((querySnapshot) => {
        const data = [];
        querySnapshot.forEach((doc) => {
          const values = doc.data();
          values.changes = JSON.stringify(values.changes);
          // Optional: Split up date and time for filling into the form.
          console.log(values.created_at);
          data.push(values);
        });
        console.log('Data:', data);
        // FIXME: Make renderTable available as a util.
        if (data.length) this.renderTable(`${model}-logs`, 'log', data, dataModel);
        else this.renderPlaceholder();
      });
  },

  /*----------------------------------------------------------------------------
  CoA Generation and Review
  ----------------------------------------------------------------------------*/

  generateCoA() {
    /*
     * Generate a CoA PDF.
     */
    console.log('Generating CoA...');    
    return new Promise((resolve, reject) => {
      const sample = JSON.parse(localStorage.getItem('sample'));
      const sampleId = sample['sample_id'];
      const data = { sample_ids: [sampleId] };
      authRequest(`/api/certificates/generate?organization_id=${orgId}`, data).then((response) => {
        if (response.error) {
          showNotification('Error getting templates', response.message, { type: 'error' });
          reject(response.error);
        } else {
          resolve(response.data);
          document.getElementById('certificate-placeholder').classList.add('d-none');
          document.getElementById('certificate-container').classList.remove('d-none');
        }
      });
    });
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
