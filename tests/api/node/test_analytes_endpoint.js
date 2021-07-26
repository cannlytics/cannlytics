/**
 * Test Analytes Endpoint with Node.js | Cannlytics Console
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
 
// Create an analyte.

let data = {
  analyte_id: 'cbt',
  cas: 0.0,
  date: '2021-07-16T00:00:00Z',
  formula: '((measurement]*40*50)/[mass])/10058',
  initials: 'KLS',
  key: 'cbt',
  limit: 100,
  lod: 1,
  loq: 1,
  measurement_units: 'ppm',
  name: 'CBT',
  public: false,
  result_units: 'percent'
 };
 axios.post(`${base}/analytes?organization_id=${orgId}`, data, options)
   .then(response => {
     console.log(response.data.data);
   })
   .catch(error => {
     console.log(error);
   });
 
// Get analytes.

axios.get(`${base}/analytes?organization_id=${orgId}`, options)
  .then(response => {
    console.log(response.data.data);
  })
  .catch(error => {
    console.log(error);
  });
 
// Update an analyte.

data = {
  analyte_id: 'cbt',
  limit: 'n/a',
 };
axios.post(`${base}/analytes?organization_id=${orgId}`, data, options)
  .then(response => {
    console.log(response.data.data);
  })
  .catch(error => {
    console.log(error);
  });
 
// Delete an analyte.

const objID = 'cbt';
data = { analysis_id: objID };
axios.delete(`${base}/analytes/${objID}?organization_id=${orgId}`, { data, ...options})
  .then(response => {
    console.log(response.data);
  })
  .catch(error => {
    console.log(error);
  });
 