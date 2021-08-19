/**
 * Test Projects Endpoint with Node.js | Cannlytics Console
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
 
// Create a project.

const data = {
created_at: '07/19/2021',
created_at_time: '16:20',
created_by: 'KLS',
notes: '',
organization: 'Cannlytics',
project_id: 'TEST',
received_at: '07/19/2021',
received_at_time: '4:20',
transfer_ids: ''
};
axios.post(`${base}/projects?organization_id=${orgId}`, data, options)
  .then(response => {
    console.log(response.data);
  })
  .catch(error => {
    console.log(error);
  });

// Get projects.

axios.get(`${base}/projects?organization_id=${orgId}`, options)
  .then(response => {
    console.log(response.data);
  })
  .catch(error => {
    console.log(error);
  });
 
// Update a project.

data = {
  project_id: 'TEST',
  notes: 'Too cool for school.',
};
axios.post(`${base}/projects?organization_id=${orgId}`, data, options)
  .then(response => {
    console.log(response.data);
  })
  .catch(error => {
    console.log(error);
  });
 
// Delete a project.

const objID = 'TEST';
data = { area_id: objID };
axios.delete(`${base}/projects/${objID}?organization_id=${orgId}`, { data, ...options})
  .then(response => {
    console.log(response.data);
  })
  .catch(error => {
    console.log(error);
  });
 