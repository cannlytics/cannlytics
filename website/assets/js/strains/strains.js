/**
 * Strains JavaScript | Cannlytics Website
 * Copyright (c) 2021-2022 Cannlytics
 * 
 * Authors: Keegan Skeate <https://github.com/keeganskeate>
 * Created: 2/13/2024
 * Updated: 3/26/2024
 * License: MIT License <https://github.com/cannlytics/cannlytics-website/blob/main/LICENSE>
 */
import { getCollection, getDocument } from '../firebase.js';
import { formatDecimal } from '../utils.js';

export const strainsJS = {

  async searchStrainNames() {

  },

  async initializeStrain() {
    /**
     * Initialize the strain page.
     */
    let data = JSON.parse(localStorage.getItem('strain'));
    const slug = window.location.pathname.split('/').pop();
    console.log('Strain slug:', slug);
    if (data && data.id === slug) {
      console.log('Initializing strain page from local data:', data);
    } else {
      const path = `public/data/strains/${slug}`;
      try {
        data = await getDocument(path);
      } catch (error) {
        console.error('Error fetching strain data:', error);
        return;
      }
      console.log('Initializing strain page from Firestore:', data);
    }
    // TODO: Initialize the strain page with the data.
    // document.getElementById('strainName').textContent = data.name;
    // document.getElementById('strainDescription').textContent = data.description;
    // document.getElementById('strainImageUrl').src = data.imageUrl;
    // document.getElementById('strainTotalFavorites').textContent = data.totalFavorites;
    // total_tests
    // strain_type
    // first_date_tested
  },
  
  initializeStrains() {
    /**
     * Initialize the strains page.
     */
    console.log('Initializing strains page...');
  
    const searchTerm = document.getElementById('searchInput').value;
    // const startDate = document.getElementById('dateTestedStart').value;
    // const endDate = document.getElementById('dateTestedEnd').value;
    const selectedState = document.querySelector('.btn-group .btn-primary').id.replace('btn', '');
    const startDate = null;
    const endDate = null;
  
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

  renderListView(strains) {
    /**
     * Render the strains in a list view.
     */
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
    /**
     * Render the strains in a grid view.
     */
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
      onRowClicked: (params) => {
        console.log('Selected:', params.data);
        const strainId = params.data.id;
        localStorage.setItem('strain', JSON.stringify(params.data));
        window.location.href = `/strains/${strainId}`;
      },
    };
    agGrid.createGrid(strainsContainer, gridOptions);
    cannlytics.ui.setTableTheme();
  },

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
