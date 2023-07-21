/**
 * App JavaScript | Cannlytics Console
 * Copyright (c) 2021-2022 Cannlytics
 * 
 * Authors: Keegan Skeate <https://github.com/keeganskeate>
 * Created: 12/7/2020
 * Updated: 1/13/2022
 * License: MIT License <https://github.com/cannlytics/cannlytics-console/blob/main/LICENSE>
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
import { navigationHelpers } from '../ui/ui.js';
import { theme } from '../settings/theme.js';

export const dataTables = {

  dataModel: {},
  limit: 1000,
  logLimit: 1000,
  fileLimit: 1000,
  tableHidden: true,
  gridOptions: {},
  selectGridOptions: {},

  changeLimit(event) {
    /**
     * Change the limit for streamData.
     * @param {Event} event A user-driven event.
     */
    this.limit = event.target.value;
  },

  // Optional: Pass data model directly
  async downloadWorksheet(orgId, model) {
    /**
     * Download a worksheet to facilitate importing data.
     * @param {String} orgId The ID for a specific organization.
     * @param {String} model The name of a given data model.
     */
    if (!this.dataModel.worksheet_url) {
      this.dataModel = await getDocument(`organizations/${orgId}/data_models/${model}`);
    }
    const response = await fetch(this.dataModel.worksheet_url);
    const blob = await response.blob();
    const url = window.URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.style = 'display: none';
    link.setAttribute('download', `${model}_worksheet.xlsm`);
    document.body.appendChild(link);
    link.click();
    link.parentNode.removeChild(link);
    window.URL.revokeObjectURL(blob);
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
  
      // Specify the table options.
      this.gridOptions = {
        columnDefs: columnDefs,
        defaultColDef: { flex: 1,  minWidth: 175, editable },
        enterMovesDownAfterEdit: editable,
        singleClickEdit: editable,
        suppressRowClickSelection: editable,
        pagination: true,
        paginationAutoPageSize: true,
        rowClass: 'app-action',
        rowHeight: 25,
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

  searchData(model, modelSingular) {
    /**
     * Search a data model.
     * @param {String} model The name of a given data model.
     * @param {String} modelSingular A given data model.
     */
    const path = `organizations/${orgId}/${model}`;
    const params = {};
    if (this.limit) params.max = this.limit;
    if (orderBy && desc) {
      params.desc = true;
      params.order = orderBy;
    } else if (orderBy) {
      params.order = orderBy;
    }
    listenToCollection(path, params, (querySnapshot) => {
      const data = [];
      querySnapshot.forEach((doc) => {
        data.push(doc.data());
      });
      if (data.length) this.renderTable(model, modelSingular, data, this.dataModel);
      else this.renderPlaceholder();
    });
  },

  searchTable(model, modelSingular, orgId) {
    /**
     * A general search of a data model table.
     * @param {String} model The name of a given data model.
     * @param {String} modelSingular A given data model.
     * @param {String} orgId The ID for a specific organization.
     */
    // TODO: Iterate over data model fields, query for a match, break if any
    // documents are found. Prefer to iterate over data model fields in a logical
    // manner. For example, if the search contains an abbreviation, then we may know
    // that it is an ID, etc.
    // TODO: Implement search....
    this.dataModel.fields.forEach((field) => {
      // TODO: Render results....
    })
    // TODO: Show clear search button.
    document.getElementById('clear-button').classList.remove('d-none');
  },

  clearSearch(model, modelSingular, orgId) {
    /**
     * Reset the table after performing a search.
     * @param {String} model The name of a given data model.
     * @param {String} modelSingular A given data model.
     * @param {String} orgId The ID for a specific organization.
     */
    document.getElementById('clear-button').classList.add('d-none');
    document.getElementById('searchInput').value = '';
    this.streamData(model, modelSingular, orgId);
  },

  awaitStreamData(model, modelSingular, orgId, limit = null, editable = false) {
    /**
     * Wait to stream data until a user is detected.
     * @param {String} model The name of a given data model.
     * @param {String} modelSingular A given data model.
     * @param {String} orgId The ID for a specific organization.
     * @param {Number} limit A limit for the number of observations to stream.
     * @param {Boolean} editable Whether or not the data can be edited from the 
     * user interface.
     */
     onAuthChange((user) => {
      if (user) this.streamData(model, modelSingular, orgId, limit=limit, editable=editable)
    });
  },

  async streamData(model, modelSingular, orgId, limit = null, editable = false) {
    /**
     * Stream data, listening for any changes. Search by date range (by updated_at)
     * by first. If no observations are found, then search with a limit and set
     * the start_date to the earliest updated_at time, if any observations were found.
     * @param {String} model The name of a given data model.
     * @param {String} modelSingular A given data model.
     * @param {String} orgId The ID for a specific organization.
     * @param {Number} limit A limit for the number of observations to stream.
     * @param {Boolean} editable Whether or not the data can be edited from the 
     * user interface.
     */
    // Optional: Get parameters (desc, orderBy) from the user interface.
    // Optional: Implement search with filters, e.g. .where("state", "==", "OK")
    // Optional: Pass dataModel from template.
    const collectionPath = `organizations/${orgId}/${model}`;
    const dataModelsPath = `organizations/${orgId}/data_models/${model}`;
    this.dataModel = await getDocument(dataModelsPath);
    console.log('Data model:', this.dataModel)
    let params = {};
    if (!limit) {
      let startDate = new Date(new Date().setDate(new Date().getDate() - 1)).toISOString().slice(0, 10);
      let endDate = new Date().toISOString().slice(0, 10);
      try {
        startDate = document.getElementById('time_start').value;
        endDate = document.getElementById('time_end').value;
      } catch (error) {
        // FIXME: Unknown error
      }
      const filters = [
        { key: 'updated_at', operation: '>=', value: startDate },
        { key: 'updated_at', operation: '<=', value: `${endDate}T23:59:59` },
      ];
      params = { desc: true, order: 'updated_at', filters }
    } else {
      params = { desc: true, max: limit, order: 'updated_at' };
    }
    listenToCollection(collectionPath, params, (querySnapshot) => {
        const data = [];
        let earliest = '';
        querySnapshot.forEach((doc) => {
          const item = doc.data();
          if (!earliest || item.updated_at < earliest) earliest = item.updated_at;
          data.push(item);
        });
        if (data.length) {
          this.renderTable(model, modelSingular, data, this.dataModel, editable);
          try {
            document.getElementById('time_start').value = earliest.slice(0, 10);
          } catch (error) { /* Date input likely hidden. */ }
        }
        else if (!limit) this.streamData(model, modelSingular, orgId, 100, editable);
        else this.renderPlaceholder();
      }
    );
  },

  async streamLogs(
    model,
    modelId,
    orgId,
    filterBy = 'key',
    orderBy = 'created_at',
    start = '',
    end = '',
    period = 7
  ) {
    /**
     * Stream logs, listening for any changes.
     * @param {String} model The name of a given data model.
     * @param {String} modelSingular A given data model.
     * @param {String} orgId The ID for a specific organization.
     * @param {String} filterBy The key at which to filter the log search, `key` by default.
     * @param {String} orderBy The key at which to order the log search, `created_at` by default.
     * @param {String} start The time, in ISO format, to begin log retrieval.
     * @param {String} end The time, in ISO format, to end log retrieval.
     * @param {Number} period If no `start`, use `period` to determine the number
     * of days of logs to retrieve.
     */
    if (!start) start = new Date(new Date().setDate(new Date().getDate()-period)).toISOString().substring(0, 10);
    if (!end) {
      end = new Date()
      end.setUTCHours(23, 59, 59, 999);
      end = end.toISOString();
    }
    const dataModelPath = `organizations/${orgId}/data_models/logs`;
    const dataModel = await getDocument(dataModelPath);
    dataModel.fields = dataModel.fields.filter(function(obj) {
      return !(['log_id', 'changes', 'user'].includes(obj.key));
    });
    const collectionPath = `organizations/${orgId}/logs`;
    const filters = [
      { key: filterBy, operation: '==', value: modelId },
      { key: orderBy, operation: '>=', value: start },
      { key: orderBy, operation: '<=', value: end },
    ];
    const params = {
      desc: true,
      filters,
      max: this.logLimit,
      order: orderBy,
    };
    listenToCollection(collectionPath, params, (querySnapshot) => {
      const data = [];
      querySnapshot.forEach((doc) => {
        const values = doc.data();
        values.changes = JSON.stringify(values.changes);
        // Optional: Split up date and time before filling into the form.
        data.push(values);
      });
      if (data.length) this.renderTable(`${model}-logs`, 'log', data, dataModel);
      else this.renderPlaceholder();
    });
  },

  startEdit(model, modelSingular, orgId, limit = null) {
    /**
     * Start editing a data table.
     * @param {String} model The name of a given data model.
     * @param {String} modelSingular A given data model.
     * @param {String} orgId The ID for a specific organization.
     * @param {Number} limit The limit for any data being streamed in the edit.
     */
    this.streamData(model, modelSingular, orgId, limit, true);
    const newButton = document.getElementById('new-button');
    if (newButton) newButton.classList.add('d-none');
    document.getElementById('import-form').classList.add('d-none');
    document.getElementById('import_options').classList.add('d-none');
    document.getElementById('export-table-button').classList.add('d-none');
    document.getElementById('edit-table-button').classList.add('d-none');
    // document.getElementById('date-selection').classList.add('d-none');
    document.getElementById('cancel-edit-table-button').classList.remove('d-none');
    document.getElementById('save-table-button').classList.remove('d-none');
  },

  cancelEdit(model, modelSingular, orgId, limit = null) {
    /**
     * Cancel editing a data table.
     * @param {String} model The name of a given data model.
     * @param {String} modelSingular A given data model.
     * @param {String} orgId The ID for a specific organization.
     * @param {Number} limit The limit for any data being streamed in the edit.
     */
    const newButton = document.getElementById('new-button');
    if (newButton) newButton.classList.remove('d-none');
    document.getElementById('import-form').classList.remove('d-none');
    document.getElementById('import_options').classList.remove('d-none');
    document.getElementById('export-table-button').classList.remove('d-none');
    document.getElementById('edit-table-button').classList.remove('d-none');
    // document.getElementById('date-selection').classList.remove('d-none');
    document.getElementById('cancel-edit-table-button').classList.add('d-none');
    document.getElementById('save-table-button').classList.add('d-none');
    this.streamData(model, modelSingular, orgId, limit);
  },

  /*----------------------------------------------------------------------------
   * Sub-Model Functions
   *--------------------------------------------------------------------------*/

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

  loadSelectTable(model, modelSingular, orgId, limit = 1000) {
    /**
     * Render a table used for selection.
     * @param {String} model The name of a given data model.
     * @param {String} modelSingular A given data model.
     * @param {String} orgId The ID for a specific organization.
     * @param {Number} limit The limit for any data being streamed in the table.
     */
    const path = `organizations/${orgId}/${model}`;
    const params = { max: limit };
    listenToCollection(path, params, (querySnapshot) => {
      const data = [];
      querySnapshot.forEach((doc) => data.push(doc.data()));
      this.renderSelectTable(data, model, orgId);
    })
  },

  async renderSelectTable(data, model, orgId) {
    /**
     * Render a selection table.
     * @param {Array} data An array of observation data to render in the table.
     * @param {String} model The name of a given data model.
     * @param {String} orgId The ID for a specific organization.
     */

    // Specify the table columns according to the data model fields from organization settings.
    const dataModel = await getDocument(`organizations/${orgId}/data_models/${model}`);
    const columnDefs = dataModel.fields.map(function(e) {
      const dateColumn = e.key.endsWith('_at') ? 'datePicker' : null;
      return { headerName: e.label, field: e.key, sortable: true, filter: true, cellEditor: dateColumn };
    });

    // Enable checkbox selection.
    columnDefs[0]['checkboxSelection'] = true;
    columnDefs[0]['headerCheckboxSelection'] = true;

    // Specify the table options.
    this.selectGridOptions = {
      columnDefs: columnDefs,
      defaultColDef: {
        flex: 1,
        minWidth: 200,
      },
      rowClass: 'app-action',
      rowHeight: 25,
      rowSelection: 'multiple',
      singleClickEdit: true,
      suppressRowClickSelection: true,
      overlayLoadingTemplate: `
        <div class="spinner-grow text-success" role="status">
          <span class="visually-hidden">Loading...</span>
        </div>
      `,
      overlayNoRowsTemplate: `
        <div class="card-body bg-transparent text-center" style="max-width:320px;">
          <img
            src="/static/${dataModel.image_path}"
            style="width:75px;"
          >
          <h2 class="fs-5 text-dark mt-3 mb-1">
            Add ${dataModel.key}
          </h2>
          <p class="text-secondary fs-6 text-small">
            <small>${dataModel.description}</small>
          </p>
        </div>
      `,
    };

    // Render the table.
    const eGridDiv = document.querySelector(`#${dataModel.key}-selection-table`);
    eGridDiv.innerHTML = '';
    new agGrid.Grid(eGridDiv, this.selectGridOptions);
    window.cannlytics.theme.setTableTheme();
    this.selectGridOptions.api.setRowData(data);
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

  async saveTable(
    model,
    modelSingular,
    orgId,
    parentModel = null,
    parentModelSingular = null,
    parentId = null,
  ) {
    /**
     * Save a sub-model's data, associating the data with the current data
     * model entry using the parent data model's ID.
     * @param {String} model The name of a given data model.
     * @param {String} modelSingular A given data model.
     * @param {String} orgId The ID for a specific organization.
     * @param {String} parentModel The name of any parent data model.
     * @param {String} parentModelSingular The singular name of any parent data model.
     * @param {String} parentId The ID of any parent data.
     */
    // FIXME: Save the table and re-render without being so janky!!!
    const data = [];
    await this.gridOptions.api.forEachNode((rowNode, index) => {
      const item = rowNode.data;
      if (parentModelSingular) item[`${parentModelSingular}_id`] = parentId;
      data.push(item);
    });
    try {
      const url = `/api/${model}?organization_id=${orgId}`;
      await authRequest(url, data);
      const message = `Data saved under ${model} for organization ${orgId}.`;
      showNotification('Data saved', message, /* type = */ 'success');
      document.getElementById(`${modelSingular}-delete-table-button`).classList.add('d-none');
    } catch(error) {
      showNotification('Error saving data', error.message, /* type = */ 'error');
    }
  },

  async streamSubModelData(model, modelSingular, orgId, key, value, limit=null) {
    /**
     * Stream data for a sub-model.
     * @param {String} model The name of a given data model.
     * @param {String} modelSingular A given data model.
     * @param {String} orgId The ID for a specific organization.
     * @param {String} key A field on which to filter the data.
     * @param {Dynamic} value A value to use to filter the data.
     * @param {Number} limit The maximum number of observations to stream.
     */
    const subDataModel = await getDocument(`organizations/${orgId}/data_models/${model}`);
    const path = `organizations/${orgId}/${model}`;
    let params = {};
    if (!limit) {
      const startDate = document.getElementById('time_start').value;
      const endDate = document.getElementById('time_end').value;
      params = {
        desc: true,
        filters: [
          { key: 'updated_at', operation: '>=', value: startDate },
          { key: 'updated_at', operation: '<=', value: `${endDate}T23:59:59` },
        ],
        order: 'updated_at',
      };
    } else {
      params = { max: limit };
    }
    if (key) {
      const filters = params.filters || [];
      filters.push({ key: 'key', operation: '==', value });
      params['filters'] = filters;
    }
    listenToCollection(path, params, (querySnapshot) => {
      const data = [];
      querySnapshot.forEach((doc) => {
        const item = doc.data();
        data.push(item);
      });
      this.renderSubModelTable(data, subDataModel);
    });
  },

  renderSubModelTable(data, dataModel) {
    /**
     * Render a table for data from a sub-model.
     * @param {Array} data An array of observations to render in the table.
     * @param {Object} dataModel Information about a data model.
     */

    var onSelectionChanged = this.onSelectionChanged;

    // Specify the table columns according to the data model fields from organization settings.
    const columnDefs = dataModel.fields.map(function(e) {
      const dateColumn = e.key.endsWith('_at') ? 'datePicker' : null;
      return { headerName: e.label, field: e.key, sortable: true, filter: true, cellEditor: dateColumn };
    });

    // Enable checkbox selection.
    columnDefs[0]['checkboxSelection'] = true;
    columnDefs[0]['headerCheckboxSelection'] = true;

    // Specify the table options.
    this.gridOptions = {
      columnDefs: columnDefs,
      defaultColDef: {
        flex: 1,
        minWidth: 200,
        editable: true,
      },
      // enterMovesDown: true,
      enterMovesDownAfterEdit: true,
      rowClass: 'app-action',
      rowHeight: 25,
      rowSelection: 'multiple',
      singleClickEdit: true,
      suppressRowClickSelection: true,
      onSelectionChanged: onSelectionChanged,
      overlayLoadingTemplate: `
        <div class="spinner-grow text-success" role="status">
          <span class="visually-hidden">Loading...</span>
        </div>
      `,
      overlayNoRowsTemplate: `
        <div class="card-body bg-transparent text-center" style="max-width:320px;">
          <img
            src="/static/${dataModel.image_path}"
            style="width:75px;"
          >
          <h2 class="fs-5 text-dark mt-3 mb-1">
            Add ${dataModel.key}
          </h2>
          <p class="text-secondary fs-6 text-small">
            <small>${dataModel.description}</small>
          </p>
        </div>
      `,
    };

    // Render the table.
    const eGridDiv = document.querySelector(`#${dataModel.key}-table`);
    eGridDiv.innerHTML = '';
    new agGrid.Grid(eGridDiv, this.gridOptions);
    window.cannlytics.theme.setTableTheme();

    // Get any template data and provide it to the table via the AG Grid API.
    this.gridOptions.api.setRowData(data);
    if (data.length) document.getElementById(`${dataModel.singular}-save-table-button`).classList.remove('d-none');
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

  /*----------------------------------------------------------------------------
   * File Functions
   *--------------------------------------------------------------------------*/

  async streamFiles(model, modelSingular, modelId, orgId, orderBy = 'uploaded_at') {
    /**
     * Stream data about files for a given data model.
     * @param {String} model The name of a given data model.
     * @param {String} modelSingular A given data model.
     * @param {String} modelId The ID for a specific observation.
     * @param {String} orgId The ID for a specific organization.
     * @param {String} orderBy The field at which to order files, `uploaded_at` by default.
     */
    const dataModel = await getDocument(`organizations/${orgId}/data_models/files`);
    dataModel.fields = dataModel.fields.filter(function(obj) {
      return !(obj.hidden);
    });
    const path = `organizations/${orgId}/${model}/${modelId}/files`;
    const params = {
      desc: true,
      order: orderBy,
      max: this.fileLimit,
    };
    listenToCollection(path, params, (querySnapshot) => {
      const data = [];
      querySnapshot.forEach((doc) => {
        const values = doc.data();
        data.push(values);
      });
      if (data.length) this.renderTable(`${modelSingular}-files`, 'file', data, dataModel);
      else this.renderPlaceholder();
    });
  },

  async uploadModelFile(event, params) {
    /**
     * Upload a file to Firebase Storage for a given data model,
     * saving the file information through the API.
     * @param {Event} event A user-driven event.
     * @param {Object} params An object of relevant parameters:
     *  model, modelSingular, modelId, orgId, userId, userName, userEmail, photoUrl
     */
    // FIXME: Pass parameters as arguments instead of an object for better maintainability.
    // TODO: Upload files through the API instead.
    const { model, modelSingular, modelId, orgId, userId, userName, userEmail, photoUrl } = params;
    const { files } = event.target;    
    if (files.length) {
      const [ file ] = files;
      const name = file.name;
      const fileRef =  `organizations/${orgId}/${model}/${modelId}/files/${name}`;
      const [ docRef ] = fileRef.split('.');
      showNotification('Uploading image', formatBytes(file.size), /* type = */ 'wait');
      const fileId = await this.createID(model, modelSingular, orgId, 'F');
      const version = await this.getFileVersion(fileRef) + 1;
      try {
        await uploadFile(fileRef, file);
        const url = await getFileURL(fileRef);
      } catch(error) {
        showNotification('Upload Error', 'Error uploading file.', /* type = */ 'error')
      }
      const data = {
        content_type: file.type,
        file_id: fileId,
        file_size: file.size,
        key: modelId,
        modified_at: file.lastModifiedDate,
        name: name,
        uploaded_at: new Date().toISOString(),
        uploaded_by: userName,
        user: userId,
        user_email: userEmail,
        user_name: userName,
        user_photo_url: photoUrl,
        ref: fileRef,
        type: model,
        url: url,
        version: version,
        // Optional: Create short link
      };
      try {
        await setDocument(docRef, data);
        showNotification('File saved', `File saved to your ${model} under ${modelId}.`, /* type = */ 'success');
      } catch(error) {
        showNotification('Upload Error', 'Error saving file data.', /* type = */ 'error');
      }
    }
  },

  async deleteModelFile(event, params) {
    /**
     * Remove a file from storage and delete the file's data from Firestore.
     * @param {Event} event A user-driven event.
     * @param {Object} params An object of relevant parameters:
     *  model, modelSingular, modelId, orgId 
     */
    // TODO: Pass parameters as arguments instead of an object for better maintainability.
    const name = document.getElementById('input_name').value;
    const { model, modelSingular, modelId, orgId } = params;
    const fileRef =  `organizations/${orgId}/${model}/${modelId}/files/${name}`;
    const [ docRef ] = fileRef.split('.');
    await deleteFile(fileRef);
    await deleteDocument(docRef);
    showNotification('File deleted', 'File removed and file data deleted.', /* type = */ 'success');
    window.location.href = window.location.href.substring(0, window.location.href.lastIndexOf('/'));
  },

  async getFileVersion(fileRef) {
    /**
     * Get the version of a given file, if it exists.
     * @param {String} fileRef The storage reference for a given file.
     */
    const data = await getDocument(fileRef)
    return data.version || 0;
  },

  pinFile(event, params) {
    /**
     * Pin a given file.
     * @param {Event} event A user-driven event.
     * @param {Object} params An object of relevant parameters:
     *  model, modelSingular, modelId, orgId
     */
    // TODO: Pass parameters as arguments instead of an object for better maintainability.
    const pinned = event.target.checked;
    const name = document.getElementById('input_name').value;
    const { model, modelSingular, modelId, orgId } = params;
    const fileRef =  `organizations/${orgId}/${model}/${modelId}/files/${name}`;
    const [ docRef ] = fileRef.split('.');
    setDocument(docRef, { pinned });
  },
  
  /*----------------------------------------------------------------------------
   * Utility Functions
   *--------------------------------------------------------------------------*/

  async createID(model, modelSingular, orgId, abbreviation, count = 1) {
    /**
     * Create a unique ID.
     * @param {String} model The name of a given data model.
     * @param {String} modelSingular A given data model.
     * @param {String} orgId The ID for a specific organization.
     * @param {String} abbreviation The abbreviation for the data model.
     * @param {Number} count A unique count number to attach to an ID, 1 by default.
     */
    if (!orgId) orgId = document.getElementById('organization_id').value;
    const currentCount = await this.getCurrentCount(model, orgId) + count;
    const date = new Date().toISOString().substring(0, 10);
    const dateString = date.replaceAll('-', '').slice(2);
    const id = `${abbreviation}${dateString}-${currentCount}`
    // FIXME: Prompt user to re-authenticate if Firestore unauthenticated error.
    try {
      document.getElementById(`input_${modelSingular}_id`).value = id;
    } catch(error) { /* No input to fill in. */ }
    return id;
  },

  async getCurrentCount(modelType, orgId) {
    /**
     * Get the current count for a given data model.
     * @param {String} modelType A type for a given model.
     * @param {String} orgId The ID for a specific organization.
     * @returns {Number} Returns the current number of models currently existing
     *    at the current day.
     */
    const date = new Date().toISOString().substring(0, 10);
    const ref = `organizations/${orgId}/stats/organization_settings/daily_totals/${date}`;
    const data = await getDocument(ref);
    const total = data[`total_${modelType}`];
    if (total) return total.length;
    else return 0;
  },

  /*----------------------------------------------------------------------------
   * UNDER DEVELOPMENT
   *--------------------------------------------------------------------------*/

  advancedSearch() {
    /** Add advanced search parameters for streaming data. */
    // TODO: Implement advanced search.
  },

  search() {
    /**
     * General search function to query the entire app and return the most
     * relevant page.
     */
    // TODO: Implement search by ID for all data models, plus granular search.
    const searchTerms = document.getElementById('navigation-search').value;
    setURLParameter('q', searchTerms)
  },

}
