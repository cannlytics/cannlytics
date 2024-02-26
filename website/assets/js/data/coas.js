/**
 * CoADoc JavaScript | Cannlytics Website
 * Copyright (c) 2022 Cannlytics
 * 
 * Authors: Keegan Skeate <https://github.com/keeganskeate>
 * Created: 7/19/2022
 * Updated: 8/21/2022
 * License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>
 */
import { Modal } from 'bootstrap';
import { Html5QrcodeScanner } from 'html5-qrcode';
import { authRequest, downloadBlob, hasClass, showNotification, snakeCase } from '../utils.js';
import { theme } from '../ui/theme.js';

export const CoADoc = {

  // CoADoc parameters.
  minWidth: 100,
  gridOptions: {},
  rowHeight: 40,

  // Local functions.
  downloadSampleResults: downloadSampleResults,
  renderSamplePlaceholder: renderSamplePlaceholder,

  initializeCoADoc() {
    /**
     * Initialize the CoADoc user interface.
     */

    // Wire-up search button and input.
    const searchInput = document.getElementById('coa-search-input');
    document.getElementById('coa-doc-search-button').onclick = function() {
      if (!searchInput.value) {
        const message = 'CoA URL or Metrc ID required.';
        showNotification('Invalid CoA URL / Metrc ID', message, /* type = */ 'error');
        return;
      }
      cannlytics.data.coas.postCoAData({ urls: [searchInput.value] });
    }
    searchInput.addEventListener('keydown', function (e) {
      if (e.code === 'Enter') {
        if (!searchInput.value) {
          const message = 'CoA URL or Metrc ID required.';
          showNotification('Invalid CoA URL / Metrc ID', message, /* type = */ 'error');
          return;
        }
        cannlytics.data.coas.postCoAData({ urls: [searchInput.value] });
      }
    });

    // Future work: Search / autocomplete for metrc ID as the user types?

    // Wire-up CoA file import functions.
    document.getElementById('coa-url-input').onchange = function() {
      cannlytics.data.coas.uploadCoAFile(null, 'coa-url-import-form');
    }
    document.getElementById('coas-input').onchange = function() {
      cannlytics.data.coas.uploadCoAFile();
    }
    document.getElementById('coa-doc-import-button').onclick = function() {
      document.getElementById('coas-input').click();
    }

    // Wire-up download buttons.
    document.getElementById('coa-doc-export-button').onclick = downloadAllResults;
    document.getElementById('download-sample-results-button').onclick = function() {
      cannlytics.data.coas.downloadSampleResults(document.getElementById('download-sample-results-button'));
    }

    // Wire-up save button.
    // document.getElementById('save-sample-results-button').onclick = saveSampleResults;

    // Wire up clear button.
    document.getElementById('coa-doc-clear-button').onclick = this.resetCoADocForm;

    // Wire-up the results modal.
    const modal = document.getElementById('results-modal')
    modal.addEventListener('show.bs.modal', openResults);

    // Initialize the QR code scanner.
    this.initializeQRCodeScanner();

    // Initialize the drag and drop.
    this.initializeDragAndDrop();

    // Initialize the data table.
    this.renderCoADataTable();

  },

  initializeDragAndDrop() {
    /**
     * Initialize the drag-and-drop file upload.
     */
    $(document).on('dragover', 'html', function(e) {
      e.preventDefault();
      e.stopPropagation();
    });
    $(document).on('drop', 'html', function(e) {
      e.preventDefault();
      e.stopPropagation(); 
    });
    $(document).on('dragenter', '.box__dragbox', function (e) {
        e.stopPropagation();
        e.preventDefault();
        document.getElementById('dropbox-text').innerHTML = `Drop your CoA <code>.pdf</code> or a <code>.zip</code> here!`;
        document.getElementById('dropbox_background').style.opacity = 1;
    });
    $(document).on('dragover', '.box__dragbox', function (e) {
        e.stopPropagation();
        e.preventDefault();
        document.getElementById('dropbox-text').innerHTML = `Drop your CoA <code>.pdf</code> or a <code>.zip</code> here!`;
        document.getElementById('dropbox_background').style.opacity = 1;
    });
    $(document).on('dragleave', '.box__dragbox', function (e) {
        e.stopPropagation();
        e.preventDefault();
        document.getElementById('dropbox-text').innerHTML = `Drop a CoA <code>.pdf</code> or a <code>.zip</code> of CoAs to parse.`;
        document.getElementById('dropbox_background').style.opacity = 0;
    });
    $(document).on('drop', '.box__dragbox', function (event) {
        event.stopPropagation();
        event.preventDefault();
        document.getElementById('dropbox-text').innerText = 'Uploaded Coa File!';
        const formData = new FormData();
        const droppedFiles = event.originalEvent.dataTransfer.files;
        $.each( droppedFiles, function(i, file) {
          const { type, name } = file;
          if (!(type.includes('pdf') || type.includes('zip'))) {
            const message = 'Invalid file type. Expecting a .pdf or .zip file.';
            showNotification('Invalid CoA File', message, /* type = */ 'error');
            return;
          }
          const key = snakeCase(name);
          formData.append(key, file);
        });
        cannlytics.data.coas.uploadCoAFile(formData);
    });
  },
  
  initializeQRCodeScanner() {
    /**
     * Initialize the QR Code scanner.
     */
    const qrCodeOptions = { fps: 10, qrbox: {width: 250, height: 250} };
    let html5QrcodeScanner = new Html5QrcodeScanner('reader', qrCodeOptions, false);
    html5QrcodeScanner.render(this.onScanSuccess, this.onScanFailure);
    document.getElementById('html5-qrcode-button-camera-permission').classList.add(
      'btn',
      'btn-sm-light',
      'btn-md-light',
      'mb-1',
      'serif',
    );
    document.getElementById('html5-qrcode-anchor-scan-type-change').classList.add(
      'app-action',
      'serif',
    );
  },

  resetCoADocForm() {
    /**
     * Clear the CoA Doc form.
     */
    cannlytics.data.coas.gridOptions.api.setRowData([]);
    cannlytics.data.coas.initializeQRCodeScanner();
    const template = `Drop a CoA <code>.pdf</code> or a <code>.zip</code>
    of CoAs to parse.`;
    document.getElementById('coa-search-input').value = '';
    document.getElementById('dropbox_background').style.opacity = 0;
    document.getElementById('dropbox-text').innerHTML = template;
    document.getElementById('coa-results-tabs').classList.add('d-none');
    document.getElementById('coa-results-content').classList.add('d-none');
    document.getElementById('coa-sample-results-placeholder').classList.remove('d-none');
    document.querySelectorAll('.sample-card').forEach((card) => {
      card.parentNode.removeChild(card);
    });
  },

  async renderCoAResults(data) {
    /**
     * Render the CoA results for the user as both
     * a card in a list of samples as well as a row on a table.
     * @param {Object} data The CoA results to render.
     */
    const { gridOptions } = cannlytics.data.coas;
    const rows = [];
    await gridOptions.api.forEachNode((rowNode, index) => {
      rows.push(rowNode.data);
    })
    data.forEach((item) => {
      renderCoAResult(item);
      rows.push(item);
    });
    gridOptions.api.setRowData(rows);
    document.getElementById('coa-data-placeholder').classList.add('d-none');
    document.getElementById('coa-sample-results-placeholder').classList.add('d-none');
  },

  async postCoAData(data) {
    /**
     * Post CoA URLs to the CoADoc API for data extraction.
     * @param {Object} data The data for the API POST request.
     */
    const response = await authRequest('/api/data/coas', data);
    if (response.success) {
      this.renderCoAResults(response.data);
    } else {
      const message = 'An error occurred when parsing the CoA. Please try again later or email support.';
      showNotification('Error Parsing CoA', message, /* type = */ 'error');
    }
  },

  async uploadCoAFile(formData, formId = 'coa-doc-import-form') {
    /**
     * Upload CoA file for processing.
     * @param {FormData} formData: The CoA file form data.
     * @param {String} formId: If no form data is provided, then provide a form ID.
     */
  
    // Show a loading placeholder, record the ID for updating later.
    renderSamplePlaceholder();
  
    // Get the form if no data is passed.
    if (!formData) formData = new FormData(document.forms[formId]);
  
    // Optional: It would be good to do further / better file checking before posting the form.
    // https://stackoverflow.com/questions/7977084/check-file-type-when-form-submit

    // Define the success callback.
    const successCallback = this.renderCoAResults;
  
    // Make a request to the CoADoc API.
    $.ajax({
      headers: { 'X-CSRFToken': cannlytics.utils.getCookie('csrftoken') },
      url: '/api/data/coas',
      type: 'POST',
      data: formData,
      dataType: 'json',
      cache: false,
      contentType: false,
      processData: false,
      success: function(response) {
        successCallback(response.data);
      },
      error: function() {
        // Show and error and remove the placeholder.
        const message = 'An error occurred when uploading your CoA for parsing. Please try again later or email support.';
        showNotification('Error Uploading CoA for Parsing', message, /* type = */ 'error');
        try {
          const placeholder = document.querySelector('.sample-placeholder-template');
          placeholder.parentNode.removeChild(placeholder);
        } catch (error) {
          // No placeholder to hide.
        }
      }
    });
  },

  /**
   * QR Code Logic
   */

  async onScanSuccess(decodedText, decodedResult) {
    /**
     * Hand QR code scan success.
     * @param {String} decodedText: The decoded QR code text.
     * @param {Object} decodedResult: The decoded QR code object..
     */
    const postData = { urls: [decodedText] };
    const response = await authRequest('/api/data/coas', postData);
    if (response.success) {
      this.renderCoAResults(response.data);
    } else {
      const message = 'An error occurred when parsing the CoA. Please try again later or email support.';
      showNotification('Error Parsing CoA', message, /* type = */ 'error');
    }
  },

  onScanFailure(error) {
    /**
     * Hand QR code scan failure.
     * @param {Object} error: An error object.
     */
    const message = 'An error occurred when parsing the CoA. Please try again later or email support.';
    showNotification('Error Parsing CoA', message, /* type = */ 'error');
  },

  /**
   * Table functions
   */

  renderCoADataTable() {
    /**
     * Render the table for CoA data.
     */

    // Define the fields.
    const fields = [
      { key: 'product_name', label: 'Product' },
      { key: 'product_type', label: 'Type' },
      { key: 'producer', label: 'Producer' },
      { key: 'date_tested', label: 'Tested' },
      { key: 'analyses', label: 'Analyses' },
      { key: 'number_of_results', label: 'Results' },
    ];

    // Get data model fields from organization settings.
    const columnDefs = fields.map(function(e) { 
      return { headerName: e.label, field: e.key, sortable: true, filter: true };
    });

    // Enable checkbox selection,
    columnDefs[0]['checkboxSelection'] = true;
    columnDefs[0]['headerCheckboxSelection'] = true;

    // Render templates.
    const overlayLoadingTemplate = `
      <div class="spinner-grow text-success" role="status">
        <span class="visually-hidden">Loading...</span>
      </div>
    `;
    const overlayNoRowsTemplate = ``;

    // Specify table options.
    this.gridOptions = {
      columnDefs: columnDefs,
      defaultColDef: { flex: 1,  minWidth: this.minWidth, editable: false },
      enterMovesDownAfterEdit: true,
      overlayLoadingTemplate: overlayLoadingTemplate,
      overlayNoRowsTemplate: overlayNoRowsTemplate,
      pagination: true,
      paginationAutoPageSize: true,
      rowClass: 'app-action',
      rowHeight: this.rowHeight,
      rowSelection: 'multiple',
      singleClickEdit: true,
      suppressRowClickSelection: true,
      onGridReady: event => theme.toggleTheme(theme.getTheme()),
      onRowClicked: onRowClicked,
    };

    // Render the table
    const table = document.getElementById('coa-data-table');
    table.innerHTML = '';
    new agGrid.Grid(table, this.gridOptions);
    this.gridOptions.api.setRowData([]);

  },

  async removeCoADataTableRow(sampleId) {
    /**
     * Remove a row for the CoA data table.
     * @param {String} sampleId A sample ID for the row to be removed.
     */
    const { gridOptions } = cannlytics.data.coas;
    const rows = [];
    await gridOptions.api.forEachNode((rowNode, index) => {
      if (rowNode.data !== sampleId) rows.push(rowNode.data);
    })
    gridOptions.api.setRowData(rows);
  },

};

