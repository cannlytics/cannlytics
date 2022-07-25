/**
 * CoA Data JavaScript | Cannlytics Website
 * Copyright (c) 2022 Cannlytics
 * 
 * Authors: Keegan Skeate <https://github.com/keeganskeate>
 * Created: 7/19/2022
 * Updated: 7/24/2022
 * License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>
 */
import { Html5QrcodeScanner } from 'html5-qrcode';
import { authRequest, showNotification, snakeCase } from '../utils.js';

export const coaJS = {

  initializeQRCodeScanner: initializeQRCodeScanner,
  renderCoAResults: renderCoAResults,
  uploadCoAFile: uploadCoAFile,

  initializeCoADoc() {

    // Wire up reset button.
    document.getElementById('coa-doc-reset-button').onclick = this.resetCoADocForm;

    // Attach import functionality.
    const searchInput = document.getElementById('coa-search-input');
    document.getElementById('coa-doc-search-button').onclick = function() {
      console.log('Function triggered:', searchInput.value);
      document.getElementById('coa-url-input').value = searchInput.value;
    }
    searchInput.addEventListener('keydown', function (e) {
      if (e.code === 'Enter') {
        console.log('Function triggered:', searchInput.value);
        document.getElementById('coa-url-input').value = searchInput.value;
      }
    });

    // Future work: Wire up export data button.
    // 'coa-doc-export-button'

    // Optional: Wire up report error button.
    // coa-doc-report-error-button
    // cannlytics.settings.reportError({ 'status_code': 404, 'version': {{ APP_VERSION_NUMBER }} });

    // Optional: Wire-up request a LIMS/lab button.
    // request-lims-button

    // Optional: Detect if the user is using mobile.

    // Initialize the QR code scanner.
    this.initializeQRCodeScanner();

    // Initialize the drag and drop.
    this.initializeDragAndDrop();

    // TODO: Render the table placeholder!

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
        uploadCoAFile(formData);
    });
  },

  resetCoADocForm() {
    /**
     * Clear the CoA Doc form.
     */
    const template = `Drop a CoA <code>.pdf</code> or a <code>.zip</code>
    of CoAs to parse.`;
    document.getElementById('coa-search-input').value = '';
    document.getElementById('dropbox_background').style.opacity = 0;
    document.getElementById('dropbox-text').innerHTML = template;
    document.getElementById('coa-results-tabs').classList.add('d-none');
    document.getElementById('coa-results-content').classList.add('d-none');
    this.initializeQRCodeScanner();
    // TODO: Clear any uploaded files and the the data table.
  },

  addCoAFile() {
    /**
     * Add a CoA File to be parsed.
     */
    // TODO: Implement!
  },

  addCoAURL() {
    /**
     * Add a CoA URL to be parsed.
     */
    // TODO: Implement!
  },

  removeCoA() {
    /**
     * Remove a CoA that is pending parsing.
     */
    // TODO: Implement!
  },

  parseCoAs() {
    /**
     * Parse all CoA files and URLs pending parsing.
     */
    // TODO: Implement!
  },

  exportCoADataTable() {
    /**
     * Export the CoA data table to a `.xlsx`,
     * `.json`, or `.csv` file.
     */
    // TODO: Implement!
  },

  renderCoADataTable() {
    /**
     * Render the table for CoA data.
     */
    // TODO: Implement!
  },

  renderCoADataTableRow() {
    /**
     * Add a row to the CoA data table.
     */
    // TODO: Implement!

    // First 6 digits of `sample_id`.
    // `product_name`
    // `product_type`
    // `producer`
    // `date_tested`
    // `analyses` as chips
    // `results.length`
  },


  reportError() {
    /**
     * Report encountered error(s).
     */
    // TODO: Implement!
  },

  requestLIMS() {
    /**
     * Request a given lab or LIMS be added to the
     * CoADoc parsing routine.
     */
    // TODO: Implement!
  },

  // TODO: Toggle between table and list views.


}

