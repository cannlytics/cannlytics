/**
 * Test Measurements Endpoint with Node.js | Cannlytics Console
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
 
// Create a measurement.

let data = {
  analysis: '',
  analysis_id: '',
  analyte: '',
  analyte_id: '',
  created_at: '',
  created_at_time: '',
  created_by: '',
  dilution_factor: '',
  instrument: '',
  instrument_id: '',
  measurement: '',
  measurement_id: 'M-5',
  measurement_units: '',
  notes: '',
  product_name: '',
  sample_id: 'S2',
  sample_type: '',
  sample_weight: '',
  units: ''
};
axios.post(`${base}/measurements?organization_id=${orgId}`, data, options)
  .then(response => {
    console.log(response.data);
  })
  .catch(error => {
    console.log(error);
  });
 
// Get measurements.

axios.get(`${base}/measurements?organization_id=${orgId}`, options)
  .then(response => {
    console.log(response.data);
  })
  .catch(error => {
    console.log(error);
  });
 
// Update a measurement.

data = {
  measurement_id: 'M-5',
  notes: 'Be careful what you measure.',
};
axios.post(`${base}/measurements?organization_id=${orgId}`, data, options)
  .then(response => {
    console.log(response.data);
  })
  .catch(error => {
    console.log(error);
  });
 
// Delete a measurement.

const objID = 'TEST';
data = { area_id: objID };
axios.delete(`${base}/measurements/${objID}?organization_id=${orgId}`, { data, ...options})
  .then(response => {
    console.log(response.data);
  })
  .catch(error => {
    console.log(error);
  });
 