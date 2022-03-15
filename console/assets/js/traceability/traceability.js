/**
 * Traceability JavaScript | Cannlytics Console
 * Copyright (c) 2021-2022 Cannlytics
 * 
 * Authors: Keegan Skeate <keegan@cannlytics.com>
 * Created: 6/12/2021
 * Updated: 12/7/2021
 * License: MIT License <https://github.com/cannlytics/cannlytics-console/blob/main/LICENSE>
 */

import { authRequest, deserializeForm, showNotification } from '../utils.js';
import { theme } from '../settings/theme.js';

/*---------------------------------------------------------------------
 Employees
 --------------------------------------------------------------------*/

const employees = {

  getEmployees(tableId, orgId, licenseNumber, versionId) {
    /**
     * Get data from the API and in a table.
     * @param {String} tableId A table element ID for rendering data in the user interface.
     * @param {String} orgId A specific organization ID.
     * @param {String} licenseNumber The license number for the organization.
     * @param {String} versionId The secret version, the organization's state.
     */
    
    // Get the data.
    const query = `license=${licenseNumber}&org_id=${orgId}&version_id=${versionId}`;
    const url = `/api/traceability/employees?${query}`;
    authRequest(url).then((response) => {
      const { data } = response;
      if (data) {
        document.getElementById('data-placeholder').classList.add('d-none');
        document.getElementById('data-table').classList.remove('d-none');
      }
      console.log('Table data:', data);

      // Define the columns for the table.
      const columnDefs = [
        { field: 'full_name', headerName: 'Name', sortable: true, filter: true },
        { field: 'license.number', headerName: 'License', sortable: true, filter: true },
        { field: 'license.license_type', headerName: 'Type', sortable: true, filter: true },
        { field: 'license.start_date', headerName: 'Start Date', sortable: true, filter: true },
        { field: 'license.end_date', headerName: 'End Date', sortable: true, filter: true },
      ];

      // Specify the table options.
      const gridOptions = {
        columnDefs: columnDefs,
        pagination: true,
        paginationAutoPageSize: true,
        suppressRowClickSelection: false,
        onRowClicked: event => this.openObject('employee', event),
        onGridReady: event => theme.toggleTheme(theme.getTheme()),
      };

      // Render the table
      const eGridDiv = document.querySelector(`#${tableId}`);
      new agGrid.Grid(eGridDiv, gridOptions);
      gridOptions.api.setRowData(data);
    });
  },

};

/*---------------------------------------------------------------------
 Items
 --------------------------------------------------------------------*/

 const items = {

  getItems(tableId, orgId, licenseNumber, versionId) {
    /** Get data from the API and in a table.
     * @param {String} tableId A table element ID for rendering data in the user interface.
     * @param {String} orgId A specific organization ID.
     * @param {String} licenseNumber The license number for the organization.
     * @param {String} versionId The secret version, the organization's state.
     */

    // Get the data.
    const query = `license=${licenseNumber}&org_id=${orgId}&version_id=${versionId}`;
    const url = `/api/traceability/items?${query}`;
    authRequest(url).then((response) => {
      const { data } = response;
      if (data) {
        document.getElementById('data-placeholder').classList.add('d-none');
        document.getElementById('data-table').classList.remove('d-none');
      }
      console.log('Table data:', data);

      // Define the columns for the table.
      const columnDefs = [
        { field: 'id', headerName: 'ID', sortable: true, filter: true },
        { field: 'name', headerName: 'Name', sortable: true, filter: true },
        { field: 'product_category_type', headerName: 'Category', sortable: true, filter: true },
        { field: 'default_lab_testing_state', headerName: 'Testing Status', sortable: true, filter: true },
        { field: 'unit_weight', headerName: 'Weight', sortable: true, filter: true },
        { field: 'unit_weight_unit_of_measure_name', headerName: 'Units', sortable: true, filter: true },
      ];

      // Specify the table options.
      const gridOptions = {
        columnDefs: columnDefs,
        pagination: true,
        paginationAutoPageSize: true,
        suppressRowClickSelection: false,
        onRowClicked: event => this.openObject('item', event),
        onGridReady: event => theme.toggleTheme(theme.getTheme()),
      };

      // Render the table
      const eGridDiv = document.querySelector(`#${tableId}`);
      new agGrid.Grid(eGridDiv, gridOptions);
      gridOptions.api.setRowData(data);
    });
  },

  createItem() {
    /** Create a given location. */

  },

  updateItem() {
    /** Update a given location. */

  },

  deleteItem() {
    /** Delete a given location. */

  },

  saveItem() {
    /** Create or update a given location. */
  },

  exportItems() {
    /** Export locations data to Excel (.xlsx or .csv). */
  },

  importItems() {
    /** Import locations data from Excel (.xlsx or .csv). */
  },

};

