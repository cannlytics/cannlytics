/**
 * Contacts JavaScript | Cannlytics Console
 * Copyright (c) 2021-2022 Cannlytics
 * 
 * Authors: Keegan Skeate <https://github.com/keeganskeate>
 * Created: 12/3/2020
 * Updated: 12/14/2021
 * License: MIT License <https://github.com/cannlytics/cannlytics-console/blob/main/LICENSE>
 */

 export const contacts = {

  logLimit: 10,

  async renderTable(model, modelSingular, orgId, data) {
    /**
     * Render a data table in the user interface.
     * @param {String} model
     * @param {String} modelSingular
     * @param {String} orgId
     * @param {Array} data
     */

    // Render the table if it's the first time that it's shown.
    if (this.tableHidden) {

      // Hide the placeholder and show the table.
      document.getElementById('loading-placeholder').classList.add('d-none');
      // document.getElementById('data-placeholder').classList.add('d-none');
      document.getElementById('data-table').classList.remove('d-none');
      this.tableHidden = false;
  
      // Get data model fields from organization settings.
      this.dataModel = await getDocument(`organizations/${orgId}/data_models/${model}`);
      const columnDefs = this.dataModel.fields.map(function(e) { 
        return { headerName: e.label, field: e.key, sortable: true, filter: true };
      });
  
      // Specify the table options.
      this.gridOptions = {
        columnDefs: columnDefs,
        defaultColDef: { flex: 1,  minWidth: 175 },
        pagination: true,
        paginationAutoPageSize: true,
        rowClass: 'app-action',
        rowSelection: 'single',
        suppressRowClickSelection: false,
        onRowClicked: event => navigationHelpers.openObject(model, modelSingular, event.data),
        onGridReady: event => theme.toggleTheme(theme.getTheme()),
      };
  
      // Render the table
      const eGridDiv = document.querySelector(`#${model}-table`);
      new agGrid.Grid(eGridDiv, this.gridOptions);
      this.gridOptions.api.setRowData(data);

    } else {

      // Update the table's data.
      this.gridOptions.api.setRowData(data);

    }

  },

  streamLogs(model, modelId, orgId, orderBy = '', desc = false) {
    /**
     * Stream logs, listening for any changes.
     * @param {String} model A type of data model to filter the stream logs of by.
     * @param {String} modelId A specific data model to stream its logs.
     * @param {String} orgId The organization ID of the logs to retrieve.
     * @param {String} orderBy A field to order logs by. 
     * @param {Boolean} desc Whether or not the logs should be in descending order.
     */
    // FIXME:
    const path = `contacts/${orgId}/logs`;
    const filters = [];
    if (model) filters.push({ key: 'type', operation: '==', value: model });
    else if (modelId) filters.push({ key: 'key', operation: '==', value: modelId });
    const params = {
      desc,
      filters,
      order: orderBy,
      max: this.logLimit,
    };
    listenToCollection(path, params, (querySnapshot) => {
      const data = [];
      querySnapshot.forEach((doc) => {
        data.push(doc.data());
      });
      // FIXME: Does this need to be rendered?
      // if (data.length) this.drawTable(model, modelSingular, orgId, data);
      // else this.drawPlaceholder();
    });
  },

}
