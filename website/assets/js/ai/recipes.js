/**
 * AI JavaScript | Cannlytics Website
 * Copyright (c) 2023 Cannlytics
 * 
 * Authors: Keegan Skeate <https://github.com/keeganskeate>
 * Created: 2/5/2023
 * Updated: 2/5/2023
 * License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>
 */
import { Modal } from 'bootstrap';
import { reportError } from '../payments/payments.js';
import { authRequest, capitalize, createUUID } from '../utils.js';
import { autocomplete } from '../ui/autocomplete.js';
import { showLoadingButton, hideLoadingButton } from '../ui/ui.js';
import { getCurrentUser, listenToCollection } from '../firebase.js';

export const RecipesAI = {

  initializeRecipes() {
    /**
     * Initialize the recipes page.
     */

    // Stream any user's recipes.
    const user = getCurrentUser();
    if (user != null) {
      this.streamUserRecipes();
    }

    // Stream public recipes.
    this.streamPublicRecipes();
  },

  /** Data Functionality */

  streamUserRecipes() {
    /**
     * Stream user recipes from Firestore.
     */
    console.log('Streaming user recipes...');
    // listenToCollection(
    //   path,
    //   params,
    //   queryCallback = null,
    //   addedCallback = null,
    //   modifiedCallback = null,
    //   removedCallback = null,
    //   errorCallback = null,
    // )
  },

  streamPublicRecipes() {
    /**
     * Stream public recipes from Firestore.
     */
    console.log('Streaming public recipes...');
    // listenToCollection(
    //   path,
    //   params,
    //   queryCallback = null,
    //   addedCallback = null,
    //   modifiedCallback = null,
    //   removedCallback = null,
    //   errorCallback = null,
    // )
  },

  /** API Functionality */

  async createRecipe() {
    /**
     * Create a recipe through the API.
     */
    // Show loading button.
    showLoadingButton('create-button');

    // TODO: Format the request data.
    const postData = {
      'image_type': '',
      'ingredients': [],
      'product_name': 'Infused cannabis coffee',
      'doses': null,
      'special_instructions': null,
      'creativity': 0.420,
      'public': true,
      'total_thc': 800,
      'total_cbd': 0,
    };

    // Make a request to create a recipe.
    const response = await authRequest('/api/ai/recipes', postData);
    if (response.success) {
      console.log(response.data)
    } else {
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

  deleteRecipe() {
    /**
     * Delete a recipe through the API.
     */
  },

  addRecipeReview() {
    /**
     * Add a recipe review through the API.
     */
  },

  addRecipeFeedback() {
    /**
     * Add recipe feedback through the API.
     */
  },

  /** UI Functionality */

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
      console.log('Color:')
      console.log(response);
      tempNode.style.backgroundColor = response['data'];
    } catch(error) {
      // Unable to query a color.
    }
    
    // Get an emoji for the badge from Firestore/OpenAI.
    // If emoji is not in Firestore, ask OpenAI and save to Firestore.
    try {
      const response = await authRequest('/api/ai/emoji', {text: value});
      console.log('Emoji:')
      console.log(response);
      document.getElementById(id).innerHTML = response['data'] + value;
    } catch(error) {
      // Unable to query a color.
    }
  },

  // TODO: Open recipe in a dialog.

  // TODO: Search recipes.

}


