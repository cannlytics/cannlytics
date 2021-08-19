/**
 * Test Analyses Endpoint with Node.js | Cannlytics Console
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
const base = 'https://console.cannlytics.com/api'; // PRODUCTION: ✓
// const base = 'http://127.0.0.1:8000/api'; // DEV: ✓
const orgId = 'test-company';

// Create analysis.
let data = {
  'analysis_id': 'hemp-analysis',
  'analytes': ['cbd', 'cbda', 'thc', 'thca'],
  'date': '2021-07-19',
  'initials': 'KLS',
  'key': 'hemp-analysis',
  'name': 'Hemp Analysis',
  'price': '',
  'public': false
};
axios.post(`${base}/analyses?organization_id=${orgId}`, data, options)
  .then(response => {
    console.log('Created:', response.data.data);
  })
  .catch(error => {
    console.log(error);
  });

// Get analyses.
axios.get(`${base}/analyses?organization_id=${orgId}`, options)
  .then(response => {
    console.log( 'Retrieved:', response.data.data);
  })
  .catch(error => {
    console.log(error);
  });

// Update analysis.
data = {
  'analysis_id': 'hemp-analysis',
  'price': '$50',
};
axios.post(`${base}/analyses?organization_id=${orgId}`, data, options)
  .then(response => {
    console.log('Updated:', response.data.data);
  })
  .catch(error => {
    console.log(error);
  });

// Delete analysis.
const objID = 'hemp-analysis';
data = { analysis_id: objID };
axios.delete(`${base}/analyses?organization_id=${orgId}`, { data, ...options})
  .then(response => {
    console.log('Delete:', response.data.data);
  })
  .catch(error => {
    console.log(error);
  });
