/**
 * Projects JavaScript | Cannlytics Console
 * Author: Keegan Skeate
 * Created: 6/18/2021
 * Updated: 6/18/2021
 */

import { authRequest, formDeserialize, formSerialize, showNotification } from '../utils.js';
import { theme } from '../settings/theme.js';


export const projects = {


  initialize() {
    console.log('Initializing projects!')
  },


  getProjects(orgId, licenseNumber, versionId = 'latest') {
    /*
     * Get projects.
     */

    // Get the data.
    // TODO: Add parameters
    const query = `license=${licenseNumber}&org_id=${orgId}&version_id=${versionId}`;
    const url = `/api/projects?${query}`;
    authRequest(url).then((response) => {
      const { data } = response;
      if (data) {
        document.getElementById('data-placeholder').classList.add('d-none');
        document.getElementById('data-table').classList.remove('d-none');
      }
      console.log('Table data:', data);

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
    });

  },


  deleteProject(projectId, orgId, licenseNumber, versionId = 'latest') {
    /*
     * Delete a project.
     */
    const url = `/api/projects/${projectId}`
    const filters = `?license=${licenseNumber}&org_id=${orgId}&version_id=${versionId}`;
    authRequest(url + filters, null, { delete: true }).then((response) => {
      if (response.error) {
        showNotification('Deleting project failed', response.message, { type: 'error' });
      } else {
        const message = "Project deleted from your database, hopefully you know what you're doing!";
        showNotification('Project deleted', message, { type: 'success' });
      }
    });
  },


  saveProject() {
    /*
     * Create or update a project.
     */
    const form = document.getElementById('project-form');
    const data = formSerialize(form);
    authRequest(`/api/projects/${data.project_id}`, data).then((response) => {
      if (response.error) {
        showNotification('Error saving project', response.message, { type: 'error' });
      } else {
        showNotification('Project saved', 'Project data saved.', { type: 'success' });
      }
    });
  },


  openProject(row) {
    /*
     * Navigate to a selected project.
     */
    localStorage.setItem('project', JSON.stringify(row.data));
    window.location.href = `/projects/project?id=${row.data.id}`;
  },


  viewProject() {
    /*
     * Render a project's data when navigating to a project page.
     */
    const data = JSON.parse(localStorage.getItem('project'));
    formDeserialize(document.forms['project-form'], data);
  },


};
