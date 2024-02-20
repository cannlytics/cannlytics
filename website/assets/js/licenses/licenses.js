/**
 * Licenses JavaScript | Cannlytics Website
 * Copyright (c) 2021-2022 Cannlytics
 * 
 * Authors: Keegan Skeate <https://github.com/keeganskeate>
 * Created: 2/13/2024
 * Updated: 2/19/2024
 * License: MIT License <https://github.com/cannlytics/cannlytics-website/blob/main/LICENSE>
 */

export const licensesJS = {
  
  initializeLicenses() {
    /**
     * Initialize the licenses page.
     */
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
