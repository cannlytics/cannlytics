/**
 * Dashboard JavaScript | Cannlytics Console
 * Copyright (c) 2021-2022 Cannlytics
 * 
 * Authors: Keegan Skeate <https://github.com/keeganskeate>
 * Created: 12/3/2020
 * Updated: 12/16/2021
 * License: MIT License <https://github.com/cannlytics/cannlytics-console/blob/main/LICENSE>
 */
import { signUp } from '../auth/auth.js';
import {
  changeEmail,
  getCurrentUser,
  onAuthChange,
  updateUserDisplayName,
} from '../firebase.js';
import { uploadOrgPhoto } from '../settings/organizations.js';
import { uploadUserPhoto } from '../settings/user.js';
import { authRequest, serializeForm, slugify, showNotification } from '../utils.js';

export const dashboard = {

  initializeGetStarted(stage) {
    /**
     * Initializes the get started forms.
     * @param {String} stage
     */
    onAuthChange(async (user) => {
      if (user) {
        if (stage === 'profile') {
          const data = await authRequest('/api/users');
          initializeGetStartedProfileUI(data);
        }
        else if (stage === 'organization') {
          initializeGetStartedOrganizationUI({});
        }
      }
    });
  },

  async saveUserData(type) {
    /**
     * Save's a user's data.
     * @param {String} orgType The type of user.
     */
    const data = serializeForm('user-form');
    const baseURL = window.location.origin;
    const user = getCurrentUser();
    data.type = type;
    data.account_created = true;
    if (user === null) {
      if (!data.email) {
        showNotification('Sign up error', 'Email required. Your email is private and used for verification and optional notifications only.', /* type = */ 'error');
        return;
      }
      try { 
        await signUp(data.email);
        document.location.href = `${baseURL}/get-started/organization?from=${type}`;
      } catch(error) {
        showNotification('Sign up error', error.message, /* type = */ 'error');
      }
    } else {
      if (!data.email) {
        showNotification('Sign up error', 'Email required. Your email is private and used for verification and optional notifications only.', /* type = */ 'error');
        return;
      }
      if (data.email !== user.email) {
        await changeEmail(data.email);
      }
      if (data.name !== user.displayName) {
        await updateUserDisplayName(data.name);
      }
      await authRequest('/api/users', data);
      document.location.href = `${baseURL}/get-started/organization?from=${type}`;
    }
  },

  selectSupportTier(tier) {
    /**
     * Add selected indicator to support choices.
     * @param {String} tier The user's selected tier of support.
     */
    const cards = document.getElementsByClassName('support-card');
    for (let i = 0; i < cards.length; i++) {
      cards[i].classList.remove('border-success', 'gold-shadow');
      if (cards[i].id === `tier-${tier}`) {
        cards[i].classList.add('border-success', 'gold-shadow');
        document.getElementById('input_tier').value = tier;
      }
    }
    document.getElementById('paypal-button-container').innerHTML = '';
    document.getElementById('finish-support-button').classList.remove('d-none');
    document.getElementById('cancel-support-button').classList.add('d-none');
  },

  async subscribe(subscription, redirect = true) {
    /**
     * Save a user's subscription data to Firestore.
     * @param {Object} subscription
     * @param {Boolean} redirect
     */
    const orgId = document.getElementById('organization_id').value;
    const response = await authRequest(`/src/payments/subscribe?organization_id=${orgId}`, subscription);
    if (response.success) {
      showNotification('Subscribed', response.message, /* type = */ 'success');
      if (redirect) window.location.href = window.location.origin;
    } else {
      showNotification('Unable to subscribe', response.message, /* type = */ 'error');
    }
  },

  showOrganizationForm(type) {
    /**
     * Show either the join or create organization forms or neither.
     * @param {String} type The type of organization.
     */
    document.getElementById('organization-setup-instructions').classList.add('d-none');
    document.getElementById('organization-choice').classList.add('d-none');
    if (type === 'join') {
      document.getElementById('cancel-join-organization').classList.remove('d-none');
      document.getElementById('join-organization-form').classList.remove('d-none');
    } else if (type === 'create') {
      document.getElementById('cancel-create-organization').classList.remove('d-none');
      document.getElementById('create-organization').classList.remove('d-none');
    } else {
      document.getElementById('cancel-join-organization').classList.add('d-none');
      document.getElementById('cancel-create-organization').classList.add('d-none');
      document.getElementById('join-organization-form').classList.add('d-none');
      document.getElementById('create-organization').classList.add('d-none');
      document.getElementById('organization-choice').classList.remove('d-none');
      document.getElementById('cancel-join-organization').classList.add('d-none');
      document.getElementById('organization-setup-instructions').classList.remove('d-none');
      document.getElementById('join-organization-input').value = '';
    }
  },

}

