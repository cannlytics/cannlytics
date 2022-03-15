/**
 * Lab Analyses JavaScript | Cannlytics Website
 * Copyright (c) 2022 Cannlytics
 * 
 * Authors: Keegan Skeate <keegan@cannlytics.com>
 * Created: 1/9/2022
 * Updated: 1/9/2022
 * License: MIT License <https://github.com/cannlytics/cannlytics-website/blob/main/LICENSE>
 */
import { Modal } from 'bootstrap';
import { authRequest, showNotification } from '../utils.js';
import { setTableTheme } from '../ui/ui.js';
import { downloadBlob, sortArrayOfObjects } from '../utils.js';
import { getCurrentUser } from '../firebase.js';

export const labAnalyses = {

  tableData: [],
  gridOptions: {},

  async initializeAnalysesTable() {
    /**
     * Initialize analyses for a lab.
     */

    // Get analyses from the API.
    this.tableData = await this.getAnalyses();
    this.tableData = sortArrayOfObjects(this.tableData, 'name');

    // Define columns.
    const columnDefs = [
      {
        headerName: '', 
        field: 'analysis_id', 
        width: 25,
        sortable: false, 
        autoHeight: true,
        cellRenderer: renderViewAnalysisButton,
        cellClass: 'px-0',
      },
      {
        headerName: 'Analysis',
        field: 'name',
        sortable: true,
        filter: true,
        width: 160,
      },
    ];

    // Specify the table options.
    this.gridOptions = {
      columnDefs: columnDefs,
      rowClass: 'text-black',
      getRowStyle: params => {
        return { background: params.data.color };
      },
      pagination: true,
      paginationAutoPageSize: true,
      onGridReady: event => setTableTheme(),
    };

    // Hide the placeholder and show the table.
    document.getElementById('loading-placeholder').classList.add('d-none');
    document.getElementById('data-table').classList.remove('d-none');

    // Render the table.
    const table = document.querySelector('#analyses-table');
    table.innerHTML = '';
    new agGrid.Grid(table, this.gridOptions);
    this.gridOptions.api.setRowData(this.tableData);

    // View all of the regulations.
    const rowCount = this.gridOptions.api.getDisplayedRowCount();
    table.style.height = `${rowCount * 43 + 90}px`;

  },

  async downloadAnalysesData() {
    /**
     * Download analyses data, prompting the user to sign in if they are not already.
     */
    const user = getCurrentUser();
    if (!user) {
      const modal = new Modal.getInstance(document.getElementById('sign-in-dialog'));
      modal.show();
      return;
    }
    const url = `${window.location.origin}/src/data/download-analyses-data`;
    const time = new Date().toISOString().slice(0, 19).replace(/T|:/g, '-');
    try {
      const response = await authRequest(url);
      const blob = await response.blob();
      downloadBlob(blob, /* filename = */ `analyses-${time}.csv`);
    } catch(error) {
      const message = 'Error downloading analyses data. Please try again later and/or contact support.';
      showNotification('Download Error', message, /* type = */ 'error' );
    }
  },

  async getAnalyses() {
    /**
     * Get analyses through the API.
     * @returns {Array}
     */
    const { data } = await authRequest('/api/data/analyses');
    return data;
  },

};

const renderViewAnalysisButton = (params) => {
  return `
  <a
    class="btn btn-sm nav-link"
    href="${window.location.origin}/testing/analyses/${params.value.replace('_', '-')}"
    title="View Analysis"
  >
  🔎
  </a>`;
}
