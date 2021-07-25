/**
 * Test Analyses Endpoint with Node.js | Cannlytics Console
 * Author: Keegan Skeate
 * Created: 7/25/2021
 * Updated: 7/25/2021
 */
const axios = require('axios');

// Define API parameters.
const apiKey = process.env.apiKey;
const base = 'https://console.cannlytics.com/api'
const orgId = 'test-company';
const options = {
  headers: { 'Authorization' : `Bearer ${apiKey}` }
}

// Create analysis.

// Get analyses.
axios.get(`${base}/analyses?organization_id=${orgId}`, options)
  .then(response => {
    console.log(response.data.url);
    console.log(response.data.explanation);
  })
  .catch(error => {
    console.log(error);
  });

// Update analysis.

// Delete analysis.
