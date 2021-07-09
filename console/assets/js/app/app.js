/**
 * App JavaScript | Cannlytics Console
 * Author: Keegan Skeate <contact@cannlytics.com>
 * Created: 12/7/2020
 * Updated: 7/9/2021
 */

import { auth, db, getDocument, getUserToken } from '../firebase.js';
import { authRequest, deserializeForm, getCookie, serializeForm, showNotification } from '../utils.js';
import { navigationHelpers } from '../ui/ui.js';
import { theme } from '../settings/theme.js';


export const app = {

  initialize() {
    /*
    * Initialize the console.
    */

    // Redirect not signed in users to the homepage.
    auth.onAuthStateChanged((user) => {
      console.log('Authenticated user:', user)
      if (!user) window.location.href = 'https://cannlytics.com';
    });

    // Enable any and all tooltips.
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map((tooltipTriggerEl) => new bootstrap.Tooltip(tooltipTriggerEl) );

  },

  /*----------------------------------------------------------------------------
  C.R.U.D. (General create, read, update, and delete)
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
    console.log(`input_${modelSingular}_id`);
    let id = document.getElementById(`input_${modelSingular}_id`).value;
    if (!id) id = await this.createID(model, modelSingular, orgId, abbreviation);
    const data = serializeForm(`${modelSingular}-form`);
    console.log('Model:', model);
    console.log('URL:', `/api/${model}/${id}?organization_id=${orgId}`);
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
  Data display functions
  ----------------------------------------------------------------------------*/

  dataModel: {},
  limit: 10,
  logLimit: 10,
  tableHidden: true,
  gridOptions: {},


  changeLimit(event) {
    /*
     * Change the limit for streamData.
     */
    this.limit = event.target.value;
     // FIXME: Refresh the table?
     // streamData(model, modelSingular, orgId)
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


  renderTable(model, modelSingular, data, dataModel) {
    /*
     * Render a data table in the user interface.
     */

    // Render the table if it's the first time that it's shown.
    if (this.tableHidden) {

      // Hide the placeholder and show the table.
      document.getElementById('loading-placeholder').classList.add('d-none');
      document.getElementById('data-placeholder').classList.add('d-none');
      document.getElementById('data-table').classList.remove('d-none');
      this.tableHidden = false;
  
      // Get data model fields from organization settings.
      const columnDefs = dataModel.fields.map(function(e) { 
        return { headerName: e.label, field: e.key, sortable: true, filter: true };
      });
  
      // Specify the table options.
      this.gridOptions = {
        columnDefs: columnDefs,
        defaultColDef: { flex: 1,  minWidth: 175 },
        pagination: true,
        paginationAutoPageSize: true,
        rowClass: 'app-action',
        rowHeight: 25,
        rowSelection: 'single',
        suppressRowClickSelection: false,
        onRowClicked: event => navigationHelpers.openObject(model, modelSingular, event.data),
        onGridReady: event => theme.toggleTheme(theme.getTheme()),
      };
  
      // Render the table
      const eGridDiv = document.querySelector(`#${model}-table`);
      new agGrid.Grid(eGridDiv, this.gridOptions);
      this.gridOptions.api.setRowData(data);

    } else {

      // Update the table's data.
      this.gridOptions.api.setRowData(data);

    }

  },


  async streamData(model, modelSingular, orgId) {
    /*
     * Stream data, listening for any changes.
     */
    // Optional: Get parameters (desc, orderBy) from the user interface.
    // TODO: Implement search with filters, e.g. .where("state", "==", "OK")
    // TODO: Pass dataModel from template.
    const desc = false;
    const orderBy = null;
    this.dataModel = await getDocument(`organizations/${orgId}/data_models/${model}`);
    let ref = db.collection('organizations').doc(orgId).collection(model);
    if (this.limit) ref = ref.limit(this.limit);
    if (orderBy && desc) ref = ref.orderBy(orderBy, 'desc');
    else if (orderBy) ref = ref.orderBy(orderBy);
    ref.onSnapshot((querySnapshot) => {
      const data = [];
      querySnapshot.forEach((doc) => {
        data.push(doc.data());
      });
      console.log('Table data:', data);
      if (data.length) this.renderTable(model, modelSingular, data, this.dataModel);
      else this.renderPlaceholder();
    });
  },


  async streamLogs(model, modelId, orgId, filterBy='key', orderBy='created_at', start='', end='') {
    /*
     * Stream logs, listening for any changes.
     */
    if (!start) start = new Date(new Date().setDate(new Date().getDate()-1)).toISOString().substring(0, 10);
    if (!end) {
      end = new Date()
      end.setUTCHours(23, 59, 59, 999);
      end = end.toISOString();
    }
    const dataModel = await getDocument(`organizations/${orgId}/data_models/logs`);
    dataModel.fields = dataModel.fields.filter(function(obj) {
      return !(['log_id', 'changes', 'user'].includes(obj.key));
    });
    console.log('Start:', start);
    console.log('End:', end);
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
          // FIXME: Split up date and time for filling into the form.
          console.log(values.created_at);
          data.push(values);
        });
        console.log('Logs:', data);
        if (data.length) this.renderTable('contact-logs', 'log', data, dataModel);
        else this.renderPlaceholder();
      });
  },

  
  /*----------------------------------------------------------------------------
  Utility functions
  ----------------------------------------------------------------------------*/

  async createID(model, modelSingular, orgId, abbreviation) {
    /*
     * Create a unique ID.
     */
    if (!orgId) orgId = document.getElementById('organization_id').value;
    const currentCount = await this.getCurrentCount(model, orgId) + 1;
    const date = new Date().toISOString().substring(0, 10);
    const dateString = date.replaceAll('-', '').slice(2);
    const id = `${abbreviation}${dateString}-${currentCount}`
    document.getElementById(`input_${modelSingular}_id`).value = id;
    return id;
  },


  getCurrentCount: (modelType, orgId) => new Promise((resolve, reject) => {
    /*
     * Get the current count for a given data model.
     */
    const date = new Date().toISOString().substring(0, 10);
    const ref = `organizations/${orgId}/stats/organization_settings/daily_totals/${date}`;
    console.log('Ref:', ref);
    getDocument(ref).then((data) => {
      const total = data[`total_${modelType}`];
      if (total) resolve(total.length)
      else resolve(0);
    })
    .catch((error) => reject(error));
  }),


  async exportData(modelSingular, id = null) {
    /*
     * Export given collection data to Excel.
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


  /*----------------------------------------------------------------------------
  UNDER DEVELOPMENT
  ----------------------------------------------------------------------------*/


  advancedSearch() {
    /* Add advanced search parameters for streaming data. */
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
