/**
 * Test Instruments Endpoint with Node.js | Cannlytics Console
 * Author: Keegan Skeate
 * Created: 7/25/2021
 * Updated: 7/26/2021
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
 
// Create an instrument.

let data = {
  calibrated_by: '',
  instrument_id: 'TEST',
  area_id: '',
  description: '',
  area_name: '',
  calibrated_at: 0,
  vendor: 'Nomad',
  name: 'Romulus',
  initials: 'KLS',
  instrument_type: 'HPLC',
  date: '2021-07-19T00:00:00Z',
  data_path: ''
};
 axios.post(`${base}/instruments?organization_id=${orgId}`, data, options)
   .then(response => {
     console.log(response.data);
   })
   .catch(error => {
     console.log(error);
   });
 
// Get instruments.

axios.get(`${base}/instruments?organization_id=${orgId}`, options)
  .then(response => {
    console.log(response.data);
  })
  .catch(error => {
    console.log(error);
  });
 
// Update an instrument.

data = {
  calibrated_at: '2020-07-19',
  calibrated_by: 'KLS',
  instrument_id: 'TEST',
  initials: 'KLS',
  name: 'Remus',
  vendor: 'Rome',
};
axios.post(`${base}/instruments?organization_id=${orgId}`, data, options)
  .then(response => {
    console.log(response.data);
  })
  .catch(error => {
    console.log(error);
  });
 
// Delete an instrument.

const objID = 'TEST';
data = { area_id: objID };
axios.delete(`${base}/instruments/${objID}?organization_id=${orgId}`, { data, ...options})
  .then(response => {
    console.log(response.data);
  })
  .catch(error => {
    console.log(error);
  });
 