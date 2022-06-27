/**
 * Statistics JavaScript | Cannlytics Website
 * Copyright (c) 2022 Cannlytics
 * 
 * Authors: Keegan Skeate <https://github.com/keeganskeate>
 * Created: 5/31/2022
 * Updated: 6/9/2022
 * License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>
 */
import { authRequest, capitalize, getUrlParameter, showNotification } from '../utils.js';
import { getDocument } from '../firebase.js';
import { hideLoadingButton, showLoadingButton } from '../ui/ui.js';
import { autocomplete } from '../ui/autocomplete.js';

export const personalityStats = {

  

}

export const stats = {

  // Statistics state variables.
  model: 'full',
  modelStats: {},
  strains: {},
  variables: {},


  initializeModel() {
    /**
     * Initialize the model.
     */
    this.model = getUrlParameter('model') || 'full';
    this.model = this.model.replace('-', '_');
    document.getElementById('model-selection').value = this.model;
    document.getElementById(`${this.model}-fields`).classList.remove('d-none');
    document.getElementById('strain-name').value = getUrlParameter('strain') || getUrlParameter('strain_name');
  },


  changeField(field, type) {
    /**
     * Change a field in the form.
     * @param {Element} field An input field.
     * @param {String} type The type of input; `'input'` or `'range'`.
     */
    const rangeId = `${type}-${this.model}-${field.name}`;
    document.getElementById(rangeId).value = field.value;
  },


  changeModel(select) {
    /**
     * Change the prediction model, updating the user interface.
     * @param {Element} select A selection element.
     */
    this.model = select.value;
    const boxes = document.querySelectorAll('.stats-model');
    boxes.forEach(box => { box.classList.add('d-none'); });
    document.getElementById(`${this.model}-fields`).classList.remove('d-none');
  },


  clearStrainName() {
    /**
     * Clear the strain name.
     */
    document.getElementById('strain-name').value = '';
  },


  async getModelStats() {
    /**
     * Get the statistics for a given statistical model.
     */
    const response = await authRequest(`/api/stats/effects?model=${this.model}`);
    this.modelStats = response.data;
  },


  async getVariables(ref) {
    /**
     * Get variable definitions and save them to local storage.
     * If there are compound query params, then they are parsed into the lab
     * results form. If the user passes a `predict` parameter, then predictions
     * are retrieved.
     * @param {String} ref The reference to the variable definitions.
     * @returns {Object} The variable definitions.
     */
    const data = await getDocument(ref);
    this.variables = data;
    const fields = this.variables.variables[this.model];
    fields.forEach((field) => {
      const { key } = field;
      let value = getUrlParameter(key);
      if (value) {
        // value = value.toFixed(2);
        document.getElementById(`input-${ this.model }-${ key }`).value = value;
        document.getElementById(`range-${ this.model }-${ key }`).value = value;
      }
    });
    // TODO: Handle strain names in URL?
    const predict = getUrlParameter('predict');
    if (predict) this.getPredictions();
  },


  async getPredictions() {
    /**
     * Get model predictions given the user's observation.
     */

    // Show loading wand on button.
    showLoadingButton('predict-button');

    // Format the observation.
    const model = document.getElementById('model-selection').value;
    const strainName = document.getElementById('strain-name').value;
    const body = { 'model': model, 'samples': [{ strain_name: strainName }] };

    // Get all of the analyte values for the given model.
    const fields = document.querySelectorAll(`.${model}-field`);
    fields.forEach((field) => {
      body.samples[0][field.name] = parseFloat(field.value);
    });

    // Make a request for model predictions.
    const response = await authRequest('/api/stats/effects', body);
    const { data } = response;
    const sample = data.samples[0];

    // Render effects, separating positive and negative effects, and aromas.
    this.renderPredictionForm(sample, data.model_stats);

    // Show the predictions.
    document.getElementById('prediction-id').value = sample.prediction_id;
    document.getElementById('predictions').classList.remove('d-none');

    // Remove loading wand from button.
    hideLoadingButton('predict-button');

    // TODO: Update the URL so the user can easily copy and return.

  },


  async getStrains(query = '') {
    /**
     * Get cannabis strains from the API.
     * @param {String} query An optional API query string, e.g. `'?limit=420'`.
     */
    let url = `/api/data/strains${query}`;
    const response = await authRequest(url);
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
        matched = true;
        this.renderLabResultsForm(strain);
        this.renderPredictionForm(strain, strain.model_stats);
        // TODO: Update the URL so the user can easily copy and return.
      }
    });
    if (!matched) showNotification('No Strain Records', 'No strain records at this moment.', 'error');
  },


  renderLabResultsForm(results) {
    /**
     * Render given lab results into the lab results form.
     * @param {Object} results An object of lab results.
     */
    const fields = this.variables.variables[this.model];
    fields.forEach((field) => {
      const { key } = field;
      let value = results[key];
      if (value) value = value.toFixed(2);
      document.getElementById(`input-${ this.model }-${ key }`).value = value;
      document.getElementById(`range-${ this.model }-${ key }`).value = value;
    });
  },


  renderPredictionForm(prediction, modelStats) {
    /**
     * Render the effects and aromas of a prediction in the prediction form.
     * @param {Object} prediction An object of model predictions.
     * @param {Object} modelStats An object of model statistics.
     */
    document.getElementById('predicted-effects').innerHTML = '';
    document.getElementById('predicted-aromas').innerHTML = '';
    const effects = prediction.potential_effects || prediction.predicted_effects;
    const aromas = prediction.potential_aromas || prediction.predicted_aromas;
    effects.forEach((obs) => { this.renderEffect(obs, 'effects', modelStats); });
    aromas.forEach((obs) => { this.renderEffect(obs, 'aromas', modelStats); });
    document.getElementById('predictions').classList.remove('d-none');
    if (effects.length === 0) this.renderPlaceholder('effects');
    if (aromas.length === 0) this.renderPlaceholder('aromas');
    // TODO: Bonus! Load 3 similar strains
  },


  renderEffect(value, type, modelStats) {
    /**
     * Render effect in the UI.
     * @param {String} value The key of the effect or aroma to render.
     * @param {String} type The type of values, `'effects'` or `'aromas'`.
     * @param {Object} modelStats An object of model statistics.
     */

    // Clone the card template.
    const docFrag = document.createDocumentFragment();
    const tempNode = document.getElementById('effect-card').cloneNode(true);
    const name = value.replace('effect_', '').replace('aroma_', '').replace('_', ' ');
    tempNode.id = `predicted-${value}`;

    // If it's a positive effect, then color green (success).
    // If it's a negative effect then color red (danger).
    // If it's an aroma then color based on the aroma's assigned color.
    if (type === 'effects') {
      const { positive } = this.variables[type][value];
      if (positive) tempNode.querySelector('.card-body').classList.add('text-bg-success');
      else tempNode.querySelector('.card-body').classList.add('text-bg-danger');
      tempNode.querySelector('.card-title').classList.add('text-dark');
      tempNode.querySelector('.tpr').classList.add('text-dark');
      // tempNode.querySelector('.fpr').classList.add('text-dark');
    } else {
      tempNode.querySelector('.card-body').style.backgroundColor = this.variables[type][value].color;
      tempNode.querySelector('.card-title').classList.add('text-black');
      tempNode.querySelector('.tpr').classList.add('text-black');
      // tempNode.querySelector('.fpr').classList.add('text-black');
    }

    // Get the effect/aroma icon.
    tempNode.querySelector('img').src = this.variables[type][value].icon_url;
    tempNode.querySelector('img').alt = `${name}`;
    tempNode.querySelector('.card-title').textContent = capitalize(name);

    // Get the model statistics.
    let tpr = 0 ;
    // let fpr = 0;
    try {
      tpr = (modelStats[value]['true_positive_rate'] * 100).toFixed(2);
      // fpr = (modelStats[value]['false_positive_rate'] * 100).toFixed(2);
    } catch(error) {
      tpr = (modelStats['true_positive_rate'][value] * 100).toFixed(2);
      // fpr = (modelStats['false_positive_rate'][value] * 100).toFixed(2);
    }
    tempNode.querySelector('.tpr').textContent = `TPR: ${tpr}%`;
    // tempNode.querySelector('.fpr').textContent = `FPR: ${fpr}%`;

    // Add the card to the UI.
    tempNode.classList.remove('d-none');
    docFrag.appendChild(tempNode);
    document.getElementById(`predicted-${type}`).appendChild(docFrag);
  },


  renderPlaceholder(type) {
    /**
     * Render a placeholder for no effects or aromas.
     * @param {String} type The type of placeholder, `'effects'` or `'aromas'`.
     */
    const docFrag = document.createDocumentFragment();
    const tempNode = document.getElementById('effect-placeholder-card').cloneNode(true);
    tempNode.querySelector('.card-title').textContent = `No Predicted ${capitalize(type)}`;
    tempNode.querySelector('.card-note').textContent = `Recommend ${type} below.`;
    tempNode.classList.remove('d-none');
    tempNode.id = `${type}-placeholder`;
    docFrag.appendChild(tempNode);
    document.getElementById(`predicted-${type}`).appendChild(docFrag);
  },


  resetObservationForm() {
    /**
     * Reset the form being used to submit observations.
     */
    document.getElementById('lab-results-form').reset();
  },


  closePredictions() {
    /**
     * Close the predictions.
     */
    document.getElementById('predictions').classList.add('d-none');
  },


  savePredictions() {
    /**
     * Save the model predictions.
     */

    // TODO: Implement: Export results to .xlsx and a .pdf
  },


  sharePredictions() {
    /**
     * Share the model predictions.
     */
    // TODO: Implement: Copy URL to clipboard?
  },


  selectActual(type, input) {
    /**
     * Select an actual effect.
     * @param {String} type The type of effect, , `'effect'` or `'aroma'`.
     */
    const value = input.value;
    const id = `actual-${type}-${value}`;
    const docFrag = document.createDocumentFragment();
    const tempNode = document.getElementById('actual-effect-template').cloneNode(true);
    const name = value.replace('effect_', '').replace('aroma_', '').replace('_', ' ');
    tempNode.classList.remove('d-none');
    if (type === 'effect') {
      const { positive } = this.variables[`${type}s`][value];
      if (positive) tempNode.classList.add('text-bg-success');
      else tempNode.classList.add('text-bg-danger');
    } else {
      tempNode.style.backgroundColor = this.variables[`${type}s`][value].color;
      tempNode.querySelector('.badge-text').classList.add('text-black');
    }
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

    // Populate the form with the lab results.
    // renderLabResultsForm(results);

  },


  selectRating(el) {
    /**
     * Select a prediction rating with the following 3 steps.
     * 1. Remove outline from all ratings.
     * 2. Add outline to the option that the user selected.
     * 3. Add the rating to the input.
     * @param {Element} el The button element selected.
     */
    const boxes = document.querySelectorAll('.btn-scale');
    boxes.forEach(box => { box.classList.remove('border-dark'); });
    el.classList.add('border-dark');
    const value = parseInt(el.textContent);
    document.getElementById('prediction-rating').value = value;
  },


  findSimilarStrains(sample) {
    /**
     * Find the most similar strains by given effects.
     * @param {Object} sample An object of sample data.
     */
    const candidates = {};

    // TODO: Get strains for each effect and aroma.
    sample.predicted_effects.forEach(async (effect) => {
      const strains = await getStrains(query = `?effects=${effect}`);
      // TODO: Keep list of predicted effects and aromas for each strain.

    });

    // TODO: Return candidates with the most effect and aroma matches.
  
  },


};
