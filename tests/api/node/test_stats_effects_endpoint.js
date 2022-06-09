/**
 * Test Effects and Aromas API
 * Copyright (c) 2022 Cannlytics
 * 
 * Authors: Keegan Skeate <https://github.com/keeganskeate>
 * Created: 6/9/2022
 * Updated: 6/9/2022
 * License: MIT License <https://opensource.org/licenses/MIT>
 */
const axios = require('axios');

// Define the base URL
const base = 'https://cannlytics.com/api';

// Get a model's statistics.
params = { model: 'full' };
axios.get(`${base}/stats/effects`, { params })
  .then(response => {
    console.log(response.data);
  })
  .catch(error => {
    console.log(error);
  });


// Post lab results to get potential effects and aromas (simple model).
var data = {
  'model': 'simple',
  'samples': [
    {
      'strain_name': 'Old-time Moonshine',
      'total_cbd': 0.4,
      'total_thc': 20.0
    },
  ]
};
axios.post(`${base}/stats/effects`, data)
  .then(response => {
    console.log(response.data);
  })
  .catch(error => {
    console.log(error);
  });

// Post lab results to get potential effects and aromas (full model).
var data = {
  'model': 'full',
  'samples': [
    {
      'strain_name': 'Super Sport',
      'cbc': 0,
      'cbd': 0,
      'cbda': 0,
      'cbg': 0,
      'cbga': 1.58,
      'cbn': 0,
      'delta_8_thc': 0,
      'delta_9_thc': 0.65,
      'thca': 39.29,
      'thcv': 0.21,
      'alpha_bisabolol': 0,
      'alpha_pinene': 1.07,
      'alpha_terpinene': 0,
      'beta_caryophyllene': 0,
      'beta_myrcene': 0.63,
      'beta_pinene': 0.28,
      'camphene': 0,
      'carene': 0,
      'caryophyllene_oxide': 0,
      'd_limonene': 0.17,
      'eucalyptol': 0,
      'gamma_terpinene': 0,
      'geraniol': 0,
      'guaiol': 0,
      'humulene': 0,
      'isopulegol': 0,
      'linalool': 0,
      'nerolidol': 0,
      'ocimene': 0,
      'p_cymene': 0,
      'terpinene': 0,
      'terpinolene': 0,
    },
  ]
};
axios.post(`${base}/stats/effects`, data)
  .then(response => {
    console.log(response.data);
  })
  .catch(error => {
    console.log(error);
  });


// Post actual aromas and effects, rating the usefulness of the predictions.
var data = {
  'samples': [
    {
      'prediction_id': '01g4taktnzx8c8vvcz1w28ee0p',
      'strain_name': 'Old-time Moonshine',
      'effects': ['happy', 'focused'],
      'aromas': ['citrus', 'pine'],
      'rating': 10,
    },
    {
      'prediction_id': '01g54v5yvpfvfch3h8e61ne83x',
      'strain_name': 'Super Sport',
      'effects': ['focused', 'creative'],
      'aromas': ['diesel', 'flowery'],
      'rating': 10,
    },
  ]
};
axios.post(`${base}/stats/effects/actual`, data)
  .then(response => {
    console.log(response.data);
  })
  .catch(error => {
    console.log(error);
  });
