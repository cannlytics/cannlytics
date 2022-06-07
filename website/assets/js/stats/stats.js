/**
 * Statistics JavaScript | Cannlytics Website
 * Copyright (c) 2022 Cannlytics
 * 
 * Authors: Keegan Skeate <contact@cannlytics.com>
 * Created: 5/31/2022
 * Updated: 6/6/2022
 * License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>
 */
import { authRequest, capitalize, getUrlParameter, showNotification } from '../utils.js';
import { getDocument } from '../firebase.js';
import { navigationHelpers, hideLoadingButton, showLoadingButton } from '../ui/ui.js';
import { autocomplete } from '../ui/autocomplete.js';

export const stats = {


  strains: {},


  initializeModel() {
    /**
     * Initialize the model.
     */
    // FIXME:
    let model = getUrlParameter('model') || 'simple';
    model = model.replace('-', '_');
    document.getElementById('model-selection').value = model;
    document.getElementById(`${model}-fields`).classList.remove('d-none');
  },


  changeField(field) {
    /**
     * Change a field in the form.
     */
    // TODO: Implement.
    console.log('TODO: Change the corresponding input:', field);
  },


  changeModel(model) {
    /**
     * Change the prediction model, updating the user interface.
     */
    // TODO: Implement.
    console.log('TODO: Change the model!', model);
  },


  // async getDefinitions(ref) {
  //   /**
  //    * Get variable definitions and save them to local storage.
  //    * @param {String} ref The reference to the variable definitions.
  //    * @returns {Object} The variable definitions.
  //    */
  //   const data = await getDocument(ref);
  //   localStorage.setItem('variables', JSON.stringify(data));
  //   return data;
  // },


  getModelStats() {
    /**
     * Get the statistics for a given statistical model.
     */

    // TODO: Implement endpoint to get model statistics.
    // modelStats = authRequest('/api/market/download-lab-data');

    // TODO: Save model statistics to local storage.

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


  async getStrains() {
    /**
     * Get cannabis strains from the API.
     */
    const response = await authRequest('/api/data/strains');
    const strainNames = response.data.map(x => x.strain_name);
    autocomplete(document.getElementById('strain-name'),  strainNames);
    this.strains = response.data;
  },


  getStrainResults() {
    /**
     * Load a strain's average results into the user interface.
     */
    const strainName = document.getElementById('strain-name').value;
    let matched = false;
    this.strains.forEach((strain) => {
      if (strain.strain_name == strainName) {
        console.log('Matched:', strain);
        matched = true;
        // TODO: Populate the lab results form and predictions with the strain averages.
        this.renderPredictionForm(strain);
      }
    });
    if (!matched) showNotification('No Strain Records', 'No strain records at this moment.', 'error');
  },


  renderPredictionForm(prediction) {
    /**
     * Render the effects and aromas of a prediction in the prediction form.
     */
    document.getElementById('predicted-effects').innerHTML = '';
    // document.getElementById('predicted-symptoms').innerHTML = '';
    document.getElementById('predicted-aromas').innerHTML = '';
    const modelStats = prediction.model_stats;
    prediction.potential_effects.forEach((obs) => {
      // FIXME: Separate effects and symptoms.
      this.renderEffect(obs, 'predicted-effects', modelStats);
    });
    prediction.potential_aromas.forEach((obs) => {
      this.renderEffect(obs, 'predicted-aromas', modelStats);
    });
    document.getElementById('predictions').classList.remove('d-none');
  },


  renderEffect(value, listId, modelStats) {
    /**
     * Render effect in the UI.
     */
    const id = `predicted-${value}`;
    const docFrag = document.createDocumentFragment();
    const tempNode = document.getElementById('effect-card').cloneNode(true);
    const name = value.replace('effect_', '').replace('aroma_', '').replace('_', '');
    tempNode.id = id;

    // TODO: If it's a positive effect, then color green (success).
    // If it's a negative effect then color red (danger).
    // If it's an aroma then color based on the aroma's assigned color.
    tempNode.querySelector('.card-body').classList.add('text-bg-success');

    // FIXME: Get the effect/aroma icon.
    tempNode.querySelector('img').src = `https://cannlytics.com/static/website/images/emojies/${value}.svg`;
    tempNode.querySelector('img').alt = `${name}`;
    tempNode.querySelector('.card-title').textContent = capitalize(name);
    // tempNode.querySelector('.tpr').textContent = modelStats['true_positive_rate'][value];
    // tempNode.querySelector('.fpr').textContent = modelStats['false_positive_rate'][value];

    tempNode.classList.remove('d-none');
    docFrag.appendChild(tempNode);
    document.getElementById(listId).appendChild(docFrag);
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
    const id = `actual-${type}-${input.value}`;
    const docFrag = document.createDocumentFragment();
    const tempNode = document.getElementById('actual-effect-template').cloneNode(true);
    console.log(tempNode);
    const name = input.value.replace('effect_', '').replace('aroma_', '').replace('_', '');
    // tempNode.innerText = capitalize(name);
    tempNode.classList.remove('d-none');
    // TODO: If it's a positive effect, then color green (success).
    // If it's a negative effect then color red (danger).
    // If it's an aroma then color based on the aroma's assigned color.
    tempNode.classList.add('text-bg-success');
    tempNode.id = id;
    tempNode.querySelector('.badge-text').textContent = capitalize(name);
    tempNode.querySelector('.btn').onclick = function() {
      document.getElementById(id).classList.add('d-none');
    };
    docFrag.appendChild(tempNode);
    document.getElementById(`actual-${type}s`).appendChild(docFrag);
    input.value = '';
  },


  async submitActual() {
    /**
     * Submit the user's actually observed outcome.
     */

    // Get actual effects and aromas.
    showLoadingButton('submit-actual-button');
    const effects = Array.from(document.getElementById('actual-effects').children, ({textContent}) => textContent.trim());
    const aromas = Array.from(document.getElementById('actual-aromas').children, ({textContent}) => textContent.trim());

    // Format the user's actual data.
    const predictionId = document.getElementById('prediction-id').value;
    const predictionRating = document.getElementById('prediction-rating').value;
    const strainName = document.getElementById('strain-name').value;
    const body = {
      'samples': [
        {
          'aromas': aromas,
          'effects': effects,
          'prediction_id': predictionId,
          'prediction_rating': predictionRating,
          'strain_name': strainName,
        },
      ]
    };

    // Post the user's actual data.
    const response = await authRequest('/api/stats/effects/actual', body);
    if (!response.success) {
      showNotification('Error posting feedback', response.message, { type: 'error' });
      hideLoadingButton('submit-actual-button');
      return;
    }

    // Handle the user interface.
    document.getElementById('feedback-form').classList.add('d-none');
    document.getElementById('feedback-submit').classList.add('d-none');
    document.getElementById('feedback-thank-you').classList.remove('d-none');
    hideLoadingButton('submit-actual-button');

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


  selectRating(el) {
    /**
     * Select a prediction rating with the following 3 steps.
     * 1. Remove outline from all ratings.
     * 2. Add outline to the option that the user selected.
     * 3. Add the rating to the input.
     */
    const boxes = document.querySelectorAll('.btn-scale');
    boxes.forEach(box => {
      box.classList.remove('border-dark');
    });
    el.classList.add('border-dark');
    const value = parseInt(el.textContent);
    document.getElementById('prediction-rating').value = value;
  },


  showSearch() {
    /**
     * Show the search input for the user to search by strains.
     */
    const strains = this.getStrains();
    // TODO: Implement.
  },


  hideSearch() {
    /**
     * Hide the search input.
     */
    // TODO: Implement.
  },


  searchStrains() {
    /**
     * Search strains.
     */
  },


  cancelSearchStrains() {
    /**
     * Cancel searching strains.
     */
    document.getElementById('strain-name').value = '';
  },


  renderStrainData() {
    /**
     * Render a strain's lab results and predicted effects + aromas.
     */
    // TODO: Implement.
  },


};
