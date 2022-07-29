/**
 * CoADoc JavaScript | Cannlytics Website
 * Copyright (c) 2022 Cannlytics
 * 
 * Authors: Keegan Skeate <https://github.com/keeganskeate>
 * Created: 7/19/2022
 * Updated: 7/29/2022
 * License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>
 */
import { Html5QrcodeScanner } from 'html5-qrcode';
import { authRequest, showNotification, snakeCase } from '../utils.js';

export const CoADoc = {
  downloadSampleResults: downloadSampleResults,
  initializeCoADoc: initializeCoADoc,
  initializeDragAndDrop: initializeDragAndDrop,
  initializeQRCodeScanner: initializeQRCodeScanner,
  renderCoAResults: renderCoAResults,
  renderSamplePlaceholder: renderSamplePlaceholder,
  resetCoADocForm: resetCoADocForm,
  uploadCoAFile: uploadCoAFile,
};

/**
 * Initialization functions.
 */

function initializeCoADoc() {

  // FIXME: Attach search import functionality.
  const searchInput = document.getElementById('coa-search-input');
  document.getElementById('coa-doc-search-button').onclick = function() {
    console.log('Function triggered:', searchInput.value);
    renderSamplePlaceholder();
    // document.getElementById('coa-url-input').value = searchInput.value;
  }
  searchInput.addEventListener('keydown', function (e) {
    if (e.code === 'Enter') {
      console.log('Function triggered:', searchInput.value);
      document.getElementById('coa-url-input').value = searchInput.value;
    }
  });

  // Initialize the QR code scanner.
  initializeQRCodeScanner();

  // Initialize the drag and drop.
  initializeDragAndDrop();

  // Wire-up export button.
  document.getElementById('coa-doc-export-button').onclick = downloadResults;

  // Wire-up the results modal.
  const modal = document.getElementById('results-modal')
  modal.addEventListener('show.bs.modal', openResults);

}

