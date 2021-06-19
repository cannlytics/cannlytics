/**
 * Dashboard JavaScript | Cannlytics Console
 * Author: Keegan Skeate <keegan@cannlytics.com>
 * Created: 12/3/2020
 * Updated: 6/10/2021
 */

import { auth, changePhotoURL, storageErrors } from '../firebase.js';
import { authRequest, hasClass, Password, serializeForm, slugify, showNotification } from '../utils.js';
// import { uploadUserPhoto } from '../settings/user.js';

export const dashboard = {


  initializeGetStarted(stage) {
    /*
     * Initializes the get started forms.
     */

    // Optional: Initialize authentication from the back-end?
    auth.onAuthStateChanged((user) => {
      if (user) {
        if (stage === 'profile') {
          // initializeGetStartedProfileUI(user)
          authRequest('/api/users').then((data) => initializeGetStartedProfileUI(data));
        }
        else if (stage === 'organization') {
          initializeGetStartedOrganizationUI({});
        }
      }
    });
  },


  joinOrganizationRequest() {
    /*
     * Send the owner of an organization a request for a user to join.
     */
    const organization = document.getElementById('join-organization-input').value;
    if (!organization) {
      showNotification('Organization required', 'Enter an organization name.', { type: 'error' });
      return;
    }
    authRequest('/api/organizations/join', { organization, join: true }).then((response) => {
      if (response.success) {
        showNotification('Organization request sent', response.message, { type: 'success' });
      } else {
        showNotification('Organization request failed', response.message, { type: 'error' });
      }
    });
  },


  selectSupportTier(tier) {
    /*
     * Add selected indicator to support choices.
     */
    const cards = document.getElementsByClassName('support-card');
    for (let i = 0; i < cards.length; i++) {
      cards[i].classList.remove('border-success');
      if (cards[i].id === `tier${tier}`) {
        cards[i].classList.add('border-success');
      }
    }
  },


  saveOrganization(orgType) {
    /*
     * Save's a user's organization choice.
     */
    const elements = document.getElementById('create-organization-form').elements;
    const data = {};
    for (let i = 0 ; i < elements.length ; i++) {
      const item = elements.item(i);
      if (item.name) data[item.name] = item.value;
    }
    const orgId = slugify(data['name'])
    authRequest(`/api/organizations`, data).then((response) => {
      // Optional: Show better error messages.
      // Optional: Tell user if organization name is already taken
      if (response.error) {
        showNotification('Organization request failed', response.message, { type: 'error' });
      } else {
        // Optional: Navigate straight to the dash if the user requested to join an organization.
        // showNotification('Organization request sent', response.message, { type: 'success' });
        document.location.href = `/get-started/support/?from=${orgType}`;
      }
    });
  },


  saveUserData(type) {
    /*
     * Save's a user's data.
     */
    const user = auth.currentUser;
    const data = serializeForm('user-form');
    const baseURL = window.location.origin;
    data.type = type;
    if (user === null) {
      signUp(data.email).then(() => {
        document.location.href = `${baseURL}/get-started/organization/?from=${type}`;
      }).catch((error) => {
        showNotification('Sign up error', error.message, { type: 'error' });
        // Optional: Show error class (.is-invalid) if invalid
      });
    } else {
      if (data.email !== user.email) {
        user.updateEmail(data.email);
      }
      if (data.name !== user.displayName) {
        user.updateProfile({ displayName: data.name });
      }
      authRequest('/api/users', data).then(() => {
        document.location.href = `${baseURL}/get-started/organization/?from=${type}`;
      });
    }
  },


  saveSupport() {
    /*
     * Save's a user's support option.
     */
    let tier = 'Free';
    const cards = document.getElementsByClassName('support-card');
    for (let i = 0; i < cards.length; i++) {
      if (hasClass(cards[i], 'border-success')) {
        tier = cards[i].id.replace('tier', '');
      }
    }
    authRequest('/api/users', { support: tier }).then(() => {
      document.location.href = '/';
    });
  },


  showOrganizationForm(type) {
    /*
     * Show either the join or create organization forms or neither.
     */
    document.getElementById('organization-choice').classList.add('d-none');
    document.getElementById('cancel-organization-choice').classList.remove('d-none');
    if (type === 'join') {
      document.getElementById('join-organization-form').classList.remove('d-none');
    } else if (type === 'create') {
      document.getElementById('create-organization-form').classList.remove('d-none');
    } else {
      document.getElementById('join-organization-form').classList.add('d-none');
      document.getElementById('create-organization-form').classList.add('d-none');
      document.getElementById('organization-choice').classList.remove('d-none');
      document.getElementById('cancel-organization-choice').classList.add('d-none');
    }
  },


  // chooseUserPhoto() {
  //   /*
  //    * Choose a file to upload.
  //    */
  //   const fileSelect = document.getElementById('userPhotoUrl');
  //   fileSelect.click();
  // },


  choosePhoto() {
    /*
     * Choose a file to upload.
     */
    const fileSelect = document.getElementById('selectPhotoUrl');
    fileSelect.click();
  },


}


