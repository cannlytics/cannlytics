/**
 * Organizations JavaScript | Cannlytics Console
 * Author: Keegan Skeate
 * Created: 6/9/2021
 * Updated: 8/13/2021
 */
import { changePhotoURL, getDownloadURL, getCollection, getDocument, updateDocument, uploadFile, storageErrors } from '../firebase.js';
import { authRequest, deserializeForm, serializeForm, slugify, showNotification } from '../utils.js';

export const organizationSettings = {


  chooseOrganizationPhoto() {
    /*
     * Choose a file to upload.
     */
    const fileSelect = document.getElementById('organization_photo_url_input');
    fileSelect.click();
  },


  initializeOrganizationsForm(orgId) {
    /*
     * Initialize the organizations user interface.
     */
    const fileElem = document.getElementById('organization_photo_url_input');
    fileElem.addEventListener('change', this.uploadOrganizationPhoto, false);
    this.resetOrganizationsForm(orgId);
  },


  resetOrganizationsForm(orgId) {
    /*
     * Reset a form with currently saved data, replacing any changes.
     */
    authRequest(`/api/organizations/${orgId}`).then((response) => {
      const form = document.forms['organization-form'];
      form.reset();
      deserializeForm(form, response.data);
      if (response.data.photo_url) {
        document.getElementById('organization_photo_url').src = response.data.photo_url;
      } else {
        document.getElementById('organization_photo_url').src = "/static/console/images/icons/outline/teamwork.svg";
      }
      if (response.data.public) {
        document.getElementById('public-choice').checked = true;
      } else if (response.private) {
        document.getElementById('private-choice').checked = true;
      }
    });
  },


  uploadOrganizationPhoto() {
    /*
     * Upload a organization photo through the API.
     */
    const orgId = document.getElementById('organization_id_input').value;
    if (this.files.length) {
      showNotification('Uploading image', 'Uploading your organization image...', { type: 'wait' });
      const file = this.files[0];
      const ext = file.name.split('.')[1];
      const ref = `organizations/${orgId}/organization_settings/logo.${ext}`;
      uploadFile(ref, file).then((snapshot) => {
        getDownloadURL(ref).then((url) => {
          updateDocument(`organizations/${orgId}`, {
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


  changeActiveOrganization(orgId) {
    /*
     * Change the active organization for the user.
     */
    // TODO: Move orgId to beginning of user's list and refresh.
    console.log('Change organizations:', orgId);
  },


  changeOrganizationPublicStatus(orgId) {
    /*
     * Change the organization's public status.
     */
    const publicChoice = document.getElementById('public-choice').checked;
    authRequest(`/api/organizations/${orgId}`, { public: publicChoice }).then((response) => {
      const type = publicChoice ? 'public' : 'private';
      showNotification('Status saved', `Your organization is now ${type}.`, { type: 'success' });
    })
    .catch((error) => {
      showNotification('Error changing status.', error, { type: 'error' });
    });
  },


  toggleTraceabilityEndpoint(event) {
    /*
     * Toggle a traceability endpoint on or off for a given organization.
     */
    const endpoint = event.target.id.split('_')[1];
    const { checked } = event.target;
    console.log('Toggling traceability endpoint:', endpoint, checked);

  },


  getSubscription() {
    /*
     * Get an organization's subscription data.
     */
    const orgId = document.getElementById('organization_id').value;
    return new Promise(async (resolve) => {
      const data = await getDocument(`organizations/${orgId}/organization_settings/subscription`);
      resolve(data);
    });
  },


  getTeamMembers(orgId, claims, render=true) {
    /*
     * Get team member data.
     */
    authRequest(`/api/organizations/${orgId}/team`, ).then((response) => {
      response.data.forEach((item) => {
        if (render) addTeamMemberCard(orgId, claims, item);
      });
    });
  },


  getTeamMember(orgId, userId) {
    /*
     * Get a team member's data.
     */
    authRequest(`/api/organizations/${orgId}/team/${userId}`, ).then((response) => {
      response.data.forEach((item) => {
        deserializeForm(document.forms['team-member-form'], item);
        if (item.photo_url) document.getElementById('user-photo-url').src = item.photo_url;
      });
    });
  },


  getTraceabilitySettings() {
    /*
     * Get an organization's traceability settings.
     */
    const orgId = document.getElementById('organization_id').value;
    return new Promise(async (resolve) => {
      const data = await getDocument(`organizations/${orgId}/organization_settings/traceability_settings`);
      resolve(data);
    });
  },


  async getTeamMemberLogs(orgId, userId) {
    /*
     * Get logs for a given team member.
     */
    console.log('User id:', userId);
    const data = await getCollection(`organizations/${orgId}/logs`, {
      desc: true,
      filters: [{'key': 'user', 'operation': '==', 'value': userId}],
      limit: 100, // TODO: Adjust limit
      orderBy: 'created_at',
    });
    console.log('Team member logs:', data);
  },


  deleteOrganization() {
    /*
     * Delete (archive) an organization.
     */
    // TODO: Make authRequest to delete an organization.
  },


  removeTeamMember(uid) {
    /*
     * Remove a team member from an organization through the API (owner's only).
     */
    // TODO: Make authRequest to remove a team member.
    console.log('Removing team member:', uid);
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
      // TODO: Tell user if organization name is already taken
      if (response.error) {
        showNotification('Organization request failed', response.message, { type: 'error' });
      } else {
        const baseURL = window.location.origin;
        document.location.href = `${baseURL}/get-started/support/?from=${orgType}`;
      }
    });
  },


  saveOrganizationSettings(event, orgId) {
    /*
     * Save an organization's settings.
     */
    event.preventDefault();
    const form = document.getElementById('organization-form');
    const data = serializeForm(form);
    document.getElementById('save-button').classList.add('d-none');
    document.getElementById('save-button-loading').classList.remove('d-none');
    authRequest(`/api/organizations/${orgId}`, data).then((response) => {
      if (response.success) {
        showNotification('Organization details saved', 'Organization details successfully saved.', { type: 'success' });
      } else {
        showNotification('Failed to save organization details', response.message, { type: 'error' });
      }
      document.getElementById('save-button-loading').classList.add('d-none');
      document.getElementById('save-button').classList.remove('d-none');
    });
  },


  saveDataModel(modelType) {
    /*
     * Save fields for a given data model type.
     */
    // TODO: Save data model fields to /organizations/${orgId}/organization_settings
    console.log('Saving fields for', modelType);
  },


  getOrganizationSettings() {
    /*
     * Save an organization's settings.
     */
    // TODO: Get settings from /organizations/${orgId}/organization_settings as a promise.
  },


  saveTeam() {
    /*
     * Save organization team members and send invites.
     */
    // TODO: Invite team members through the API.
  },


  uploadOrgPhoto(orgId) {
    /*
     * Upload a photo for an organization through the API.
     */
    if (this.files.length) {
  
      // Show a notification.
      showNotification('Uploading photo', 'Uploading your organization picture...', { type: 'wait' });
      
      // Fill the photo into the UI.
      changePhotoURL(this.files[0]).then((downloadURL) => {
        authRequest('/api/organizations', { photo_url: downloadURL, uid: orgId });
        document.getElementById('org-photo-url').src = downloadURL;
        showNotification('Uploading photo complete', 'Successfully uploaded organization picture.', { type: 'success' });
      }).catch((error) => {
        showNotification('Photo Change Error', storageErrors[error.code], { type: 'error' });
      });
    }
  },


  viewOrganization(orgId) {
    /*
     * View an organization on navigation.
     */
    authRequest(`/api/organizations/${orgId}`).then((response) => {
      if (response.data) {
        console.log('Retrieved data:', response.data);
        deserializeForm(document.forms['organization-form'], response.data);
      } else {
        console.log(response);
      }
    });
    
  }


}


/*
 * UI Management
 */

function addTeamMemberCard(orgId, claims, data, gridId='team-member-grid') {
  /*
   * Add a data card to an existing grid.
   * TODO: Render delete option if owner.
   */
  let badges = '';
  let options = '';
  let license = '';
  let phone = '';
  let position = '';
  if (data.license) license = `<div>License: ${data.license}</div>`;
  if (data.phone) phone = `<div>${data.phone}</div>`;
  if (data.position) position = `<div>${data.position}</div>`;
  if (claims.owner.includes(claims.uid)) {
    badges = '<span class="badge rounded-pill bg-gradient-orange">Owner</span>';
    options = `
  <div class="d-flex align-items-center">
    <a class="btn btn-sm-light me-2" href="/settings/organizations/${orgId}/team/${data.uid}">
      Edit
    </a>
    <button class="btn btn-sm-light text-danger" onclick="cannlytics.settings.removeTeamMember('${data.uid}')">
      Remove
    </button>
  </div>`
  }
  if (claims.qa.includes(claims.uid)) {
    badges = '<span class="badge rounded-pill bg-warning">QA</span>';
  }
  if (claims.billing.includes(claims.uid)) {
    badges = '<span class="badge rounded-pill bg-warning">Billing</span>';
  }
  if (claims.staff.includes(claims.uid)) {
    badges = '<span class="badge rounded-pill bg-gradient-green">Staff</span>';
  }
  var div = document.getElementById(gridId);
  var text = `
<div
  class="card shade-hover border-secondary rounded-3 app-action col col-sm-1 col-md-2 p-3 mb-3 h-100"
  style="width:275px;"
>
<a class="card-block stretched-link text-decoration-none" href="/settings/organizations/${orgId}/team/${data.uid}">
  <div class="d-flex justify-content-between">
    <div class="d-flex align-items-center">
      <div class="icon-container float-left align-self-start me-2">
        <img src="${data.photo_url}" height="50px">
      </div>
      <div class="col">
        <h4 class="fs-5 text-dark">${data.name}</h4>
        <div class="text-dark">${data.email}</div>`;
        if (position) text += `<div class="text-secondary">${position}</div>`;
        if (phone) text += `<div class="text-secondary">${phone}</div>`;
        if (license) text += `<div class="text-secondary">${license}</div>`;
      text += `</div>
    </div>
  </div>
  <div class="card-body bg-transparent mt-2 p-0">
    ${badges}
  </div>
</a>
</div>`;
div.innerHTML = text;
}