/**
 * CoA Results functions.
 */

function downloadAllResults() {
  /**
   * Download all of the parsed CoA sample results.
   * If the table is active and only a subset of rows are selected, then
   * only the selected rows are downloaded.
   */
  const data = [];
  const selectedRows = cannlytics.data.coas.gridOptions.api.getSelectedNodes();
  const tableActive = hasClass(document.getElementById('coa-list'), 'active')
  if (selectedRows.length & tableActive) {
    selectedRows.forEach((row) => {
      data.push(row.data);
    });
  } else {
    const allSamples = document.querySelectorAll('.sample-card');
    allSamples.forEach((sampleCard) => {
      const obs = JSON.parse(sampleCard.querySelector('.sample-data').textContent);
      data.push(obs);
    });
  }
  downloadCoAData(data);
}

async function downloadSampleResults(event) {
  /**
   * Download the results for a single parsed CoA sample.
   */
  const sampleId = event.getAttribute('data-bs-sample');
  const sampleCard = document.getElementById(`sample-${sampleId}`);
  const obs = JSON.parse(sampleCard.querySelector('.sample-data').textContent);
  downloadCoAData([obs]);
}

async function downloadCoAData(data) {
  /**
   * Make a request to format a CoA datafile for downloading.
   */
  const postData = { data };
  const timestamp = new Date().toISOString().slice(0, 19).replace(/T|:/g, '-');
  // FIXME: This is throwing a 403 error.
  try {
    const response = await authRequest('/api/data/coas/download', postData, { file: true });
    const blob = await response.blob();
    downloadBlob(blob, /* filename = */ `coa-data-${timestamp}.xlsx`);
  } catch(error) {
    const message = 'Error downloading CoA data. Please try again later and/or contact support.';
    showNotification('Download Error', message, /* type = */ 'error' );
  }
}

