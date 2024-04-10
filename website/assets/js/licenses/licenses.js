/**
 * Licenses JavaScript | Cannlytics Website
 * Copyright (c) 2021-2022 Cannlytics
 * 
 * Authors: Keegan Skeate <https://github.com/keeganskeate>
 * Created: 2/13/2024
 * Updated: 3/29/2024
 * License: MIT License <https://github.com/cannlytics/cannlytics-website/blob/main/LICENSE>
 */
import { getCollection, getDocument } from '../firebase.js';
import { formatDecimal } from '../utils.js';

export const licensesJS = {

  async initializeLicensee() {
    /**
     * Initialize the licensee page.
     */
    let data = JSON.parse(localStorage.getItem('licensee'));
    const slug = window.location.pathname.split('/').pop();
    if (data && data.id === slug) {
      console.log('Initializing licensee page from local data:', data);
    } else {
      const path = `public/data/licenses/${slug}`;
      data = await getDocument(path);
      console.log('Initializing licensee page from Firestore:', data);
    }
    // Render licensee data in the UI
    document.getElementById('licenseeImageUrl').src = data.image_url || '';
    document.getElementById('licenseeLegalName').textContent = data.business_legal_name || '';
    document.getElementById('licenseeDbaName').textContent = data.business_dba_name || '';
    document.getElementById('licenseeNumber').textContent = data.license_number || '';
    document.getElementById('licenseeType').textContent = data.license_type || '';

    // Business Information
    document.getElementById('businessLegalName').textContent = data.business_legal_name || '';
    document.getElementById('businessDbaName').textContent = data.business_dba_name || '';

    // License Details
    document.getElementById('licenseType').textContent = data.license_type || '';
    document.getElementById('licenseNumber').textContent = data.license_number || '';
    document.getElementById('licenseStatus').textContent = data.license_status || '';
    document.getElementById('licenseStatusDate').textContent = data.license_status_date || '';
    // Populate other license details

    // Contact Information
    document.getElementById('businessEmail').textContent = data.business_email || '';
    document.getElementById('businessPhone').textContent = data.business_phone || '';
    document.getElementById('businessWebsite').textContent = data.business_website || '';

    // Location
    document.getElementById('premiseStreetAddress').textContent = data.premise_street_address || '';
    document.getElementById('premiseCity').textContent = data.premise_city || '';
    // Populate other location details

  },
  
  initializeLicensees() {
    /**
     * Initialize the licensees page.
     */
    console.log('Initializing licensees page...');
  
    const searchTerm = document.getElementById('searchInput').value;
    const selectedState = document.querySelector('.btn-group .btn-primary').id.replace('btn', '');
    const startDate = null;
    const endDate = null;
  
    // Fetch licensees data from Firestore
    this.fetchLicensees(searchTerm, startDate, endDate, selectedState)
      .then((licensees) => {
        console.log('Licensees:', licensees);

        // Add event listeners for view toggle buttons
        document.getElementById('listViewButton').addEventListener('click', () => {
          this.renderListView(licensees);
        });
        document.getElementById('gridViewButton').addEventListener('click', () => {
          this.renderGridView(licensees);
        });

        // Default to grid view
        this.renderGridView(licensees);

      })
      .catch((error) => {
        console.error('Error initializing licensees:', error);
        const licenseesContainer = document.getElementById('licenseesContainer');
        licenseesContainer.innerHTML = '';
        const errorMessage = document.createElement('p');
        errorMessage.textContent = 'Failed to fetch licensees data. Please try again later.';
        licenseesContainer.appendChild(errorMessage);
      });

  },

  fetchLicensees(searchTerm, startDate, endDate, selectedState) {
    /**
     * Fetch licensees data from Firestore based on search term, date range, and selected state.
     */
    const filters = [];
    if (searchTerm) {
      filters.push({ key: 'business_legal_name', operation: '>=', value: searchTerm });
      filters.push({ key: 'business_legal_name', operation: '<=', value: searchTerm + '\uf8ff' });
    }
    if (selectedState && selectedState !== 'ALL') {
      filters.push({ key: 'state', operation: '==', value: selectedState });
    }
    console.log('FILTERS:');
    console.log(filters);
    return getCollection('data/licenses/all', {
      order: 'business_legal_name',
      max: 10,
      filters: filters,
    });
  },

  renderListView(licensees) {
    /**
     * Render the licensees in a list view.
     */
    document.getElementById('listViewButton').classList.add('btn-primary');
    document.getElementById('listViewButton').classList.remove('btn-outline-primary');
    document.getElementById('gridViewButton').classList.remove('btn-primary');
    document.getElementById('gridViewButton').classList.add('btn-outline-primary');
  
    const licenseesContainer = document.getElementById('licenseesContainer');
    licenseesContainer.innerHTML = '';
  
    if (licensees && licensees.length > 0) {
      licensees.forEach((licensee) => {
        const licenseeCard = createLicenseeCard(licensee);
        licenseesContainer.appendChild(licenseeCard);
      });
  
      // Initialize Masonry after rendering the licensee cards
      new Masonry(licenseesContainer, {
        itemSelector: '.col-sm-6',
        percentPosition: true,
      });
    } else {
      const noDataMessage = document.createElement('p');
      noDataMessage.textContent = 'No licensees data available.';
      licenseesContainer.appendChild(noDataMessage);
    }
  },

  renderGridView(licensees) {
    /**
     * Render the licensees in a grid view.
     */
    document.getElementById('gridViewButton').classList.add('btn-primary');
    document.getElementById('gridViewButton').classList.remove('btn-outline-primary');
    document.getElementById('listViewButton').classList.remove('btn-primary');
    document.getElementById('listViewButton').classList.add('btn-outline-primary');
    const licenseesContainer = document.getElementById('licenseesContainer');
    licenseesContainer.innerHTML = '';
    const gridOptions = {
      columnDefs: [
        { field: 'business_legal_name', headerName: 'Legal Name', flex: 1 },
        { field: 'business_dba_name', headerName: 'DBA Name', flex: 1 },
        {
          field: 'license_number',
          headerName: 'License Number',
          flex: 1,
        },
        {
          field: 'license_type',
          headerName: 'License Type',
          flex: 1,
        },
        {
          field: 'premise_city',
          headerName: 'City',
          flex: 1,
        },
      ],
      rowData: licensees,
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
        const licenseeId = params.data.id;
        localStorage.setItem('licensee', JSON.stringify(params.data));
        window.location.href = `/licenses/${licenseeId}`;
      },
    };
    agGrid.createGrid(licenseesContainer, gridOptions);
    cannlytics.ui.setTableTheme();
  },

  initializeRetailers() {
    /**
     * Initialize the retailers page.
     */
    const stateFipsCodes = {
      "01": "Alabama",
      "02": "Alaska",
      "04": "Arizona",
      "05": "Arkansas",
      "06": "California",
      "08": "Colorado",
      "09": "Connecticut",
      "10": "Delaware",
      "11": "District of Columbia",
      "12": "Florida",
      "13": "Georgia",
      "15": "Hawaii",
      "16": "Idaho",
      "17": "Illinois",
      "18": "Indiana",
      "19": "Iowa",
      "20": "Kansas",
      "21": "Kentucky",
      "22": "Louisiana",
      "23": "Maine",
      "24": "Maryland",
      "25": "Massachusetts",
      "26": "Michigan",
      "27": "Minnesota",
      "28": "Mississippi",
      "29": "Missouri",
      "30": "Montana",
      "31": "Nebraska",
      "32": "Nevada",
      "33": "New Hampshire",
      "34": "New Jersey",
      "35": "New Mexico",
      "36": "New York",
      "37": "North Carolina",
      "38": "North Dakota",
      "39": "Ohio",
      "40": "Oklahoma",
      "41": "Oregon",
      "42": "Pennsylvania",
      "44": "Rhode Island",
      "45": "South Carolina",
      "46": "South Dakota",
      "47": "Tennessee",
      "48": "Texas",
      "49": "Utah",
      "50": "Vermont",
      "51": "Virginia",
      "53": "Washington",
      "54": "West Virginia",
      "55": "Wisconsin",
      "56": "Wyoming"
    };

    function zoomToState(d, us) {
      /**
       * Zoom into an individual state.
       */

      // Show the close button.
      document.getElementById('closeBtn').style.display = 'inline-block';

      d3.select('#state-map').style("display", "block");
  
      // Render the individual state map.
      renderIndividualStateMap(d, us);

      // Hide the national map.
      d3.select('#map').style("display", "none");

    }

    function renderIndividualStateMap(d, us) {
      /**
       * Render an individual state map.
       */
  
      // Get the state from the topojson data.
      const states = topojson.feature(us, us.objects.states).features;
      const state = states.find(s => s.id === d.id);
    
      // Prepare the SVG container for the state map.
      const stateMapDiv = d3.select('#state-map');
      stateMapDiv.selectAll("*").remove(); // Clear previous content
      const mapDiv = document.getElementById('state-map');
      const width = mapDiv.offsetWidth;
      const height = mapDiv.offsetHeight;

      // Assuming the initial projection was used to draw the national map.
      const statePath = d3.geoPath(); // Reuse the path generator with the initial projection
    
      // Append a new SVG for the state.
      const stateSVG = stateMapDiv.append('svg')
        .attr('width', width)
        .attr('height', height);
    
      // Calculate bounding box for the state path.
      const bounds = statePath.bounds(state),
            dx = bounds[1][0] - bounds[0][0],
            dy = bounds[1][1] - bounds[0][1],
            x = (bounds[0][0] + bounds[1][0]) / 2,
            y = (bounds[0][1] + bounds[1][1]) / 2;
    
      // Compute scale and translation to fit the state in the container.
      const scale = .95 / Math.max(dx / width, dy / height);
      const translate = [(width / 2) - scale * x, (height / 2) - scale * y];
    
      // Render the state path with the computed transformation.
      stateSVG.append("path")
          .datum(state)
          .attr("fill", "#ccc")
          .attr("d", statePath)
          .attr("stroke", "white")
          .attr("stroke-linejoin", "round")
          .attr("transform", "translate(" + translate + ")scale(" + scale + ")");
    
      // Show the close button.
      document.getElementById('closeBtn').style.display = 'block';
    }

    // Load the map.
    const geoJSON = 'https://d3js.org/us-10m.v1.json';
    const mapDiv = document.getElementById('map'); // Get the container element
    const width = mapDiv.offsetWidth; // Use the container's width
    const height = window.innerHeight; // Use the window's height or any other logic for the height
    console.log('Width:', width, 'Height:', height);
    const aspectRatio = { width: 960, height: 600 };

    // Create the SVG element inside the map container with a viewBox.
    const svg = d3.select('#map').append('svg')
                  .attr('viewBox', `0 0 ${aspectRatio.width} ${aspectRatio.height}`);

    // Render the map.
    let path = d3.geoPath();
    d3.json(geoJSON).then(us => {
        var states = topojson.feature(us, us.objects.states).features;

        // Paths for each state.
        svg.append("g")
          .selectAll("path")
          .data(states)
          .join("path")
          .attr("fill", "#ccc")
          .attr("d", path)
          .on('click', function(event, d) {
            zoomToState(d, us);
            document.getElementById('closeBtn').style.display = 'inline-block'; // Show the close button.
          })
          .append("title")
          .text(d => stateFipsCodes[d.id]);
          
        // Outline between states.
        svg.append("path")
           .datum(topojson.mesh(us, us.objects.states, (a, b) => a !== b))
           .attr("fill", "none")
           .attr("stroke", "white")
           .attr("stroke-linejoin", "round")
           .attr("d", path);
    });

    // Attach close functionality.
    document.getElementById('closeBtn').addEventListener('click', function() {
      this.style.display = 'none'; // Hide the close button.
      d3.select('#state-map').selectAll("*").remove(); // Hide the state map.
      d3.select('#map').style("display", "block"); // Show the national map.
      d3.select('#state-map').style("display", "none");
    });

  },

};

// Helper function to create a licensee card element.
const createLicenseeCard = (licensee) => {
  const cardElement = document.createElement('div');
  cardElement.classList.add('col-sm-6', 'col-md-4', 'mb-4');

  const cardInnerElement = document.createElement('div');
  cardInnerElement.classList.add('card');

  const cardBodyElement = document.createElement('div');
  cardBodyElement.classList.add('card-body');

  const titleElement = document.createElement('h5');
  titleElement.classList.add('card-title');
  titleElement.textContent = licensee.business_legal_name;

  const descriptionElement = document.createElement('p');
  descriptionElement.classList.add('card-text');
  descriptionElement.textContent = licensee.business_dba_name;

  cardBodyElement.appendChild(titleElement);
  cardBodyElement.appendChild(descriptionElement);
  cardInnerElement.appendChild(cardBodyElement);
  cardElement.appendChild(cardInnerElement);

  return cardElement;
};