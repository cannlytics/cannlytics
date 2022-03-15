/**
 * User Settings JavaScript | Cannlytics Console
 * Copyright (c) 2021-2022 Cannlytics
 * 
 * Authors: Keegan Skeate <keegan@cannlytics.com>
 * Created: 1/2/2021
 * Updated: 12/14/2021
 * License: MIT License <https://github.com/cannlytics/cannlytics-console/blob/main/LICENSE>
 */
import { Modal } from 'bootstrap';
import {
  changeEmail,
  getCurrentUser,
  getFileURL,
  setDocument,
  updateUserDisplayName,
  updateUserPhoto,
  uploadFile,
} from '../firebase.js';
import {
  authRequest,
  deserializeForm,
  serializeForm,
  showNotification,
} from '../utils.js';

export const userSettings = {

  /* ---------------------------------------------------------------------------
   * Account details.
   ---------------------------------------------------------------------------*/

  chooseUserPhoto() {
    /**
     * Choose a file to upload.
     */
    const fileSelect = document.getElementById('userPhotoUrl');
    fileSelect.click();
  },

  initializeAccountForm() {
    /**
     * Initialize the user account form.
     */
    const fileElem = document.getElementById('userPhotoUrl');
    fileElem.addEventListener('change', uploadUserPhoto, false);
    this.resetAccountForm();
  },

  async resetAccountForm() {
    /**
     * Reset a form with currently saved data, replacing any changes.
     */
    const data = await authRequest('/api/users');
    const userForm = document.forms['user-form'];
    userForm.reset();
    deserializeForm(userForm, data);
  },

  async saveAccount() {
    /** 
    * Saves a user's account fields.
    */
    const user = getCurrentUser();
    const data = serializeForm('user-form');
    if (data.email !== user.email) {
      await changeEmail(data.email);
    }
    if (data.name !== user.displayName) {
      await updateUserDisplayName(data.name);
    }
    await authRequest('/api/users', data);
    const message = 'Your account data has been successfully saved.'
    showNotification('Account saved', message, /* type = */ 'success');
  },

  uploadUserPhoto,

  /* ---------------------------------------------------------------------------
   * Pin and signature management.
   ---------------------------------------------------------------------------*/

  async createPin(event) {
    /** 
    * Create a pin for a user.
    * @param {Event} event A user-driven event.
    */
    event.preventDefault();
    const pin = document.getElementById('pin_input').value;
    const response = await authRequest('/api/auth/create-pin', { pin })
    if (response.success) {
      document.getElementById('pin_input').value = '';
      showNotification('Pin created', response.message, /* type = */ 'success');
      window.location.href = '/settings/user';
    } else {
      showNotification('Invalid pin', response.message, /* type = */ 'error');
    }
  },

  async deleteSignature() {
    /** 
    * Remove a signature from a user's settings.
    */
    const response = await authRequest('/api/auth/delete-signature');
    if (response.success) {
      showNotification('Signature deleted', response.message, /* type = */ 'success');
      window.location.reload(); // Optional: Hide banner more elegantly.
    } else {
      showNotification('Signature deletion failed', response.message, /* type = */ 'error');
    }
  },

  async deletePin() {
    /** 
    * Delete all existing pins for a user.
    */
    const response = authRequest('/api/auth/delete-pin')
    if (response.success) {
      showNotification('Voided user pin', response.message, /* type = */ 'success');
      window,location.reload(); // Optional: Hide banner more elegantly.
    } else {
      showNotification('Voiding pin failed', response.message, /* type = */ 'error');
    }
  },

  async saveSignature(uid, data, type = 'data_url') {
    /** 
    * Upload a signature for a user.
    * @param {String} uid A unique user ID.
    * @param {Object} data Data about a user's signature.
    */
    // TODO: Prefer to upload signature through the API.
    // const response = await authRequest('/api/auth/create-signature', { data_url: data });
    const signatureRef = `users/${uid}/user_settings/signature.png`;
    showNotification('Uploading signature', 'Uploading your signature image...', /* type = */ 'wait');
    try {
      await uploadFile(signatureRef, data, type);
      const url = await getFileURL(signatureRef);
    } catch(error) {
      showNotification('Error uploading signature', 'An error occurred when uploading your signature.', /* type = */ 'error');
    }
    try {
      const timestamp = new Date().toISOString();
      const publicData = {
        signature_created_at: timestamp,
        signature_ref: signatureRef,
      };
      const privateData = {
        ...publicData,
        ...{ signature_url: url },
      };
      await setDocument(`users/${uid}`, publicData);
      await setDocument(`users/${uid}/user_settings/signature`, privateData);
    } catch(error) {
      showNotification('Error saving signature', 'An error occurred when saving your signature.', /* type = */ 'error');
    }
    showNotification('Signature saved', 'Signature saved with your files.', /* type = */ 'success');
    window.location.href = '/settings/user';
  },

  async viewSignature(event) {
    /**
     * Require the user to enter their pin before showing their signature.
     * @param {Event} event A user-driven event.
     */
    event.preventDefault();
    const pin = document.getElementById('pin_input').value;
    const response = await authRequest('/api/auth/get-signature', { pin });
    if (response.success) {
      const modalEl = document.getElementById('pinModal')
      const modal = Modal.getInstance(modalEl);
      const signatureEl = document.getElementById('signature-canvas');
      signatureEl.classList.remove('d-none');
      signatureEl.src = response.signature_url;
      document.getElementById('view_button').classList.add('d-none');
      document.getElementById('hide_button').classList.remove('d-none');
      modal.hide();
    } else {
      showNotification('Invalid pin', response.message, /* type = */ 'error');
    }
  },

  hideSignature() {
    /**
     * Hide a signature after it has been shown.
     */
    document.getElementById('hide_button').classList.add('d-none');
    document.getElementById('view_button').classList.remove('d-none');
    document.getElementById('signature-canvas').classList.add('d-none');
  },

  uploadSignature(event, uid) {
    /**
     * Upload an existing signature file to Firebase Storage.
     * @param {Event} event A user-driven event.
     * @param {String} uid A unique user ID.
     */
    if (event.target.files.length) {
      saveSignature(uid, event.target.files[0], /* type = */ 'file');
    }
  },

  getUserLogs(orgId) {
    /** 
    * Record time and user of any activity.
    * @param {String} orgId A specific organization ID.
    */
    // TODO: Implement.
    throw 'Not implemented yet.';
  },

};

export async function uploadUserPhoto() {
  /**
   * Upload a user's photo through the API.
   */
  if (this.files.length) {
    showNotification('Uploading photo', 'Uploading your profile picture...', /* type = */ 'wait');
    const downloadURL = await updateUserPhoto(this.files[0]);
    await authRequest('/api/users', { photo_url: downloadURL });
    const renderedUserPhotos = document.getElementsByClassName('user-photo-url');
    for (let i = 0, len = renderedUserPhotos.length; i < len; i++) {
      renderedUserPhotos[i].src = downloadURL;
    }
    showNotification('Uploading photo complete', 'Successfully uploaded your profile picture.', /* type = */ 'success');
  }
};
