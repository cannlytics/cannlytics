/**
 * User Settings JavaScript | Cannlytics Console
 * Author: Keegan Skeate <keegan@cannlytics.com>
 * Created: 1/2/2021
 * Updated: 6/17/2021
 */

import { auth, changePhotoURL, storageErrors } from '../firebase.js';
import { authRequest, formDeserialize, serializeForm, showNotification } from '../utils.js';


export const userSettings = {


  chooseUserPhoto() {
    /*
     * Choose a file to upload.
     */
    const fileSelect = document.getElementById('userPhotoUrl');
    fileSelect.click();
  },


  exportAccount(data) {
    /* 
    * TODO: Exports a user's data.
    */
    console.log('Export all of a users data to Excel.');
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


  createPin(data) {
    /* 
    * Create a pin for a user.
    */
   // TODO:
   console.log('Todo: Create a pin!');
  },


  uploadSignature(data) {
    /* 
    * Upload a signature for a user.
    */
    // TODO:
    const collection = db.collection('organizations');
    return collection.add(data);
  },


  deleteSignature(data) {
    /* 
    * Remove a signature from a user.
    */
    // TODO:
    const collection = db.collection('organizations');
    return collection.add(data);
  },


};
