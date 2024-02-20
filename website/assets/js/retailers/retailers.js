/**
 * Retailers JavaScript | Cannlytics Website
 * Copyright (c) 2021-2022 Cannlytics
 * 
 * Authors: Keegan Skeate <https://github.com/keeganskeate>
 * Created: 2/19/2024
 * Updated: 2/19/2024
 * License: MIT License <https://github.com/cannlytics/cannlytics-website/blob/main/LICENSE>
 */

export const retailersJS = {
  
  initializeRetailers() {
    /**
     * Initialize the retailers page.
     */
    var geoJSON = 'https://d3-geomap.github.io/d3-geomap/topojson/countries/USA.json';
    d3.json(geoJSON).then(data => {
      const svg = d3.select('body').append('svg');
      const path = d3.geoPath();
      
      svg.selectAll('path')
        .data(data.features)
        .enter().append('path')
        .attr('d', path)
        .on('click', function(event, d) {
            console.log('State clicked:', d.properties.name);
            // You can use Firestore here to fetch or update data based on the state clicked
        });
    });
  },

};
