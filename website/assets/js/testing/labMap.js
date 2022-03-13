/**
 * Map JavaScript | Cannlytics Website
 * Copyright (c) 2021-2022 Cannlytics
 * 
 * Authors: Keegan Skeate <keegan@cannlytics.com>
 * Created: 1/17/2021
 * Updated: 1/9/2022
 * License: MIT License <https://github.com/cannlytics/cannlytics-website/blob/main/LICENSE>
 */

const getGoogleClusterInlineSvg = function(color) {
  var encoded = window.btoa('<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" viewBox="-100 -100 200 200"><defs><g id="a" transform="rotate(45)"><path d="M0 47A47 47 0 0 0 47 0L62 0A62 62 0 0 1 0 62Z" fill-opacity="0.7"/><path d="M0 67A67 67 0 0 0 67 0L81 0A81 81 0 0 1 0 81Z" fill-opacity="0.5"/><path d="M0 86A86 86 0 0 0 86 0L100 0A100 100 0 0 1 0 100Z" fill-opacity="0.3"/></g></defs><g fill="' + color + '"><circle r="42"/><use xlink:href="#a"/><g transform="rotate(120)"><use xlink:href="#a"/></g><g transform="rotate(240)"><use xlink:href="#a"/></g></g></svg>');
  return ('data:image/svg+xml;base64,' + encoded);
};

