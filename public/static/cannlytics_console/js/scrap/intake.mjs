/**
 * --------------------------------------------------------------------------
 * Cannlytics (v1.0.0): intake.js
 * Licensed under GPLv3 (https://github.com/cannlytics/cannlytics_console/blob/main/LICENSE)
 * --------------------------------------------------------------------------
 */

// import {
//   helper,
// } from './util/index';

 /**
 * ------------------------------------------------------------------------
 * Constants
 * ------------------------------------------------------------------------
 */

 A = 10

  /**
 * ------------------------------------------------------------------------
 * Intake Functions
 * ------------------------------------------------------------------------
 */

export function addTextToBody(text) {
  const div = document.createElement('div');
  div.textContent = text;
  document.body.appendChild(div);
}

export function getData() {
  console.log('Getting data...')
}

export class cannlyticsIntake {

  initializeGraphs() {
    console.log('loaded intake!')
    // var data = cannlyticsConsole.getData()
    // cannlyticsConsole.renderGraph('myChart', data)
  }

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
  }

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
  }

}
