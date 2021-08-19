/**
 * Test Samples Endpoint with Node.js | Cannlytics Console
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
 
// Create a sample.

let data = {
  batch_id: '',
  coa_url: '',
  created_at: '07/19/2021',
  created_at_time: '',
  created_by: 'KLS',
  notes: '',
  project_id: 'TEST',
  sample_id: 'SAMPLE-1',
  updated_at: '07/19/2021',
  updated_at_time: '',
  updated_by: ''
};
 axios.post(`${base}/samples?organization_id=${orgId}`, data, options)
   .then(response => {
     console.log(response.data);
   })
   .catch(error => {
     console.log(error);
   });
 
// Get samples.

axios.get(`${base}/samples?organization_id=${orgId}`, options)
  .then(response => {
    console.log(response.data);
  })
  .catch(error => {
    console.log(error);
  });
 
// Update a sample.

data = {
  sample_id: 'SAMPLE-1',
  batch_id: 'Night Crew Batch 86',
};
axios.post(`${base}/samples?organization_id=${orgId}`, data, options)
  .then(response => {
    console.log(response.data);
  })
  .catch(error => {
    console.log(error);
  });
 
// Delete a sample.

const objID = 'TEST';
data = { area_id: objID };
axios.delete(`${base}/samples/${objID}?organization_id=${orgId}`, { data, ...options})
  .then(response => {
    console.log(response.data);
  })
  .catch(error => {
    console.log(error);
  });
 