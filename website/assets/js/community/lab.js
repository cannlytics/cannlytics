/**
 * lab.js | Cannlytics Website
 * Created: 1/17/2021
 */

// import { firestore } from 'firebase';
import { auth } from '../firebase.js';

export const lab = {

  // State

  lab: {},

  // Functions

  initializeDetails() {
    const form = document.querySelector('form');
    form.addEventListener('submit', cannlytics.community.updateLab);
    if (auth.currentUser) {
      document.getElementById('edit-button').classList.remove('visually-hidden');
    }
  },


  toggleEditLab(edit=true) {
    /*
     * Toggle editing for a lab.
     */
    // Restrict editing to user's with an account.
    if (!auth.currentUser) {
      document.getElementById('login-alert').classList.add('show');
      return;
    }

    // Keep track of changes.
    var form = document.querySelector('form');
    var data = Object.fromEntries(new FormData(form));

    // Show buttons.
    var editButton = document.getElementById('edit-button');
    var cancelButton = document.getElementById('cancel-button');
    var saveButton = document.getElementById('save-button');
    if (edit) {
      editButton.classList.add('visually-hidden');
      cancelButton.classList.remove('visually-hidden');
      saveButton.classList.remove('visually-hidden');
      this.lab = data;
    } else {
      editButton.classList.remove('visually-hidden');
      cancelButton.classList.add('visually-hidden');
      saveButton.classList.add('visually-hidden');
      Object.keys(this.lab).forEach((key) => {
        var input = document.getElementById(`input-${key}`);
        input.value = this.lab[key];
      });
    }

    // Toggle inputs.
    var inputs = document.getElementsByClassName('form-control');
    for (var i = 0; i < inputs.length; i++) {
      var input = inputs.item(i);
      if (edit) { // Begin editing.
        input.readOnly = false;
        input.classList.remove('form-control-plaintext');
      }
      else { // Cancel editing, filling in original values.
        input.readOnly = true;
        input.classList.add('form-control-plaintext');
      }
    }
  },


  addLab(event) {
    /*
     * Submit a lab to be added to the directory through the API.
     */
    // TODO: Get lab data.

    // TODO: Post data to the API.
  },


  updateLab(event) {
    /*
     * Update a lab through the API.
     */

    // Get the form data.
    event.preventDefault();
    const form = new FormData(event.target);
    const data = Object.fromEntries(form.entries());

    // Get the user's token and post the lab data to the API for processing.
    auth.currentUser.getIdToken(/* forceRefresh */ true).then((token) => {
      fetch('/api/v1/labs/', {
        method: 'post',
        credentials: 'same-origin',
        headers: {
            // 'X-CSRFToken': getCookie('csrftoken'), // necessary?
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`,
        },
        body: JSON.stringify(data)
      });
        // TODO: Show toast of save success with items changed.
        // .then(response => response.json())
        // .then((data) => {
        //   console.log('Data:', data);
        // })
        // .catch((error) => {
        //   console.log('Error:', error);
        // });
    }).catch((error) => {
      // Handle error
    });

  },


  getLabAnalyses(id) {
    /*
     * Get analyses for a lab.
     */
    return new Promise((resolve, reject) => {
      var headers = { headers: { 'Accept': 'application/json' } };
      fetch(`/api/v1/labs/${id}/logs/`, headers)
        .then(response => response.json())
        .then(data => resolve(data.data));
      });
  },


  getLabLogs(id) {
    /*
     * Get change logs for a lab.
     */
    return new Promise((resolve, reject) => {
      var headers = { headers: { 'Accept': 'application/json' } };
      fetch(`/api/v1/labs/${id}/analyses/`, headers)
        .then(response => response.json())
        .then(data => resolve(data.data));
      });    
  },


  initializeAnalyses(id) {
    /*
     * Initialize analyses for a lab.
     */
    this.getLabAnalyses(id).then((data) => {
      // TODO: Show the data!
    });
  },


  initializeLogs(id) {
    /*
     * Initialize logs for a lab.
     */
    this.getLabLogs(id).then((data) => {
      // TODO: Show the data!
    });

  },


}