function initializeDragAndDrop() {
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

function resetCoADocForm() {
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
  initializeQRCodeScanner();
  const sampleCards = document.querySelectorAll('.sample-card');
  sampleCards.forEach((card) => {
    card.parentNode.removeChild(card);
  });
  // TODO: Clear the data table.
}

/**
 * CoA Results functions.
 */

function downloadResults() {
  /**
   * Download all of the parsed CoA sample results.
   */
  console.log('Download all of the results!');
  // TODO: Implement!
}

async function downloadSampleResults() {
  /**
   * Download the results for a single parsed CoA sample.
   */

  // TODO: Get the sample data from the modal?
  // JSON.parse(jsonString);

  // TODO: Post the JSON to the API for downloading.
  const postData = { data: {} };
  const response = await authRequest('/api/data/coas/download', postData);
}

function openResults(event) {
  const button = event.relatedTarget;
  const sampleId = button.getAttribute('data-bs-sample');
  console.log('Show results for:', sampleId);

  // TODO: Get sample data from appropriate `.sample-data` element textContent.

  // TODO: Wire up the download button!

  // const modalTitle = modal.querySelector('.modal-title')
  // const modalBodyInput = modal.querySelector('.modal-body input')
  // modalTitle.textContent = `New message to ${recipient}`
  // modalBodyInput.value = recipient
}

function removeCoA() {
  /**
   * Remove a CoA that is pending parsing.
   */
  // TODO: Implement!
}

function renderSamplePlaceholder() {
  /**
   * Render a placeholder for a loading sample.
   */
  
  // Hide the general placeholder.
  document.getElementById('coa-sample-results-placeholder').classList.add('d-none');

  // Clone the sample template.
  const timestamp = new Date().toISOString().slice(0, 19).replaceAll(':', '-');
  const docFrag = document.createDocumentFragment();
  const tempNode = document.getElementById('sample-placeholder-template').cloneNode(true);
  tempNode.classList.add('sample-card');
  tempNode.id = `${tempNode.id}-${timestamp}`;

  // Wire-up the remove button.
  tempNode.querySelector('.btn').onclick = function() {
    tempNode.parentNode.removeChild(tempNode);
    const placeholder = document.querySelector('.sample-card');
    if (!placeholder) {
      document.getElementById('coa-sample-results-placeholder').classList.remove('d-none');
    }
  };

  // Add the card to the UI.
  tempNode.classList.remove('d-none');
  docFrag.appendChild(tempNode);
  // document.getElementById('coa-grid-container').appendChild(docFrag);
  const grid = document.getElementById('coa-grid-container');
  grid.insertBefore(docFrag, grid.firstChild);
}

function renderCoAResults(data) {
  /**
   * Render the CoA results for the user as both
   * a card in a list of samples as well as a row on a table.
   */
  data.forEach((item) => {
    renderCoAResult(item);
  });
}

function renderCoAResult(obs) {
  /**
   * Render the CoA results for the user as both
   * a card in a list of samples as well as a row on a table.
   */
  document.getElementById('coa-results-tabs').classList.remove('d-none');
  document.getElementById('coa-results-content').classList.remove('d-none');
  console.log('Rendering results:', obs);
  
  // Remove the first placeholder.
  const placeholder = document.querySelector('.sample-placeholder-template');
  placeholder.parentNode.removeChild(placeholder);

  // Clone the sample template.
  const timestamp = new Date().toISOString().slice(0, 19).replaceAll(':', '-');
  const docFrag = document.createDocumentFragment();
  const tempNode = document.getElementById('sample-card-template').cloneNode(true);
  tempNode.classList.add('sample-card');
  tempNode.id = `${tempNode.id}-${timestamp}`;

  // Add the sample details.
  // TODO: Add more sample details.
  if (obs.images.length) {
    const img = tempNode.querySelector('.sample-image');
    img.src = obs.images[0]['url'];
    img.classList.remove('d-none');
  }
  tempNode.querySelector('.product-name').innerText = obs.product_name;
  tempNode.querySelector('.product-type').innerText = obs.product_type;
  if (obs.producer) tempNode.querySelector('.producer').innerText = obs.producer;
  tempNode.querySelector('.date-tested').innerText = obs.date_tested;
  tempNode.querySelector('.stretched-link').setAttribute('data-bs-sample', obs.sample_id);
  tempNode.querySelector('.sample-data').textContent = JSON.stringify(obs);

  // Wire-up the remove button.
  tempNode.querySelector('.btn').onclick = function() {
    tempNode.parentNode.removeChild(tempNode);
    const placeholder = document.querySelector('.sample-card');
    if (!placeholder) {
      document.getElementById('coa-sample-results-placeholder').classList.remove('d-none');
    }
  };

  // Add the card to the UI.
  tempNode.classList.remove('d-none');
  docFrag.appendChild(tempNode);
  const grid = document.getElementById('coa-grid-container');
  grid.insertBefore(docFrag, grid.firstChild);

  // TODO: Wire-up the sample card to show a modal of sample results.

  // TODO: Keep track of results for downloading!!!

  console.log('Results should be rendered...');

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

/**
 * User interface functions.
 */

async function uploadCoAFile(formData, formId = 'coa-doc-import-form') {
  /**
   * Upload CoA file for processing.
   * @param {FormData} formData: The CoA file form data.
   * @param {String} formId: If no form data is provided, then provide a form ID.
   */

  // Show a loading placeholder, record the ID for updating later.
  renderSamplePlaceholder();

  // Get the form.
  if (!formData) formData = new FormData(document.forms[formId]);

  // FIXME: It would be good to do some file checking before posting the form.
  // https://stackoverflow.com/questions/7977084/check-file-type-when-form-submit

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
      renderCoAResults(response.data);
    },
    error: function() {
      // TODO: Show an error message.
    }
  });
}

/**
 * QR Code Logic
 */

async function onScanSuccess(decodedText, decodedResult) {
  /**
   * Hand QR code scan success.
   * @param {String} decodedText: The decoded QR code text.
   * @param {Object} decodedResult: The decoded QR code object..
   */
  const postData = { urls: [decodedText] };
  const response = await authRequest('/api/data/coas', postData);
  if (response.success) {
    renderCoAResults(response.data);
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

/**
 * Table functions
 */

function exportCoADataTable() {
  /**
   * Export the CoA data table to a `.xlsx`,
   * `.json`, or `.csv` file.
   */
  // TODO: Implement!
}

function renderCoADataTable() {
  /**
   * Render the table for CoA data.
   */
  // TODO: Implement!
}

function renderCoADataTableRow() {
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
}
