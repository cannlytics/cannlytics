/**
 * Test Results Endpoint with Node.js | Cannlytics Console
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
 
// Create a result.

let data = {
  approved_at: '',
  approved_at_time: '',
  approved_by: '',
  non_mandatory: 'on',
  notes: '',
  package_id: '',
  package_label: '',
  product_name: '',
  released: 'on',
  released_at: '',
  released_at_time: '',
  result: '',
  result_id: 'RESULT-1',
  reviewed_at: '',
  reviewed_at_time: '',
  reviewed_by: '',
  sample_id: '',
  sample_type: '',
  status: '',
  tested_at: '',
  tested_at_time: '',
  units: '',
  voided_at: '',
  voided_at_time: ''
};
 axios.post(`${base}/results?organization_id=${orgId}`, data, options)
   .then(response => {
     console.log(response.data);
   })
   .catch(error => {
     console.log(error);
   });
 
// Get results.

axios.get(`${base}/results?organization_id=${orgId}`, options)
  .then(response => {
    console.log(response.data);
  })
  .catch(error => {
    console.log(error);
  });
 
// Update a result.

data = {
  result_id: 'RESULT-1',
  notes: 'Now is better than never!',
};
axios.post(`${base}/results?organization_id=${orgId}`, data, options)
  .then(response => {
    console.log(response.data);
  })
  .catch(error => {
    console.log(error);
  });
 
// Delete a result.

const objID = 'TEST';
data = { area_id: objID };
axios.delete(`${base}/results/${objID}?organization_id=${orgId}`, { data, ...options})
  .then(response => {
    console.log(response.data);
  })
  .catch(error => {
    console.log(error);
  });
 