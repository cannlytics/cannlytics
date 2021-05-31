/**
 * Dashboard JavaScript | Cannlytics Console
 * Licensed under GPLv3 (https://github.com/cannlytics/cannlytics_console/blob/main/LICENSE)
 * Author: Keegan Skeate
 * Created: 12/3/2020
 * Updated: 5/2/2021
 */

import { auth, changePhotoURL, storageErrors } from '../firebase.js';
import { authRequest, hasClass, Password, serializeForm, showNotification } from '../utils.js';

export const dashboard = {


  initializeGetStarted(stage) {
    /*
     * Initializes the get started forms.
     */
    // FIXME: Initialize from back-end?
    // auth.onAuthStateChanged((user) => {
    //   console.log('Detected user in dashboard:', user)
    //   if (user) {
    //     if (stage === 'profile') {
    //       initializeGetStartedProfileUI(user)
    //       // authRequest('/api/users').then((data) => initializeGetStartedProfileUI(data));
    //     }
    //   }
    // });
    // if (stage === 'organization') {
    //   authRequest('/api/organizations').then((data) => initializeGetStartedOrganizationUI(data));
    // }
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


  saveOrganization() {
    /*
     * Save's a user's organization choice.
     */
    const elements = document.getElementById('create-organization-form').elements;
    const data = {};
    for (let i = 0 ; i < elements.length ; i++) {
      const item = elements.item(i);
      data[item.name] = item.value;
    }
    authRequest('/api/organizations', data).then((response) => {
      console.log('Saved org:', response);
      // TODO:
      // if (response.success) {
      //   showNotification('Organization request sent', response.message, { type: 'success' });
      // } else {
      //   showNotification('Organization request failed', response.message, { type: 'error' });
      // }
    });
  },


  saveUserData(type) {
    /*
     * Save's a user's data. FIXME: Kind of broken
     */
    const terms = document.getElementById('login-terms-accepted');
    if (!terms.checked) {
      const message = 'Please accept the terms of service and read the privacy and security policies.';
      showNotification('Terms not accepted', message, { type: 'error' });
      terms.classList.add('is-invalid');
      return;
    } else {
      terms.classList.remove('is-invalid');
    }
    const user = auth.currentUser;
    const data = serializeForm('userForm');
    data.type = type;
    if (user === null) {
      signUp(data.email).then(() => {
        document.location.href = `/get-started/organization/?from=${type}`;
      }).catch((error) => {
        showNotification('Sign up error', error.message, { type: 'error' });
        // TODO: Show error class if invalid (.is-invalid)
      });
    } else {
      if (data.email !== user.email) {
        user.updateEmail(data.email);
      }
      if (data.name !== user.displayName) {
        user.updateProfile({ displayName: data.name });
      }
      authRequest('/api/users', data).then(() => {
        document.location.href = `/get-started/organization/?from=${type}`;
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


  chooseUserPhoto() {
    /*
     * Choose a file to upload.
     */
    const fileSelect = document.getElementById('userPhotoUrl');
    fileSelect.click();
  },


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


function uploadUserPhoto() {
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


function uploadOrgPhoto() {
  if (this.files.length) {
    showNotification('Uploading photo', 'Uploading your organization picture...', { type: 'wait' });
    
    // TODO:
    // changePhotoURL(this.files[0]).then((downloadURL) => {
    //   authRequest('/api/users', { photo_url: downloadURL });
    //   document.getElementById('user-photo-url').src = downloadURL;
    //   document.getElementById('userPhotoNav').src = downloadURL;
    //   document.getElementById('userPhotoMenu').src = downloadURL;
    //   showNotification('Uploading photo complete', 'Successfully uploaded your profile picture.', { type: 'success' });
    // }).catch((error) => {
    //   showNotification('Photo Change Error', storageErrors[error.code], { type: 'error' });
    // });
  }
}


/*
 * UI Management
 */


function initializeGetStartedProfileUI(data) {

  // Set the user's photo.
  try {
    if (data.photo_url || data.photoURL || data.email) {
      document.getElementById('user-photo-url').src = data.photo_url || data.photoURL || `https://robohash.org/${data.email}?set=set5`;
    }
  } catch (error) {}


  // Populate form.
  const { elements } = document.querySelector('form')
  for (const [ key, value ] of Object.entries(data)) {
    const field = elements.namedItem(key)
    try {
      field && (field.value = value);
    } catch(error) {}
  }

  // Attach functionality.
  const fileElem = document.getElementById('userPhotoUrl');
  fileElem.addEventListener('change', uploadUserPhoto, false);

}


function initializeGetStartedOrganizationUI(data) {

  // TODO: Set the organization's photo.
  // try {
  //   if (data.photo_url) document.getElementById('user-photo-url').src = data.photo_url;
  // } catch (error) {}


  // Populate form.
  const { elements } = document.querySelector('form')
  for (const [ key, value ] of Object.entries(data)) {
    const field = elements.namedItem(key)
    try {
      field && (field.value = value);
    } catch(error) {}
  }

  // Attach functionality.
  const fileElem = document.getElementById('selectPhotoUrl');
  fileElem.addEventListener('change', uploadOrgPhoto, false);

}





// SCRAP

// getUserData() {
//   /*
//    * Stream the user's data.
//    */
//   return new Promise((resolve) => {
//     const uid = auth.currentUser.uid;
//     db.collection('users').doc(uid).onSnapshot((doc) => {
//       const data = doc.data();
//       console.log("User data:", data);
//       resolve(data);
//     });
//   });
// },
