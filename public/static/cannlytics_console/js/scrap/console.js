/**
 * --------------------------------------------------------------------------
 * Cannlytics (v1.0.0): console.js
 * Licensed under GPLv3 (https://github.com/cannlytics/cannlytics_console/blob/main/LICENSE)
 * --------------------------------------------------------------------------
 */
/* globals Chart:false, feather:false */

// TODO: Search
// TODO: Change lab
// TODO: Sign out
// TODO: Change picture
// TODO: Toggle theme
  // add/remove dropdown-menu-dark to dropdown

// function main() {
//   //here you can do your basic setup or delegate the control of the app to a different .js file.
// }

// cannlyticsIntake.initializeGraphs()

(function () {
  'use strict'

  // Initialize icons.
  feather.replace()

  // TODO: Determine the page.
  var page = window.document.location.pathname.split('/')[1]
  console.log(page)
  
  // TODO: Render page-specific JavaScript.
  // if (page === 'intake') {
  //   cannlyticsIntake.initializeGraphs()
  // }
  // import('./intake.js').then((module) => {
  //   cannlyticsIntake.initializeGraphs()
  // })

}());
