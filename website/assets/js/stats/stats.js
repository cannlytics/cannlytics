/**
 * Statistics JavaScript | Cannlytics Website
 * Copyright (c) 2022 Cannlytics
 * 
 * Authors: Keegan Skeate <contact@cannlytics.com>
 * Created: 5/31/2022
 * Updated: 5/31/2022
 * License: MIT License <https://github.com/cannlytics/cannlytics-website/blob/main/LICENSE>
 */
// import { authRequest } from '../utils.js';
import { getDocument } from '../firebase.js';

export const stats = {


  changeField(field) {
    /**
     * Change a field in the form.
     */
    console.log('TODO: Change the corresponding input:', field);
  },


  changeModel(model) {
    /**
     * Change the prediction model, updating the user interface.
     */
    console.log('TODO: Change the model!', model);
  },


  async getDefinitions(ref) {
    /**
     * Get variable definitions and save them to local storage.
     * @param {String} ref The reference to the variable definitions.
     * @returns {Object} The variable definitions.
     */
    const data = await getDocument(ref);
    localStorage.setItem('variables', JSON.stringify(data));
    return data;

  },


  getModelStats() {
    /**
     * Get the statistics for a given statistical model.
     */

    // TODO: Implement endpoint to get model statistics.
    // modelStats = authRequest('/api/market/download-lab-data');

    // TODO: Save model statistics to local storage.

  },


  getObservation() {
    /**
     * Get historically observed observations to load into the form.
     */

    // TODO: Get a specific observation (e.g. a strain).


    // TODO: Populate the observation form.

  },


  getPredictions() {
    /**
     * Get model predictions given the user's observation.
     */

    // TODO: Format the observation.

    // TODO: Make a request for model predictions.

    // TODO: Handle the user interface given the predictions.

  },


  renderPredictionForm(predictions) {
    /**
     * Render the prediction form.
     */
    // Get the variables.
    const variables = localStorage.getItem('variables');
    console.log('Variables:', variables);

    // TODO: Plug in the predictions.

    // TODO: Style as necessary.

  },


  resetObservationForm() {
    /**
     * Reset the form being used to submit observations.
     */

    // TODO: Implement.

  },


  savePredictions() {
    /**
     * Save the model predictions.
     */

    // TODO: Implement.

  },


  sharePredictions() {
    /**
     * Share the model predictions.
     */

    // TODO: Implement.


    // TODO: Show notification.

  },


  submitActual() {
    /**
     * Submit the user's actually observed outcome.
     */

    // TODO: Format the user's actual data.

    // TODO: Post the user's actual data.

    // TODO: Handle the user interface.

  },


  uploadLabResults() {
    /**
     * Load lab results into the form from a user-selected file.
     */

    // TODO: Read the user-selected file.

    // TODO: Ensure the file is the correct type and doesn't appear malicious.

    // TODO: Read any lab results from the file.

    // TODO: Clean the lab results if necessary.

    // TODO: Populate the form with the lab results.

  },


};
