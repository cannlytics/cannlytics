"use strict";
/*
 * ATTENTION: The "eval" devtool has been used (maybe by default in mode: "development").
 * This devtool is neither made for production nor for readable output files.
 * It uses "eval()" calls to create a separate source file in the browser devtools.
 * If you are trying to read the output file, select a different devtool (https://webpack.js.org/configuration/devtool/)
 * or disable the default devtool with "devtool: false".
 * If you are looking for production-ready output files, see mode: "production" (https://webpack.js.org/configuration/mode/).
 */
self["webpackHotUpdatecannlytics"]("cannlytics",{

/***/ "./assets/js/app/app.js":
/*!******************************!*\
  !*** ./assets/js/app/app.js ***!
  \******************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

eval("__webpack_require__.r(__webpack_exports__);\n/* harmony export */ __webpack_require__.d(__webpack_exports__, {\n/* harmony export */   \"app\": () => (/* binding */ app)\n/* harmony export */ });\n/* harmony import */ var _auth_auth_js__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! ../auth/auth.js */ \"./assets/js/auth/auth.js\");\n/* harmony import */ var _firebase_js__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! ../firebase.js */ \"./assets/js/firebase.js\");\n/* harmony import */ var _utils_js__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(/*! ../utils.js */ \"./assets/js/utils.js\");\n/* harmony import */ var _ui_ui_js__WEBPACK_IMPORTED_MODULE_3__ = __webpack_require__(/*! ../ui/ui.js */ \"./assets/js/ui/ui.js\");\n/* harmony import */ var _dataTables_js__WEBPACK_IMPORTED_MODULE_4__ = __webpack_require__(/*! ./dataTables.js */ \"./assets/js/app/dataTables.js\");\n/* harmony import */ var _dataModels_js__WEBPACK_IMPORTED_MODULE_5__ = __webpack_require__(/*! ./dataModels.js */ \"./assets/js/app/dataModels.js\");\n/**\r\n * App JavaScript | Cannlytics Console\r\n * Copyright (c) 2021-2023 Cannlytics\r\n * \r\n * Authors: Keegan Skeate <https://github.com/keeganskeate>\r\n * Created: 12/7/2020\r\n * Updated: 1/8/2023\r\n * License: MIT License <https://github.com/cannlytics/cannlytics-console/blob/main/LICENSE>\r\n */const app={..._dataModels_js__WEBPACK_IMPORTED_MODULE_5__.dataModels,..._dataTables_js__WEBPACK_IMPORTED_MODULE_4__.dataTables,initialize(redirect=false){/**\r\n     * Initialize the console's features and functionality.\r\n     * @param {Boolean} redirect Whether or not to redirect the user to the\r\n     *    dashboard (optional).\r\n     */ // Enable any and all tooltips.\n_ui_ui_js__WEBPACK_IMPORTED_MODULE_3__.initHelpers.initializeTooltips();// Create a user session if a user is detected.\n(0,_firebase_js__WEBPACK_IMPORTED_MODULE_1__.onAuthChange)(async user=>signInUser(user,redirect));// Hide the sidebar on small screens.\ntry{_ui_ui_js__WEBPACK_IMPORTED_MODULE_3__.navigationHelpers.toggleSidebar('sidebar-menu');}catch(error){/* User not signed in. */}}// getSessionCookie(nullValue='None') {\n//   /** Gets the session cookie, returning 'None' by default if the cookie is null. */\n//   return (document.cookie.match(/^(?:.*;)?\\s*__session\\s*=\\s*([^;]+)(?:.*)?$/)||[,nullValue])[1];\n// },\n};function getSessionCookie(nullValue='None'){/** Gets the session cookie, returning 'None' by default if the cookie is null. */return(document.cookie.match(/^(?:.*;)?\\s*__session\\s*=\\s*([^;]+)(?:.*)?$/)||[,nullValue])[1];}async function signInUser(user,redirect=false){/**\r\n   * Create a session when a user is detected, checking\r\n   * if any Google credentials may have been passed.\r\n   */if(user){// Set user data on first login.\nif(user.metadata.createdAt==user.metadata.lastLoginAt){const{email}=user;const defaultPhoto=`https://cannlytics.com/robohash/${user.uid}?width=60&height=60`;const data={email,photo_url:defaultPhoto};await (0,_utils_js__WEBPACK_IMPORTED_MODULE_2__.authRequest)('/api/users',data);}// Only authenticate with the server as needed.\nconst currentSession=getSessionCookie();if(currentSession==='None')await (0,_utils_js__WEBPACK_IMPORTED_MODULE_2__.authRequest)('/src/auth/login');if(redirect)window.location.href=window.location.origin;try{document.getElementById('splash').classList.add('d-none');document.getElementById('page').classList.remove('d-none');}catch(error){// No splash page.\n}}else{// If the user has not persisted their session, then log out of their\n// Django session, and redirect to the sign in page.\nawait (0,_auth_auth_js__WEBPACK_IMPORTED_MODULE_0__.checkForCredentials)();const currentSession=getSessionCookie();if(currentSession==='None')await (0,_utils_js__WEBPACK_IMPORTED_MODULE_2__.authRequest)('/src/auth/logout');if(!window.location.href.includes('account')){window.location.href=`${window.location.origin}\\\\account\\\\sign-in`;await page.waitForNavigation();}document.getElementById('page').classList.remove('d-none');}}\n\n//# sourceURL=webpack://cannlytics/./assets/js/app/app.js?");

/***/ })

},
/******/ function(__webpack_require__) { // webpackRuntimeModules
/******/ /* webpack/runtime/getFullHash */
/******/ (() => {
/******/ 	__webpack_require__.h = () => ("744220311a8d77049ecd")
/******/ })();
/******/ 
/******/ }
);