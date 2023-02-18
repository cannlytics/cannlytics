/**
 * AI JavaScript | Cannlytics Website
 * Copyright (c) 2023 Cannlytics
 * 
 * Authors: Keegan Skeate <https://github.com/keeganskeate>
 * Created: 2/5/2023
 * Updated: 2/8/2023
 * License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>
 */
import { Modal } from 'bootstrap';
import { reportError } from '../payments/payments.js';
import { authRequest, capitalize, createUUID, showNotification } from '../utils.js';
import { autocomplete } from '../ui/autocomplete.js';
import { showLoadingButton, hideLoadingButton } from '../ui/ui.js';
import { onAuthChange, getCurrentUser, listenToCollection } from '../firebase.js';
import { updateDoc } from 'firebase/firestore';

export const RecipesAI = {

  initializeRecipes() {
    /**
     * Initialize the recipes page.
     */

    // Stream any user's recipes.
    onAuthChange(user => {
      if (user) {
        this.streamUserRecipes(user.uid);
      }
    });

    // Stream public recipes.
    // this.streamPublicRecipes();

    // Wire-up the recipe modal.
    const modal = document.getElementById('recipe-dialog')
    modal.addEventListener('show.bs.modal', this.openRecipe);
  },

  /** Data Functionality */

  streamUserRecipes(uid) {
    /**
     * Stream user recipes from Firestore.
     */
    const path = `users/${uid}/recipes`;
    const params = {desc: true, max: 10, order: 'created_at'};
    listenToCollection(path, params,
      (querySnapshot) => {
        if (querySnapshot.empty) {
          document.getElementById('user-recipes-placeholder').classList.remove('d-none');
          return;
        } else {
          try {
            document.getElementById('user-recipes-placeholder').classList.add('d-none');
            document.getElementById('user-recipes').textContent = '';
          } catch(error) {
            // User may not be signed in on server.
          }
        }
        querySnapshot.forEach((doc) => {

          // Render or update recipe thumbnails.
          this.addRecipeThumbnail(doc.id, doc.data());

        });
      },
      (error) => {
        showNotification('Error retrieving recipes', error, /* type = */ 'error');
      },
    )
  },

  streamPublicRecipes() {
    /**
     * Stream public recipes from Firestore.
     */

    // FIXME: Stream public recipes.
    // listenToCollection(
    //   path,
    //   params,
    //   queryCallback = null,
    //   addedCallback = null,
    //   modifiedCallback = null,
    //   removedCallback = null,
    //   errorCallback = null,
    // )

    // TODO: Hide `public-recipes-placeholder` if recipes.

    // TODO: Add filled recipe templates to `public-recipes` container.

    // TODO: Show `public-recipes-placeholder` if no recipes.
  },

  /** API Functionality */

  async createRecipe() {
    /**
     * Create a recipe through the API.
     */
    // Show loading button.
    showLoadingButton('create-button');

    // Get all of the ingredients.
    const ingredients = []
    const ingredientInputs = document.getElementsByClassName('ingredient');
    Array.prototype.forEach.call(ingredientInputs, function(el) {
      const ingredient = el.textContent;
      if (ingredient != '') ingredients.push(ingredient);
    });

    // Get the units for the results.
    const units = document.getElementById('units-input').value;

    // Calculate total THC and CBD using the decarboxylation rate.
    const decarb = 0.877;
    let thc = parseFloat(document.getElementById('thc-input').value);
    if (isNaN(thc)) thc = 0.0;
    const thca = parseFloat(document.getElementById('thca-input').value);
    if (!isNaN(thca)) thc = thc + (decarb * thca);
    let cbd = parseFloat(document.getElementById('cbd-input').value);
    if (isNaN(cbd)) cbd = 0.0;
    const cbda = parseFloat(document.getElementById('cbda-input').value);
    if (!isNaN(cbda)) cbd = cbd + (decarb * cbda);

    // Incorporate weight and units into the total THC and CBD calculation.
    const weight = document.getElementById('weight-input').value;
    const weightUnits = document.getElementById('weight-units-input').value;
    if (weightUnits == 'g' && units == 'percent') {
      thc = thc * 10 * weight;
      cbd = cbd * 10 * weight;
    } else if (weightUnits == 'g') {
      thc = thc * weight;
      cbd = cbd * weight;
    } else {
      thc = thc * (weight * 0.001);
      cbd = cbd * (weight * 0.001);
    }

    // Get all other compounds.
    const doses = [];
    const compoundNames = document.getElementsByClassName('compound-name');
    const compoundAmounts = document.getElementsByClassName('compound-amount');
    Array.prototype.forEach.call(compoundNames, function(el, n) {
      const name = el.value;
      const amount = compoundAmounts[n].value;
      if (name != '') {
        doses.push({'units': units, 'value': amount, 'name': name});
      }
    });

    // Restrict creativity to between 0 and 1 before posting.
    let creativity = document.getElementById('creativity-input').value * 0.01;
    if (creativity < 0) creativity = 0;
    if (creativity > 1) creativity = 1;

    // Format the request data.
    const postData = {
      'image_type': document.getElementById('image-type-input').value,
      'ingredients': ingredients,
      'product_name': document.getElementById('product-name-input').value,
      'product_type': document.getElementById('product-type-input').value,
      'doses': doses,
      'special_instructions': document.getElementById('special-instructions-input').value,
      'creativity': creativity,
      'public': document.getElementById('public-input').checked,
      'total_thc': thc,
      'total_cbd': cbd,
      'units': 'mg',
    };

    // Show baking notification.
    const message = 'Baking recipe... this may take a hot minute!';
    showNotification('Baking recipe', message, /* type = */ 'wait');

    // Make a request to create a recipe.
    try {
      response = await authRequest('/api/ai/recipes', postData);
      console.log(response);
      const message = 'Created your new recipe. Enjoy!';
      showNotification('Recipe created', message, /* type = */ 'success');
    } catch(error) {
      const message = 'Error encountered when creating recipe. Please try again later or email support.';
      showNotification('Error creating recipe', message, /* type = */ 'error');
    }

    // Hide loading button.
    hideLoadingButton('create-button');
  },

  updateRecipe() {
    /**
     * Update a recipe through the API.
     */

    // TODO: Format the request data.
    const postData = {
      'ingredients': [],
      'title': '',
      'doses': null,
      'instructions': '',
      'special_instructions': null,
      'creativity': 0.420,
      'change_recipe': true,
      'change_image': true,
      'change_title': true,
      'public': true,
    };
  },

  async deleteRecipe() {
    /**
     * Delete a recipe through the API.
     */
    // Get the recipe ID.
    const id = document.getElementById('recipe-id').textContent;

    // Make a request to delete the recipe.
    const response = await authRequest('/api/ai/recipes', null, {delete: true});
    if (!response.success) {
      const message = 'Error encountered when deleting recipe. Please try again later or email support.';
      showNotification('Error deleting recipe', message, /* type = */ 'error');
    }

    // Close the modal.
    const modal = new Modal(document.getElementById('recipe-dialog'), {});
    modal.hide();
  },

  addRecipeReview() {
    /**
     * Add a recipe review through the API.
     */
    // TODO: Implement!
    const options = {params: {action: 'review'}};
  },

  async addRecipeFeedback() {
    /**
     * Add recipe feedback through the API.
     */
    // Show loading indicator.
    showLoadingButton('recipe-feedback');
  
    // Get the user's feedback.
    const data = {
      feedback: document.getElementById('feedback-review').value,
      like: null,
      recipe_id: document.getElementById('recipe-id').textContent,
    };

    // Post the user's feedback through the API.
    const options = {params: {action: 'feedback'}};
    const response = await authRequest('/api/ai/recipes?action=feedback', data);
    if (!response.success) {
      showNotification('Error posting feedback', response.message, { type: 'error' });
      hideLoadingButton('recipe-feedback');
      return;
    }

    // Handle the user interface.
    try {
      hideLoadingButton('recipe-feedback');
      document.getElementById('feedback-form').classList.add('d-none');
      document.getElementById('feedback-submit').classList.add('d-none');
      document.getElementById('feedback-thank-you').classList.remove('d-none');  
    } catch(error) {
      // User interface not behaving!
    }
  },

  saveRecipe() {
    /**
     * Save a user's edits to their recipe.
     */
    // Get the recipe ID.
    const id = document.getElementById('recipe-id').textContent;
    const user = getCurrentUser();
    const uid = user.uid;

    // Save the data to Firestore!
    const ref = `users/${uid}/recipes/${id}`;
    updateDoc(ref, {
      description: document.getElementById('recipe-description').value,
      recipe: document.getElementById('recipe-text').value,
      // TODO: Allow the user to edit and save more fields:
      // - title
    })

    // Close the modal.
    const modal = new Modal(document.getElementById('recipe-dialog'), {});
    modal.hide();
  },

  /** UI Functionality */

  resetRecipe() {
    /**
     * Reset the recipe form.
     */
    document.getElementById('thc-input').value = '';
    document.getElementById('thca-input').value = '';
    document.getElementById('cbd-input').value = '';
    document.getElementById('cbda-input').value = '';
    document.getElementById('ingredients').textContent = '';
    document.getElementById('additional-compounds').textContent = '';
    document.getElementById('public-input').checked = false;
    document.getElementById('creativity-input').value = 42;
    document.getElementById('creativity-percent-input').value = 42;
    document.getElementById('product-name-input').value = '';
    document.getElementById('product-type-input').value = 'flower';
    document.getElementById('weight-units-input').value = 'g';
    document.getElementById('units-input').value = 'percent';
    document.getElementById('image-type-input').value = 'Drawing';
    document.getElementById('special-instructions-input').value = '';
  },

  async addIngredient(inputId, containerId, templateId) {
    /**
     * Add an ingredient.
     */
    // Get the value.
    const input = document.getElementById(inputId);
    const value = input.value;
    if (value === null || value === '') return;

    // Create a new badge.
    const id = createUUID();
    const docFrag = document.createDocumentFragment();
    const tempNode = document.getElementById(templateId).cloneNode(true);
    const name = value.replaceAll('_', ' ');
    tempNode.classList.remove('d-none');
    
    // Add the badge to the UI with a remove button.
    tempNode.querySelector('.badge-text').classList.add('text-black');
    tempNode.id = id;
    tempNode.querySelector('.badge-text').textContent = capitalize(name);
    tempNode.querySelector('.btn').onclick = function() {
      document.getElementById(id).remove();
    };
    docFrag.appendChild(tempNode);
    document.getElementById(containerId).appendChild(docFrag);
    input.value = '';

    // Get a color for the badge from Firestore/OpenAI.
    // If color is not in Firestore, ask OpenAI and save to Firestore.
    try {
      const response = await authRequest('/api/ai/color', {text: value});
      tempNode.style.backgroundColor = response['data'];
    } catch(error) {
      // Unable to query a color.
    }

    // Get an emoji for the badge from Firestore/OpenAI.
    // If emoji is not in Firestore, ask OpenAI and save to Firestore.
    try {
      const response = await authRequest('/api/ai/emoji', {text: value});
      const html = document.getElementById(id).innerHTML
      document.getElementById(id).innerHTML = response['data'] + html;
    } catch(error) {
      // Unable to query a color.
    }
  },

  changeUnits() {
    /**
     * Change the units (mg, ml, %)
     */
  },

  changeWeight() {
    /**
     * Change the units (mg, ml, %)
     */
  },

  changeWeightUnits() {
    /**
     * Change the units (mg, ml, %)
     */
  },

  calcTotalTHC() {
    /**
     * Calculate total THC.
     */
  },

  changeCreativity(field, id) {
    /**
     * Change a field in the form.
     * @param {Element} field An input field.
     * @param {String} id The ID of the corresponding input.
     */
    document.getElementById(id).value = field.value;
  },

  addCompound() {
    /**
     * Add a compound to the recipe.
     */
    const containerId = 'additional-compounds';
    const templateId = 'compound-template';
    const id = createUUID();
    const docFrag = document.createDocumentFragment();
    const tempNode = document.getElementById(templateId).cloneNode(true);
    tempNode.id = id;
    tempNode.classList.remove('d-none');
    tempNode.querySelector('.btn').onclick = function() {
      document.getElementById(id).remove();
    };
    const inputs = tempNode.getElementsByTagName('input')
    inputs[0].id = `${id}-name`;
    inputs[1].id = `${id}-amount`;
    docFrag.appendChild(tempNode);
    document.getElementById(containerId).appendChild(docFrag);
  },

  addRecipeThumbnail(id, obs) {
    /**
     * Add a compound to the recipe.
     */
    const containerId = 'user-recipes';
    const templateId = 'recipe-thumbnail';
    const docFrag = document.createDocumentFragment();
    const el = document.getElementById(templateId).cloneNode(true);
    el.id = id;
    el.classList.remove('d-none');

    // Add image.
    const img = el.querySelector('.recipe-image');
    img.src = obs['file_url'];
    img.classList.remove('d-none');

    // Render thumbnail data.
    el.querySelector('.title').textContent = obs.title;
    el.querySelector('.description').textContent = obs.description;

    // Save data to HTML and set-up dialog.
    el.querySelector('.stretched-link').setAttribute('data-bs-sample', id);
    el.querySelector('.recipe-data').textContent = JSON.stringify(obs);

    // TODO: Wire-up delete button
    // el.querySelector('.btn').onclick = function() {
    //   document.getElementById(id).remove();
    // };

    // Add thumbnail to the UI.
    docFrag.appendChild(el);
    document.getElementById(containerId).appendChild(docFrag);
  },

  openRecipe(event) {
    /**
     * Open recipe in a dialog.
     * @param {Event} event The button that triggered the function.
     */
    // Get the recipe ID.
    const button = event.relatedTarget;
    const id = button.getAttribute('data-bs-sample');
    
    // Get the data from HTML.
    const card = document.getElementById(id);
    const obs = JSON.parse(card.querySelector('.recipe-data').textContent);
    
    // Render the recipe data.
    document.getElementById('recipe-id').textContent = id;
    document.getElementById('recipe-dialog-title').textContent = obs.title;
    document.getElementById('recipe-text').value = obs.recipe;
    document.getElementById('recipe-description').value = obs.description;
    
    // TODO: Render recipe metadata:
    // - version
    // - updated_at
    // - created_at
    // - created_by

    // TODO: Render recipe inputs:
    // - total_weight
    // - product_name
    // - product_subtype
    // - product_type
    // - public

    // TODO: Render lists:
    // - ingredients
    // - THC / THCA / CBD / CBDA (?)
    // - doses of other compounds
    document.getElementById('serving_thc').textContent = `THC: ${obs.serving_thc}mg`;
    document.getElementById('serving_cbd').textContent = `CBD: ${obs.serving_cbd}mg`;
    document.getElementById('total_thc').textContent = `THC: ${obs.total_thc}mg`;
    document.getElementById('total_cbd').textContent = `CBD: ${obs.total_cbd}mg`;
    document.getElementById('number_of_servings').textContent = `Number of servings: ${obs.number_of_servings}`;

    // Render the image.
    const img = document.getElementById('recipe-large-image');
    img.src = obs['file_url'];
    img.classList.remove('d-none');

    // Reset the feedback form.
    document.getElementById('feedback-form').classList.remove('d-none');
    document.getElementById('feedback-submit').classList.remove('d-none');
    document.getElementById('feedback-thank-you').classList.add('d-none'); 
    document.getElementById('feedback-review').value = '';
  },

  // Future work: Search recipes.

}
