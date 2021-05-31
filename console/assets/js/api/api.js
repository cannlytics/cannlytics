/**
 * API Interface | Cannlytics Console
 * Author: Keegan Skeate
 * Created: 4/24/2021
 * Description: The `api` object interfaces with the Cannlytics API to send
 * and retrieve data to and from the back-end, where data is processed and
 * stored in the Firestore database and Metrc API.
 */

import { authRequest } from '../utils.js';
 

export const api = {

  /*----------------------------------------------------------------------------
  Analyses
  ----------------------------------------------------------------------------*/
 
  getAnalyses: (params) => authRequest('/api/analysis', null, { params }),
  createAnalysis: (data) => authRequest('/api/analysis', data),
  updateAnalysis: (data) => authRequest('/api/analysis', data),
  deleteAnalysis: (data) => authRequest('/api/analysis', data, { delete: true }),

  /*----------------------------------------------------------------------------
  Analytes
  ----------------------------------------------------------------------------*/
 
  getAnalytes: (params) => authRequest('/api/analytes', null, { params }),
  createAnalyte: (data) => authRequest('/api/analytes', data),
  updateAnalyte: (data) => authRequest('/api/analytes', data),
  deleteAnalyte: (data) => authRequest('/api/analytes', data, { delete: true }),

  /*----------------------------------------------------------------------------
  Areas
  ----------------------------------------------------------------------------*/
 
  getAreas: (params) => authRequest('/api/areas', null, { params }),
  createArea: (data) => authRequest('/api/areas', data),
  updateArea: (data) => authRequest('/api/areas', data),
  deleteArea: (data) => authRequest('/api/areas', data, { delete: true }),

  /*----------------------------------------------------------------------------
  Clients
  ----------------------------------------------------------------------------*/
 
  getClients: (params) => authRequest('/api/clients', null, { params }),
  createClient: (data) => authRequest('/api/clients', data),
  updateClient: (data) => authRequest('/api/clients', data),
  deleteClient: (data) => authRequest('/api/clients', data, { delete: true }),

  // Client contacts.
  getClientContacts: (orgId) => authRequest(`/api/clients/${orgId}/contacts`),
  createClientContact: (orgId, data) => authRequest(`/api/clients/${orgId}/contacts`, data),
  updateClientContact: (orgId, data) => authRequest(`/api/clients/${orgId}/contacts`, data),
  deleteClientContact: (orgId, data) => authRequest(`/api/clients/${orgId}/contacts`, data, { delete: true }),

  /*----------------------------------------------------------------------------
  Inventory
  ----------------------------------------------------------------------------*/
 
  getInventory: (params) => authRequest('/api/inventory', null, { params }),
  createInventory: (data) => authRequest('/api/inventory', data),
  updateInventory: (data) => authRequest('/api/inventory', data),
  deleteInventory: (data) => authRequest('/api/inventory', data, { delete: true }),

  /*----------------------------------------------------------------------------
  Instruments
  ----------------------------------------------------------------------------*/
 
  getInstruments: (params) => authRequest('/api/instruments', null, { params }),
  createInstruments: (data) => authRequest('/api/instruments', data),
  updateInstruments: (data) => authRequest('/api/instruments', data),
  deleteInstruments: (data) => authRequest('/api/instruments', data, { delete: true }),

  /*----------------------------------------------------------------------------
  Invoices
  ----------------------------------------------------------------------------*/
 
  getInvoices: (params) => authRequest('/api/invoices', null, { params }),
  createInvoices: (data) => authRequest('/api/invoices', data),
  updateInvoices: (data) => authRequest('/api/invoices', data),
  deleteInvoices: (data) => authRequest('/api/invoices', data, { delete: true }),

  /*----------------------------------------------------------------------------
  Users (Mesh with staff/team/contacts)
  ----------------------------------------------------------------------------*/
 
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
 
  getOrganizations: (params) => authRequest('/api/organizations', null, { params }),
  createOrganization: (data) => authRequest('/api/organizations', data),
  updateOrganization: (data) => authRequest('/api/organizations', data),
  deleteOrganization: (data) => authRequest('/api/organizations', data, { delete: true }),

  // Organization settings.
  getOrganizationSettings: (orgId) => authRequest(`/api/organizations/${orgId}/settings`),
  updateOrganizationSettings: (orgId, data) => authRequest(`/api/organizations/${orgId}/settings`, data),

  /*----------------------------------------------------------------------------
  Samples
  ----------------------------------------------------------------------------*/
 
  getSamples: (params) => authRequest('/api/samples', null, { params }),
  createSamples: (data) => authRequest('/api/samples', data),
  updateSamples: (data) => authRequest('/api/samples', data),
  deleteSamples: (data) => authRequest('/api/samples', data, { delete: true }),

  /*----------------------------------------------------------------------------
  Transfers
  ----------------------------------------------------------------------------*/
 
  getTransfers: (params) => authRequest('/api/transfers', null, { params }),
  createTransfers: (data) => authRequest('/api/transfers', data),
  updateTransfers: (data) => authRequest('/api/transfers', data),
  deleteTransfers: (data) => authRequest('/api/transfers', data, { delete: true }),

}
