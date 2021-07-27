/**
 * Test Contacts Endpoint with Node.js | Cannlytics Console
 * Author: Keegan Skeate
 * Created: 7/25/2021
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
 
// Create a contact.

let data = {
  address: '',
  city: '',
  contact_id: 'TEST',
  county: '',
  email: '',
  latitude: '',
  longitude: '',
  organization: 'Cannlytics Test Contact',
  phone: '',
  state: '',
  street: '',
  website: '',
  zip_code: ''
};
axios.post(`${base}/contacts?organization_id=${orgId}`, data, options)
  .then(response => {
    console.log(response.data);
  })
  .catch(error => {
    console.log(error);
  });
 
// Get contacts.

axios.get(`${base}/contacts?organization_id=${orgId}`, options)
  .then(response => {
    console.log(response.data);
  })
  .catch(error => {
    console.log(error);
  });
 
// Update a contact.

data = {
  contact_id: 'TEST',
  city: 'Tulsa',
  state: 'OK',
};
axios.post(`${base}/contacts?organization_id=${orgId}`, data, options)
  .then(response => {
    console.log(response.data);
  })
  .catch(error => {
    console.log(error);
  });
 
// Delete a contact.

const objID = 'TEST';
data = { area_id: objID };
axios.delete(`${base}/contacts/${objID}?organization_id=${orgId}`, { data, ...options})
  .then(response => {
    console.log(response.data);
  })
  .catch(error => {
    console.log(error);
  });
 