/**
 * Samples JavaScript | Cannlytics Console
 * Copyright (c) 2021-2022 Cannlytics
 * 
 * Authors: Keegan Skeate <keegan@cannlytics.com>
 * Created: 6/9/2021
 * Updated: 12/14/2021
 * License: MIT License <https://github.com/cannlytics/cannlytics-console/blob/main/LICENSE>
 */
import { authRequest, deserializeForm, serializeForm, showNotification } from '../utils.js';
import { theme } from '../settings/theme.js';

export const samples = {

  initialize() {
    /**
     * Initialize the samples user interface.
     */
  },

  async getSamples(orgId, licenseNumber, versionId = 'latest') {
    /**
    * Get samples.
    * @param {String} orgId
    * @param {String} licenseNumber
    * @param {String} versionId
    */

    // Get the data.
    // TODO: Add parameters
    const query = `license=${licenseNumber}&org_id=${orgId}&version_id=${versionId}`;
    const url = `/api/samples?${query}`;
    const response = await authRequest(url);
    const { data } = response;
    if (data) {
      document.getElementById('data-placeholder').classList.add('d-none');
      document.getElementById('data-table').classList.remove('d-none');
    }
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
  },

  async deleteSample(sampleId, orgId, licenseNumber, versionId = 'latest') {
    /**
    * Delete a sample.
    * @param {String} sampleId
    * @param {String} orgId
    * @param {String} licenseNumber
    * @param {String} versionId
    */
    const url = `/api/samples/${sampleId}`
    const filters = `?license=${licenseNumber}&org_id=${orgId}&version_id=${versionId}`;
    const response = await authRequest(url + filters, null, { delete: true });
    if (response.error) {
      showNotification('Deleting sample failed', response.message, /* type = */ 'error');
    } else {
      const message = "Sample deleted and removed from its project.";
      showNotification('Sample deleted', message, /* type = */ 'success');
    }
  },

  async saveSample() {
    /**
    * Create or update a sample.
    */
    const form = document.getElementById('sample-form');
    const data = serializeForm(form);
    const response = await authRequest(`/api/samples/${data.sample_id}`, data);
    if (response.error) {
      showNotification('Error saving sample', response.message, /* type = */ 'error');
    } else {
      showNotification('Sample saved', 'Sample data saved.', /* type = */ 'success');
    }
  },

  openSample(row) {
    /**
    * Navigate to a selected sample.
    * @param {Object} row A row object containing `data` with an `data.id`.
    */
    localStorage.setItem('sample', JSON.stringify(row.data));
    window.location.href = `/samples/sample?id=${row.data.id}`;
  },

  viewSample() {
    /**
    * Render a sample's data when navigating to a sample page.
    */
    const data = JSON.parse(localStorage.getItem('sample'));
    deserializeForm(document.forms['sample-form'], data);
  },

};
 