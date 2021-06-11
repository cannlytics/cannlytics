/**
 * Organizations JavaScript | Cannlytics Console
 * Author: Keegan Skeate
 * Created: 6/9/2021
 * Updated: 6/11/2021
 */

 export const organizations = {

  initialize() {
    /*
     * Initialize the organizations user interface.
     */
    console.log('Initializing organizations!')
  },


  getOrganizations() {
    /*
     * 
     */
  },


  updateOrganization() {
    /*
     * 
     */
  },


  createOrganization() {
    /*
     * 
     */
  },


  deleteOrganization() {
    /*
     * 
     */
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
        document.location.href = `/get-started/support/?from=${orgType}`;
      }
    });
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