function renderCoAResults() {
  /**
   * Render the CoA results for the user as both
   * a card in a list of samples as well as a row on a table.
   */
  document.getElementById('coa-results-tabs').classList.remove('d-none');
  document.getElementById('coa-results-content').classList.remove('d-none');
  console.log('Rendering results....');
  // DEV:
  const data = {};
}


function renderCoAImage(obs) {
  /**
   * Render a CoA image, first from an image URL if provided,
   * then from PNG data if provided.
   */
  if (obs.images) {
    console.log('Render first image:', obs.images);
  } else if (obs.image_data) {
    // var blob = new Blob([obs.image_data], {'type': 'image/png'});
    // var url = URL.createObjectURL(blob);
    // console.log('Render:', url);
    var img = document.createElement('img');
    img.src = 'data:image/gif;base64,R0lGODlhEAAOALMAAOazToeHh0tLS/7LZv/0jvb29t/f3//Ub//ge8WSLf/rhf/3kdbW1mxsbP//mf///yH5BAAAAAAALAAAAAAQAA4AAARe8L1Ekyky67QZ1hLnjM5UUde0ECwLJoExKcppV0aCcGCmTIHEIUEqjgaORCMxIC6e0CcguWw6aFjsVMkkIr7g77ZKPJjPZqIyd7sJAgVGoEGv2xsBxqNgYPj/gAwXEQA7';
    img.width = '16';
    img.height = '14';
    document.body.appendChild(img);
  }
  
}


async function uploadCoAFile(formData, formId = 'coa-doc-import-form') {
  /**
   * Upload CoA file for processing.
   * @param {FormData} formData: The CoA file form data.
   * @param {String} formId: If no form data is provided, then provide a form ID.
   */
  if (!formData) formData = new FormData(document.forms[formId]);

  // FIXME: It would be good to do some file checking before posting the form.
  // https://stackoverflow.com/questions/7977084/check-file-type-when-form-submit

  $.ajax({
    headers: { 'X-CSRFToken': cannlytics.utils.getCookie('csrftoken') },
    url: '/api/data/coas',
    type: 'POST',
    data: formData,
    dataType: 'json',
    cache: false,
    contentType: false,
    processData: false,
    success: function(data) {
      // $form.addClass( data.success == true ? 'is-success' : 'is-error' );
      // if (!data.success) $errorMsg.text(data.error);
      // TODO: Render data!
      console.log('Success!');
      console.log(data);
      renderCoAResults(data);
    },
    error: function() {
      // TODO: Show an error message.
    }
  });
}

function initializeQRCodeScanner() {
  /**
   * Initialize the QR Code scanner.
   */
  const qrCodeOptions = { fps: 10, qrbox: {width: 250, height: 250} };
  let html5QrcodeScanner = new Html5QrcodeScanner('reader', qrCodeOptions, false);
  html5QrcodeScanner.render(onScanSuccess, onScanFailure);
  document.getElementById('reader__camera_permission_button').classList.add(
    'btn',
    'btn-sm-light',
    'btn-md-light',
    'mb-1',
    'serif',
  );
  document.getElementById('reader__dashboard_section_swaplink').classList.add(
    'app-action',
    'serif',
  );
}

async function onScanSuccess(decodedText, decodedResult) {
  /**
   * Hand QR code scan success.
   * @param {String} decodedText: The decoded QR code text.
   * @param {Object} decodedResult: The decoded QR code object..
   */
  const postData = { urls: [decodedText] };
  const response = await authRequest('/api/data/coas', postData);
  if (response.success) {

    // TODO: Render the data in the user interface.
    console.log('Response data:', response.data);

  } else {
    const message = 'An error occurred when parsing the CoA. Please try again later or email support.';
    showNotification('Error Parsing CoA', message, /* type = */ 'error');
  }
}

function onScanFailure(error) {
  /**
   * Hand QR code scan failure.
   * @param {Object} error: An error object.
   */
  console.warn(`Code scan error = ${error}`);
  const message = 'An error occurred when parsing the CoA. Please try again later or email support.';
  showNotification('Error Parsing CoA', message, /* type = */ 'error');
}
