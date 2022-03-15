/**
 * Labs JavaScript | Cannlytics Website
 * Copyright (c) 2021-2022 Cannlytics
 * 
 * Authors: Keegan Skeate <keegan@cannlytics.com>
 * Created: 1/17/2021
 * Updated: 1/17/2022
 * License: MIT License <https://github.com/cannlytics/cannlytics-website/blob/main/LICENSE>
 */
import { authRequest, showNotification } from '../utils.js';
import { addSelectOptions, setTableTheme } from '../ui/ui.js';
import { downloadBlob, sortArrayOfObjects } from '../utils.js';
import { getCurrentUser } from '../firebase.js';

export const labs = {

  // State
  analyses: [],
  gridOptions: {},
  lab: {},
  labs: [],

  /*----------------------------------------------------------------------------
   * Lab UI Initialization
   *--------------------------------------------------------------------------*/

  async initializeLabsTable() {
    /**
     * Initialize a table of labs.
     */
    this.labs = await this.getLabs();
    console.log('Found labs:', this.labs);
    this.labs = sortArrayOfObjects(this.labs, 'state');

    // Get analyses from the API.
    this.analyses = await this.getAnalyses();
    console.log('Analyses:', this.analyses);

    // Define columns.
    const columnDefs = [
      {
        headerName: '', 
        field: 'slug', 
        width: 25,
        sortable: false, 
        autoHeight: true,
        cellRenderer: renderViewLabButton,
        cellClass: 'px-0',
      },
      {
        headerName: 'Lab',
        field: 'name',
        sortable: true,
        filter: true,
      },
      {
        headerName: 'State',
        field: 'state',
        sortable: true,
        filter: true,
        width: 100,
      },
      {
        headerName: 'Analyses', field: 'analyses',
        sortable: true,
        filter: true,
        cellRenderer: renderAnalyses,
        width: 200,
      },
      {
        headerName: 'Phone',
        field: 'phone',
        sortable: true,
        filter: true,
        cellRenderer: renderAuthRequired,
        width: 150,
      },
      {
        headerName: 'Email',
        field: 'email',
        sortable: true,
        filter: true,
        cellRenderer: renderAuthRequired,
        width: 240,
      },
      {
        headerName: 'Address',
        field: 'formatted_address',
        sortable: true,
        filter: true,
        width: 300,
      },
      {
        headerName: 'License',
        field: 'license',
        sortable: true,
        filter: true,
      },
    ];

    // Specify the table options.
    this.gridOptions = {
      columnDefs: columnDefs,
      enableCellTextSelection: true,
      ensureDomOrder: true,
      pagination: true,
      paginationAutoPageSize: true,
      onGridReady: event => setTableTheme(),
    };

    // Hide the placeholder and show the table.
    document.getElementById('loading-placeholder').classList.add('d-none');
    document.getElementById('data-table').classList.remove('d-none');

    // Render the table.
    const table = document.querySelector('#labs-table');
    table.innerHTML = '';
    new agGrid.Grid(table, this.gridOptions);
    this.gridOptions.api.setRowData(this.labs);

    // Add available state filters.
    let stateOptions = this.labs.map(x => { return { label: x.state, value: x.state } });
    stateOptions = stateOptions.filter((v , i, a) => a.findIndex(t => (t.value === v.value)) === i);
    stateOptions = sortArrayOfObjects(stateOptions, 'value');
    addSelectOptions('lab-state-selection', stateOptions);

    // Initialize table search.
    this.initializeLabTableSearch();

  },

  async initializeLabDetails() {
    /**
     * Initialize lab details page.
     */
    const form = document.querySelector('form');
    form.addEventListener('submit', this.suggestLabEdit);
  },

  async initializeLogs(id) {
    /**
     * Initialize logs for a lab.
     * @param {String} id The ID of a lab.
     */
    const data = this.getLabLogs(id);
    // TODO: Show the a lab logs!
    console.log('Found logs:', data);
  },

  initializeLabTableSearch() {
    /**
     * Setup search for the table of labs.
     */
    const clearButton = document.getElementById('clear-button');
    const searchButton = document.getElementById('search-button');
    const searchInput = document.getElementById('search-input');
    clearButton.addEventListener('click', () => {
      searchInput.value = '';
      this.gridOptions.api.setRowData(this.labs);
      document.getElementById('clear-button').classList.add('d-none');
    });
    searchButton.addEventListener('click', () => {
      this.searchLabTable(searchInput)
    });
    searchInput.addEventListener('keydown', (event) => {
      this.searchLabTable(searchInput)
    });
  },

  /*----------------------------------------------------------------------------
   * Lab API Utilities
   *--------------------------------------------------------------------------*/

  async getAnalyses() {
    /**
     * Get analyses through the API.
     * @returns {Array}
     */
    const { data } = await authRequest('/api/data/analyses');
    return data;
  },

  async getAnalysis(id) {
    /**
     * Get analyses through the API.
     * @param {String} id The ID of an analysis.
     * @returns {Object}
     */
     const { data } = await authRequest(`/api/data/analyses/${id}`);
     return data;
  },

  async getLabs() {
    /**
     * Get labs through the API.
     * @returns {Array}
     */
    const { data } = await authRequest('/api/labs');
    return data;
  },

  async getLab(licenseNumber) {
    /**
     * Get lab data through the API.
     * @param {String} licenseNumber The ID of a lab.
     * @returns {Object}
     */
    const { data } = await authRequest(`/api/labs/${licenseNumber}`);
    return data;
  },

  async getLabAnalyses(id) {
    /**
     * Get analyses for a lab.
     * @param {String} id The ID of a lab.
     */
    const { data } = await authRequest(`/api/labs/${id}/analyses`);
    return data;
  },

  async getLabLogs(id) {
    /**
     * Get change logs for a lab.
     * @param {String} id The ID of a lab.
     */
    const { data } = await authRequest(`/api/labs/${id}/logs`);
    return data;
  },

  /*----------------------------------------------------------------------------
   * Lab List Functionality
   *--------------------------------------------------------------------------*/

  async downloadLabData() {
    /**
     * Download lab data, prompting the user to sign in if they are not already.
     */
    const time = new Date().toISOString().slice(0, 19).replace(/T|:/g, '-');
    try {
      const response = await authRequest('/src/data/download-lab-data', null, { file: true });
      const blob = await response.blob();
      downloadBlob(blob, /* filename = */ `labs-${time}.csv`);
    } catch(error) {
      const message = 'Error downloading lab data. Please try again later and/or contact support.';
      showNotification('Download Error', message, /* type = */ 'error' );
    }
  },

  filterLabsByState(event) {
    /**
     * Filter the table of labs by a given state.
     * @param {Element} event The 
     */
    const state = event.value;
    const subset = [];
    this.labs.forEach(lab => {
      if (lab.state === state || state === 'all') subset.push(lab);
    });
    this.gridOptions.api.setRowData(subset);
    if (state === 'all') this.viewLessLabs(/* original = */ true);
    else this.viewAllLabs();
  },

  searchLabTable(element) {
    /**
     * Search the lab table for a given query.
     * @param {String} value The query value.
     */
    const query = element.value.toLowerCase();
    console.log('Query:', query);
    if (!query) {
      this.gridOptions.api.setRowData(this.labs);
      document.getElementById('clear-button').classList.add('d-none');
    }
    else {
      const subset = [];
      this.labs.forEach(lab => {
        const searchFields = (({ name, trade_name, license }) => ({ name, trade_name, license }))(lab);
        const comparisonValues = Object.values(searchFields);
        let comparisonValue = '';
        comparisonValues.every((obsValue) => {
          try {
            comparisonValue = obsValue.toLowerCase();
          } catch(error) { return true }
          if (comparisonValue.includes(query) || comparisonValue.startsWith(query)) {
            subset.push(lab);
            return false;
          }
          return true;
        });
      });
      this.gridOptions.api.setRowData(subset);
      document.getElementById('clear-button').classList.remove('d-none');
    }
  },

  searchLabTableClear() {
    /**
     * Clear the search and reset the table.
     */
    const currentState = document.getElementById('lab-state-selection').value;
    this.filterLabsByState(currentState);
  },

  viewAllLabs() {
    /**
     * View all of the labs by adjusting the table's height.
     */
    const rowCount = this.gridOptions.api.getDisplayedRowCount();
    const table = document.getElementById('labs-table');
    table.style.height = `${rowCount * 43 + 110}px`;
    document.getElementById('view-all-labs').classList.add('d-none');
    document.getElementById('view-less-labs').classList.remove('d-none');
  },

  viewLessLabs(original = false) {
    /**
     * View only a handful of labs at a time.
     * @param {Boolean} original Whether or not the table should be returned to its original size.
     */
    const currentHeight = document.getElementById('labs-table').style.height;
    if (parseInt(currentHeight, 10) > 540 || original) {
      document.getElementById('labs-table').style.height = '540px';
    }
    document.getElementById('view-all-labs').classList.remove('d-none');
    document.getElementById('view-less-labs').classList.add('d-none');
  },

  /*----------------------------------------------------------------------------
   * Lab Functionality
   *--------------------------------------------------------------------------*/

  toggleEditLab(edit = true) {
    /**
     * Toggle editing for a lab if permitted by the user's account.
     * @param {bool} edit Whether or not the lab can be edited.
     */

    // Keep track of changes.
    const form = document.querySelector('form');
    const data = Object.fromEntries(new FormData(form));

    // Show buttons.
    const editButton = document.getElementById('edit-button');
    const cancelButton = document.getElementById('cancel-button');
    const saveButton = document.getElementById('save-button');
    if (edit) {
      editButton.classList.add('visually-hidden');
      cancelButton.classList.remove('visually-hidden');
      saveButton.classList.remove('visually-hidden');
      this.lab = data;
    } else {
      editButton.classList.remove('visually-hidden');
      cancelButton.classList.add('visually-hidden');
      saveButton.classList.add('visually-hidden');
      Object.keys(this.lab).forEach((key) => {
        document.getElementById(`input-${key}`).value = this.lab[key];
      });
    }

    // Toggle inputs.
    // FIXME: Color input and DEA / A2LA remain disabled.
    const inputs = document.getElementsByClassName('form-control');
    for (let i = 0; i < inputs.length; i++) {
      const input = inputs.item(i);
      if (edit) { // Begin editing.
        input.readOnly = false;
        input.classList.remove('form-control-plaintext');
      }
      else { // Cancel editing, filling in original values.
        input.readOnly = true;
        input.classList.add('form-control-plaintext');
      }
    }
  },

  async suggestLabEdit(event) {
    /**
     * Update a lab through the API.
     * @param {Event} event A user-driven event.
     */
    event.preventDefault();
    const form = new FormData(event.target);
    const data = Object.fromEntries(form.entries());
    authRequest('/src/email/suggestion', data);
    if (response.success) {
      const message = 'Successfully submitted new lab data. Your suggestion will be reviewed and updated upon approval.';
      showNotification('Lab Data Submitted', message, /* type = */ 'success');
    } else {
      const message = 'An error occurred when trying to save lab data. Ensure that you are signed in.';
      showNotification('Error Submitted Lab Data', message, /* type = */ 'error');
    }
    this.toggleEditLab(false);
  },

  suggestAnalyses() {
    /**
     * Suggest analyses for a given lab to the staff.
     */
    // TODO:
  },

  suggestPrices() {
    /**
     * Suggest analyses prices for a given lab to the staff.
     */
    // TODO:
  },

  viewLab(slug) {
    /**
     * View a selected lab.
     * @param {String} slug The lab's name as a slug.
     */
    window.location.href = `${window.location.origin}/testing/labs/${slug}`
  },

}