function onRowClicked(row) {
  /**
   * Open the modal of sample results when a row of the table is clicked.
   * @param {RowNode} row A table row.
   */
  const modal = new Modal(document.getElementById('results-modal'), {});;
  modal.show();
  renderSampleResults(row.data.sample_id);
}

function openResults(event) {
  /**
   * Open a sample's results in a modal.
   * @param {Event} event The button that triggered the function.
   */
  try {
    const button = event.relatedTarget;
    const sampleId = button.getAttribute('data-bs-sample');
    renderSampleResults(sampleId);
  } catch (error) {
    // Results rendered through table click.
  }
}

function renderSampleImage(el, sample) {
  /**
   * Render a sample's image given it's data. Render's a default image if no image is found.
   * @param {Element} el An element containing an image element with a ".sample-image" class.
   * @param {Map} sample The sample data, including a `images`, `image_url`, `image_data, or `lab_image_url` field.
   */
  const img = el.querySelector('.sample-image');
  const defaultImage = 'https://firebasestorage.googleapis.com/v0/b/cannlytics.appspot.com/o/public%2Fimages%2Fbackgrounds%2Fmisc%2Fsample-placeholder.png?alt=media&token=e8b96368-5d80-49ec-bbd0-3d21654b677f';
  if (sample.images === null) {
    if (sample.image_data) img.src = sample.image_data;
    else if (sample.image_url) img.src = sample.image_url;
    else if (sample.lab_image_url) img.src = sample.lab_image_url;
    else img.src = defaultImage;
  } else {
    try {
      if (sample.images.length) img.src = sample.images[0]['url'];
      else img.src = defaultImage;
    } catch(error) {
      img.src = defaultImage;
    }
  }
  img.classList.remove('d-none');
}

