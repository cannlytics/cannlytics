/**
 * Traceability JavaScript | Cannlytics Console
 * Author: Keegan Skeate
 * Created: 6/12/2021
 * Updated: 6/12/2021
 */

export const traceability = {

  initialize() {
    console.log('Initializing traceability...');
  },


  saveLicenses() {
    /*
     * Save an organization's licenses.
     */
    console.log('TODO: Save licenses!');

    // Get the licenses data.
    const elements = document.getElementById('licenses-form').elements;
    const licenses = [];
    let data = {};
    for (let i = 0 ; i < elements.length ; i++) {
      const item = elements.item(i);
      if (item.name) {
        console.log(item.name, item.value);
        data[item.name] = item.value;
      }
      // Split license data rows.
      // Optional: More elegantly split license data.
      if (item.name === 'user_api_key') {
        licenses.push(data);
        data = {};
      }
    }
    console.log('Data', licenses);

    // Post the data.
    authRequest(`/api/organizations`, {'licenses': licenses}).then((response) => {
      console.log('Saved licenses:', response);
      // TODO: Show better error messages.
      // TODO: Tell user if organization name is already taken
      if (response.error) {
        showNotification('Organization request failed', response.message, { type: 'error' });
      } else {
        // showNotification('Organization request sent', response.message, { type: 'success' });
        // TODO: Re-render licenses.
        location.reload();
      }
    });
  },

}
