/**
 * Settings JavaScript | Cannlytics Console
 * Author: Keegan Skeate
 * Created: 12/3/2020
 * Updated: 5/11/2021
 */

import { auth, db } from '../firebase.js';
import { accountSettings } from './account.js';
import { errorSettings } from './errors.js';
import { apiRequest, serializeForm, showNotification } from '../utils.js';
import { ui } from '../ui/ui.js';

const apiSettings = {

  createAPIKey() {
    /* 
    * Create an API key.
    */
    const data = serializeForm('new-api-key-form');
    console.log('Creating API key...', data);
    ui.showLoadingButton('create-api-key-button');
    apiRequest('/api/create-key', data).then((response) => {
      // TODO: Add new key to the table!
      console.log(response);
    }).finally(() => {
      ui.hideLoadingButton('create-api-key-button');
    });
  },

  deleteAPIKey(data) {
    /* 
    * Delete an API key.
    */
    console.log('Deleting API key...', data);
    // TODO: Post name of key that needs to be deleted.
  },

  getAPIKeys(uid) {
    /* 
    * Get all of a user's API key information.
    */
    console.log('Getting all API keys...', uid);
    // FIXME: Get from /api/get_api_key_hmacs instead
    return new Promise((resolve, reject) => {
      apiRequest('/api/get-keys').then((response) => {
        resolve(response['data']);
      });
      // db.collection('admin').doc('api').collection('api_key_hmacs')
      // .get()
      // .then((querySnapshot) => {
      //   const data = [];
      //   querySnapshot.forEach((doc) => {
      //     data.push(doc.data());
      //   });
      //   resolve(data);
      // })
      // .catch((error) => {
      //   reject(error);
      // });
      // .onSnapshot((querySnapshot) => {
      //   var data = [];
      //   querySnapshot.forEach((doc) => {
      //     data.push(doc.data().name);
      //   });
      //   resolve(data);
      // });
    });
    // const ref = db.collection('admin').document('api').collection('api_key_hmacs')
    //   .where('uid', '==', uid);
    // ref.onSnapshot(snapshot => {
    //   snapshot.docChanges.forEach(change => {
    //     this.renderAPIKey(change);
    //   });
    // });
  },

  renderAPIKey(change) {
    /* 
    * Get all of a user's API key information.
    */
    if (change.type === 'added') {
      console.log('Add data to table:', change.doc);
    }
    else if (change.type === 'removed') {
      console.log('Remove row from table:', change.doc.id);
    }
  },

  selectAPIKey(data) {
    /*
     * Select an API key from the table.
     */
  },

}


const orgSettings = {

  newOrganization() {
    // const id = uuidv4();
    // TODO:
    console.log('Create new org');
  },

  addOrganization(data) {
    /* 
    * Add an organizations.
    */
    const collection = db.collection('organizations');
    return collection.add(data);
  },

  getOrganizations() {
    /* 
    * Get all of a user's organizations.
    */
    auth.onAuthStateChanged((user) => {
      if (user) {
        // console.log(user.uid);
        // TODO: Get all of a users/{id} org_id's.
        // TODO: Get all organizations/{id} documents for org_id's.
        console.log('Get all organizations for user id:', user.uid);
        // const query = db.collection('organizations').limit(50);
        // query.onSnapshot(snapshot => {
        //   if (!snapshot.size) return render();
        //   snapshot.docChanges.forEach(change => {
        //     if (change.type === 'added') {
        //       render(change.doc);
        //     }
        //     else if (change.type === 'removed') {
        //       document.getElementById(change.doc.id).remove();
        //     }
        //   });
        // });
      }
    });
  //  idbStore.get('user').then((data) => {
  //   console.log('IDB User:', data);
  //   console.log('Getting organizations!');
  //  });
  },

  archiveOrganizations() {
    /* 
    * Archive one of a user's organizations.
    */
   // TODO: Add to archived organizations.
    const collection = firebase.firestore().collection('ships');
    return collection.doc(id).delete()
      .catch(function(error) {
        console.error('Error removing document: ', error);
      });
  },

  updateOrganization() {
    /* 
    * Update a user's organizations.
    */
    // TODO:
  },

}


const coreSettings = {

  logAction() {
    /* 
    * Record time and user of any activity.
    */
    // TODO:
  },

  sendFeedback() {
    /*
     * Send feedback through Firestore-triggered Google Cloud Function.
     */
    const user = auth.currentUser || {};
    const message = document.getElementById('feedback-message').value;
    const timestamp = Date.now().toString(); // Optional: Specify time zone.
    const code = Math.random().toString(36).slice(-3);
    const data = {
      name: user.displayName || 'Anonymous user',
      email: user.email || 'No user',
      organization: user.organization || 'No organization',
      body: message,
      from: 'contact@cannlytics.com',
      reply: 'contact@cannlytics.com',
      recipients: ['contact@cannlytics.com'],
      subject: 'New Cannlytics Console feedback!',
      promo: code,
    };
    db.collection('users').doc(user.uid).collection('feedback')
      .doc(timestamp)
      .set(data).then(() => {
        showNotification('Feedback sent', 'Thank you for your feedback', { type: 'success' });
      }).catch((error) => {
        showNotification('Error sending feedback', error.message, { type: 'error' });
      });
  }

};

export const settings = {
  ...apiSettings,
  ...coreSettings,
  ...accountSettings,
  ...errorSettings,
};
