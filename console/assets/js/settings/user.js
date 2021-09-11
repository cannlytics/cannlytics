/**
 * User Settings JavaScript | Cannlytics Console
 * Author: Keegan Skeate <keegan@cannlytics.com>
 * Created: 1/2/2021
 * Updated: 7/3/2021
 */

import {
  auth,
  changePhotoURL,
  getDownloadURL,
  storageErrors,
  updateDocument,
  uploadImage,
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
    /*
     * Choose a file to upload.
     */
    const fileSelect = document.getElementById('userPhotoUrl');
    fileSelect.click();
  },


  initializeAccountForm() {
    /*
     * Initialize the user account form.
     */
    const fileElem = document.getElementById('userPhotoUrl');
    fileElem.addEventListener('change', this.uploadUserPhoto, false);
    this.resetAccountForm();
  },


  resetAccountForm() {
    /*
     * Reset a form with currently saved data, replacing any changes.
     */
    authRequest('/api/users').then((data) => {
      const userForm = document.forms['user-form'];
      userForm.reset();
      deserializeForm(userForm, data);
    });
  },


  saveAccount() {
    /* 
    * Saves a user's account fields.
    */
    const user = auth.currentUser;
    const data = serializeForm('user-form');
    if (data.email !== user.email) {
      user.updateEmail(data.email);
    }
    if (data.name !== user.displayName) {
      user.updateProfile({ displayName: data.name });
    }
    authRequest('/api/users', data).then(() => {
      const message = 'Your account data has been successfully saved.'
      showNotification('Account saved', message, { type: 'success' });
    });
  },


  uploadUserPhoto() {
    /*
     * Upload a user's photo through the API.
     */
    if (this.files.length) {
      showNotification('Uploading photo', 'Uploading your profile picture...', { type: 'wait' });
      changePhotoURL(this.files[0]).then((downloadURL) => {
        authRequest('/api/users', { photo_url: downloadURL });
        document.getElementById('user-photo-url').src = downloadURL;
        document.getElementById('userPhotoNav').src = downloadURL;
        document.getElementById('userPhotoMenu').src = downloadURL;
        const message = 'Successfully uploaded your profile picture.';
        showNotification('Uploading photo complete', message, { type: 'success' });
      }).catch((error) => {
        showNotification('Photo Change Error', storageErrors[error.code], { type: 'error' });
      });
    }
  },

  /* ---------------------------------------------------------------------------
   * Pin and signature management.
   ---------------------------------------------------------------------------*/

  createPin(event) {
    /* 
    * Create a pin for a user.
    */
    event.preventDefault();
    const pin = document.getElementById('pin_input').value;
    authRequest('/api/auth/create-pin', { pin }).then((response) => {
      if (response.success) {
        document.getElementById('pin_input').value = '';
        showNotification('Pin created', response.message, { type: 'success' });
        window.location.href = '/settings/user';
      } else {
        showNotification('Invalid pin', response.message, { type: 'error' });
      }
    });
  },


  deleteSignature(data) {
    /* 
    * Remove a signature from a user's settings.
    */
    authRequest('/api/auth/delete-signature').then((response) => {
      if (response.success) {
        showNotification('Signature deleted', response.message, { type: 'success' });
        window.location.reload(); // Optional: Hide banner more elegantly.
      } else {
        showNotification('Signature deletion failed', response.message, { type: 'error' });
      }
    });
  },


  deletePin() {
    /* 
    * Delete all existing pins for a user.
    */
    authRequest('/api/auth/delete-pin').then((response) => {
      if (response.success) {
        showNotification('Voided user pin', response.message, { type: 'success' });
        window,location.reload(); // Optional: Hide banner more elegantly.
      } else {
        showNotification('Voiding pin failed', response.message, { type: 'error' });
      }
    });
  },


  saveSignature(uid, data) {
    /* 
    * Upload a signature for a user.
    */
    // FIXME: Upload signature through the API.
    // authRequest('/api/auth/create-signature', { data_url: data }).then((response) => {
    //   if (response.success) {
    //     showNotification('Signature saved', response.message, { type: 'success' });
    //   } else {
    //     showNotification('Signature upload failed', response.message, { type: 'error' });
    //   }
    // });
    const signatureRef = `users/${uid}/user_settings/signature.png`;
    uploadImage(signatureRef, data).then((snapshot) => {
      getDownloadURL(signatureRef).then((url) => {
        updateDocument(`users/${uid}`, {
          signature_created_at: new Date().toISOString(),
          signature_ref: signatureRef,
        })
        updateDocument(`users/${uid}/user_settings/signature`, {
          signature_created_at: new Date().toISOString(),
          signature_ref: signatureRef,
          signature_url: url,
        }).then(() => {
          showNotification('Signature saved', 'Signature saved with your files.', { type: 'success' });
          window.location.href = '/settings/user';
        })
        .catch((error) => {
          console.log(error);
          showNotification('Error saving signature', 'An error occurred when saving your signature.', { type: 'error' });
        });
      }).catch((error) => {
        console.log(error)
        showNotification('Error uploading signature', 'An error occurred when uploading your signature.', { type: 'error' });
      });
    });
  },


  viewSignature(event) {
    /*
     * Require the user to enter their pin before showing their signature.
     */
    event.preventDefault();
    const pin = document.getElementById('pin_input').value;
    authRequest('/api/auth/get-signature', { pin }).then((response) => {
      if (response.success) {
        var modalEl = document.getElementById('pinModal')
        var modal = bootstrap.Modal.getInstance(modalEl);
        const signatureEl = document.getElementById('signature-canvas');
        signatureEl.classList.remove('d-none');
        signatureEl.src = response.signature_url;
        document.getElementById('view_button').classList.add('d-none');
        document.getElementById('hide_button').classList.remove('d-none');
        modal.hide();
      } else {
        showNotification('Invalid pin', response.message, { type: 'error' });
      }
    })
    .catch((error) => {
      showNotification('Invalid pin', error.message, { type: 'error' });
    });
  },


  hideSignature() {
    /*
     * Hide a signature after it has been shown.
     */
    document.getElementById('hide_button').classList.add('d-none');
    document.getElementById('view_button').classList.remove('d-none');
    document.getElementById('signature-canvas').classList.add('d-none');
  },


  uploadSignature(event, uid) {
    /*
     * Upload an existing signature file to Firebase Storage.
     * FIXME: Save to users/${uid}/user_settings/signature
     */
    const signatureRef = `users/${uid}/user_settings/signature.png`;
    if (event.target.files.length) {
      showNotification('Uploading signature', 'Uploading your signature image...', { type: 'wait' });
      uploadFile(signatureRef, event.target.files[0]).then((snapshot) => {
        getDownloadURL(signatureRef).then((url) => {
          updateDocument(`users/${uid}`, {
            signature_created_at: new Date().toISOString(),
            signature_ref: signatureRef,
            signature_url: url,
          }).then(() => {
            showNotification('Signature saved', 'Signature saved with your files.', { type: 'success' });
            window.location.href = '/settings/user';
          })
          .catch((error) => console.log(error));
        }).catch((error) => console.log(error));
      });
    }
  },

  // DRAFT
  getUserLogs(orgId) {
    /* 
    * Record time and user of any activity.
    */
  },

};