function renderSampleResults(sampleId) {
  /**
   * Render the sample results in the modal.
   * @param {String} sampleId A sample ID for the sample results to be rendered.
   */

  // Get sample data from appropriate `.sample-data` element textContent.
  const sampleCard = document.getElementById(`sample-${sampleId}`);
  const obs = JSON.parse(sampleCard.querySelector('.sample-data').textContent);
  
  /* TODO: Render all of the sample details.

    Sample Details
    - product_name
    - product_type
    - sample_id (generated)
    - strain_name (augmented)
    - lab_id
    - batch_number
    - metrc_ids
    - metrc_lab_id
    - metrc_source_id

    Analysis Overview
    - analyses (with method and status)
    - coa_urls
    - date_collected
    - date_received
    - date_tested
    - status
    - total_cannabinoids
    - total_thc
    - total_cbd
    - total_cbg
    - total_thcv
    - total_cbc
    - total_cbdv
    - total_terpenes

    Product Information
    - product_size
    - serving_size
    - servings_per_package
    - sample_weight

    Producer Information
    - producer_address
    - producer_street
    - producer_city
    - producer_state
    - producer_zipcode
    - producer_license_number

    Distributor Information
    - distributor
    - distributor_address
    - distributor_street
    - distributor_city
    - distributor_state
    - distributor_zipcode
    - distributor_license_number

    Lab Information
    - lab
    - lab_image_url
    - lab_license_number
    - lab_address
    - lab_street
    - lab_city
    - lab_county (augmented)
    - lab_state
    - lab_zipcode
    - lab_phone
    - lab_email
    - lab_website
    - lab_latitude (augmented)
    - lab_longitude (augmented)

  */
  const el = document.querySelector('.modal-sample-details');
  renderSampleImage(el, obs);
  el.querySelector('.product-name').innerText = obs.product_name;
  el.querySelector('.product-type').innerText = obs.product_type;
  if (obs.producer) el.querySelector('.producer').innerText = obs.producer;
  el.querySelector('.date-tested').innerText = obs.date_tested;
  el.querySelector('.sample-data').textContent = JSON.stringify(obs);

  // Wire up / ensure the the download button works!
  document.getElementById('download-sample-results-button').setAttribute('data-bs-sample', obs.sample_id);

  // Change the modal title.
  const modalTitle = document.querySelector('.modal-title')
  modalTitle.textContent = `Sample Results | ${obs.product_name}`;

  // Render the results in a table.
  renderSampleResultsTable(obs.results)

}

