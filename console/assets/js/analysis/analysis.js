/**
 * Cannlytics Console (v1.0.0): analysis.js
 * Licensed under GPLv3 (https://github.com/cannlytics/cannlytics_console/blob/main/LICENSE)
 * Author: Keegan Skeate
 * Created: 12/3/2020
 */
// import Chart from 'chart.js';
// import "chartjs-chart-box-and-violin-plot/build/Chart.BoxPlot.js";

function randomValues(count, min, max) {
  const delta = max - min;
  return Array.from({length: count}).map(() => Math.random() * delta + min);
}

export const analysis = {

  initialize() {
    this.drawGraphs();
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

}
