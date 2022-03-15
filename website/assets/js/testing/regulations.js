/**
 * Lab Regulations JavaScript | Cannlytics Website
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

export const labRegulations = {

  tableData: [],
  gridOptions: {},

  async initializeRegulationsTable() {
    /**
     * Initialize analyses for a lab.
     */

    // Get regulations from the API.
    this.tableData = await this.getRegulations();
    this.tableData = sortArrayOfObjects(this.tableData, 'state');

    // Define columns.
    const columnDefs = [
      {
        headerName: '', 
        field: 'state', 
        width: 25,
        sortable: false, 
        autoHeight: true,
        cellRenderer: renderViewRegulationButton,
        cellClass: 'px-0',
      },
      {
        headerName: 'State',
        field: 'state_name',
        sortable: true,
        filter: true,
        width: 140,
      },
      {
        headerName: 'Adult Use',
        field: 'adult_use',
        sortable: true,
        filter: true,
        width: 140,
        cellRenderer: renderCheck,
        cellClass: 'text-center pe-5',
        headerClass: 'text-center',
      },
      {
        headerName: 'Adult Use Permitted',
        field: 'adult_use_permitted',
        sortable: true,
        filter: true,
        width: 175,
      },
      {
        headerName: 'Medicinal',
        field: 'medicinal',
        sortable: true,
        filter: true,
        width: 140,
        cellRenderer: renderCheck,
        cellClass: 'text-center pe-5',
        headerClass: 'text-center',
      },
      {
        headerName: 'Medicinal Permitted',
        field: 'medicinal_permitted',
        sortable: true,
        filter: true,
        width: 175,
      },
      {
        headerName: 'Traceability',
        field: 'traceability_system',
        sortable: true,
        filter: true,
        width: 150,
      },
    ];

    // Specify the table options.
    this.gridOptions = {
      columnDefs: columnDefs,
      pagination: true,
      paginationAutoPageSize: true,
      onGridReady: event => setTableTheme(),
    };

    // Hide the placeholder and show the table.
    document.getElementById('loading-placeholder').classList.add('d-none');
    document.getElementById('data-table').classList.remove('d-none');

    // Render the table.
    const table = document.querySelector('#regulations-table');
    table.innerHTML = '';
    new agGrid.Grid(table, this.gridOptions);
    this.gridOptions.api.setRowData(this.tableData);

    // View all of the regulations.
    const rowCount = this.gridOptions.api.getDisplayedRowCount();
    table.style.height = `${rowCount * 42.25 + 110}px`;

  },

  async downloadRegulationData() {
    /**
     * Download regulation data, prompting the user to sign in if they are not already.
     */
    const user = getCurrentUser();
    if (!user) {
      const modal = new Modal.getInstance(document.getElementById('sign-in-dialog'));
      modal.show();
      return;
    }
    const url = `${window.location.origin}/src/data/download-regulation-data`;
    const time = new Date().toISOString().slice(0, 19).replace(/T|:/g, '-');
    try {
      const response = await authRequest(url);
      const blob = await response.blob();
      downloadBlob(blob, /* filename = */ `regulations-${time}.csv`);
    } catch(error) {
      const message = 'Error downloading regulations data. Please try again later and/or contact support.';
      showNotification('Download Error', message, /* type = */ 'error' );
    }
  },

  async getRegulations() {
    /**
     * Get regulations through the API.
     * @returns {Array}
     */
    const { data } = await authRequest('/api/data/regulations');
    return data;
  },

};

const renderViewRegulationButton = (params) => {
  return `
  <a
    class="btn btn-sm nav-link"
    href="${window.location.origin}/testing/regulations/${params.value.toLowerCase()}"
    title="View Regulation"
  >
  🔎
  </a>`;
}

const renderCheck = (params) => {
  if (!params.value) return '';
  return `
  <svg
    xmlns:dc="http://purl.org/dc/elements/1.1/"
    xmlns:cc="http://creativecommons.org/ns#"
    xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
    xmlns:svg="http://www.w3.org/2000/svg"
    xmlns="http://www.w3.org/2000/svg"
    xmlns:sodipodi="http://sodipodi.sourceforge.net/DTD/sodipodi-0.dtd"
    xmlns:inkscape="http://www.inkscape.org/namespaces/inkscape"
    id="check-emoji"
    style="width:24px;height:24px;"
    viewBox="0 0 72 72"
    version="1.1"
    sodipodi:docname="check.svg"
    inkscape:version="1.0.1 (3bc2e813f5, 2020-09-07)">
    <metadata
      id="metadata13">
      <rdf:RDF>
        <cc:Work
          rdf:about="">
          <dc:format>image/svg+xml</dc:format>
          <dc:type
            rdf:resource="http://purl.org/dc/dcmitype/StillImage" />
        </cc:Work>
      </rdf:RDF>
    </metadata>
    <defs
      id="defs11" />
    <sodipodi:namedview
      pagecolor="#ffffff"
      bordercolor="#666666"
      borderopacity="1"
      objecttolerance="10"
      gridtolerance="10"
      guidetolerance="10"
      inkscape:pageopacity="0"
      inkscape:pageshadow="2"
      inkscape:window-width="1920"
      inkscape:window-height="1094"
      id="namedview9"
      showgrid="false"
      inkscape:zoom="7.3951584"
      inkscape:cx="17.008886"
      inkscape:cy="32.036678"
      inkscape:window-x="-11"
      inkscape:window-y="-11"
      inkscape:window-maximized="1"
      inkscape:current-layer="emoji" />
    <g
      id="color"
      style="fill:#45b649;fill-opacity:1;">
      <path
        fill="#b1cc33"
        d="m61.5 23.3-8.013-8.013-25.71 25.71-9.26-9.26-8.013 8.013 17.42 17.44z"
        id="path2"
        style="fill:#45b649;fill-opacity:1" />
    </g>
    <g
      id="line">
      <path
        fill="none"
        stroke="#000"
        stroke-linecap="round"
        stroke-linejoin="round"
        stroke-miterlimit="10"
        stroke-width="2"
        d="m10.5 39.76 17.42 17.44 33.58-33.89-8.013-8.013-25.71 25.71-9.26-9.26z"
        id="path5" />
    </g>
  </svg>`;
}