/*
 * Internal Functions
 */

function signUp(email) {
  /*
   * Sign up a user.
   */
  return new Promise((resolve, reject) => {
    var password = Password.generate(32);
    firebase.auth().createUserWithEmailAndPassword(email, password)
      .then(() => {
        authRequest('/api/users', { email, photo_url: `https://robohash.org/${email}?set=set5` })
          .then((data) => {
            resolve(data);
          })
          .catch((error) => {
            reject(error);
          })
      })
      .catch((error) => {
        reject(error);
      });
  });
  // var termsAccepted = document.getElementById('login-terms-accepted').checked;
  // if (!termsAccepted) {
  //   showError(
  //     'Terms not accepted',
  //     'Please agree with our terms of service and read our privacy policy to create an account.'
  //   );
  //   return;
  // }
  // var password = document.getElementById('login-password').value;
}

// Moved to settings/user.js
function uploadUserPhoto() {
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
      showNotification('Uploading photo complete', 'Successfully uploaded your profile picture.', { type: 'success' });
    }).catch((error) => {
      showNotification('Photo Change Error', storageErrors[error.code], { type: 'error' });
    });
  }
}


function uploadOrgPhoto(orgId) {
  /*
   * Upload a photo for an organization through the API.
   */
  if (this.files.length) {
    showNotification('Uploading photo', 'Uploading your organization picture...', { type: 'wait' });
    changePhotoURL(this.files[0]).then((downloadURL) => {
      authRequest('/api/organizations', { photo_url: downloadURL, uid: orgId });
      document.getElementById('org-photo-url').src = downloadURL;
      showNotification('Uploading photo complete', 'Successfully uploaded organization picture.', { type: 'success' });
    }).catch((error) => {
      showNotification('Photo Change Error', storageErrors[error.code], { type: 'error' });
    });
  }
}


/*
 * UI Management
 */


function initializeGetStartedProfileUI(data) {
  /*
   * Initialize the get-started profile section's form with existing values.
   */

  // Populate the form's fields.
  const form = document.getElementById('user-form');
  const { elements } = form;
  for (const [ key, value ] of Object.entries(data)) {
    const field = elements.namedItem(key);
    console.log(key, field);
    try {
      field && (field.value = value);
    } catch(error) {}
  }

  // Attach functionality.
  const fileElem = document.getElementById('userPhotoUrl');
  fileElem.addEventListener('change', uploadUserPhoto, false);

}


function initializeGetStartedOrganizationUI(data) {
  /*
   * Initialize the get-started organization section.
   */

  // Attach functionality.
  const fileElem = document.getElementById('selectPhotoUrl');
  fileElem.addEventListener('change', uploadOrgPhoto, false);

}