function renderSampleResultsTable(results) {
  /**
   * Render a table to display the sample results.
   */
  const fields = [
    { key: 'analysis', label: 'Analysis' },
    { key: 'name', label: 'Compound' },
    { key: 'value', label: 'Result' },
    { key: 'units', label: 'Units' },
    { key: 'status', label: 'Status' },
  ];
  const columnDefs = fields.map(function(e) { 
    return { headerName: e.label, field: e.key, sortable: true, filter: true, editable: false };
  });
  const overlayLoadingTemplate = `
    <div class="spinner-grow text-success" role="status">
      <span class="visually-hidden">Loading...</span>
    </div>
  `;
  const overlayNoRowsTemplate = ``;
  const resultsGridOptions = {
    columnDefs: columnDefs,
    defaultColDef: { flex: 1,  minWidth: 100, editable: false },
    enterMovesDownAfterEdit: true,
    overlayLoadingTemplate: overlayLoadingTemplate,
    overlayNoRowsTemplate: overlayNoRowsTemplate,
    rowClass: 'app-action',
    rowHeight: 25,
    singleClickEdit: true,
    suppressRowClickSelection: true,
    onGridReady: event => theme.toggleTheme(theme.getTheme()),
  };
  const table = document.getElementById('results-data-table');
  table.innerHTML = '';
  new agGrid.Grid(table, resultsGridOptions);
  resultsGridOptions.api.setRowData(results);
}

