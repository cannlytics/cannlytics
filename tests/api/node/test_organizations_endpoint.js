/**
 * Test Organizations Endpoint with Node.js | Cannlytics Console
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

// Get organizations.

axios.get(`${base}/organizations`, options)
  .then(response => {
    console.log(response.data);
  })
  .catch(error => {
    console.log(error);
  });

// TODO: Create an organization.

// TODO: Update an organization.

// Should deleting an organization be allowed through the API?
 