/**
 * Samples JavaScript | Cannlytics Console
 * Author: Keegan Skeate
 * Created: 6/9/2021
 * Updated: 6/18/2021
 */

import { authRequest, formDeserialize, formSerialize, showNotification } from '../utils.js';
import { theme } from '../settings/theme.js';
 
 
export const samples = {
 
 
  initialize() {
    console.log('Initializing samples!')
  },
 
 
  getSamples(orgId, licenseNumber, versionId = '1') {
    /*
    * Get samples.
    */

    // Get the data.
    // TODO: Add parameters
    const query = `license=${licenseNumber}&org_id=${orgId}&version_id=${versionId}`;
    const url = `/api/samples?${query}`;
    authRequest(url).then((response) => {
      const { data } = response;
      if (data) {
        document.getElementById('data-placeholder').classList.add('d-none');
        document.getElementById('data-table').classList.remove('d-none');
      }
      console.log('Table data:', data);

      // TODO: Define the columns for the table.
      const columnDefs = [
        { field: 'sample_id', headerName: 'Sample ID', sortable: true, filter: true },
      ];

      // Specify the table options.
      const gridOptions = {
        columnDefs: columnDefs,
        pagination: true,
        paginationAutoPageSize: true,
        suppressRowClickSelection: false,
        onRowClicked: event => this.openProject(event),
        onGridReady: event => theme.toggleTheme(theme.getTheme()),
      };

      // Render the table
      const eGridDiv = document.querySelector(`#${tableId}`);
      new agGrid.Grid(eGridDiv, gridOptions);
      gridOptions.api.setRowData(data);
    });

  },


  deleteSample(sampleId, orgId, licenseNumber, versionId = '1') {
    /*
    * Delete a sample.
    */
    const url = `/api/samples/${sampleId}`
    const filters = `?license=${licenseNumber}&org_id=${orgId}&version_id=${versionId}`;
    authRequest(url + filters, null, { delete: true }).then((response) => {
      if (response.error) {
        showNotification('Deleting sample failed', response.message, { type: 'error' });
      } else {
        const message = "Sample deleted and removed from its project.";
        showNotification('Sample deleted', message, { type: 'success' });
      }
    });
  },


  saveSample() {
    /*
    * Create or update a sample.
    */
    const form = document.getElementById('sample-form');
    const data = formSerialize(form);
    authRequest(`/api/samples/${data.sample_id}`, data).then((response) => {
      if (response.error) {
        showNotification('Error saving sample', response.message, { type: 'error' });
      } else {
        showNotification('Sample saved', 'Sample data saved.', { type: 'success' });
      }
    });
  },


  openSample(row) {
    /*
    * Navigate to a selected sample.
    */
    localStorage.setItem('sample', JSON.stringify(row.data));
    window.location.href = `/samples/sample?id=${row.data.id}`;
  },


  viewSample() {
    /*
    * Render a sample's data when navigating to a sample page.
    */
    const data = JSON.parse(localStorage.getItem('sample'));
    formDeserialize(document.forms['sample-form'], data);
  },


};
 