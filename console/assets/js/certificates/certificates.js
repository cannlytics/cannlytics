/**
 * Certificates JavaScript | Cannlytics Console
 * Copyright (c) 2021-2022 Cannlytics
 * 
 * Authors: Keegan Skeate <https://github.com/keeganskeate>
 * Created: 8/9/2021
 * Updated: 12/13/2021
 * License: MIT License <https://github.com/cannlytics/cannlytics-console/blob/main/LICENSE>
 */
import { getFileURL, setDocument, uploadFile } from '../firebase.js';
import { authRequest, showNotification } from '../utils.js';

export const certificates = {

  async streamCertificates(status, start='', end='', orderBy='updated_at') {
    /**
     * Stream certificates, listening for any changes.
     * @param {String} status The status of certificates to stream.
     * @param {String} start The start time, in ISO format, to begin streaming certificates.
     * @param {String} end The end time, in ISO format, to stop streaming certificates.
     * @param {String} orderBy The field to order certificates, `updated_at` by default.
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
    // FIXME: Re-write with listenToCollection
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
          data.push(values);
        });
        // FIXME: Make renderTable available as a util.
        if (data.length) this.renderTable(`${model}-logs`, 'log', data, dataModel);
        else this.renderPlaceholder();
      });
  },

  /*----------------------------------------------------------------------------
  CoA Generation and Review
  ----------------------------------------------------------------------------*/

  generateCoA(orgId) {
    /**
     * Generate a CoA PDF.
     * @param {String} orgId A specific organization ID.
     */
    // const message = 'A Pro subscription is required to issue certificates.';
    // showNotification('Pro Subscription Required', message, /* type = */ 'error');
    // TODO: Close modal.
    return new Promise((resolve, reject) => {
      const sample = JSON.parse(localStorage.getItem('sample'));
      const sampleId = sample['sample_id'];
      const data = { sample_ids: [sampleId] };
      authRequest(`/api/certificates/generate?organization_id=${orgId}`, data).then((response) => {
        if (response.error) {
          showNotification('Error getting templates', response.message, /* type = */ 'error');
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
    /**
     * Review a CoA.
     */
    const message = 'A Pro subscription is required to issue certificates.';
    showNotification('Pro Subscription Required', message, /* type = */ 'error');
  },

  approveCoA() {
    /**
     * Approve a CoA.
     */
    const message = 'A Pro subscription is required to issue certificates.';
    showNotification('Pro Subscription Required', message, /* type = */ 'error');
  },

  postCoA() {
    /**
     * Post a CoA to the traceability system.
     */
    const message = 'A Pro subscription is required to issue certificates.';
    showNotification('Pro Subscription Required', message, /* type = */ 'error');
  },

  releaseCoA() {
    /**
     * Release a CoA.
     */
    const message = 'A Pro subscription is required to issue certificates.';
    showNotification('Pro Subscription Required', message, /* type = */ 'error');
  },

  unapproveCoA() {
    /**
     * Un-approve a CoA.
     */
    const message = 'A Pro subscription is required to issue certificates.';
    showNotification('Pro Subscription Required', message, /* type = */ 'error');
  },

  unreviewCoA() {
    /**
     * Un-review a CoA.
     */
    const message = 'A Pro subscription is required to issue certificates.';
    showNotification('Pro Subscription Required', message, /* type = */ 'error');
  },

  /*----------------------------------------------------------------------------
  Templates
  ----------------------------------------------------------------------------*/

  getCoATemplates(orgId) {
    /**
     * Get CoA templates.
     * @param {String} orgId A specific organization ID.
     */
    return new Promise((resolve, reject) => {
      authRequest(`/api/templates?organization_id=${orgId}`).then((response) => {
        if (response.error) {
          showNotification('Error getting templates', response.message, /* type = */ 'error');
          reject(response.error);
        } else {
          resolve(response.data);
        }
      });
    });
  },

  saveCoATemplate() {
    /**
     * Save CoA template data to Firestore.
     */
  },

  uploadCoATemplate(event, orgId) {
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
      uploadFile(ref, file).then((snapshot) => {
        getFileURL(ref).then((url) => {
          // FIXME: Insufficient permissions. Post data to the API instead.
          setDocument(`organizations/${orgId}/templates/${name}`, {
            photo_uploaded_at: new Date().toISOString(),
            photo_modified_at: file.lastModifiedDate,
            photo_size: file.size,
            photo_type: file.type,
            photo_ref: ref,
            photo_url: url,
          }).then(() => {
            showNotification('Photo saved', 'Organization photo saved with your organization files.', /* type = */ 'success');
            document.getElementById('organization_photo_url').src = url;
          })
          .catch((error) => showNotification('Photo Change Error', 'Error saving photo.', /* type = */ 'error'));
        }).catch((error) => showNotification('Photo Change Error', 'Error uploading photo.', /* type = */ 'error'));
      });
    }
  },

};
