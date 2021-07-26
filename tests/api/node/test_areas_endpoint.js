/**
 * Test Areas Endpoint with Node.js | Cannlytics Console
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
 
// Create an area.

let data = {
  active: true,
  area_id: 'area-51',
  area_type: 'Default',
  name: 'Area 51',
  quarantine: true,
 };
 axios.post(`${base}/areas?organization_id=${orgId}`, data, options)
   .then(response => {
     console.log(response.data);
   })
   .catch(error => {
     console.log(error);
   });
 
// Get areas.

axios.get(`${base}/areas?organization_id=${orgId}`, options)
  .then(response => {
    console.log(response.data);
  })
  .catch(error => {
    console.log(error);
  });
 
// Update an area.

data = {
  area_id: 'area-51',
  active: false,
 };
axios.post(`${base}/areas?organization_id=${orgId}`, data, options)
  .then(response => {
    console.log(response.data);
  })
  .catch(error => {
    console.log(error);
  });
 
// Delete an area.

const objID = 'area-51';
data = { area_id: objID };
axios.delete(`${base}/areas/${objID}?organization_id=${orgId}`, { data, ...options})
  .then(response => {
    console.log(response.data);
  })
  .catch(error => {
    console.log(error);
  });
 