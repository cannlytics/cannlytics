/**
 * User Settings JavaScript | Cannlytics Console
 * Author: Keegan Skeate <keegan@cannlytics.com>
 * Created: 1/2/2021
 * Updated: 7/3/2021
 */

import { auth, changePhotoURL, storageErrors, updateDocument, uploadImage, verifyUserToken } from '../firebase.js';
import { authRequest, formDeserialize, serializeForm, showNotification } from '../utils.js';


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
      formDeserialize(userForm, data);
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
        window,location.reload(); // TODO: Hide banner more elegantly.
      } else {
        showNotification('Voiding pin failed', response.message, { type: 'error' });
      }
    });
  },


  uploadSignature(data) {
    /* 
    * Upload a signature for a user.
    */
    authRequest('/api/auth/create-signature', { data_url: data }).then((response) => {
      if (response.success) {
        showNotification('Signature saved', response.message, { type: 'success' });
      } else {
        showNotification('Signature upload failed', response.message, { type: 'error' });
      }
    });
    // uploadImage(signatureRef, data)
    //   .then(() => {
    //     getDownloadURL(signatureRef).then((url) => {
    //       console.log('Retrieved download URL:', url)
    //       updateDocument(`users/${uid}`, {
    //         signature_ref: signatureRef,
    //         signature_url: url,
    //       });
    //       // Update the UI.
    //       // var img = document.getElementById('myimg');
    //       // img.setAttribute('src', url);
    //     });
    //   });
  },


  viewSignature(event) {
    /*
     * Require the user to enter their pin before showing their signature.
     */
    // TODO: Ask user to enter their pin in a dialog.
    // Get a user's signature image data url given their pin
    event.preventDefault();
    const pin = document.getElementById('pin_input').value;
    authRequest('/api/auth/get-signature', { pin }).then((response) => {
      if (response.success) {
        // TODO: Show the returned data image URL!
        console.log(response.signature_url);
      } else {
        showNotification('Invalid pin', response.message, { type: 'error' });
      }
    });
  },


  // showSignature(event) {
  //   /*
  //    * Show a user's signature after they have successfully entered their pin.
  //    */
  //   // TODO: Load the image using the signature_ref
  //   // TODO: Show the image on the page.
  //   // FIXME: Is this secure?
  //   event.preventDefault();
  //   const pin = document.getElementById('pin_input').value;
  //   authRequest('/api/auth/verify-pin', { pin }).then((response) => {
  //     if (response.success) {
  //       verifyUserToken(response.token).then((response) => {
  //         console.log(response);
  //         // TODO: Securely show signature
  //       })
  //       .catch((error) => {
  //         showNotification('Invalid pin', error.message, { type: 'error' });
  //       });
  //     }
  //   });
  // },


};
