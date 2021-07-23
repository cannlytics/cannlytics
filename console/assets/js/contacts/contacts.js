/**
 * Contacts JavaScript | Cannlytics Console
 * Author: Keegan Skeate
 * Created: 12/3/2020
 * Updated: 6/9/2021
 */

 export const contacts = {

  logLimit: 10,


  async renderTable(model, modelSingular, orgId, data) {
    /*
     * Render a data table in the user interface.
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
      console.log('Data Model:', this.dataModel);
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


  streamLogs(model, modelId, orgId) {
    /*
     * Stream logs, listening for any changes.
     */
    const desc = false;
    const orderBy = null;
    db.collection('organizations').doc(orgId).collection('logs')
      .where('key', '==', modelId)
      .orderBy(orderBy, 'desc')
      .limit(this.logLimit)
      .onSnapshot((querySnapshot) => {
        const data = [];
        querySnapshot.forEach((doc) => {
          data.push(doc.data());
        });
        console.log('Logs:', data);
        // if (data.length) this.drawTable(model, modelSingular, orgId, data);
        // else this.drawPlaceholder();
      });
  },

}
