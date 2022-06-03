/**
 * Projects JavaScript | Cannlytics Console
 * Copyright (c) 2021-2022 Cannlytics
 * 
 * Authors: Keegan Skeate <https://github.com/keeganskeate>
 * Created: 6/18/2021
 * Updated: 12/14/2021
 * License: MIT License <https://github.com/cannlytics/cannlytics-console/blob/main/LICENSE>
 */
import { authRequest, deserializeForm, serializeForm, showNotification } from '../utils.js';
import { theme } from '../settings/theme.js';

export const projects = {

  initialize() {
    /**
     * Initialize the projects user interface.
     */
  },

  async getProjects(orgId, licenseNumber, versionId = 'latest') {
    /**
     * Get projects.
     * @param {String} orgId
     * @param {String} licenseNumber
     * @param {String} versionId
     */

    // Get the data.
    // TODO: Add parameters
    const query = `license=${licenseNumber}&org_id=${orgId}&version_id=${versionId}`;
    const url = `/api/projects?${query}`;
    const response = await authRequest(url);
    const { data } = response;
    if (data) {
      document.getElementById('data-placeholder').classList.add('d-none');
      document.getElementById('data-table').classList.remove('d-none');
    }
    // TODO: Define the columns for the table.
    const columnDefs = [
      { field: 'project_id', headerName: 'Project ID', sortable: true, filter: true },
    ];

    // Specify the table options.
    const gridOptions = {
      columnDefs: columnDefs,
      pagination: true,
      paginationAutoPageSize: true,
      suppressRowClickSelection: false,
      onRowClicked: event => this.openProject(event),
      onGridReady: event => theme.toggleTheme(theme.getTheme()),
    };

    // Render the table
    const eGridDiv = document.querySelector(`#${tableId}`);
    new agGrid.Grid(eGridDiv, gridOptions);
    gridOptions.api.setRowData(data);
  },

  async deleteProject(projectId, orgId, licenseNumber, versionId = 'latest') {
    /**
     * Delete a project.
     * @param {String} projectId
     * @param {String} orgId
     * @param {String} licenseNumber
     * @param {String} versionId
     */
    const url = `/api/projects/${projectId}`
    const filters = `?license=${licenseNumber}&org_id=${orgId}&version_id=${versionId}`;
    const response = await authRequest(url + filters, null, { delete: true });
    if (response.error) {
      showNotification('Deleting project failed', response.message, /* type = */ 'error');
    } else {
      const message = "Project deleted from your database, hopefully you know what you're doing!";
      showNotification('Project deleted', message, /* type = */ 'success');
    }
  },

  async saveProject() {
    /**
     * Create or update a project.
     */
    const form = document.getElementById('project-form');
    const data = serializeForm(form);
    const url = `/api/projects/${data.project_id}`;
    const response = await authRequest(url, data);
    if (response.error) {
      showNotification('Error saving project', response.message, /* type = */ 'error');
    } 
    else {
      showNotification('Project saved', 'Project data saved.', /* type = */ 'success');
    }
  },

  openProject(row) {
    /**
     * Navigate to a selected project.
     * @param {Object} row A row object containing `data` with an `data.id`.
     */
    localStorage.setItem('project', JSON.stringify(row.data));
    window.location.href = `${window.location.origin}/projects/project?id=${row.data.id}`;
  },

  viewProject() {
    /**
     * Render a project's data when navigating to a project page.
     */
    const data = JSON.parse(localStorage.getItem('project'));
    deserializeForm(document.forms['project-form'], data);
  },

  importProjects() {
    /**
     * Import a data file (.csv or .xlsx) of project data.
     */
    // TODO:
  },

  exportProjects() {
    /**
     * Import a data file (.csv or .xlsx) of project data.
     */
    // TODO:
  },

};