function renderSamplePlaceholder() {
  /**
   * Render a placeholder for a loading sample.
   */
  
  // Hide the general placeholder.
  document.getElementById('coa-sample-results-placeholder').classList.add('d-none');
  document.getElementById('coa-results-tabs').classList.remove('d-none');
  document.getElementById('coa-results-content').classList.remove('d-none');

  // Clone the sample template.
  const timestamp = new Date().toISOString().slice(0, 19).replaceAll(':', '-');
  const docFrag = document.createDocumentFragment();
  const el = document.getElementById('sample-placeholder-template').cloneNode(true);
  el.classList.add('sample-card', 'sample-placeholder-rendered');
  el.classList.remove('d-none');
  el.id = `${el.id}-${timestamp}`;

  // Wire-up the remove button.
  el.querySelector('.btn').onclick = function() {
    el.parentNode.removeChild(el);
    const placeholder = document.querySelector('.sample-card');
    if (!placeholder) {
      document.getElementById('coa-sample-results-placeholder').classList.remove('d-none');
    }
  };

  // Add the card to the UI.
  docFrag.appendChild(el);
  const grid = document.getElementById('coa-grid-container');
  grid.insertBefore(docFrag, grid.firstChild);
}

function renderCoAResult(obs) {
  /**
   * Render the CoA results for the user as both
   * a card in a list of samples as well as a row on a table.
   * @param {Object} obs The CoA result data.
   */
  document.getElementById('coa-results-tabs').classList.remove('d-none');
  document.getElementById('coa-results-content').classList.remove('d-none');
  const sampleId = obs.sample_id;
  
  // Remove the first placeholder.
  try {
    const placeholder = document.querySelector('.sample-placeholder-rendered');
    placeholder.parentNode.removeChild(placeholder);
  } catch (error) {
    // No placeholder to hide.
  }

  // Clone the sample template.
  const docFrag = document.createDocumentFragment();
  const el = document.getElementById('sample-card-template').cloneNode(true);
  el.classList.add('sample-card');
  el.id = `sample-${sampleId}`;

  // Add the sample details.
  // Optional: Add more sample details.
  renderSampleImage(el, obs);
  el.querySelector('.product-name').innerText = obs.product_name;
  el.querySelector('.product-type').innerText = obs.product_type;
  if (obs.producer) el.querySelector('.producer').innerText = obs.producer;
  el.querySelector('.date-tested').innerText = obs.date_tested;
  el.querySelector('.stretched-link').setAttribute('data-bs-sample', sampleId);
  el.querySelector('.sample-data').textContent = JSON.stringify(obs);

  // Wire-up the remove button.
  el.querySelector('.btn').onclick = function() {
    cannlytics.data.coas.removeCoADataTableRow(sampleId);
    el.parentNode.removeChild(el);
    const placeholder = document.querySelector('.sample-card');
    if (!placeholder) {
      document.getElementById('coa-sample-results-placeholder').classList.remove('d-none');
    }
  };

  // Add the card to the UI.
  el.classList.remove('d-none');
  docFrag.appendChild(el);
  const grid = document.getElementById('coa-grid-container');
  grid.insertBefore(docFrag, grid.firstChild);
}

// TODO: Add the ability for user's to save their lab results to their account.
// function saveSampleResults() {
//   /**
//    * Save edited sample results for downloading.
//    */

//   // Future work: Get the edited data.
//   console.log('Save the sample results!')

//   // Future work: Update the sample `el` by sampleId!
//   // const sampleId = event.getAttribute('data-bs-sample');
//   // const sampleCard = document.getElementById(`sample-${sampleId}`);
//   // el.querySelector('.sample-data').textContent = JSON.stringify(obs);
// }