/*---------------------------------------------------------------------
 Lab Tests
 --------------------------------------------------------------------*/

const labTests = {

  getLabTests(tableId, orgId, licenseNumber, versionId) {
    /**
     * Get data from the API and in a table.
     * @param {String} tableId A table element ID for rendering data in the user interface.
     * @param {String} orgId A specific organization ID.
     * @param {String} licenseNumber The license number for the organization.
     * @param {String} versionId The secret version, the organization's state.
     */
    const query = `license=${licenseNumber}&org_id=${orgId}&version_id=${versionId}`;
    const url = `/api/traceability/lab-tests?${query}`;
    authRequest(url).then((response) => {
      const { data } = response;
      if (data) {
        document.getElementById('data-placeholder').classList.add('d-none');
        document.getElementById('data-table').classList.remove('d-none');
      }
      console.log('Table data:', data);

      // Define the columns for the table.
      const columnDefs = [
        { field: 'lab_test_result_id', headerName: 'ID', sortable: true, filter: true },
        { field: 'result_release_date_time', headerName: 'Released At', sortable: true, filter: true },
        { field: 'test_performed_date', headerName: 'Test Date', sortable: true, filter: true },
        { field: 'test_type_name', headerName: 'Test', sortable: true, filter: true },
        { field: 'test_result_level', headerName: 'Result', sortable: true, filter: true },
        { field: 'overall_passed', headerName: 'Pass', sortable: true, filter: true },
        { field: 'test_comment', headerName: 'Notes', sortable: true, filter: true },
      ];

      // Specify the table options.
      const gridOptions = {
        columnDefs: columnDefs,
        pagination: true,
        paginationAutoPageSize: true,
        suppressRowClickSelection: false,
        onRowClicked: event => this.openObject('lab-test', event, 's', 'lab_test_result_id'),
        onGridReady: event => theme.toggleTheme(theme.getTheme()),
      };

      // Render the table
      const eGridDiv = document.querySelector(`#${tableId}`);
      new agGrid.Grid(eGridDiv, gridOptions);
      gridOptions.api.setRowData(data);
    });
  },

  createLabTest() {
    /** Create a given lab test. */

  },

  updateLabTest() {
    /** Update a given lab test. */

  },

  deleteLabTest() {
    /** Delete a given lab test. */

  },

  saveLabTest() {
    /** Create or update a given lab test. */
  },

  exportLabTests() {
    /** Export lab test data to Excel (.xlsx or .csv). */
  },

  importLabTests() {
    /** Import lab test data from Excel (.xlsx or .csv). */
  },

};

/*---------------------------------------------------------------------
 Locations
 --------------------------------------------------------------------*/

