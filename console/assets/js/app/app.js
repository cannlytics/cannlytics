/**
 * App JavaScript | Cannlytics Console
 * Author: Keegan Skeate <contact@cannlytics.com>
 * Created: 12/7/2020
 * Updated: 7/6/2021
 */

import { auth, db, getDocument, getUserToken } from '../firebase.js';
import { authRequest, getCookie, serializeForm, showNotification } from '../utils.js';
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


  save(model, modelSingular) {
    /* Create an entry in the database if it does not exist,
    otherwise update the entry. */
    // FIXME: Delete old entry if ID changes.
    document.getElementById('form-save-button').classList.add('d-none');
    document.getElementById('form-save-loading-button').classList.remove('d-none');
    let id = document.getElementById(`input_${modelSingular}_id`).value;
    if (!id) id = this.createID(model, modelSingular);
    const data = serializeForm(`${modelSingular}-form`);
    const orgId = document.getElementById('organization_id').value;
    console.log('TODO: save data:', model, modelSingular, orgId, data,);
    authRequest(`/api/${model}/${id}?organization_id=${orgId}`, data)
      .then((response) => {
        const message = 'Data saved. You can safely navigate pages.'
        showNotification('Data saved', message, { type: 'success' });
      })
      .catch((error) => {
        showNotification('Error saving data', error.message, { type: 'error' });
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
  tableHidden: true,
  gridOptions: {},


  changeLimit(event) {
    /* Change the limit for streamData. */
    this.limit = event.target.value;
     // FIXME: Refresh the table?
     // streamData(model, modelSingular, orgId)
  },


  drawPlaceholder() {
    /* Render a no-data placeholder in the user interface. */
    document.getElementById('loading-placeholder').classList.add('d-none');
    document.getElementById('data-table').classList.add('d-none');
    document.getElementById('data-placeholder').classList.remove('d-none');
    this.tableHidden = true;
  },


  async drawTable(model, modelSingular, orgId, data) {
    /* Render a data table in the user interface. */

    // Render the table if it's the first time that it's shown.
    if (this.tableHidden) {

      // Hide the placeholder and show the table.
      document.getElementById('loading-placeholder').classList.add('d-none');
      document.getElementById('data-placeholder').classList.add('d-none');
      document.getElementById('data-table').classList.remove('d-none');
      this.tableHidden = false;
  
      // Get data model fields from organization settings.
      this.dataModel = await getDocument(`organizations/${orgId}/data_models/${model}`);
      console.log('Data Model:', this.dataModel);
      const columnDefs = this.dataModel.fields.map(function(e) { 
        return { headerName: e.label, field: e.key, sortable: true, filter: true };
      });
  
      // Specify the table options.
      this.gridOptions = {
        columnDefs: columnDefs,
        defaultColDef: { flex: 1,  minWidth: 175 },
        pagination: true,
        paginationAutoPageSize: true,
        rowClass: 'app-action',
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


  streamData(model, modelSingular, orgId) {
    /*
     * Stream data, listening for any changes.
     */
    // Optional: Get parameters (desc, orderBy) from the user interface.
    // TODO: Implement search with filters, e.g. .where("state", "==", "OK")
    const desc = false;
    const orderBy = null;
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
      if (data.length) this.drawTable(model, modelSingular, orgId, data);
      else this.drawPlaceholder();
    });
  },
  
  /*----------------------------------------------------------------------------
  Utility functions
  ----------------------------------------------------------------------------*/

  createID(model, modelSingular) {
    /* Create a unique ID. */
    console.log('Create ID...', modelSingular);
    // TODO: Get organization settings and assign ID based on data model ID schema.
    const modelAbbreviations = {
      'analyses': 'AN',
      'analytes': 'AT',
      'areas': 'A',
      'contacts': 'C',
      'instruments': 'IS',
      'inventory': 'IN',
      'measurements': 'M',
      'projects': 'P',
      'samples': 'S',
      'transfers': 'TR'
    };
    const abbreviation = modelAbbreviations[model]
    const date = new Date().toISOString().substring(0, 10);
    const dateString = date.replaceAll('-', '');
    const id = `${abbreviation}${dateString}-`
    // TODO: Save next available counter in organization settings instead of using random bit!
    console.log(id);
    document.getElementById(`input_${modelSingular}_id`).value = id;
    return id;
  },


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


  async downloadWorksheet(orgId, model) {
    /*
     * Download a worksheet to facilitate importing data.
     */
    if (!this.dataModel.worksheet_url) {
      this.dataModel = await getDocument(`organizations/${orgId}/data_models/${model}`);
    }
    // const idToken = await getUserToken();
    // const csrftoken = getCookie('csrftoken');
    // const headerAuth = new Headers({
    //   'Content-Type': 'application/json',
    //   'Authorization': `Bearer ${idToken}`,
    //   'X-CSRFToken': csrftoken,
    //   'mode': 'no-cors',
    // });
    // const init = { headers: headerAuth, method: 'GET' };
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

  // importData(model) {
  //   /*
  //    * Import a data file (.csv or .xlsx) to Firestore for a given model type.
  //    */
  //   // TODO:
  //   console.log('TODO: import data:', model);
  // },


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
    // const urlParams = new URLSearchParams(window.location.search);
    // urlParams.set('q', searchTerms);
    // window.location.search = urlParams;
    // window.location.href = '/search';
    setGetParameter('q', searchTerms)
    // const query = URLSearchParams(window.location.search).get('q');
    // console.log(query);
  },

}


/*----------------------------------------------------------------------------
  Local functions
----------------------------------------------------------------------------*/

function setGetParameter(paramName, paramValue) {
  /* Add query parameter to the URL. */
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