function initializeGetStartedProfileUI(data) {
  /**
   * Initialize the get-started profile section's form with existing values.
   * @param {Object} data
   */

  // Populate the form's fields.
  const form = document.getElementById('user-form');
  const { elements } = form;
  for (const [ key, value ] of Object.entries(data)) {
    const field = elements.namedItem(key);
    try {
      field && (field.value = value);
    } catch(error) {}
  }

  // Attach functionality.
  const fileElem = document.getElementById('userPhotoUrl');
  fileElem.addEventListener('change', uploadUserPhoto, false);

}

async function initializeGetStartedOrganizationUI(data) {
  /**
   * Initialize the get-started organization section,
   * attaching functionality.
   * @param {Object} data
   */
  const fileElem = document.getElementById('organization-photo-url');
  fileElem.addEventListener('change', uploadOrgPhoto, false);
  
  // Load public organizations for the user to chose an organization to join.
  const response = await authRequest('/api/organizations?public=true');
  const orgNames = response.data.map(org => `${org.name} (${org.id})`);
  autocomplete(document.getElementById('join-organization-input'),  orgNames);
}

// TODO: Refactor
function autocomplete(inp, arr) {
  /*the autocomplete function takes two arguments,
  the text field element and an array of possible autocompleted values:*/
  var currentFocus;
  /*execute a function when someone writes in the text field:*/
  inp.addEventListener("input", function(e) {
    var a, b, i, val = this.value;
    /*close any already open lists of autocompleted values*/
    closeAllLists();
    if (!val) { return false;}
    currentFocus = -1;
    /*create a DIV element that will contain the items (values):*/
    a = document.createElement("DIV");
    a.setAttribute("id", this.id + "autocomplete-list");
    a.setAttribute("class", "autocomplete-items");
    /*append the DIV element as a child of the autocomplete container:*/
    this.parentNode.appendChild(a);
    /*for each item in the array...*/
    for (i = 0; i < arr.length; i++) {
      /*check if the item starts with the same letters as the text field value:*/
      if (arr[i].substr(0, val.length).toUpperCase() == val.toUpperCase()) {
        /*create a DIV element for each matching element:*/
        b = document.createElement("DIV");
        /*make the matching letters bold:*/
        b.innerHTML = "<strong>" + arr[i].substr(0, val.length) + "</strong>";
        b.innerHTML += arr[i].substr(val.length);
        /*insert a input field that will hold the current array item's value:*/
        b.innerHTML += "<input type='hidden' value='" + arr[i] + "'>";
        /*execute a function when someone clicks on the item value (DIV element):*/
        b.addEventListener("click", function(e) {
          /*insert the value for the autocomplete text field:*/
          inp.value = this.getElementsByTagName("input")[0].value;
          /*close the list of autocompleted values,
          (or any other open lists of autocompleted values:*/
          closeAllLists();
        });
        a.appendChild(b);
      }
    }
});
/*execute a function presses a key on the keyboard:*/
inp.addEventListener("keydown", function(e) {
  var x = document.getElementById(this.id + "autocomplete-list");
  if (x) x = x.getElementsByTagName("div");
  if (e.keyCode == 40) {
    /*If the arrow DOWN key is pressed,
    increase the currentFocus variable:*/
    currentFocus++;
    /*and and make the current item more visible:*/
    addActive(x);
  } else if (e.keyCode == 38) { //up
    /*If the arrow UP key is pressed,
    decrease the currentFocus variable:*/
    currentFocus--;
    /*and and make the current item more visible:*/
    addActive(x);
  } else if (e.keyCode == 13) {
    /*If the ENTER key is pressed, prevent the form from being submitted,*/
    e.preventDefault();
    if (currentFocus > -1) {
      /*and simulate a click on the "active" item:*/
      if (x) x[currentFocus].click();
    }
  }
});
function addActive(x) {
  /*a function to classify an item as "active":*/
  if (!x) return false;
  /*start by removing the "active" class on all items:*/
  removeActive(x);
  if (currentFocus >= x.length) currentFocus = 0;
  if (currentFocus < 0) currentFocus = (x.length - 1);
  /*add class "autocomplete-active":*/
  x[currentFocus].classList.add("autocomplete-active");
}
function removeActive(x) {
  /*a function to remove the "active" class from all autocomplete items:*/
  for (var i = 0; i < x.length; i++) {
    x[i].classList.remove("autocomplete-active");
  }
}
function closeAllLists(elmnt) {
  /*close all autocomplete lists in the document,
  except the one passed as an argument:*/
  var x = document.getElementsByClassName("autocomplete-items");
  for (var i = 0; i < x.length; i++) {
    if (elmnt != x[i] && elmnt != inp) {
    x[i].parentNode.removeChild(x[i]);
  }
}
}
/*execute a function when someone clicks in the document:*/
document.addEventListener("click", function (e) {
  closeAllLists(e.target);
});
}
