/**
 * Organizations JavaScript | Cannlytics Console
 * Author: Keegan Skeate
 * Created: 6/9/2021
 * Updated: 7/5/2021
 */
import { api } from '../api/api.js';
import { theme } from '../settings/theme.js';
import { changePhotoURL, getDownloadURL, updateDocument, uploadFile, storageErrors } from '../firebase.js';
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
      console.log('Organization data:', response.data);
      const form = document.forms['organization-form'];
      form.reset();
      deserializeForm(form, response.data);
      if (response.data.photo_url) {
        document.getElementById('organization_photo_url').src = response.data.photo_url;
      } else {
        document.getElementById('organization_photo_url').src = "/static/console/images/icons/outline/teamwork.svg";
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


  getOrganizations(tableId) {
    /*
     * Get and display a user's organizations.
     */
    // TODO: Specify the columns.
    // address: ""
    // city: ""
    // country: ""
    // email: ""
    // external_id: ""
    // linkedin: ""
    // name: "Cannlytics"
    // owner: "v86tNoemQzgrnMvlWq6mxCASg523"
    // phone: ""
    // public: "false"
    // state: ""
    // team: ["v86tNoemQzgrnMvlWq6mxCASg523"]
    // trade_name: ""
    // uid: "cannlytics"
    // website: ""
    // zip_code: ""
    const columnDefs = [
      { field: 'name', sortable: true, filter: true },
      { field: 'email', sortable: true, filter: true },
      { field: 'phone', sortable: true, filter: true }
    ];

    // Specify the table options.
    const gridOptions = {
      columnDefs: columnDefs,
      pagination: true,
      rowSelection: 'multiple',
      suppressRowClickSelection: false,
      // singleClickEdit: true,
      // onRowClicked: event => console.log('A row was clicked'),
      onGridReady: event => theme.toggleTheme(theme.getTheme()),
    };

    // Get the data and render the table.
    api.get('organizations').then((data) => {
      console.log('Table data:', data); // DEV:
      const eGridDiv = document.querySelector(`#${tableId}`);
      new agGrid.Grid(eGridDiv, gridOptions);
      gridOptions.api.setRowData(data);
    })
    .catch((error) => {
      console.log('Error:', error);
    });

    // TODO: Attach export functionality
    //function exportTableData() {
    //  gridOptions.api.exportDataAsCsv();
    //}
  },


  getTeamMembers(orgId, owner, uid) {
    /*
     * Get team member data.
     */
    console.log('Owner:', owner);
    const isOwner = owner === uid;
    authRequest(`/api/organizations/${orgId}/team`, ).then((response) => {
      console.log('Team member data:', response.data);
      response.data.forEach((item) => {
        addTeamMemberCard('team-member-grid', item, owner, isOwner, orgId);
      });
    });
  },


  // updateOrganization() {
  //   /*
  //    * 
  //    */
  // },


  // createOrganization() {
  //   /*
  //    * 
  //    */
  // },


  deleteOrganization() {
    /*
     * 
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
    // FIXME:
    const elements = document.getElementById('create-organization-form').elements;
    const data = {};
    for (let i = 0 ; i < elements.length ; i++) {
      const item = elements.item(i);
      if (item.name) data[item.name] = item.value;
    }
    const orgId = slugify(data['name'])
    console.log('Org ID:', orgId);
    console.log('Data to upload:', data);
    authRequest(`/api/organizations`, data).then((response) => {
      console.log('Saved org:', response);
      // TODO: Show better error messages.
      // TODO: Tell user if organization name is already taken
      if (response.error) {
        showNotification('Organization request failed', response.message, { type: 'error' });
      } else {
        // showNotification('Organization request sent', response.message, { type: 'success' });
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
    console.log('Organization data:', data);
    // TODO: Save settings to /organizations/${orgId}/organization_settings
    authRequest(`/api/organizations/${orgId}`, data).then((response) => {
      if (response.success) {
        showNotification('Organization details saved', 'Organization details successfully saved.', { type: 'success' });
      } else {
        showNotification('Failed to save organization details', response.message, { type: 'error' });
      }
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

function initializeGetStartedOrganizationUI(data) {
  /*
   * Initialize the get-started organization section.
   */

  // Populate form.
  // const { elements } = document.querySelector('form')
  // for (const [ key, value ] of Object.entries(data)) {
  //   const field = elements.namedItem(key)
  //   try {
  //     field && (field.value = value);
  //   } catch(error) {}
  // }

  // Attach functionality.
  const fileElem = document.getElementById('selectPhotoUrl');
  fileElem.addEventListener('change', uploadOrgPhoto, false);

}


function addTeamMemberCard(gridId, data, owner, isOwner, orgId) {
  /*
   * Add a data card to an existing grid.
   * TODO: Render delete option if owner.
   */
  let badge = '';
  let options = '';
  let license = '';
  let phone = '';
  let position = '';
  if (data.license) license = `<div>License: ${data.license}</div>`;
  if (data.phone) phone = `<div>${data.phone}</div>`;
  if (data.position) position = `<div>${data.position}</div>`;
  if (owner) {
    badge = '<span class="badge rounded-pill bg-warning">Owner</span>';
  } else if (isOwner) {
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
  var div = document.getElementById(gridId);
  div.innerHTML += `
<div
  class="card shade-hover border-secondary rounded-3 app-action col col-sm-1 col-md-2 p-3 mb-3"
  style="width:275px; height:150px;"
>
<a class="card-block stretched-link text-decoration-none" href="/settings/organizations/${orgId}/team/${data.uid}">
  <div class="d-flex justify-content-between">
    <div class="d-flex align-items-center">
      <div class="icon-container me-2">
        <img src="${data.photo_url}" height="50px">
      </div>
      <h4 class="fs-5 text-dark">${data.name}</h4>
    </div>
    ${options}
  </div>
  <div class="card-body bg-transparent p-0">
    ${badge}
    <div class="col text-dark align-items-center">
      ${position}
      <div>${data.email}</div>
      ${phone}
      ${license}
    </div>
  </div>
</a>
</div>`;
}
