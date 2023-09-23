/**
 * Intake JavaScript | Cannlytics Console
 * Copyright (c) 2021-2022 Cannlytics
 * 
 * Authors: Keegan Skeate <https://github.com/keeganskeate>
 * Created: 12/3/2020
 * Updated: 6/3/2021
 * License: MIT License <https://github.com/cannlytics/cannlytics-console/blob/main/LICENSE>
 */
// import Chart from 'chart.js';

// TODO: Get transfers
// TODO: search transfers
// TODO: Create transfer
// TODO: Edit transfer
// TODO: Delete transfer

// TODO: Get projects
// TODO: Search projects
// TODO: Create project
// TODO: Edit project
// TODO: Delete project

export const intake = {

  initialize() {
    this.drawProgressGraph();
    // var data = cannlyticsConsole.getData()
    // cannlyticsConsole.renderGraph('myChart', data)
  },

  drawProgressGraph() {
    var data = {
      datasets: [{
        data: [10, 20],
        backgroundColor: [
          'rgba(255, 206, 86, 0.2)',
          'rgba(54, 162, 235, 0.2)',
        ],
        borderColor: [
          'rgba(255, 206, 86, 1)',
          'rgba(54, 162, 235, 1)',
        ],
        borderWidth: 1,
      }],
      labels: [
        'In-Transit',
        'Received',
      ],
    }; // TODO: Get from Firestore
    var ctx = document.getElementById('graph-progress');
    var myPieChart = new Chart(ctx, {
      type: 'pie',
      data: data,
      options: {
        cutoutPercentage: 50,
      },
    });
  },

  // TODO: Get data
  getData() {
    return [
      15339,
      21345,
      18483,
      24003,
      23489,
      24092,
      12034
    ]
  },

  // TODO: Render graphs
  renderGraph(id, data) {
    var ctx = document.getElementById(id)
    // eslint-disable-next-line no-unused-vars
    var myChart = new Chart(ctx, {
      type: 'line',
      data: {
        labels: [
          'Sunday',
          'Monday',
          'Tuesday',
          'Wednesday',
          'Thursday',
          'Friday',
          'Saturday'
        ],
        datasets: [{
          data: data,
          lineTension: 0,
          backgroundColor: 'transparent',
          borderColor: '#007bff',
          borderWidth: 4,
          pointBackgroundColor: '#007bff'
        }]
      },
      options: {
        scales: {
          yAxes: [{
            ticks: {
              beginAtZero: false
            }
          }]
        },
        legend: {
          display: false
        }
      }
    })
  },

}
