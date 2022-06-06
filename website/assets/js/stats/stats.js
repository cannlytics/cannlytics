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
import { getDocument } from '../firebase.js';
import { hideLoadingButton, showLoadingButton } from '../ui/ui.js';

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


  async getPredictions() {
    /**
     * Get model predictions given the user's observation.
     */

    // Show loading wand on button.
    showLoadingButton('predict-button');

    // TODO: Format the observation.
    const body = {
      'model': 'simple',
      'samples': [
        {
          'strain_name': 'Website test',
          'total_cbd': 0.4,
          'total_thc': 20,
        }
      ]
    }

    // Make a request for model predictions.
    const response = await authRequest('/api/stats/effects', body);
    const { data } = response;
    const sample = data.samples[0];

    // TODO: Render effects, separating positive and negative effects.
    // `data.predicted_effects`
    console.log('Predicted effects:', sample.predicted_effects);

    // TODO: Render aromas.
    // `data.aromas`
    console.log('Predicted aromas:', sample.aromas);
    
    // TODO: Render model statistics for each effect and aroma.
    const fpr = sample.model_stats.false_positive_rate;
    const tpr = sample.model_stats.true_positive_rate;

    // Show the predictions.
    document.getElementById('prediction-id').value = sample.prediction_id;
    document.getElementById('predictions').classList.remove('d-none');

    // Remove loading wand from button.
    hideLoadingButton('predict-button');

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


  closePredictions() {
    /**
     * Close the predictions.
     */
    // Optional: clear the predictions.
    document.getElementById('predictions').classList.add('d-none');
  },


  savePredictions() {
    /**
     * Save the model predictions.
     */

    // TODO: Implement.
    console.log('Save predictions...');
  },


  sharePredictions() {
    /**
     * Share the model predictions.
     */

    // TODO: Implement.


    // TODO: Show notification.

  },


  selectActual(type, input) {
    /**
     * Select an actual effect.
     */
    console.log('Selected:', type, input);
    input.value = '';
    // TODO: Create a new badge with the effect.
    // Optional: If it's a positive effect, then color green (success).
    // If it's a negative effect then color red (danger).
    // If it's an aroma then color based on the aroma's assigned color.
  },


  async submitActual() {
    /**
     * Submit the user's actually observed outcome.
     */

    // TODO: Format the user's actual data.
    const actual = {
      'samples': [
        {
          'prediction_id': '01g4taktnzx8c8vvcz1w28ee0p',
          'strain_name': 'Old-time Moonshine',
          'effects': ['happy', 'focused'],
          'aromas': ['citrus', 'pine'],
          'rating': 10,
        },
      ]
    };

    // Post the user's actual data.
    const response = await authRequest('/api/stats/effects/actual', body);
    console.log(response);

    // Handle the user interface.
    document.getElementById('feedback-form').classList.add('d-none');
    document.getElementById('feedback-submit').classList.add('d-none');
    document.getElementById('feedback-thank-you').classList.remove('d-none');

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


  selectRating() {
    /**
     * Select a prediction rating.
     */
    // TODO: Remove outline from all ratings.

    // TODO: Add outline to the option that the user selected.

    // TODO: Add the rating to the input.
  },


};
