/**
 * Data Tables JavaScript | Cannlytics Website
 * Copyright (c) 2021-2022 Cannlytics
 * 
 * Authors: Keegan Skeate <https://github.com/keeganskeate>
 * Created: 12/7/2020
 * Updated: 7/20/2022
 * License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>
 */
import {
  deleteDocument,
  deleteFile,
  getDocument,
  getFileURL,
  getUserToken,
  listenToCollection,
  onAuthChange,
  setDocument,
  uploadFile,
} from '../firebase.js';
import {
  authRequest,
  formatBytes,
  getCookie,
  serializeForm,
  setURLParameter,
  showNotification,
} from '../utils.js';
import { theme } from '../ui/theme.js';

export const dataTables = {

  limit: 1000,
  hidden: true,
  minWidth: 175,
  gridOptions: {},
  rowHeight: 25,
  selectGridOptions: {},

  changeLimit(event) {
    /**
     * Change the limit for streamData.
     * @param {Event} event A user-driven event.
     */
    this.limit = event.target.value;
  },

  async exportData(modelSingular, id = null) {
    /**
     * Export given collection data to Excel.
     * Optional: Also export any sub-model data table.
     * @param {String} modelSingular The name of a singular observation.
     * @param {String} id An ID for the data export.
     */
    const data = serializeForm(`${modelSingular}-form`);
    const idToken = await getUserToken();
    const csrftoken = getCookie('csrftoken');
    const headerAuth = new Headers({
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${idToken}`,
      'X-CSRFToken': csrftoken,
    });
    const init = {
      headers: headerAuth,
      method: 'POST',
      body: JSON.stringify({ data: [data] }),
    };
    const fileName = (id) ? id : modelSingular;
    const response = await fetch(window.location.origin + '/src/data/download', init);
    const blob = await response.blob();
    const url = window.URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.style = 'display: none';
    link.setAttribute('download', fileName + '.csv');
    document.body.appendChild(link);
    link.click();
    link.parentNode.removeChild(link);
    window.URL.revokeObjectURL(blob);
  },

  exportDataTable(model) {
    /**
     * Export a data table as a CSV file.
     * @param {String} model The name of a given data model.
     */
    this.gridOptions.api.exportDataAsCsv({
      fileName: `${model}.csv`,
    });
  },

  renderPlaceholder() {
    /**
     * Render a no-data placeholder in the user interface.
     */
    try {
      document.getElementById('simple-table-options').classList.add('d-none');

    } catch(error) {}
    try {
      document.getElementById('loading-placeholder').classList.add('d-none');

    } catch(error) {}
    try {
      document.getElementById('data-table').classList.add('d-none');

    } catch(error) {}
    try {
      document.getElementById('data-placeholder').classList.remove('d-none');
    } catch(error) {}
    this.tableHidden = true;
  },

  renderTable(model, modelSingular, data, dataModel, editable=false) {
    /**
     * Render a data table in the user interface.
     * @param {String} model The name of a given data model.
     * @param {String} modelSingular A given data model.
     * @param {Array} data An array of observations to render in the table.
     * @param {Object} dataModel Information about a data model.
     * @param {Boolean} editable Whether or not the table can be edited,
     * `false` by default.
     */

    // Render the table if it's the first time that it's shown.
    if (this.tableHidden) {

      // Hide the placeholder and show the table.
      document.getElementById('loading-placeholder').classList.add('d-none');
      document.getElementById('data-placeholder').classList.add('d-none');
      document.getElementById('simple-table-options').classList.remove('d-none');
      document.getElementById('data-table').classList.remove('d-none');
  
      // Get data model fields from organization settings.
      const columnDefs = dataModel.fields.map(function(e) { 
        return { headerName: e.label, field: e.key, sortable: true, filter: true };
      });

      // Enable checkbox selection?
      if (editable) {
        columnDefs[0]['checkboxSelection'] = true;
        columnDefs[0]['headerCheckboxSelection'] = true;
      }

      // Render templates.
      const overlayLoadingTemplate = `
        <div class="spinner-grow text-success" role="status">
          <span class="visually-hidden">Loading...</span>
        </div>
      `;
      const overlayNoRowsTemplate = ``;
      // const overlayNoRowsTemplate = `
      //   <div class="card-body bg-transparent text-center" style="max-width:320px;">
      //     <img
      //       src="/static/${dataModel.image_path}"
      //       style="width:75px;"
      //     >
      //     <h2 class="fs-5 text-dark mt-3 mb-1">
      //       Add ${dataModel.key}
      //     </h2>
      //     <p class="text-secondary fs-6 text-small">
      //       <small>${dataModel.description}</small>
      //     </p>
      //   </div>
      // `;
  
      // Specify the table options.
      this.gridOptions = {
        columnDefs: columnDefs,
        defaultColDef: { flex: 1,  minWidth: this.minWidth, editable },
        enterMovesDownAfterEdit: editable,
        singleClickEdit: editable,
        suppressRowClickSelection: editable,
        overlayLoadingTemplate: overlayLoadingTemplate,
        overlayNoRowsTemplate: overlayNoRowsTemplate,
        pagination: true,
        paginationAutoPageSize: true,
        rowClass: 'app-action',
        rowHeight: this.rowHeight,
        rowSelection: 'multiple',
        onGridReady: event => theme.toggleTheme(theme.getTheme()),
      };

      var onSelectionChanged = this.onSelectionChanged;

      if (!editable) this.gridOptions.onRowClicked = (event) => navigationHelpers.openObject(model, modelSingular, event.data);
      else this.gridOptions.onSelectionChanged = onSelectionChanged;

      // Render the table
      const eGridDiv = document.querySelector(`#${model}-table`);
      eGridDiv.innerHTML = '';
      new agGrid.Grid(eGridDiv, this.gridOptions);
      this.gridOptions.api.setRowData(data);

    } else {

      // Update the table's data.
      this.gridOptions.api.setRowData(data);

    }

  },

  async addTableRow(model, modelSingular, orgId, abbreviation) {
    /**
     * Add a new, editable row to a data table.
     * @param {String} model The name of a given data model.
     * @param {String} modelSingular A given data model.
     * @param {String} orgId The ID for a specific organization.
     * @param {String} abbreviation The abbreviation for the data model.
     */
    let count = 1;
    const rows = [];
    const newRow = {};
    const columns = this.gridOptions.columnApi.getAllColumns();
    const keys = columns.map(a => a.colId);
    keys.forEach((key) => newRow[key] = null)
    await this.gridOptions.api.forEachNode((rowNode, index) => {
      rows.push(rowNode.data);
      count += 1;
    })
    newRow[`${modelSingular}_id`] = await this.createID(model, modelSingular, orgId, abbreviation, count);
    rows.push(newRow);
    this.gridOptions.api.setRowData(rows);
    document.getElementById(`${modelSingular}-save-table-button`).classList.remove('d-none');
  },

  async deleteTableRows(
    model,
    modelSingular,
    orgId,
    parentModelSingular = '',
    removeOnly = false,
  ) {
    /**
     * Delete a row or rows from an editable data table,
     * trying to remove the data from Firestore if removeOnly is false,
     * which it is by default.
     * @param {String} model The name of a given data model.
     * @param {String} modelSingular A given data model.
     * @param {String} orgId The ID for a specific organization.
     * @param {String} parentModelSingular The singular name of any parent data model.
     * @param {Boolean} removeOnly Whether to clear the table row instead of deleting.
     */
    const rows = [];
    const idKey = `${modelSingular}_id`;
    const parentKey = `${parentModelSingular}_id`;
    const rowsToDelete = this.gridOptions.api.getSelectedRows();
    const idsToDelete = rowsToDelete.map(a => a[idKey]);
    const postData = [];
    idsToDelete.forEach((id) => {
      const entry = {};
      entry[idKey] = id;
      entry[parentKey] = '';
      postData.push(entry);
    });
    try {
      if (removeOnly) {
        await authRequest(`/api/${model}?organization_id=${orgId}`, postData);
      } else {
        await authRequest(`/api/${model}?organization_id=${orgId}`, postData, { delete: true });
      }
    } catch (error) { /* Entries may not exist in the database yet. */ }
    await this.gridOptions.api.forEachNode((rowNode, index) => {
      if (!idsToDelete.includes(rowNode.data[idKey])) {
        rows.push(rowNode.data);
      }
    });
    this.gridOptions.api.setRowData(rows);
    document.getElementById(`${modelSingular}-delete-table-button`).classList.add('d-none');
  },

  async selectTableRows() {
    /**
     * Select pre-existing entries for the table.
     */
    const rows = [];
    const selected = this.selectGridOptions.api.getSelectedRows();
    await this.gridOptions.api.forEachNode((rowNode, index) => rows.push(rowNode.data));
    const data = [...rows, ...selected];
    this.gridOptions.api.setRowData(data);
    if (data.length) {
      const elementId = `${modelSingular}-save-table-button`;
      document.getElementById(elementId).classList.remove('d-none');
    }
  },

  onSelectionChanged(event) {
    /**
     * Show options that are only available when table rows are selected.
     * @param {Event} event A user-driven event.
     */
    const selectOnly = document.getElementsByClassName('select-only-option');
    const rowCount = event.api.getSelectedNodes().length;
    for (let i = 0; i < selectOnly.length; i++) {
      const item = selectOnly.item(i);
      if (rowCount > 0) item.classList.remove('d-none');
      else item.classList.add('d-none');
    }
  },

  // Future work: Add `searchData` from console?

};
