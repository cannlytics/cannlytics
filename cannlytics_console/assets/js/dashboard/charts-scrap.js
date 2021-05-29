// import { Chart } from "frappe-charts/dist/frappe-charts.min.esm";
// import { Chart as fChart } from "frappe-charts/dist/frappe-charts.esm.js";
// import "frappe-charts/dist/frappe-charts.min.css";

// initialize() {
//   // this.drawGraphs();
//   // this.drawHeatmap();
//   // this.drawTimeseries();
// },

// drawHeatmap() {
//   console.log('Drawing heatmap');
//   // Optional: Get beginning and end of year. (6-month if mobile)
//   let data = {
//     dataPoints: {
//       "1604188800": 113, // TODO: Get daily samples received.
//     },
//     start: new Date(new Date().getFullYear(), 0, 1),
//     end: new Date(new Date().getFullYear(), 12, 31),
//   }
//   let chart = new frappe.Chart("#heatmap", {
//     type: 'heatmap',
//     data: data,
//     radius: 5,
//     discreteDomains: 1,
//     colors: ['#ebedf0', '#c0ddf9', '#73b3f3', '#3886e1', '#17459e'],
//   });
// },

// drawGraphs() {
//   var ctx = document.getElementById('graph-samples-received-matrix');
//   var graph = new Chart(ctx, {
//     type: 'matrix',
//     data: {
//       datasets: [{
//           label: 'My Matrix',
//           data: [
//               { x: 1, y: 1, v: 11 },
//               { x: 2, y: 2, v: 22 },
//               { x: 3, y: 3, v: 33 }
//           ],
//           backgroundColor: function(ctx) {
//               var value = ctx.dataset.data[ctx.dataIndex].v;
//               var alpha = (value - 5) / 40;
//               return Color('green').alpha(alpha).rgbString();
//           },
//           width: function(ctx) {
//               var a = ctx.chart.chartArea;
//               return (a.right - a.left) / 3.5;
//           },
//           height: function(ctx) {
//               var a = ctx.chart.chartArea;
//               return (a.bottom - a.top) / 3.5;
//           }
//       }]
//     },
//   });
// },


// drawTimeseries() {
//   console.log('Drawing timeseries!');
//   // TODO: Get data dynamically
//   new frappe.Chart("#timeseries", {
//     // or DOM element
//     data: {
//       labels: [
//         "Mon.",
//         "Tue.",
//         "Wed.",
//         "Thu.",
//         "Fri.",
//         "Sat.",
//         "Sun.",
//       ],
  
//       datasets: [
//         {
//           name: "Samples",
//           chartType: "bar",
//           values: [25, 40, 30, 35, 8, 52, 17, 3]
//         },
//         {
//           name: "Projects",
//           chartType: "bar",
//           values: [25, 50, 10, 15, 18, 32, 27, 14]
//         },
//         {
//           name: "Clients",
//           chartType: "line",
//           values: [15, 20, 5, 20, 58, 12, 25, 37]
//         }
//       ],
//       yMarkers: [
//         { label: "Capacity", value: 70, options: { labelPos: "left" } },
//       ],
//       // yRegions: [
//       //   { label: "Region", start: -10, end: 50, options: { labelPos: "right" } }
//       // ]
//     },
  
//     // title: "My Awesome Chart",
//     type: "axis-mixed", // or 'bar', 'line', 'pie', 'percentage'
//     height: 300,
//     colors: ['#ebedf0', '#c0ddf9', '#73b3f3', '#3886e1', '#17459e'],
//     axisOptions: {
//       xAxisMode: "tick",
//       xIsSeries: true
//     },
//     barOptions: {
//       stacked: false,
//       spaceRatio: 0.5
//     },
//   });


//   // var ctx = document.getElementById('timeseries').getContext('2d');;
//   // var myChart = new Chart(ctx, {
//   //   type: 'bar',
//   //   data: {
//   //     labels: ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"],
//   //     datasets: [
//   //       {
//   //         label: 'In-transit',
//   //         backgroundColor: "#caf270",
//   //         data: [12, 59, 5, 56, 58,12, 59],
//   //       },
//   //       {
//   //         label: 'Started',
//   //         backgroundColor: "#45c490",
//   //         data: [12, 59, 5, 56, 58,12, 59],
//   //       },
//   //       {
//   //         label: 'Complete',
//   //         backgroundColor: "#008d93",
//   //         data: [12, 59, 5, 56, 58,12, 5],
//   //       },
//   //     ],
//   //   },
//   //   options: {
//   //       tooltips: {
//   //         displayColors: true,
//   //         callbacks:{
//   //           mode: 'x',
//   //         },
//   //       },
//   //       scales: {
//   //         xAxes: [{
//   //           stacked: true,
//   //           gridLines: {
//   //             display: false,
//   //           }
//   //         }],
//   //         yAxes: [{
//   //           stacked: true,
//   //           ticks: {
//   //             beginAtZero: true,
//   //           },
//   //           type: 'linear',
//   //         }]
//   //       },
//   //       responsive: true,
//   //       maintainAspectRatio: false,
//   //       legend: { position: 'top' },
//   //     }
//   //   });