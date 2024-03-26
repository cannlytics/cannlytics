/**
 * Strains JavaScript | Cannlytics Website
 * Copyright (c) 2021-2022 Cannlytics
 * 
 * Authors: Keegan Skeate <https://github.com/keeganskeate>
 * Created: 2/13/2024
 * Updated: 3/25/2024
 * License: MIT License <https://github.com/cannlytics/cannlytics-website/blob/main/LICENSE>
 */
import { getCollection, listenToCollection } from '../firebase.js';

export const strainsJS = {
  
  initializeStrains() {
    /**
     * Initialize the strains page.
     */
    console.log('Initializing strains page...');
  
    const searchTerm = document.getElementById('searchInput').value;
    const startDate = document.getElementById('dateTestedStart').value;
    const endDate = document.getElementById('dateTestedEnd').value;
    const selectedState = document.querySelector('.btn-group .btn-primary').id.replace('btn', '');
  
    // Fetch strains data from Firestore
    this.fetchStrains(searchTerm, startDate, endDate, selectedState)
      .then((strains) => {
        console.log('Strains:', strains);

        // Add event listeners for view toggle buttons
        document.getElementById('listViewButton').addEventListener('click', () => {
          this.renderListView(strains);
        });
        document.getElementById('gridViewButton').addEventListener('click', () => {
          this.renderGridView(strains);
        });

        // Default to grid view
        this.renderGridView(strains);

      })
      .catch((error) => {
        console.error('Error initializing strains:', error);
        const strainsContainer = document.getElementById('strainsContainer');
        strainsContainer.innerHTML = '';
        const errorMessage = document.createElement('p');
        errorMessage.textContent = 'Failed to fetch strains data. Please try again later.';
        strainsContainer.appendChild(errorMessage);
      });
  
    // Listen for real-time updates
    // this.listenForStrainChanges();
  },

  fetchStrains(searchTerm, startDate, endDate, selectedState) {
    /**
     * Fetch strains data from Firestore based on search term, date range, and selected state.
     */
    const filters = [];
    if (searchTerm) {
      filters.push({ key: 'strain_name', operation: '>=', value: searchTerm });
      filters.push({ key: 'strain_name', operation: '<=', value: searchTerm + '\uf8ff' });
    }
    // if (startDate && endDate) {
    //   const startDateISO = new Date(startDate).toISOString();
    //   const endDateISO = new Date(endDate).toISOString();
    //   filters.push({ key: 'updated_at', operation: '>=', value: startDateISO });
    //   filters.push({ key: 'updated_at', operation: '<=', value: endDateISO });
    // }
    // if (selectedState && selectedState !== 'ALL') {
    //   filters.push({ key: 'state', operation: '==', value: selectedState });
    // }
    console.log('FILTERS:');
    console.log(filters);
    return getCollection('public/data/strains', {
      order: 'strain_name',
      max: 10,
      filters: filters,
    });
  },

  listenForStrainChanges() {
    /**
     * Listen for real-time changes to the strains collection.
     */
    const addedCallback = (strain) => {
      const strainsContainer = document.querySelector('.coa-container');
      const strainCard = createStrainCard(strain);
      strainsContainer.appendChild(strainCard);
    };
    const modifiedCallback = (strain) => {
      const strainCard = document.querySelector(`.strain-card[data-id="${strain.id}"]`);
      if (strainCard) {
        const newStrainCard = createStrainCard(strain);
        strainCard.replaceWith(newStrainCard);
      }
    };
    const removedCallback = (strain) => {
      const strainCard = document.querySelector(`.strain-card[data-id="${strain.id}"]`);
      if (strainCard) {
        strainCard.remove();
      }
    };
    listenToCollection(
      'public/data/strains',
      {
        order: 'strain_name',
        max: 10,
      },
      null,
      addedCallback,
      modifiedCallback,
      removedCallback
    );
  },

  renderListView(strains) {
    document.getElementById('listViewButton').classList.add('btn-primary');
    document.getElementById('listViewButton').classList.remove('btn-outline-primary');
    document.getElementById('gridViewButton').classList.remove('btn-primary');
    document.getElementById('gridViewButton').classList.add('btn-outline-primary');
  
    const strainsContainer = document.getElementById('strainsContainer');
    strainsContainer.innerHTML = '';
  
    if (strains && strains.length > 0) {
      strains.forEach((strain) => {
        const strainCard = createStrainCard(strain);
        strainsContainer.appendChild(strainCard);
      });
  
      // Initialize Masonry after rendering the strain cards
      new Masonry(strainsContainer, {
        itemSelector: '.col-sm-6',
        percentPosition: true,
      });
    } else {
      const noDataMessage = document.createElement('p');
      noDataMessage.textContent = 'No strains data available.';
      strainsContainer.appendChild(noDataMessage);
    }
  },

  renderGridView(strains) {
    document.getElementById('gridViewButton').classList.add('btn-primary');
    document.getElementById('gridViewButton').classList.remove('btn-outline-primary');
    document.getElementById('listViewButton').classList.remove('btn-primary');
    document.getElementById('listViewButton').classList.add('btn-outline-primary');
    const strainsContainer = document.getElementById('strainsContainer');
    strainsContainer.innerHTML = '';
    const gridOptions = {
      columnDefs: [
        { field: 'strain_name', headerName: 'Name', flex: 1 },
        { field: 'description', headerName: 'Description', flex: 2 },
        {
          field: 'thc',
          headerName: 'Avg. THC',
          flex: 1,
          valueFormatter: formatDecimal,
        },
        {
          field: 'cbd',
          headerName: 'Avg. CBD',
          flex: 1,
          valueFormatter: formatDecimal,
        },
        {
          field: 'total_terpenes',
          headerName: 'Avg. Terpenes',
          flex: 1,
          valueFormatter: formatDecimal,
        },
      ],
      rowData: strains,
      defaultColDef: {
        resizable: true,
        sortable: true,
        filter: true,
      },
      domLayout: 'autoHeight',
      pagination: true,
      paginationPageSize: 10,
      paginationPageSizeSelector: [5, 10, 20, 50],
    };
    agGrid.createGrid(strainsContainer, gridOptions);
  },

  initializeStrain() {
    /**
     * Initialize the strain page.
     */
  },

};

// Reusable valueFormatter function
const formatDecimal = (params) => {
  if (params.value !== undefined && params.value !== null) {
    return params.value.toFixed(2);
  }
  return '';
};

// Helper function to create a strain card element.
const createStrainCard = (strain) => {
  const cardElement = document.createElement('div');
  cardElement.classList.add('col-sm-6', 'col-md-4', 'mb-4');

  const cardInnerElement = document.createElement('div');
  cardInnerElement.classList.add('card');

  const imageElement = document.createElement('img');
  imageElement.src = strain.image_url || 'path/to/default/image.jpg';
  imageElement.classList.add('card-img-top');
  imageElement.alt = 'Strain';

  const cardBodyElement = document.createElement('div');
  cardBodyElement.classList.add('card-body');

  const titleElement = document.createElement('h5');
  titleElement.classList.add('card-title');
  titleElement.textContent = strain.name;

  const descriptionElement = document.createElement('p');
  descriptionElement.classList.add('card-text');
  descriptionElement.textContent = strain.description || 'No description available.';

  cardBodyElement.appendChild(titleElement);
  cardBodyElement.appendChild(descriptionElement);
  cardInnerElement.appendChild(imageElement);
  cardInnerElement.appendChild(cardBodyElement);
  cardElement.appendChild(cardInnerElement);

  return cardElement;
};
