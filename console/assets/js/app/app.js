/**
 * App JavaScript | Cannlytics Console
 * Author: Keegan Skeate <contact@cannlytics.com>
 * Created: 12/7/2020
 * Updated: 8/16/2021
 */

import {
  auth,
  db,
  deleteDocument,
  deleteFile,
  getDocument,
  getDownloadURL,
  getUserToken,
  updateDocument,
  uploadFile,
} from '../firebase.js';
import {
  authRequest,
  deserializeForm,
  formatBytes,
  getCookie,
  serializeForm,
  showNotification,
} from '../utils.js';
import { navigationHelpers } from '../ui/ui.js';
import { theme } from '../settings/theme.js';


export const app = {

  initialize() {
    /*
    * Initialize the console.
    */

    // Redirect not signed in users to the homepage.
    auth.onAuthStateChanged((user) => {
      const userNotLoaded = document.getElementById('userPhotoNav').src.endsWith('user.svg');
      // FIXME: Prefer to redirect from server.
      if (!user || userNotLoaded) window.location.href = `${window.location.origin}/account/sign-in`;
    });

    // Enable any and all tooltips.
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map((tooltipTriggerEl) => new bootstrap.Tooltip(tooltipTriggerEl) );

  },

  /*----------------------------------------------------------------------------
  Create, read, update, and delete
  ----------------------------------------------------------------------------*/

  get(model, id=null, options={}) {
    /* Retrieve data from the database, either an array of data objects or a
    single object if an ID is specified. Pass params in options to filter the data. */
    const modelType = model.replace(/^./, string[0].toUpperCase());
    if (id) return authRequest(`/api/${model}/${id}`);
    return authRequest(`/api/${model}`, null, options);
  },


  startDelete(model, id) {
    /* Begin the deletion process by showing a text area for deletion reason. */
    document.getElementById('deletion-reason').classList.remove('d-none');
  },


  cancelDelete() {
    /* Cancel the deletion process by hiding the text area for deletion reason. */
    document.getElementById('deletion-reason').classList.add('d-none');
  },


  delete(model, id) {
    /* Delete an entry from the database, passing the whole object
    as context if available in a form, otherwise just pass the ID. */
    const orgId = document.getElementById('organization_id').value;
    const deletionReason = document.getElementById('deletion_reason_input').value;
    const data = { deletion_reason: deletionReason };
    authRequest(`/api/${model}/${id}?organization_id=${orgId}`, data, { delete: true })
      .then((response) => {
        window.location.href = `/${model}`;
      })
      .catch((error) => {
        showNotification('Error deleting data', error.message, { type: 'error' });
      });
  },


  async save(model, modelSingular, abbreviation) {
    /* Create an entry in the database if it does not exist,
    otherwise update the entry. */
    // FIXME: Delete old entry if ID changes.
    const orgId = document.getElementById('organization_id').value;
    document.getElementById('form-save-button').classList.add('d-none');
    document.getElementById('form-save-loading-button').classList.remove('d-none');
    let id = document.getElementById(`input_${modelSingular}_id`).value;
    if (!id) id = await this.createID(model, modelSingular, orgId, abbreviation);
    const data = serializeForm(`${modelSingular}-form`);
    authRequest(`/api/${model}/${id}?organization_id=${orgId}`, data)
      .then((response) => {
        const message = 'Data saved. You can safely navigate pages.'
        showNotification('Data saved', message, { type: 'success' });
        return response;
      })
      .catch((error) => {
        showNotification('Error saving data', error.message, { type: 'error' });
        return error;
      })
      .finally(() => {
        document.getElementById('form-save-loading-button').classList.add('d-none');
        document.getElementById('form-save-button').classList.remove('d-none');
      });
  },

  /*----------------------------------------------------------------------------
  Data tables
  ----------------------------------------------------------------------------*/

  dataModel: {},
  limit: 1000,
  logLimit: 1000,
  fileLimit: 1000,
  tableHidden: true,
  gridOptions: {},
  selectGridOptions: {},


  changeLimit(event) {
    /*
     * Change the limit for streamData.
     */
    this.limit = event.target.value;
  },


  // TODO: Pass data model directly
  async downloadWorksheet(orgId, model) {
    /*
     * Download a worksheet to facilitate importing data.
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
    /*
     * Export given collection data to Excel.
     * Optional: Also export any sub-model data table.
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
    const response = await fetch(window.location.origin + '/download', init);
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
    /*
     * Export a data table as a CSV file.
     */
    this.gridOptions.api.exportDataAsCsv({
      fileName: `${model}.csv`,
    });
  },


  renderPlaceholder() {
    /*
     * Render a no-data placeholder in the user interface.
     */
    document.getElementById('loading-placeholder').classList.add('d-none');
    document.getElementById('data-table').classList.add('d-none');
    document.getElementById('data-placeholder').classList.remove('d-none');
    this.tableHidden = true;
  },


  renderTable(model, modelSingular, data, dataModel, editable=false) {
    /*
     * Render a data table in the user interface.
     * TODO: Generalize as a utility function.
     */

    // Render the table if it's the first time that it's shown.
    if (this.tableHidden) {

      // Hide the placeholder and show the table.
      document.getElementById('loading-placeholder').classList.add('d-none');
      document.getElementById('data-placeholder').classList.add('d-none');
      document.getElementById('data-table').classList.remove('d-none');
      // this.tableHidden = false;
  
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
        // onRowClicked: event => navigationHelpers.openObject(model, modelSingular, event.data),
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


  searchData(event, model, modelSingular) {
    /*
     * Search a data model.
     */
    let ref = db.collection('organizations').doc(orgId).collection(model);
    if (this.limit) ref = ref.limit(this.limit);
    if (orderBy && desc) ref = ref.orderBy(orderBy, 'desc');
    else if (orderBy) ref = ref.orderBy(orderBy);
    ref.onSnapshot((querySnapshot) => {
      const data = [];
      querySnapshot.forEach((doc) => {
        data.push(doc.data());
      });
      if (data.length) this.renderTable(model, modelSingular, data, this.dataModel);
      else this.renderPlaceholder();
    });
  },


  searchTable(model, modelSingular, orgId) {
    /*
     * A general search of a data model table.
     */
    // TODO: Iterate over data model fields, query for a match, break if any
    // documents are found. Prefer to iterate over data model fields in a logical
    // manner. For example, if the search contains an abbreviation, then we may know
    // that it is an ID, etc.
    console.log('TODO: Implement search....');
    this.dataModel.fields.forEach((field) => {
      console.log(field);
    })
    // TODO: Show clear search button.
    document.getElementById('clear-button').classList.remove('d-none');
  },


  clearSearch(model, modelSingular, orgId) {
    /*
     * Reset the table after performing a search.
     */
    console.log('TODO: Clearing search...');
    document.getElementById('clear-button').classList.add('d-none');
    document.getElementById('searchInput').value = '';
    this.streamData(model, modelSingular, orgId);
  },


  async streamData(model, modelSingular, orgId, limit=null, editable=false) {
    /*
     * Stream data, listening for any changes. Search by date range (by updated_at)
     * by first. If no observations are found, then search with a limit and set
     * the start_date to the earliest updated_at time, if any observations were found.
     */
    // Optional: Get parameters (desc, orderBy) from the user interface.
    // Optional: Implement search with filters, e.g. .where("state", "==", "OK")
    // Optional: Pass dataModel from template.
    this.dataModel = await getDocument(`organizations/${orgId}/data_models/${model}`);
    let ref = db.collection('organizations').doc(orgId).collection(model);
    if (!limit) {
      const startDate = document.getElementById('time_start').value;
      const endDate = document.getElementById('time_end').value;
      ref = ref.where('updated_at', '>=', startDate);
      ref = ref.where('updated_at', '<=', `${endDate}T23:59:59`);
      ref = ref.orderBy('updated_at', 'desc');
    } else {
      ref = ref.limit(limit);
      ref = ref.orderBy('updated_at', 'desc');
    }
    ref.onSnapshot((querySnapshot) => {
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
        } catch (error) {
          // Date input likely hidden.
        }
      }
      else if (!limit) this.streamData(model, modelSingular, orgId, 100, editable);
      else this.renderPlaceholder();
    });
  },


  async streamLogs(model, modelId, orgId, filterBy='key', orderBy='created_at', start='', end='', period=7) {
    /*
     * Stream logs, listening for any changes.
     */
    if (!start) start = new Date(new Date().setDate(new Date().getDate()-period)).toISOString().substring(0, 10);
    if (!end) {
      end = new Date()
      end.setUTCHours(23, 59, 59, 999);
      end = end.toISOString();
    }
    const dataModel = await getDocument(`organizations/${orgId}/data_models/logs`);
    dataModel.fields = dataModel.fields.filter(function(obj) {
      return !(['log_id', 'changes', 'user'].includes(obj.key));
    });
    db.collection('organizations').doc(orgId).collection('logs')
      .where(filterBy, '==', modelId)
      .where(orderBy, '>=', start)
      .where(orderBy, '<=', end)
      .orderBy(orderBy, 'desc')
      .limit(this.logLimit)
      .onSnapshot((querySnapshot) => {
        const data = [];
        querySnapshot.forEach((doc) => {
          const values = doc.data();
          values.changes = JSON.stringify(values.changes);
          // Optional: Split up date and time for filling into the form.
          data.push(values);
        });
        if (data.length) this.renderTable(`${model}-logs`, 'log', data, dataModel);
        else this.renderPlaceholder();
      });
  },


  startEdit(model, modelSingular, orgId) {
    /*
     * Start editing a data table.
     */
    this.streamData(model, modelSingular, orgId, null, true);
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


  cancelEdit(model, modelSingular, orgId) {
    /*
     * Cancel editing a data table.
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
    this.streamData(model, modelSingular, orgId);
  },


  /*----------------------------------------------------------------------------
  Sub-models
  ----------------------------------------------------------------------------*/

  async addTableRow(model, modelSingular, orgId, abbreviation) {
    /*
     * Add a new, editable row to a data table.
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


  async deleteTableRows(model, modelSingular, orgId, parentModelSingular='', removeOnly=false) {
    /*
     * Delete a row or rows from an editable data table,
     * trying to remove the data from Firestore if removeOnly is false,
     * which it is by default.
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
        authRequest(`/api/${model}?organization_id=${orgId}`, postData);
      } else {
        authRequest(`/api/${model}?organization_id=${orgId}`, postData, { delete: true });
      }
    } catch (error) {
      // Entries may not exist in the database yet.
    }
    await this.gridOptions.api.forEachNode((rowNode, index) => {
      if (!idsToDelete.includes(rowNode.data[idKey])) {
        rows.push(rowNode.data);
      }
    });
    this.gridOptions.api.setRowData(rows);
    document.getElementById(`${modelSingular}-delete-table-button`).classList.add('d-none');
  },


  loadSelectTable(model, modelSingular, orgId, limit=1000) {
    /*
     * Render a table used for selection.
     */
    let ref = db.collection('organizations').doc(orgId).collection(model);
    ref = ref.limit(limit);
    ref.onSnapshot((querySnapshot) => {
      const data = [];
      querySnapshot.forEach((doc) => {
        const item = doc.data();
        data.push(item);
      });
      this.renderSelectTable(data, model, orgId);
    });
  },


  async renderSelectTable(data, model, orgId) {
    /*
     * Render a selection table.
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
    /*
     * Select pre-existing entries for the table.
     */
    const rows = [];
    const selected = this.selectGridOptions.api.getSelectedRows();
    await this.gridOptions.api.forEachNode((rowNode, index) => rows.push(rowNode.data));
    const data = [...rows, ...selected];
    this.gridOptions.api.setRowData(data);
    if (data.length) document.getElementById(`${modelSingular}-save-table-button`).classList.remove('d-none');
  },


  async saveTable(model, modelSingular, orgId, parentModel=null, parentModelSingular=null, parentId=null) {
    /*
     * Save a sub-model's data, associating the data with the current data
     * model entry using the parent data model's ID.
     */
    const data = [];
    await this.gridOptions.api.forEachNode((rowNode, index) => {
      const item = rowNode.data;
      if (parentModelSingular) item[`${parentModelSingular}_id`] = parentId;
      data.push(item);
    });
    authRequest(`/api/${model}?organization_id=${orgId}`, data)
      .then((response) => {
        const message = `Data saved under ${model} for organization ${orgId}.`;
        showNotification('Data saved', message, { type: 'success' });
        document.getElementById(`${modelSingular}-delete-table-button`).classList.add('d-none');
      })
      .catch((error) => {
        showNotification('Error saving data', error.message, { type: 'error' });
      });
  },


  async streamSubModelData(model, modelSingular, orgId, key, value, limit=null) {
    /*
     * Stream data for a sub-model.
     */
    const subDataModel = await getDocument(`organizations/${orgId}/data_models/${model}`);
    let ref = db.collection('organizations').doc(orgId).collection(model);
    if (!limit) {
      const startDate = document.getElementById('time_start').value;
      const endDate = document.getElementById('time_end').value;
      ref = ref.where('updated_at', '>=', startDate);
      ref = ref.where('updated_at', '<=', `${endDate}T23:59:59`);
      ref = ref.orderBy('updated_at', 'desc');
    } else {
      ref = ref.limit(limit);
    }
    if (key) ref = ref.where(key, '==', value);
    ref.onSnapshot((querySnapshot) => {
      const data = [];
      querySnapshot.forEach((doc) => {
        const item = doc.data();
        data.push(item);
      });
      this.renderSubModelTable(data, subDataModel);
    });
  },


  renderSubModelTable(data, dataModel) {
    /*
     * Render a table for data from a sub-model.
     */

    // function onSelectionChanged(event) {
    //   /*
    //    * Show options that are only available when table rows are selected.
    //    */
    //   var selectOnly = document.getElementsByClassName('select-only-option');
    //   var rowCount = event.api.getSelectedNodes().length;
    //   for (var i = 0; i < selectOnly.length; i++) {
    //     const item = selectOnly.item(i);
    //     if (rowCount > 0) {
    //       item.classList.remove('d-none');
    //     } else {
    //       item.classList.add('d-none');
    //     }
    //   }
    // }
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
    /*
     * Show options that are only available when table rows are selected.
     */
    var selectOnly = document.getElementsByClassName('select-only-option');
    var rowCount = event.api.getSelectedNodes().length;
    for (var i = 0; i < selectOnly.length; i++) {
      const item = selectOnly.item(i);
      if (rowCount > 0) {
        item.classList.remove('d-none');
      } else {
        item.classList.add('d-none');
      }
    }
  },


  /*----------------------------------------------------------------------------
  Files
  ----------------------------------------------------------------------------*/


  async streamFiles(model, modelSingular, modelId, orgId, orderBy='uploaded_at') {
    /*
     * Stream data about files for a given data model.
     */
    const dataModel = await getDocument(`organizations/${orgId}/data_models/files`);
    dataModel.fields = dataModel.fields.filter(function(obj) {
      return !(obj.hidden);
    });
    db.collection('organizations')
      .doc(orgId)
      .collection(model)
      .doc(modelId)
      .collection('files')
      .orderBy(orderBy, 'desc')
      .limit(this.fileLimit)
      .onSnapshot((querySnapshot) => {
        const data = [];
        querySnapshot.forEach((doc) => {
          const values = doc.data();
          data.push(values);
        });
        console.log('Files:', data);
        if (data.length) this.renderTable(`${modelSingular}-files`, 'file', data, dataModel);
        else this.renderPlaceholder();
      });
  },


  async uploadModelFile(event, params) {
    /*
     * Upload a file to Firebase Storage for a given data model,
     * saving the file information through the API.
     */
    // Optional: Upload files through the API instead
    const { model, modelSingular, modelId, orgId, userId, userName, userEmail, photoUrl } = params;
    const { files } = event.target;    
    if (files.length) {
      const [ file ] = files;
      const name = file.name;
      const fileRef =  `organizations/${orgId}/${model}/${modelId}/files/${name}`;
      const [ docRef ] = fileRef.split('.');
      showNotification('Uploading image', formatBytes(file.size), { type: 'wait' });
      const fileId = await this.createID(model, modelSingular, orgId, 'F');
      const version = await this.getFileVersion(fileRef) + 1;
      uploadFile(fileRef, file).then((snapshot) => {
        getDownloadURL(fileRef).then((url) => {
          updateDocument(docRef, {
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
          }).then(() => {
            showNotification('File saved', `File saved to your ${model} under ${modelId}.`, { type: 'success' });
          })
          .catch((error) => {
            console.log(error);
            showNotification('Upload Error', 'Error saving file data.', { type: 'error' })
          });
        }).catch((error) => showNotification('Upload Error', 'Error uploading file.', { type: 'error' }));
      });
    }
  },


  async deleteModelFile(event, params) {
    /*
     * Remove a file from storage and delete the file's data from Firestore.
     */
    const name = document.getElementById('input_name').value;
    const { model, modelSingular, modelId, orgId } = params;
    const fileRef =  `organizations/${orgId}/${model}/${modelId}/files/${name}`;
    const [ docRef ] = fileRef.split('.');
    await deleteFile(fileRef);
    await deleteDocument(docRef);
    showNotification('File deleted', 'File removed and file data deleted.', { type: 'success' });
    window.location.href = window.location.href.substring(0, window.location.href.lastIndexOf('/'));
  },


  async getFileVersion(fileRef) {
    /*
     * Get the version of a given file, if it exists.
     */
    const data = await getDocument(fileRef)
    return data.version || 0;
  },


  pinFile(event, params) {
    /*
     * Pin a given file.
     */
    const pinned = event.target.checked;
    const name = document.getElementById('input_name').value;
    const { model, modelSingular, modelId, orgId } = params;
    const fileRef =  `organizations/${orgId}/${model}/${modelId}/files/${name}`;
    const [ docRef ] = fileRef.split('.');
    updateDocument(docRef, { pinned });
  },
  

  /*----------------------------------------------------------------------------
  Utility functions
  ----------------------------------------------------------------------------*/

  async createID(model, modelSingular, orgId, abbreviation, count=1) {
    /*
     * Create a unique ID.
     */
    if (!orgId) orgId = document.getElementById('organization_id').value;
    const currentCount = await this.getCurrentCount(model, orgId) + count;
    const date = new Date().toISOString().substring(0, 10);
    const dateString = date.replaceAll('-', '').slice(2);
    const id = `${abbreviation}${dateString}-${currentCount}`
    try {
      document.getElementById(`input_${modelSingular}_id`).value = id;
    } catch(error) {
      // No input to fill in.
    }
    return id;
  },


  getCurrentCount: (modelType, orgId) => new Promise((resolve, reject) => {
    /*
     * Get the current count for a given data model.
     */
    const date = new Date().toISOString().substring(0, 10);
    const ref = `organizations/${orgId}/stats/organization_settings/daily_totals/${date}`;
    getDocument(ref).then((data) => {
      const total = data[`total_${modelType}`];
      if (total) resolve(total.length)
      else resolve(0);
    })
    .catch((error) => reject(error));
  }),


  /*----------------------------------------------------------------------------
  UNDER DEVELOPMENT
  ----------------------------------------------------------------------------*/


  advancedSearch() {
    /* Add advanced search parameters for streaming data. */
    // TODO: Implement advanced search.
  },


  search() {
    /*
     * General search function to query the entire app and return the most
     * relevant page.
     */
    // TODO: Implement search by ID for all data models, plus granular search.
    console.log('Searching...');
    const searchTerms = document.getElementById('navigation-search').value;
    setURLParameter('q', searchTerms)
  },

}



function setURLParameter(paramName, paramValue) {
  /*
   * Add query parameter to the URL.
   */
  var url = window.location.href;
  var hash = location.hash;
  url = url.replace(hash, '');
  if (url.indexOf(paramName + "=") >= 0)
  {
      var prefix = url.substring(0, url.indexOf(paramName + "=")); 
      var suffix = url.substring(url.indexOf(paramName + "="));
      suffix = suffix.substring(suffix.indexOf("=") + 1);
      suffix = (suffix.indexOf("&") >= 0) ? suffix.substring(suffix.indexOf("&")) : "";
      url = prefix + paramName + "=" + paramValue + suffix;
  }
  else
  {
  if (url.indexOf("?") < 0)
      url += "?" + paramName + "=" + paramValue;
  else
      url += "&" + paramName + "=" + paramValue;
  }
  window.location.href = `\\search\\${url}${hash}`;
}