const locations = {

  getLocations(tableId, orgId, licenseNumber, versionId) {
    /**
     * Get data from the API and in a table.
     * @param {String} tableId A table element ID for rendering data in the user interface.
     * @param {String} orgId A specific organization ID.
     * @param {String} licenseNumber The license number for the organization.
     * @param {String} versionId The secret version, the organization's state.
     */
    const query = `license=${licenseNumber}&org_id=${orgId}&version_id=${versionId}`;
    const url = `/api/traceability/locations?${query}`;
    authRequest(url).then((response) => {
      const { data } = response;
      if (data) {
        document.getElementById('data-placeholder').classList.add('d-none');
        document.getElementById('data-table').classList.remove('d-none');
      }
      console.log('Table data:', data);

      // Create column of permissions.
      data.forEach((row) => {
        row.permissions = [];
      });
      for (var i in data) {
        data[i].permissions = [];
        if (data[i].for_harvests) data[i].permissions.push('Harvests');
        if (data[i].for_packages) data[i].permissions.push('Packages');
        if (data[i].for_plant_batches) data[i].permissions.push('Batches');
        if (data[i].for_plants) data[i].permissions.push('Plants');
      }

      // Define the columns for the table.
      const columnDefs = [
        { field: 'id', headerName: 'ID', sortable: true, filter: true },
        { field: 'name', headerName: 'Name', sortable: true, filter: true },
        { field: 'location_type_name', headerName: 'Type', sortable: true, filter: true },
        { field: 'location_type_id', headerName: 'Type ID', sortable: true, filter: true },
        { field: 'permissions', headerName: 'Permissions', sortable: true, filter: true },
      ];

      // Specify the table options.
      const gridOptions = {
        columnDefs: columnDefs,
        pagination: true,
        paginationAutoPageSize: true,
        suppressRowClickSelection: false,
        onRowClicked: event => this.openObject('location', event),
        onGridReady: event => theme.toggleTheme(theme.getTheme()),
      };

      // Render the table
      const eGridDiv = document.querySelector(`#${tableId}`);
      new agGrid.Grid(eGridDiv, gridOptions);
      gridOptions.api.setRowData(data);
    });
  },

  createLocation() {
    /** Create a given location. */

  },

  updateLocation() {
    /** Update a given location. */

  },

  deleteLocation() {
    /** Delete a given location. */

  },

  saveLocation() {
    /** Create or update a given location. */
  },

  exportLocations() {
    /** Export locations data to Excel (.xlsx or .csv). */
  },

  importLocations() {
    /** Import locations data from Excel (.xlsx or .csv). */
  },

};

/*---------------------------------------------------------------------
 Packages
 --------------------------------------------------------------------*/

 const packages = {

  getPackages(tableId, orgId, licenseNumber, versionId) {
    /**
     * Get data from the API and in a table.
     * @param {String} tableId A table element ID for rendering data in the user interface.
     * @param {String} orgId A specific organization ID.
     * @param {String} licenseNumber The license number for the organization.
     * @param {String} versionId The secret version, the organization's state.
     */
    const query = `license=${licenseNumber}&org_id=${orgId}&version_id=${versionId}`;
    const url = `/api/traceability/packages?${query}`;
    authRequest(url).then((response) => {
      const { data } = response;
      if (data) {
        document.getElementById('data-placeholder').classList.add('d-none');
        document.getElementById('data-table').classList.remove('d-none');
      }
      console.log('Table data:', data);

      // Define the columns for the table.
      const columnDefs = [
        { field: 'id', headerName: 'ID', sortable: true, filter: true },
        // { field: 'name', headerName: 'Name', sortable: true, filter: true },
        // { field: 'product_category_type', headerName: 'Category', sortable: true, filter: true },
        // { field: 'default_lab_testing_state', headerName: 'Testing Status', sortable: true, filter: true },
        // { field: 'unit_weight', headerName: 'Weight', sortable: true, filter: true },
        // { field: 'unit_weight_unit_of_measure_name', headerName: 'Units', sortable: true, filter: true },
      ];

      // Specify the table options.
      const gridOptions = {
        columnDefs: columnDefs,
        pagination: true,
        paginationAutoPageSize: true,
        suppressRowClickSelection: false,
        onRowClicked: event => this.openObject('package', event),
        onGridReady: event => theme.toggleTheme(theme.getTheme()),
      };

      // Render the table
      const eGridDiv = document.querySelector(`#${tableId}`);
      new agGrid.Grid(eGridDiv, gridOptions);
      gridOptions.api.setRowData(data);
    });
  },

  createPackage() {
    /** Create a given location. */

  },

  updatePackage() {
    /** Update a given location. */

  },

  deletePackage() {
    /** Delete a given location. */

  },

  savePackage() {
    /** Create or update a given location. */
  },

  exportPackages() {
    /** Export locations data to Excel (.xlsx or .csv). */
  },

  importPackages() {
    /** Import locations data from Excel (.xlsx or .csv). */
  },

};

