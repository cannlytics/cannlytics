/**
 * Contact JavaScript | Cannlytics Website
 * Copyright (c) 2022 Cannlytics
 * 
 * Authors: Keegan Skeate <https://github.com/keeganskeate>
 * Created: 1/7/2022
 * Updated: 7/29/2022
 * License: MIT License <https://github.com/cannlytics/cannlytics-website/blob/main/LICENSE>
 */
import { getUrlParameter } from '../utils.js';

export const contact = {

  cannedMessages: {
    algorithms: {
      message: 'I am seeking help with a cannabis-related algorithm.',
      subject: 'Seeking Algorithm Help',
    },
    analyses: {
      message: 'I would like to suggest the following analyses and their prices:',
      subject: 'Suggest Analyses',
    },
    coas: {
      message: 'I am interested in extracting the data from my CoAs.',
      subject: 'CoA Data Extraction',
    },
    custom: {
      message: 'I have a custom project that I need developed.',
      subject: 'Custom Development',
    },
    data: {
      message: 'I am seeking your open cannabis data.',
      subject: 'Seeking Cannabis Data',
    },
    edit: {
      message: 'I would like to suggest the following data edit:',
      subject: 'Suggest Data Edit',
    },
    economics: {
      message: 'I am seeking assistance with economic analysis.',
      subject: 'Seeking Economic Analysis',
    },
    forecasting: {
      message: 'I am seeking forecasting.',
      subject: 'Seeking Forecasting',
    },
    general: {
      message: 'I am reaching out, please email me back.',
      subject: 'Contacting Cannlytics',
    },
    join: {
      message: 'I am interested in joining Cannlytics.',
      subject: 'Joining Cannlytics',
    },
    invest: {
      message: 'I am interested in investing in Cannlytics.',
      subject: 'Invest in Cannlytics',
    },
    lims: {
      message: 'I am interested in using the Cannlytics LIMS.',
      subject: 'Cannlytics LIMS',
    },
    metrc: {
      message: 'I am interested in using Cannlytics to integrate with Metrc.',
      subject: 'Metrc Integration',
    },
    paper: {
      message: 'I have a paper to submit.',
      subject: 'Submitting a Paper',
    },
    partner: {
      message: 'I am seeking to partner with Cannlytics.',
      subject: 'Partner with Cannlytics',
    },
    regulations: {
      message: 'I am interested in talking with you about regulations.',
      subject: 'Asking about Regulations',
    },
  },
  mathCheckTotal: 0,

  initializeContactForm() {
    /**
     * Initialize the contact form by creating a simple math check
     * and loading any canned contact message.
     */
    const min = this.randomIntFromInterval(0, 5);
    const max = this.randomIntFromInterval(0, 4);
    this.mathCheckTotal = min + max;
    document.getElementById('math_total').value = this.mathCheckTotal;
    document.getElementById('math-check-min').textContent = min;
    document.getElementById('math-check-max').textContent = max;
    this.setContactFormTopic();
  },

  randomIntFromInterval(min, max) {
    /**
     * Generate a random number in a given interval.
     * @param {Number} min The minimum of the range.
     * @param {Number} max The maximum of the range.
     */
    return Math.floor(Math.random() * (max - min + 1) + min);
  },

  setContactFormTopic(selectedTopic) {
    /**
     * Set the topic of the contact form.
     * @param {String} selectedTopic A user selected topic.
     */
    const topic = selectedTopic || getUrlParameter('topic');
    if (topic) {
      const cannedMessage = this.cannedMessages[topic];
      document.getElementById('message_input').value = cannedMessage.message;
      // document.getElementById('subject_input').value = cannedMessage.subject;
      document.getElementById('topic_input').value = topic;
    }
  },

  submitContactForm() {
    /**
      * Submit the contact form after validation.
      */
    const mathCheck = parseInt(document.getElementById('math_input').value);
    if (mathCheck !== this.mathCheckTotal) {
      cannlytics.showNotification('Match Check Mismatch', "Please try the math check again. We've implemented this to thwart abuse.", 'error');
      return false;
    }
    const email = document.getElementById('email_input').value;
    if (email === null || email === '') {
      cannlytics.showNotification('Email Required', 'Please enter a valid email so we can reply to your message.', 'error');
      return false;
    }
    const message = document.getElementById('message_input').value;
    if (message === null || message === '') {
      cannlytics.showNotification('Message Required', 'Please enter a message so we can reply to you.', 'error');
      return false;
    }
    return true;
  },

}