/*------------------------------------------------------------------------------
  * Lab Utility Functions
  *---------------------------------------------------------------------------*/

const renderAnalyses = (params) => {
  /**
   * Render analyses as chips in an AG grid table.
   * @param {Object} params The parameters passed by AG grid.
   */
  const analyses = params.value;
  // FIXME: Show analyses for each lab as chips.
  // if (analyses) {
  //   let html = '<button class="btn btn-sm nav-link">Suggest analyses</button>';
  //   for (const analysis of analyses) {
  //     // TODO: Style analyses as chips: Assign color based on analysis.

  //     html+= `<span class="badge rounded-pill text-dark bg-info">${analysis}</span>`;
  //   }
  //   return html;
  // } else
  return `
    <a
      class="btn btn-sm nav-link background-hover text-dark"
      href="/contact?topic=analyses"
    >
      Suggest analyses
    </a>`;
};

const renderAuthRequired = (params) => {
  /**
   * Render analyses as chips in an AG grid table.
   * @param {Object} params The parameters passed by AG grid.
   */
  const user = getCurrentUser();
  if (user) {
    if (params.value) return `<span>${params.value}</span>`;
    else return '';
  } else return `
  <button
    class="btn btn-sm nav-link text-dark background-hover"
    onclick="cannlytics.ui.showModal('sign-in-dialog');"
    type="button"
  >
    Sign In or Sign Up to See
  </button>`;
};

const renderViewLabButton = (params) => {
  return `
  <a
    class="btn btn-sm nav-link"
    href="${window.location.origin}/testing/labs/${params.value}"
    title="View Lab"
  >
  🔎
  </a>`;
}
