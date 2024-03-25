/**
 * Results JavaScript | Cannlytics Website
 * Copyright (c) 2021-2022 Cannlytics
 * 
 * Authors: Keegan Skeate <https://github.com/keeganskeate>
 * Created: 2/13/2024
 * Updated: 2/13/2024
 * License: MIT License <https://github.com/cannlytics/cannlytics-website/blob/main/LICENSE>
 */

export const resultsJS = {
  
  initializeResults() {
    /**
     * Initialize the results page.
     */
    console.log('Initializing results page.');
  },

  initializeResult() {
    /**
     * Initialize the result page.
     */
  },

  getLabResults(
    state = 'ALL',
    compound = null,
    producer = null,
    timeFrame = null,
  ) {
    const path = 'public/data/lab_results';
    const filters =[
      {"key": "lab_state", "operation": "==", "value": "MA"},
      // {"key": "compound", "operation": "==", "value": "THC"},
      // {"key": "producer", "operation": "==", "value": "Cannlytics"},
      // {"key": "timestamp", "operation": ">=", "value": "2024-02-01"},
    ];
    // let query = db.collection('labResults');
    // if (state !== 'ALL') {
    //   query = query.where('state', '==', state);
    // }
    // if (compound) {
    //   query = query.where('compound', '==', compound);
    // }
    // if (producer) {
    //   query = query.where('producer', '==', producer);
    // }
    // Time frame filter implementation depends on your data structure
    // For example, if filtering for results from the past week:
    // const oneWeekAgo = new Date();
    // oneWeekAgo.setDate(oneWeekAgo.getDate() - 7);
    // query = query.where('timestamp', '>=', oneWeekAgo);
  
    // FIXME:
    // query.limit(50).get().then((querySnapshot) => {
    //   const labResults = [];
    //   querySnapshot.forEach((doc) => {
    //     labResults.push(doc.data());
    //   });
    //   renderLabResults(labResults);
    // });
  }

};
