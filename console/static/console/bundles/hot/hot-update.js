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

/***/ "./console/assets/js/waste/waste.js":
/*!******************************************!*\
  !*** ./console/assets/js/waste/waste.js ***!
  \******************************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

eval("__webpack_require__.r(__webpack_exports__);\n/* harmony export */ __webpack_require__.d(__webpack_exports__, {\n/* harmony export */   \"waste\": () => (/* binding */ waste)\n/* harmony export */ });\n/* harmony import */ var _utils_js__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! ../utils.js */ \"./console/assets/js/utils.js\");\n/**\r\n * Waste JavaScript | Cannlytics Console\r\n * Copyright (c) 2021 Cannlytics\r\n * \r\n * Authors: Keegan Skeate\r\n * Created: 2/6/2022\r\n * Updated: 2/16/2022\r\n * License: MIT License <https://github.com/cannlytics/cannlytics-console/blob/main/LICENSE>\r\n */const waste={initialize(){/**\r\n     * Initialize waste.\r\n     */},getWaste(){/**\r\n     * Get waste through the API.\r\n     */const form=document.getElementById('waste-form');const data=(0,_utils_js__WEBPACK_IMPORTED_MODULE_0__.serializeForm)(form);(0,_utils_js__WEBPACK_IMPORTED_MODULE_0__.authRequest)('/api/waste',data).then(response=>{if(response.error){(0,_utils_js__WEBPACK_IMPORTED_MODULE_0__.showNotification)('Error getting waste',response.message,{type:'error'});}else{// TODO: Render the analytics in the user interface.\ndocument.getElementById('output').classList.remove('d-none');document.getElementById('output-message').textContent=JSON.stringify(response.data);}});},getWasteAreas(){/**\r\n     * Get areas used for waste.\r\n     * @returns {Array}\r\n     */},getSampleAmount(sampleId){/**\r\n     * Get the current expected amount of a given sample.\r\n     * @param {String} sampleId The ID for a given sample.\r\n     * @returns {Number}\r\n     */ // TODO: Get and return the expected amount for a given sample from the database.\n},getSampleOriginalAmount(sampleId){/**\r\n     * Get the original amount of the sample.\r\n     * @param {String} sampleId The ID for a given sample.\r\n     * @returns {Number}\r\n     */ // TODO: Get and return the original amount for a given sample from the database.\n},getWarningLimit(){/**\r\n     * Get the limit at which the staff is warned about weight out-of-specification.\r\n     */ // TODO: Get and return the waste warning limit from the database.\n},calculatePercentUsed(){/**\r\n     * Calculate the percent used as the sample amount divided by the original\r\n     * sample amount time 100.\r\n     */const sampleAmount=this.getSampleAmount();const originalSampleAmount=this.getSampleOriginalAmount();return sampleAmount/originalSampleAmount*100;},calculatePercentDifference(currentSampleAmount){/**\r\n     * Calculated the percent difference as the current sample amount minus the\r\n     * sample amount divided by the sample_amount times 100.\r\n     */const sampleAmount=this.getSampleAmount();return(currentSampleAmount-sampleAmount)/sampleAmount*100;},raiseCorrectiveAction(){/**\r\n     * Raise corrective_action if the percent difference is above the warning limit.\r\n     */ // TODO: Create a corrective action database entry and document (using template).\n// TODO: Send corrective action notification to the staff.\n},reconcileWasteItem(){/**\r\n     * Reconcile a given waste item.\r\n     */const currentSampleAmount=0;// TODO: Get from the user interface.\nconst warningLimit=this.getWarningLimit();this.calculatePercentDifference(currentSampleAmount);if(percent_difference>warningLimit)this.raiseCorrectiveAction();}};\n\n//# sourceURL=webpack://cannlytics/./console/assets/js/waste/waste.js?");

/***/ })

},
/******/ function(__webpack_require__) { // webpackRuntimeModules
/******/ /* webpack/runtime/getFullHash */
/******/ (() => {
/******/ 	__webpack_require__.h = () => ("5de8cae95babc520c39b")
/******/ })();
/******/ 
/******/ }
);