export const labMap = {

  // State
  map: null,
  points: {},
  markerOrange: 'https://firebasestorage.googleapis.com/v0/b/cannlytics.appspot.com/o/public%2Fimages%2Fmaps%2Fmarkers%2Fmarker-orange.png?alt=media&token=264e0fe3-30db-4dd2-be61-8d6e46e5dcea',
  markerGreen: 'https://firebasestorage.googleapis.com/v0/b/cannlytics.appspot.com/o/public%2Fimages%2Fmaps%2Fmarkers%2Fmarker-green.png?alt=media&token=0d4813e6-c9c9-4b21-9b4f-b9879750438a',
  markerClusterStyles: [
    {
      anchorText: [12, 0],
      width: 42,
      height: 42,
      url: getGoogleClusterInlineSvg('#ff7f0e'),
      textColor: '#ffffff',
      textSize: 13,
    },
    {
      anchorText: [16, 0],
      width: 50,
      height: 50,
      url: getGoogleClusterInlineSvg('#2ca02c'),
      textColor: '#ffffff',
      textSize: 13,
    },
    {
      anchorText: [24, 0],
      width: 68,
      height: 68,
      url: getGoogleClusterInlineSvg('#9467bd'),
      textColor: '#ffffff',
      textSize: 13
    },
  ],

  /*----------------------------------------------------------------------------
   * Lab Map Initialization
   *--------------------------------------------------------------------------*/

  async initializeMap() {
    /**
     * Initialize the testing page.
     */
    
    // Draw the map.
    this.map = this.createMap();

    // Create marker spiderfier for overlapping markers.
    const oms = new OverlappingMarkerSpiderfier(this.map, {
      markersWontMove: true,
      markersWontHide: true,
      basicFormatEvents: true,
      ignoreMapClick: true,
    });

    // Get all of the labs.
    const data = await this.getLabs();

    // Create info windows for each lab.
    const markers = await this.createInfoWindows(this.map, oms, data);

    // Cluster dense markers.
    const markerCluster = this.createMarkerClusterer(cannlytics.testing.map, markers);

    // Wire up search.
    this.setupSearch(this.map);

  },

  createMap() {
    /**
     * Render a Google map.
     * @returns {Map}
     */
    return new google.maps.Map(document.getElementById('map'), {
      zoom: 4,
      center: new google.maps.LatLng(39.8283, -98.5795),
      gestureHandling: 'greedy',
      mapTypeId: google.maps.MapTypeId.ROADMAP,
    });
  },

  async createInfoWindows(map, oms, data) {
    /**
     * Create markers with info windows.
     * @param {Map} map The Google map.
     * @param {OverlappingMarkerSpiderfier} oms Overlapping marker spiderfier.
     * @param {Array} data A list of data used in creating info-windows.
     * @returns {Array}
     */
    // var logSearch = this.logSearch;
    const createWindow = this.createMarkerInfoWindow;
    const infowindow = new google.maps.InfoWindow();
    const markers = [];
    let searchOptions = '';
    data.forEach((item, index) => {

      // Alternate marker colors.
      // TODO: Use green for DEA registered hemp testing laboratories.
      // https://www.ams.usda.gov/rules-regulations/hemp/dea-laboratories
      let icon;
      if (index % 2) icon = this.markerOrange;
      else icon = this.markerOrange;     

      // Create marker.
      const marker = new google.maps.Marker({
        icon: icon,
        position: new google.maps.LatLng(item.latitude, item.longitude),
        map: map,
        title: item.name,
      });

      // Open infowindow on click.
      google.maps.event.addListener(marker, 'spider_click', ((marker) => {
        return function() {

          // Ensure that the website is valid.
          let url = item.website;
          if (url) {
            if (!url.startsWith('http')) {
              url = `http://${url}`;
            }
          }
          
          // Ensure that the image URL is valid.
          if (item.image_url) {
            if (!item.image_url.startsWith('http') && url) {
              item.image_url = `${url}${item.image_url}`;
            }
          }
          
          // Format the content.
          const content = createWindow(item);

          // Attach the content to the infowindow.
          infowindow.setContent(content);
          infowindow.open(map, marker);

          // TODO: Log which labs are viewed?
          // logSearch(item.id, 'window_views');
        }
      })(marker));

      // Add marker to list of markers.
      markers.push(marker);
      oms.addMarker(marker);
      const name = item.trade_name ?? item.name;
      this.points[name] = { latitude: item.latitude, longitude: item.longitude };
      searchOptions += `<option value="${name}"/>`;
    });

    // Close infowindow on map click.
    google.maps.event.addListener(map, 'click', function() {
      infowindow.close();
    });

    // Add lab names to search options.
    document.getElementById('searchOptions').innerHTML = searchOptions;

    // Return the list of markers.
    return markers;

  },

  createMarkerClusterer(map, markers) {
    /**
     * Create a clusterer for markers on the map.
     * @param {Map} map The Google map.
     * @param {Array} markers A list of markers to render.
     * @returns {MarkerClusterer}
     */
    return new MarkerClusterer(map, markers, {
      gridSize: 50,
      maxZoom: 10,
      minimumClusterSize: 4,
      styles: this.markerClusterStyles,
    });
  },

  createMarkerInfoWindow(item) {
    /**
     * Creates a marker info window.
     * @param {Object} item Information to render in the info-window.\
     * @returns {String}
     */
    const name = item.trade_name ?? item.name;
    let content = `<div class="text-dark p-3">`;
    content += `
      <a href="/labs/${item.slug}/" target="_blank">
        <img src="${item.image_url}" class="float-start me-3 mb-3" style="max-width:150px;max-height:75px;">
      </a>
      <h5 class="fs-4 mb-0">
        <a class="text-dark serif open-in-new" href="/labs/${item.slug}/">${name}</a>
      </h5>
      <p class="fs-6 mb-3">
        <small class="text-secondary">${item.formatted_address.replace(', USA', '')}</small>
      </p>
      <div class="d-flex w-100"><p class="fs-6">`;
    if (item.phone) {
      content += `Phone: <a href="tel:${item.phone_number}">${item.phone}</a><br>`;
    } else {
      content += `Phone: <a class="btn btn-sm btn-light" href="/labs/${item.slug}/?edit=true">Recommend a phone number</a><br>`;
    }
    if (item.email) {
      content += `Email: <a href="mailto:${item.email}">${item.email}</a><br>`;
    } else {
      content += `Email: <a class="btn btn-sm btn-light" href="/labs/${item.slug}/?edit=true">Recommend an email</a><br>`;
    }
    if (item.website) {
      let url = item.website;
      if (!url.startsWith('https')) url = `https://${url}`;
      content += `Website: <a href="${url}" target="_blank">${item.website}</a>`;
    } else {
      content += `Website: <a class="btn btn-sm btn-light" href="/labs/${item.slug}/?edit=true">Recommend a website</a><br>`;
    }
    content += `</p></div>`;
    if (item.description) content += `<p class="fs-6 mt-3"><small class="serif">${item.description}</small></p>`
    content += `</div>`;
    // TODO: Add analyses with prices.
    return content;
  },

  /*----------------------------------------------------------------------------
   * Lab Map Functionality
   *--------------------------------------------------------------------------*/

  onInput() {
    /**
     * Pan to a marker on selection.
     */
    const val = document.getElementById('searchInput').value;
    const opts = document.getElementById('searchOptions').childNodes;
    for (let i = 0; i < opts.length; i++) {
      if (opts[i].value === val) {
        this.panToMarker(this.map, opts[i].value)
        break;
      }
    }
  },

  panToMarker(map, value) {
    /**
     * Pan to a point on the map.
     * @param {Map} map The Google map.
     * @param {String} value A value to search for on the map.
     */
    document.getElementById('clear-button').classList.remove('d-none');
    const point = this.points[value];
    map.panTo(new google.maps.LatLng(point.latitude, point.longitude));
    map.setZoom(15);
    // this.logSearch(item.id, 'searches');
  },

  setupSearch(map) {
    /**
     * Setup search for the map.
     * @param {Map} map The Google map.
     */
    const clearButton = document.getElementById('clear-button');
    const searchButton = document.getElementById('searchButton');
    const searchInput = document.getElementById('searchInput');
    clearButton.addEventListener('click', () => {
      searchInput.value = '';
      document.getElementById('clear-button').classList.add('d-none');
      map.panTo(new google.maps.LatLng(39.8283, -98.5795));
      map.setZoom(4);
    });
    searchButton.addEventListener('click', () => {
      this.panToMarker(map, searchInput.value);
    });
    searchInput.addEventListener('keydown', (event) => {
      if (event.key === 'Enter') {
        this.panToMarker(map, searchInput.value);
      }
    });
  },

  // Optional: Log which labs people search for.
  // logSearch(id, field) {
  //   /**
  //    * Record when people search or view for a lab.
  //    * @param {String} id The ID for the log.
  //    * @param {String} field The page viewed.
  //    */
  //   const timestamp = new Date().toISOString();
  //   const update = { updated_at: timestamp };
  //   throw new NotImplementedException();
  //   // update[field] = firestore.FieldValue.increment(1);
  //   // updateDocument(`labs/${id}`, update);
  //   // updateDocument(`public/logs/website_logs/${timestamp}`, {
  //   //   action: `Incremented ${field} for ${id}.`,
  //   //   updated_at: timestamp,
  //   // });
  // },

}