/*---------------------------------------------------------------------
 Strains
 --------------------------------------------------------------------*/

const strains = {

  getStrains(tableId, orgId, licenseNumber, versionId) {
    /**
     * Get data from the API and in a table.
     * @param {String} tableId A table element ID for rendering data in the user interface.
     * @param {String} orgId A specific organization ID.
     * @param {String} licenseNumber The license number for the organization.
     * @param {String} versionId The secret version, the organization's state.
     */
    const query = `license=${licenseNumber}&org_id=${orgId}&version_id=${versionId}`;
    const url = `/api/traceability/strains?${query}`;
    authRequest(url).then((response) => {
      const { data } = response;
      if (data) {
        document.getElementById('data-placeholder').classList.add('d-none');
        document.getElementById('data-table').classList.remove('d-none');
      }
      console.log('Table data:', data);

      // Define the columns for the table.
      const columnDefs = [
        { field: 'id', headerName: 'ID', sortable: true, filter: true },
        { field: 'name', headerName: 'Name', sortable: true, filter: true },
        { field: 'genetics', headerName: 'Genetics', sortable: true, filter: true },
        { field: 'indica_percentage', headerName: 'Indica Percent', sortable: true, filter: true },
        { field: 'sativa_percentage', headerName: 'Sativa Percent', sortable: true, filter: true },
        { field: 'testing_status', headerName: 'Testing Status', sortable: true, filter: true },
        { field: 'thc_level', headerName: 'THC Level', sortable: true, filter: true },
        { field: 'is_used', headerName: 'In Use', sortable: true, filter: true },
      ];

      // Specify the table options.
      const gridOptions = {
        columnDefs: columnDefs,
        pagination: true,
        paginationAutoPageSize: true,
        suppressRowClickSelection: false,
        onRowClicked: event => this.openObject('strain', event),
        onGridReady: event => theme.toggleTheme(theme.getTheme()),
      };

      // Render the table
      const eGridDiv = document.querySelector(`#${tableId}`);
      new agGrid.Grid(eGridDiv, gridOptions);
      gridOptions.api.setRowData(data);
    });
  },

  createStrain() {
    /** Create a given strain. */

  },

  updateStrain() {
    /** Update a given strain. */

  },

  deleteStrain() {
    /** Delete a given strain. */

  },

  saveStrain() {
    /** Create or update a given strain. */
  },

  exportStrains() {
    /** Export strain data to Excel (.xlsx or .csv). */
  },

  importStrains() {
    /** Import strain data from Excel (.xlsx or .csv). */
  },

};

/*---------------------------------------------------------------------
 Transfers
 --------------------------------------------------------------------*/

const transfers = {

  getTransfers(tableId, orgId, licenseNumber, versionId) {
    /**
     * Get data from the API and in a table.
     * @param {String} tableId A table element ID for rendering data in the user interface.
     * @param {String} orgId A specific organization ID.
     * @param {String} licenseNumber The license number for the organization.
     * @param {String} versionId The secret version, the organization's state.
     */
    const query = `license=${licenseNumber}&org_id=${orgId}&version_id=${versionId}`;
    const url = `/api/traceability/transfers?${query}`;
    authRequest(url).then((response) => {
      const { data } = response;
      if (data) {
        document.getElementById('data-placeholder').classList.add('d-none');
        document.getElementById('data-table').classList.remove('d-none');
      }
      console.log('Table data:', data);

      // Define the columns for the table.
      const columnDefs = [
        { field: 'id', headerName: 'ID', sortable: true, filter: true },
        // { field: 'name', headerName: 'Name', sortable: true, filter: true },
        // { field: 'product_category_type', headerName: 'Category', sortable: true, filter: true },
        // { field: 'default_lab_testing_state', headerName: 'Testing Status', sortable: true, filter: true },
        // { field: 'unit_weight', headerName: 'Weight', sortable: true, filter: true },
        // { field: 'unit_weight_unit_of_measure_name', headerName: 'Units', sortable: true, filter: true },
      ];

      // Specify the table options.
      const gridOptions = {
        columnDefs: columnDefs,
        pagination: true,
        paginationAutoPageSize: true,
        suppressRowClickSelection: false,
        onRowClicked: event => this.openObject('transfer', event),
        onGridReady: event => theme.toggleTheme(theme.getTheme()),
      };

      // Render the table
      const eGridDiv = document.querySelector(`#${tableId}`);
      new agGrid.Grid(eGridDiv, gridOptions);
      gridOptions.api.setRowData(data);
    });
  },

  createTransfer() {
    /** Create a given location. */

  },

  updateTransfer() {
    /** Update a given location. */

  },

  deleteTransfer() {
    /** Delete a given location. */

  },

  saveTransfer() {
    /** Create or update a given location. */
  },

  exportTransfers() {
    /** Export locations data to Excel (.xlsx or .csv). */
  },

  importTransfers() {
    /** Import locations data from Excel (.xlsx or .csv). */
  },

};

