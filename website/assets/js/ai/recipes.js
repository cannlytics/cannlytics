/**
 * AI JavaScript | Cannlytics Website
 * Copyright (c) 2023 Cannlytics
 * 
 * Authors: Keegan Skeate <https://github.com/keeganskeate>
 * Created: 2/5/2023
 * Updated: 2/5/2023
 * License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>
 */
import { reportError } from '../payments/payments.js';
import { authRequest } from '../utils.js';
import { showLoadingButton, hideLoadingButton } from '../ui/ui.js';


export const RecipesAI = {

  initializeRecipes() {
    /**
     * Initialize the recipes page.
     */
  },

  getRecipes() {
    /**
     * Get recipes from the API.
     */
  },

  async createRecipe() {
    /**
     * Create a recipe through the API.
     */
    // Show loading button.
    showLoadingButton('create-button');

    // TODO: Format the request data.
    const postData = {};

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

  // TODO: Open recipe in a dialog.

  // TODO: Search recipes.

}
