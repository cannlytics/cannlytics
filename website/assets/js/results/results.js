/**
 * Results JavaScript | Cannlytics Website
 * Copyright (c) 2021-2022 Cannlytics
 * 
 * Authors: Keegan Skeate <https://github.com/keeganskeate>
 * Created: 2/13/2024
 * Updated: 2/13/2024
 * License: MIT License <https://github.com/cannlytics/cannlytics-website/blob/main/LICENSE>
 */
import { getCollection, getDocument } from '../firebase.js';
import { formatDate, formatDecimal } from '../utils.js';

export const resultsJS = {

  async searchProductNames() {

  },

  async searchCannabinoids() {

  },

  async searchTerpenes() {

  },
  
  initializeResults() {
    /**
     * Initialize the lab results page.
     */
    console.log('Initializing lab results page...');
  
    const searchTerm = document.getElementById('searchInput').value;
    const startDate = document.getElementById('dateTestedStart').value;
    const endDate = document.getElementById('dateTestedEnd').value;
    const selectedState = document.querySelector('.btn-group .btn-primary').id.replace('btn', '');
  
    // Fetch lab results data from Firestore
    this.fetchResults(searchTerm, startDate, endDate, selectedState)
      .then((results) => {
        console.log('Results:', results);

        // Add event listeners for view toggle buttons
        document.getElementById('listViewButton').addEventListener('click', () => {
          this.renderListView(results);
        });
        document.getElementById('gridViewButton').addEventListener('click', () => {
          this.renderGridView(results);
        });

        // Default to grid view
        this.renderGridView(results);

      })
      .catch((error) => {
        console.error('Error initializing results:', error);
        const resultsContainer = document.getElementById('resultsContainer');
        resultsContainer.innerHTML = '';
        const errorMessage = document.createElement('p');
        errorMessage.textContent = 'Failed to fetch lab results data. Please try again later.';
        resultsContainer.appendChild(errorMessage);
      });

  },

  fetchResults(searchTerm, startDate, endDate, selectedState) {
    /**
     * Fetch lab results data from Firestore based on search term, date range, and selected state.
     */
    const filters = [];
    if (searchTerm) {
      filters.push({ key: 'product_name', operation: '>=', value: searchTerm });
      filters.push({ key: 'product_name', operation: '<=', value: searchTerm + '\uf8ff' });
    }
    // FIXME: Add filters.
    // if (startDate && endDate) {
    //   const startDateISO = new Date(startDate).toISOString();
    //   const endDateISO = new Date(endDate).toISOString();
    //   filters.push({ key: 'date_tested', operation: '>=', value: startDateISO });
    //   filters.push({ key: 'date_tested', operation: '<=', value: endDateISO });
    // }
    // if (selectedState && selectedState !== 'ALL') {
    //   filters.push({ key: 'producer_state', operation: '==', value: selectedState });
    // }
    console.log('FILTERS:');
    console.log(filters);
    return getCollection('public/data/lab_results', {
      order: 'date_tested',
      max: 10,
      filters: filters,
    });
  },

  renderListView(results) {
    /**
     * Render the lab results in a list view.
     */
    document.getElementById('listViewButton').classList.add('btn-primary');
    document.getElementById('listViewButton').classList.remove('btn-outline-primary');
    document.getElementById('gridViewButton').classList.remove('btn-primary');
    document.getElementById('gridViewButton').classList.add('btn-outline-primary');
  
    const resultsContainer = document.getElementById('resultsContainer');
    resultsContainer.innerHTML = '';
  
    if (results && results.length > 0) {
      results.forEach((result) => {
        const resultCard = createResultCard(result);
        resultsContainer.appendChild(resultCard);
      });
  
      // Initialize Masonry after rendering the result cards
      new Masonry(resultsContainer, {
        itemSelector: '.col-sm-6',
        percentPosition: true,
      });
    } else {
      const noDataMessage = document.createElement('p');
      noDataMessage.textContent = 'No lab results data available.';
      resultsContainer.appendChild(noDataMessage);
    }
  },

  renderGridView(results) {
    /**
     * Render the lab results in a grid view.
     */
    document.getElementById('gridViewButton').classList.add('btn-primary');
    document.getElementById('gridViewButton').classList.remove('btn-outline-primary');
    document.getElementById('listViewButton').classList.remove('btn-primary');
    document.getElementById('listViewButton').classList.add('btn-outline-primary');
    const resultsContainer = document.getElementById('resultsContainer');
    resultsContainer.innerHTML = '';
    const gridOptions = {
      columnDefs: [
        { field: 'product_name', headerName: 'Product', flex: 1 },
        {
          field: 'date_tested',
          headerName: 'Date Tested',
          flex: 1,
          valueFormatter: formatDate,
        },
        {
          field: 'total_thc',
          headerName: 'Total THC',
          flex: 1,
          valueFormatter: formatDecimal,
        },
        {
          field: 'total_cbd',
          headerName: 'Total CBD',
          flex: 1,
          valueFormatter: formatDecimal,
        },
        {
          field: 'total_terpenes',
          headerName: 'Total Terpenes',
          flex: 1,
          valueFormatter: formatDecimal,
        },
        { field: 'status', headerName: 'Status', flex: 1 },
      ],
      rowData: results,
      defaultColDef: {
        resizable: true,
        sortable: true,
        filter: true,
      },
      domLayout: 'autoHeight',
      pagination: true,
      paginationPageSize: 10,
      paginationPageSizeSelector: [5, 10, 20, 50],
      onRowClicked: (params) => {
        console.log('Selected:', params.data);
        const sampleId = params.data.sample_id;
        localStorage.setItem('result', JSON.stringify(params.data));
        window.location.href = `/results/${sampleId}`;
      },
    };
    agGrid.createGrid(resultsContainer, gridOptions);
    cannlytics.ui.setTableTheme();
  },

  async initializeResult() {
    /**
     * Initialize the result page.
     */
    let data = JSON.parse(localStorage.getItem('result'));
    const slug = window.location.pathname.split('/').pop();
    if (data && data.sample_id === slug) {
      console.log('Initializing result page from local data:', data);
    } else {
      const path = `public/data/lab_results/${slug}`;
      data = await getDocument(path);
      console.log('Initializing result page from Firestore:', data);
    }
  },

  // getLabResults(
  //   state = 'ALL',
  //   compound = null,
  //   producer = null,
  //   timeFrame = null,
  // ) {
  //   const path = 'public/data/lab_results';
  //   const filters =[
  //     {"key": "lab_state", "operation": "==", "value": "MA"},
  //     // {"key": "compound", "operation": "==", "value": "THC"},
  //     // {"key": "producer", "operation": "==", "value": "Cannlytics"},
  //     // {"key": "timestamp", "operation": ">=", "value": "2024-02-01"},
  //   ];
  //   // let query = db.collection('labResults');
  //   // if (state !== 'ALL') {
  //   //   query = query.where('state', '==', state);
  //   // }
  //   // if (compound) {
  //   //   query = query.where('compound', '==', compound);
  //   // }
  //   // if (producer) {
  //   //   query = query.where('producer', '==', producer);
  //   // }
  //   // Time frame filter implementation depends on your data structure
  //   // For example, if filtering for results from the past week:
  //   // const oneWeekAgo = new Date();
  //   // oneWeekAgo.setDate(oneWeekAgo.getDate() - 7);
  //   // query = query.where('timestamp', '>=', oneWeekAgo);
  //   // query.limit(50).get().then((querySnapshot) => {
  //   //   const labResults = [];
  //   //   querySnapshot.forEach((doc) => {
  //   //     labResults.push(doc.data());
  //   //   });
  //   //   renderLabResults(labResults);
  //   // });
  // }

};

