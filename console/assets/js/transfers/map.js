/**
 * Map JavaScript | Cannlytics Console
 * Author: Keegan Skeate
 * Created: 8/12/2021
 * Updated: 8/14/2021
 * Resources:
 *    https://github.com/fullcalendar/fullcalendar-example-projects/blob/master/webpack/src/main.js
 *    https://fullcalendar.io/docs/handlers
 */
import { getDocument } from '../firebase.js';
import { authRequest } from '../utils.js';


export const maps = {

  // State

  map: null,
  points: {},
  markerOrange: '/static/console/images/maps/marker-orange.svg',
  markerGreen: '/static/console/images/maps/marker-green.svg',
  organizations: [],

  // Functions

  initializeMap() {
    /*
     * Initialize a market map, showing labs for products and showing contacts for labs.
     */

    // Draw the map.
    this.map = this.createMap();

    // Create marker spiderfier for overlapping markers.
    var oms = new OverlappingMarkerSpiderfier(this.map, {
      markersWontMove: true,
      markersWontHide: true,
      basicFormatEvents: true,
      ignoreMapClick: true,
    });

    // Get all of the labs.
    this.getLabs().then((data) => {

      this.organizations = data;

      // Create info windows for each lab.
      var markers = this.createInfoWindows(this.map, oms, data);

      // Cluster dense markers.
      this.createMarkerClusterer(this.map, markers);

      // Wire up search.
      this.setupSearch(this.map);

      // Render list.
      this.renderLabList(data);

    });
  },


  createMap() {
    /*
     * Render a Google map.
     */
    return new google.maps.Map(document.getElementById('map'), {
      zoom: 7,
      // TODO: Pan to selected state.
      center: new google.maps.LatLng(35.4676, -97.5164),
      gestureHandling: 'greedy',
      mapTypeId: google.maps.MapTypeId.ROADMAP,
    });
  },


  createInfoWindows(map, oms, data) {
    /*
     * Create markers with info windows.
     */
    var logView = this.logView;
    var createWindow = this.createMarkerInfoWindow;
    var getOrgName = this.getOrganizationName;
    var infoWindow = new google.maps.InfoWindow();
    var markers = [];
    var searchOptions = '';
    data.forEach((item, index) => {

      // Alternate marker colors.
      // Optional: Use green for DEA registered hemp testing laboratories.
      // https://www.ams.usda.gov/rules-regulations/hemp/dea-laboratories
      var icon;
      if (index % 2) icon = this.markerOrange;
      else icon = this.markerOrange;     

      // Create marker.
      var marker = new google.maps.Marker({
        icon: icon,
        position: new google.maps.LatLng(item.latitude, item.longitude),
        map: map,
        title: item.name,
      });

      // Open info window on click.
      google.maps.event.addListener(marker, 'spider_click', ((marker) => {
        return function() {

          // Ensure that the website is valid.
          var url = item.website;
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
          var content = createWindow(item);

          // Attach the content to the info window.
          infoWindow.setContent(content);
          infoWindow.open(map, marker);

          // Open in card instead.
          document.getElementById('item-selected').classList.remove('d-none');
          document.getElementById('item-selected').innerHTML = content;

          // Optional: Log which labs are viewed.
          // logView(item.id, 'window_views');
        }
      })(marker));

      // Add marker to list of markers.
      markers.push(marker);
      oms.addMarker(marker);
      var name = getOrgName(item);
      this.points[name] = { latitude: item.latitude, longitude: item.longitude };
      searchOptions += `<option value="${name}"/>`;
    });

    // Close info window on map click.
    google.maps.event.addListener(map, 'click', function() {
      infoWindow.close();
    });

    // Add lab names to search options.
    document.getElementById('searchOptions').innerHTML = searchOptions;

    return markers;

  },


  createMarkerClusterer(map, markers) {
    /*
     * Create a clusterer for markers on the map.
     */
    return new MarkerClusterer(map, markers, {
      gridSize: 50,
      maxZoom: 10,
      minimumClusterSize: 4,
      imagePath: 'https://developers.google.com/maps/documentation/javascript/examples/markerclusterer/m', // Optional: replace with local path.
    });
  },


  createMarkerInfoWindow(item) {
    /*
     * Creates a marker info window.
     * Optional: Ensure image is a valid image.
     */
    var image = item.image_url ?? 'static/images/icons/multi-tone/lab.svg';
    // var name = this.getOrganizationName(item);
    var name = '';
    if (item.trade_name && item.trade_name != 'Nan') name = item.trade_name;
    else name = item.name;
    var content = `<div class="text-dark p-3 bg-light" style="min-height:320px">`;
    content += `
      <a href="/labs/${item.slug}/" target="_blank" class="bg-light">
        <img src="${image}" class="float-start me-3 mb-3" style="max-width:150px;max-height:75px;">
      </a>`
    if (name) content += `<h6 class="text-dark mb-0">
        <a class="text-dark serif open-in-new" href="/labs/${item.slug}/">${name}</a>
      </h6>`
    content +=
      `<p class="fs-6 mb-3">
        <small class="text-secondary">${item.formatted_address.replace(', USA', '')}</small>
      </p>
      <div class="d-flex w-100"><p class="fs-6">`;
    if (item.phone) {
      content += `<small>Phone: <a class="text-link" href="tel:${item.phone_number}">${item.phone}</a></small><br>`;
    } else {
      content += `Phone: <a class="btn btn-sm btn-light" href="/labs/${item.slug}/?edit=true">Recommend a phone number</a><br>`;
    }
    if (item.email) {
      content += `<small>Email: <a class="text-link" href="mailto:${item.email}">${item.email}</a></small><br>`;
    } else {
      content += `Email: <a class="btn btn-sm btn-light" href="/labs/${item.slug}/?edit=true">Recommend an email</a><br>`;
    }
    if (item.website) {
      var url = item.website;
      if (!url.startsWith('https')) url = `https://${url}`;
      content += `<small>Website: <a class="text-link" href="${url}" target="_blank">${item.website}</a></small>`;
    } else {
      content += `Website: <a class="btn btn-sm btn-light" href="/labs/${item.slug}/?edit=true">Recommend a website</a><br>`;
    }
    content += `</p></div>`;
    if (item.description) content += `<p class="fs-6 mt-3"><small class="tiny-text serif">${item.description}</small></p>`
    // TODO: Add analyses with prices
    // TODO: Add "Transfer Samples" button!
    content += `<div class="mt-3">
      <a class="btn btn-sm bg-gradient-green text-white" href="/transfers/new?receiver=${item.slug}">
        Transfer Samples
      </a>
    </div>`;
    content += `</div>`;
    return content;
  },


  onMapSearchInput() {
    /*
     * Pan to a marker on selection.
     */
    var val = document.getElementById('searchInput').value;
    var opts = document.getElementById('searchOptions').childNodes;
    for (var i = 0; i < opts.length; i++) {
      if (opts[i].value === val) {
        this.panToMarker(this.map, opts[i].value)
        break;
      }
    }
  },

  panToMarker(map, value) {
    /*
     * Pan to a point on the map.
     */
    const point = this.points[value];
    map.panTo(new google.maps.LatLng(point.latitude, point.longitude));
    map.setZoom(15);
    // Optional: Open info window on pan.
    // Optional: Count the number of searches by lab
    // this.logView(item.id, 'searches');
  },


  setupSearch(map) {
    /*
     * Setup search for the map.
     */
    var searchButton = document.getElementById('searchButton');
    var searchInput = document.getElementById('searchInput');
    searchButton.addEventListener('click', () => {
      this.panToMarker(map, searchInput.value)
    });
    searchInput.addEventListener('keydown', (event) => {
      if (event.key === 'Enter') {
        this.panToMarker(map, searchInput.value)
      }
    });
  },


  getLabs() {
    /*
     * Get labs with API.
     */
    return new Promise((resolve, reject) => {
      const state = document.getElementById('state_input').value;
      const url = `/api/organizations/labs?state=${state}`;
      authRequest(url).then((response) => resolve(response.data));
    });
  },


  renderLabList(data) {
    /*
     * Render all labs as a list.
     */
    var div = document.getElementById('lab-list');
    var content = '';
    data.forEach((item) => {
      var image = item.image_url ?? 'static/images/icons/multi-tone/lab.svg';
      var name = this.getOrganizationName(item);
      content += `
      <button
        class="list-group-item list-group-item-action bg-transparent text-dark"
        onclick="cannlytics.transfers.selectLab('${item.slug}')"
      >
        ${name}
      </button>`;
    });
    div.innerHTML += content;
  },


  selectLab(slug) {
    /*
     * Select a lab from the list.
     */
    const item = this.findOrganization(slug, this.organizations);
    const content = this.createMarkerInfoWindow(item);
    document.getElementById('item-selected').classList.remove('d-none');
    document.getElementById('item-selected').innerHTML = content;
    const name = this.getOrganizationName(item);
    this.panToMarker(this.map, name);
  },


  findOrganization(value, array) {
    /*
     * Find an organization's data in memory.
     */
    for (var i=0; i < array.length; i++) {
      if (array[i].slug === value) {
        return array[i];
      }
    }
  },


  getOrganizationName(item) {
    /*
     * Get an organization's preferred name.
     */
    var name = '';
    if (item.trade_name && item.trade_name != 'Nan') name = item.trade_name;
    else name = item.name;
    return name;
  },


  // startTransferSamples() {
  //   /*
  //    * Begin a new transfer with a selected organization.
  //    */
  //   // /transfers/new?
  // },

  // TODO: Similar accordian for analyses.


};
