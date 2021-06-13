/**
 * Traceability JavaScript | Cannlytics Console
 * Author: Keegan Skeate
 * Created: 6/12/2021
 * Updated: 6/13/2021
 */

import { authRequest, showNotification } from '../utils.js';
import { theme } from '../settings/theme.js';

export const traceability = {

  initialize() {
    console.log('Initializing traceability...');
  },


  getEmployees(tableId) {
    /*
     * Get employees from the Metrc API, through the Cannlytics API,
     * and render the data in a table.
     */
    
    // Define the columns for the table.
    const columnDefs = [
      { field: 'FullName', sortable: true, filter: true },
      { field: 'License', sortable: true, filter: true },
    ];

    // Specify the table options.
    const gridOptions = {
      columnDefs: columnDefs,
      pagination: true,
      // rowSelection: 'multiple',
      suppressRowClickSelection: false,
      // singleClickEdit: true,
      // onRowClicked: event => console.log('A row was clicked'),
      onGridReady: event => theme.toggleTheme(theme.getTheme()),
    };

    // Get the data.
    authRequest(`/api/traceability/employees`).then((data) => {
      console.log('Table data:', data); // DEV:
      const eGridDiv = document.querySelector(`#${tableId}`);
      new agGrid.Grid(eGridDiv, gridOptions);
      gridOptions.api.setRowData(data);
    });

    // TODO: Attach export functionality
    //function exportTableData() {
    //  gridOptions.api.exportDataAsCsv();
    //}

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
