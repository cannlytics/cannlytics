/**
 * Test Transfers Endpoint with Node.js | Cannlytics Console
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
 
// Create a transfer.

let data = {
  arrived_at: '',
  arrived_at_time: '',
  departed_at: '',
  departed_at_time: '',
  receiver: '',
  receiver_org_id: '',
  sample_count: '',
  sender: '',
  sender_org_id: '',
  status: '',
  transfer_id: 'heart-of-gold',
  transfer_type: 'Delivery',
  transporter: '',
};
 axios.post(`${base}/transfers?organization_id=${orgId}`, data, options)
   .then(response => {
     console.log(response.data);
   })
   .catch(error => {
     console.log(error);
   });
 
// Get transfers.

axios.get(`${base}/transfers?organization_id=${orgId}`, options)
  .then(response => {
    console.log(response.data);
  })
  .catch(error => {
    console.log(error);
  });
 
// Update a transfer.

data = {
  transfer_id: 'heart-of-gold',
  transporter: 'Wiley',
  notes: "He's a good guy."
};
axios.post(`${base}/transfers?organization_id=${orgId}`, data, options)
  .then(response => {
    console.log(response.data);
  })
  .catch(error => {
    console.log(error);
  });
 
// Delete a transfer.

const objID = 'heart-of-gold';
data = { area_id: objID };
axios.delete(`${base}/transfers/${objID}?organization_id=${orgId}`, { data, ...options})
  .then(response => {
    console.log(response.data);
  })
  .catch(error => {
    console.log(error);
  });
 