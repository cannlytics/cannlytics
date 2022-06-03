/**
 * Statistics JavaScript | Cannlytics Website
 * Copyright (c) 2022 Cannlytics
 * 
 * Authors: Keegan Skeate <contact@cannlytics.com>
 * Created: 5/31/2022
 * Updated: 5/31/2022
 * License: MIT License <https://github.com/cannlytics/cannlytics-website/blob/main/LICENSE>
 */
import { authRequest } from '../utils.js';

export const stats = {


  getDefinitions() {
    /**
     * Get variable definitions and save them to local storage.
     */

    // TODO: Get variable definitions (through the API).

    // TODO: Save the variable definitions to local storage.

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


};
