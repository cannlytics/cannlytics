/**
 * Test Inventory Endpoint with Node.js | Cannlytics Console
 * Author: Keegan Skeate
 * Created: 7/27/2021
 * Updated: 7/27/2021
 */
 const axios = require('axios');
 require('dotenv').config();

//  Pass API key through the authorization header
// as a bearer token.
const apiKey = process.env.CANNLYTICS_API_KEY;
const options = {
  headers: { 'Authorization' : `Bearer ${apiKey}` }
};

// Define the API and your organization.
// const base = 'https://console.cannlytics.com/api'; // PRODUCTION:
const base = 'http://127.0.0.1:8000/api'; // DEV: ✓
const orgId = 'test-company';
 
// Create an inventory item.

let data = {
  admin_method: null,
  approved: null,
  approved_at: null,
  approved_at_time: '',
  area_id: null,
  area_name: null,
  category_name: null,
  category_type: null,
  dose: '',
  dose_number: '',
  dose_units: null,
  item_id: 'endo',
  item_type: null,
  moved_at: null,
  moved_at_time: '',
  name: 'Item',
  quantity: null,
  quantity_type: null,
  serving_size: '',
  status: null,
  strain_name: null,
  supply_duration_days: '',
  units: null,
  volume: '',
  volume_units: null,
  weight: '',
  weight_units: null
};
axios.post(`${base}/inventory?organization_id=${orgId}`, data, options)
  .then(response => {
    console.log(response.data);
  })
  .catch(error => {
    console.log(error);
  });
 
// Get inventory.

axios.get(`${base}/inventory?organization_id=${orgId}`, options)
  .then(response => {
    console.log(response.data);
  })
  .catch(error => {
    console.log(error);
  });
 
// Update an inventory item.

data = {
  item_id: 'endo',
  strain_name: 'Old-time Moonshine',
};
axios.post(`${base}/inventory?organization_id=${orgId}`, data, options)
  .then(response => {
    console.log(response.data);
  })
  .catch(error => {
    console.log(error);
  });
 
// Delete an inventory item.

const objID = 'endo';
data = { area_id: objID };
axios.delete(`${base}/inventory/${objID}?organization_id=${orgId}`, { data, ...options})
  .then(response => {
    console.log(response.data);
  })
  .catch(error => {
    console.log(error);
  });
