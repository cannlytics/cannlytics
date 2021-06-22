/**
 * API Interface | Cannlytics Console
 * Author: Keegan Skeate
 * Created: 4/24/2021
 * Updated: 6/21/2021
 * Description: The `api` object interfaces with the Cannlytics API to send
 * and retrieve data to and from the back-end, where data is processed and
 * stored in the Firestore database and Metrc API.
 */

import { authRequest, formDeserialize } from '../utils.js';
 

export const api = {

  /*----------------------------------------------------------------------------
  General create, read, update, and delete (C.R.U.D.)
  ----------------------------------------------------------------------------*/


  get(model, id=null, options={}) {
    /* Retrieve data from the database, either an array of data objects or a
    single object if an ID is specified. Pass params in options to filter the data. */
    const modelType = model.replace(/^./, string[0].toUpperCase());
    if (id) return authRequest(`/api/${model}/${id}`);
    return authRequest(`/api/${model}`, null, options);
  },


  delete(model, id=null) {
    /* Delete an entry from the database, passing the whole object
    as context if available in a form, otherwise just pass the ID. */
    if (id) return authRequest(`/api/${model}/${id}`, null, { delete: true });
    const form = document.getElementById(`${model}-form`);
    const data = formDeserialize(form);
    return authRequest(`/api/${model}`, data, { delete: true });
  },


  save(model, id) {
    /* Create an entry in the database if it does not exist,
    otherwise update the entry. */
    const form = document.getElementById(`${model}-form`);
    const data = formDeserialize(form);
    console.log('TODO: save data:', data);
    return authRequest(`/api/${model}/${id}`, data);
  },


  create(model) {
    /* Create an entry in the database. (Redundant?) */
    return this.save(model);
  },


  update() {
    /* Update an entry in the database. (Redundant?) */
    return this.save(model);
  },


  /* TODO: REMOVE ANYTHING UNUSED BELOW */

  /*----------------------------------------------------------------------------
  Analyses
  ----------------------------------------------------------------------------*/
 
  getAnalysis: (id) => authRequest(`/api/analyses/${id}`),
  getAnalyses: (params) => authRequest('/api/analyses', null, { params }),
  createAnalyses: (data) => authRequest('/api/analyses', data),
  updateAnalyses: (data) => authRequest('/api/analyses', data),
  deleteAnalyses: (data) => authRequest('/api/analyses', data, { delete: true }),

  /*----------------------------------------------------------------------------
  Analytes
  ----------------------------------------------------------------------------*/
 
  getAnalyte: (id) => authRequest(`/api/analytes/${id}`),
  getAnalytes: (params) => authRequest('/api/analytes', null, { params }),
  createAnalytes: (data) => authRequest('/api/analytes', data),
  updateAnalytes: (data) => authRequest('/api/analytes', data),
  deleteAnalytes: (data) => authRequest('/api/analytes', data, { delete: true }),

  /*----------------------------------------------------------------------------
  Areas
  ----------------------------------------------------------------------------*/
 
  getArea: (id) => authRequest(`/api/areas/${id}`),
  getAreas: (params) => authRequest('/api/areas', null, { params }),
  createAreas: (data) => authRequest('/api/areas', data),
  updateAreas: (data) => authRequest('/api/areas', data),
  deleteAreas: (data) => authRequest('/api/areas', data, { delete: true }),

  /*----------------------------------------------------------------------------
  Contacts
  ----------------------------------------------------------------------------*/
 
  getContact: (id) => authRequest(`/api/contacts/${id}`),
  getContacts: (params) => authRequest('/api/contacts', null, { params }),
  createContacts: (data) => authRequest('/api/contacts', data),
  updateContacts: (data) => authRequest('/api/contacts', data),
  deleteContacts: (data) => authRequest('/api/contacts', data, { delete: true }),

  // Contact contacts.
  getContactPeople: (orgId) => authRequest(`/api/contacts/${orgId}/people`),
  createContactPeople: (orgId, data) => authRequest(`/api/contacts/${orgId}/people`, data),
  updateContactPeople: (orgId, data) => authRequest(`/api/contacts/${orgId}/people`, data),
  deleteContactPeople: (orgId, data) => authRequest(`/api/contacts/${orgId}/people`, data, { delete: true }),

  /*----------------------------------------------------------------------------
  Inventory
  ----------------------------------------------------------------------------*/
 
  getItem: (id) => authRequest(`/api/inventory/${id}`),
  getInventory: (params) => authRequest('/api/inventory', null, { params }),
  createInventory: (data) => authRequest('/api/inventory', data),
  updateInventory: (data) => authRequest('/api/inventory', data),
  deleteInventory: (data) => authRequest('/api/inventory', data, { delete: true }),

  /*----------------------------------------------------------------------------
  Instruments
  ----------------------------------------------------------------------------*/
 
  getInstrument: (id) => authRequest(`/api/instruments/${id}`),
  getInstruments: (params) => authRequest('/api/instruments', null, { params }),
  createInstruments: (data) => authRequest('/api/instruments', data),
  updateInstruments: (data) => authRequest('/api/instruments', data),
  deleteInstruments: (data) => authRequest('/api/instruments', data, { delete: true }),

  /*----------------------------------------------------------------------------
  Invoices
  ----------------------------------------------------------------------------*/
 
  getInvoice: (id) => authRequest(`/api/invoices/${id}`),
  getInvoices: (params) => authRequest('/api/invoices', null, { params }),
  createInvoices: (data) => authRequest('/api/invoices', data),
  updateInvoices: (data) => authRequest('/api/invoices', data),
  deleteInvoices: (data) => authRequest('/api/invoices', data, { delete: true }),

  /*----------------------------------------------------------------------------
  Users (Mesh with staff/team/contacts)
  ----------------------------------------------------------------------------*/
 
  getUser: (id) => authRequest(`/api/users/${id}`),
  getUsers: (params) => authRequest('/api/users', null, { params }),
  createUser: (data) => authRequest('/api/users', data),
  updateUser: (data) => authRequest('/api/users', data),
  deleteUser: (data) => authRequest('/api/users', data, { delete: true }),

  // User settings.
  getUserSettings: (userId) => authRequest(`/api/users/${userId}/settings`),
  updateUserSettings: (userId, data) => authRequest(`/api/users/${userId}/settings`, data),

  /*----------------------------------------------------------------------------
  Organizations (Mesh with facilities)
  ----------------------------------------------------------------------------*/
 
  getOrganization: (id) => authRequest(`/api/organizations/${id}`),
  getOrganizations: (params) => authRequest('/api/organizations', null, { params }),
  createOrganizations: (data) => authRequest('/api/organizations', data),
  updateOrganizations: (data) => authRequest('/api/organizations', data),
  deleteOrganizations: (data) => authRequest('/api/organizations', data, { delete: true }),

  // Organization settings.
  getOrganizationSettings: (orgId) => authRequest(`/api/organizations/${orgId}/settings`),
  updateOrganizationSettings: (orgId, data) => authRequest(`/api/organizations/${orgId}/settings`, data),

  /*----------------------------------------------------------------------------
  Transfers
  ----------------------------------------------------------------------------*/
 
  getMeasurement: (id) => authRequest(`/api/measurements/${id}`),
  getMeasurements: (params) => authRequest('/api/measurements', null, { params }),
  createMeasurements: (data) => authRequest('/api/measurements', data),
  updateMeasurements: (data) => authRequest('/api/measurements', data),
  deleteMeasurements: (data) => authRequest('/api/measurements', data, { delete: true }),

  /*----------------------------------------------------------------------------
  Projects
  ----------------------------------------------------------------------------*/
 
  getProject: (id) => authRequest(`/api/projects/${id}`),
  getProjects: (params) => authRequest('/api/projects', null, { params }),
  createProjects: (data) => authRequest('/api/projects', data),
  updateProjects: (data) => authRequest('/api/projects', data),
  deleteProjects: (data) => authRequest('/api/projects', data, { delete: true }),

  /*----------------------------------------------------------------------------
  Results
  ----------------------------------------------------------------------------*/
 
  getResult: (id) => authRequest(`/api/results/${id}`),
  getResults: (params) => authRequest('/api/results', null, { params }),
  createResults: (data) => authRequest('/api/results', data),
  updateResults: (data) => authRequest('/api/results', data),
  deleteResults: (data) => authRequest('/api/results', data, { delete: true }),

  /*----------------------------------------------------------------------------
  Samples
  ----------------------------------------------------------------------------*/
 
  getSample: (id) => authRequest(`/api/samples/${id}`),
  getSamples: (params) => authRequest('/api/samples', null, { params }),
  createSamples: (data) => authRequest('/api/samples', data),
  updateSamples: (data) => authRequest('/api/samples', data),
  deleteSamples: (data) => authRequest('/api/samples', data, { delete: true }),

  /*----------------------------------------------------------------------------
  Transfers
  ----------------------------------------------------------------------------*/
 
  getTransfer: (id) => authRequest(`/api/transfers/${id}`),
  getTransfers: (params) => authRequest('/api/transfers', null, { params }),
  createTransfers: (data) => authRequest('/api/transfers', data),
  updateTransfers: (data) => authRequest('/api/transfers', data),
  deleteTransfers: (data) => authRequest('/api/transfers', data, { delete: true }),

}