/*---------------------------------------------------------------------
 Main object
 --------------------------------------------------------------------*/

export const traceability = {

  ...employees,
  ...items,
  ...labTests,
  ...locations,
  ...packages,
  ...strains,
  ...transfers,

  openObject(type, row, plural = 's', id_field='id') {
    /**
     * View a selected object.
     * @param {String} type The type of data model.
     * @param {Object} row A table row object.
     * @param {String} plural The plural of the data model.
     * @param {String} id_field The ID of an object.
     */
    const url = `/traceability/${type}${plural}/${type}?id=${row.data[id_field]}`;
    localStorage.setItem(type, JSON.stringify(row.data));
    window.location.href = url;
  },


  viewObject(type) {
    /**
     * View the data when navigating to a selected object.
     * @param {string} type The type of data being displayed.
     */
    const data = JSON.parse(localStorage.getItem(type));
    deserializeForm(document.forms[`${type}-form`], data)
    console.log('Observation data:', data);
  },


  deleteLicenseValidation(orgId, licenseNumber) {
    /**
     * Validate that a reason is present before deleting a license.
     * @param {String} orgId A specific organization ID.
     * @param {String} licenseNumber The license number for the organization.
     */
    const deletionReason = document.getElementById('license-deletion-reason-input').value;
    if (!deletionReason) {
      const message = 'A deletion reason is required for quality control.'
      showNotification('Deletion reason required', message, /* type = */ 'error');
      return;
    }
    deleteLicense(orgId, licenseNumber, deletionReason);
  },


  deleteLicense(orgId, licenseNumber, message) {
    /**
     * Delete a license from an organization's data, saving a deletion reason.
     * @param {String} orgId A specific organization ID.
     * @param {String} licenseNumber The license number for the organization.
     * @param {String} message The reason for deleting a specific license.
     */
    const url = `/api/traceability/delete-license?license=${licenseNumber}&org_id=${orgId}`;
    authRequest(url, {deletion_reason: message}).then((response) => {
      if (response.error) {
        // Optional: Show better error messages.
        showNotification('Deleting license failed', response.message, /* type = */ 'error');
      } else {
        window.location.href = '/traceability/settings';
        // Optional: Show success message
      }
    });
  },


  saveLicenses(orgId) {
    /**
     * Save an organization's licenses.
     * @param {String} orgId A specific organization ID.
     */

    // Get the licenses data.
    // Optional: Split license data rows more elegantly.
    const elements = document.getElementById('licenses-form').elements;
    const licenses = [];
    let data = {};
    for (let i = 0 ; i < elements.length ; i++) {
      const item = elements.item(i);
      if (item.name) data[item.name] = item.value;
      if (item.name === 'user_api_key') {
        licenses.push(data);
        data = {};
      }
    }

    // Post the data.
    // FIXME: Handle updating licenses.
    authRequest(`/api/organizations/${orgId}`, {'licenses': licenses}).then((response) => {
      console.log('Saved licenses:', response);
      // TODO: Show better error messages.
      // TODO: Tell user if organization name is already taken
      if (response.error) {
        showNotification('Organization request failed', response.message, /* type = */ 'error');
      } else {
        // showNotification('Organization request sent', response.message, /* type = */ 'success');
        // TODO: Re-render licenses.
        location.reload();
      }
    });

  },

};
