/**
 * Areas | Cannlytics Console
 * Author: Keegan Skeate
 * Created: 12/3/2020
 */

import { api } from '../api/api.js';
import { auth } from '../firebase.js';
import { theme } from '../settings/theme.js';

export const areas = {


  initializeAreas() {
    /*
     * Initialize areas table.
     */
    auth.onAuthStateChanged((user) => {
      this.getAreas();
    });
  },


  getAreas() {
    /*
     * Get areas from Metrc through the API.
     */

    // TODO: Specify the columns.
    const columnDefs = [
      { field: "make", sortable: true, filter: true, editable: true, checkboxSelection: true }, // , checkboxSelection: true
      { field: "model", sortable: true, filter: true, editable: true },
      { field: "price", sortable: true, filter: true, editable: true }
    ];

    // Specify the table options.
    const gridOptions = {
      columnDefs: columnDefs,
      pagination: true,
      rowSelection: 'multiple',
      suppressRowClickSelection: false,
      // singleClickEdit: true,
      // onRowClicked: event => console.log('A row was clicked'),
      onGridReady: event => theme.toggleTheme(theme.getTheme()),
    };

    // Get the data and render the table.
    api.getAreas().then((data) => {
      console.log('Areas:', data);
      const eGridDiv = document.querySelector('#areas-table');
      new agGrid.Grid(eGridDiv, gridOptions);
      gridOptions.api.setRowData(data);
    })
    .catch((error) => {
      console.log('Error:', error);
    });

    // TODO: Attach export functionality
    //function exportTableData() {
    //  gridOptions.api.exportDataAsCsv();
    //}

  },


}
