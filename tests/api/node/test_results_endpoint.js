/**
 * Test Analytes Endpoint with Node.js | Cannlytics Console
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
 
 // Create analyte.
 const data = {
  'analyte_id': 'cbt',
  'cas': 0.0,
  'date': '2021-07-16T00:00:00Z',
  'formula': '((measurement]*40*50)/[mass])/10058',
  'initials': 'KLS',
  'key': 'cbt',
  'limit': 100,
  'lod': 1,
  'loq': 1,
  'measurement_units': 'ppm',
  'name': 'CBT',
  'public': false,
  'result_units': 'percent'
 };
 axios.post(`${base}/analytes?organization_id=${orgId}`, { ...options, ...{ data } })
   .then(response => {
     console.log(response.data.data);
   })
   .catch(error => {
     console.log(error);
   });
 
 // Get analyses.
 axios.get(`${base}/analytes?organization_id=${orgId}`, options)
   .then(response => {
     console.log(response.data.data);
   })
   .catch(error => {
     console.log(error);
   });
 
 // Update analysis.
 const data = {
  'analyte_id': 'cbt',
  'limit': 'n/a',
 };
 axios.post(`${base}/analytes?organization_id=${orgId}`, options)
   .then(response => {
     console.log(response.data.data);
   })
   .catch(error => {
     console.log(error);
   });
 
 // Delete analysis.
 const objID = '';
 axios.delete(`${base}/analytes/${objID}?organization_id=${orgId}`, options)
   .then(response => {
     console.log(response.data.data);
   })
   .catch(error => {
     console.log(error);
   });
 