// Helper function to create a result card element.
const createResultCard = (result) => {
  const cardElement = document.createElement('div');
  cardElement.classList.add('col-sm-6', 'col-md-4', 'mb-4');

  const cardInnerElement = document.createElement('div');
  cardInnerElement.classList.add('card');

  const cardBodyElement = document.createElement('div');
  cardBodyElement.classList.add('card-body');

  const titleElement = document.createElement('h5');
  titleElement.classList.add('card-title');
  titleElement.textContent = result.product_name;

  const dateElement = document.createElement('p');
  dateElement.classList.add('card-text');
  dateElement.textContent = `Date Tested: ${new Date(result.date_tested).toLocaleDateString()}`;

  const thcElement = document.createElement('p');
  thcElement.classList.add('card-text');
  thcElement.textContent = `Total THC: ${result.total_thc.toFixed(2)}`;

  const cbdElement = document.createElement('p');
  cbdElement.classList.add('card-text');
  cbdElement.textContent = `Total CBD: ${result.total_cbd.toFixed(2)}`;

  const terpenesElement = document.createElement('p');
  terpenesElement.classList.add('card-text');
  terpenesElement.textContent = `Total Terpenes: ${result.total_terpenes.toFixed(2)}`;

  const statusElement = document.createElement('p');
  statusElement.classList.add('card-text');
  statusElement.textContent = `Status: ${result.status}`;

  cardBodyElement.appendChild(titleElement);
  cardBodyElement.appendChild(dateElement);
  cardBodyElement.appendChild(thcElement);
  cardBodyElement.appendChild(cbdElement);
  cardBodyElement.appendChild(terpenesElement);
  cardBodyElement.appendChild(statusElement);
  cardInnerElement.appendChild(cardBodyElement);
  cardElement.appendChild(cardInnerElement);

  return cardElement;
};
