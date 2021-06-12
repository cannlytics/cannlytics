/**
 * Analysis JavaScript | Cannlytics Console
 * Author: Keegan Skeate
 * Created: 12/3/2020
 * Updated: 6/12/2021
 */
// import Chart from 'chart.js';
// import "chartjs-chart-box-and-violin-plot/build/Chart.BoxPlot.js";

import { api } from '../api/api.js';


function randomValues(count, min, max) {
  const delta = max - min;
  return Array.from({length: count}).map(() => Math.random() * delta + min);
}


export const analyses = {


  initialize() {
    console.log('TODO: Initialize analyses...!')
    // this.drawGraphs();
  },


  drawAnalysesTable() {
    /*
     * Render the analyses table.
     */

    const columnDefs = [
      { field: 'name', sortable: true, filter: true },
      { field: 'email', sortable: true, filter: true },
      { field: 'phone', sortable: true, filter: true }
    ];

    // Specify the table options.
    // const gridOptions = {
    //   columnDefs: columnDefs,
    //   pagination: true,
    //   rowSelection: 'multiple',
    //   suppressRowClickSelection: false,
    //   // singleClickEdit: true,
    //   // onRowClicked: event => console.log('A row was clicked'),
    //   onGridReady: event => theme.toggleTheme(theme.getTheme()),
    // };

    // Get the data and render the table.
    // api.getOrganizations().then((data) => {
    //   console.log('Table data:', data); // DEV:
    //   const eGridDiv = document.querySelector(`#${tableId}`);
    //   new agGrid.Grid(eGridDiv, gridOptions);
    //   gridOptions.api.setRowData(data);
    // })
    // .catch((error) => {
    //   console.log('Error:', error);
    // });

    // TODO: Attach export functionality
    //function exportTableData() {
    //  gridOptions.api.exportDataAsCsv();
    //}

  },


  drawGraphs() {
    var ctx = document.getElementById('graph-concentrations');
    var graph = new Chart(ctx, {
      type: 'boxplot',
      data: this.data,
      options: {
        responsive: true,
        legend: {
          position: 'bottom',
        },
      },
    });
  },

  data: {
    // TODO: Get from Firestore
    // define label tree
    labels: ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'],
    datasets: [{
      label: 'Flower',
      backgroundColor: 'rgba(255, 0, 0, 0.5)',
      borderColor: 'red',
      borderWidth: 1,
      outlierColor: '#999999',
      padding: 10,
      itemRadius: 0,
      data: [
        randomValues(100, 0, 100),
        randomValues(100, 0, 20),
        randomValues(100, 20, 70),
        randomValues(100, 60, 100),
        randomValues(40, 50, 100),
        randomValues(100, 60, 120),
        randomValues(100, 80, 100)
      ]
    }, {
      label: 'Concentrates',
      backgroundColor:  'rgba(0, 0, 255, 0.5)',
      borderColor: 'blue',
      borderWidth: 1,
      outlierColor: '#999999',
      padding: 10,
      itemRadius: 0,
      data: [
        randomValues(100, 60, 100),
        randomValues(100, 0, 100),
        randomValues(100, 0, 20),
        randomValues(100, 20, 70),
        randomValues(40, 60, 120),
        randomValues(100, 20, 100),
        randomValues(100, 80, 100)
      ]
    }]
  },


  getAnalyses() {
    /*
     * Get all analyses for an organization.
     */
    // TODO: Get the data and fill it into an AG Grid table!
    api.getAnalyses(data);
  },


  saveAnalysis() {
    /*
     * Create or update an analysis.
     */
    // TODO: Serialize the analysis data!
    const data = {}
    api.createAnalyses(data);
  },


  deleteAnalysis() {
    /*
     * Delete an analysis.
     */
    // TODO: Serialize the analysis data!
    const data = {}
    api.createAnalyses(data);
  },


  exportAnalyses() {
    /*
     * Export all Analyses to Excel.
     */
    // TODO: Serialize the analysis data!
    const data = {}
    api.createAnalyses(data);
  },


}
