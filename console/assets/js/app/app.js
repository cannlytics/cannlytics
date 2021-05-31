/**
 * app.js | Cannlytics Console
 * Licensed under GPLv3 (https://github.com/cannlytics/cannlytics_console/blob/main/LICENSE)
 * Author: Keegan Skeate <contact@cannlytics.com>
 * Created: 12/7/2020
 */
import { auth, signOut } from '../firebase.js';
import { authRequest } from '../utils.js';


export const app = {

  initialize() {
    /*
    * Initialize the console.
    */
    auth.onAuthStateChanged((user) => {
      console.log('Detected user:', user)
      if (user) {
        // initializeUserUI(user);
        // authRequest('/api/auth/authenticate');
        // TODO: Get user's organizations from Firestore through the API!
        // console.log('Getting user organizations...');
        // authRequest('/api/organizations').then((data) => {
        //   console.log('User organizations:', data);
        // });
        // FIXME: Hot-fix to reload page if sidebar is prompting login.
        // const signInMenu = document.getElementById('sidebar-menu-login');
        // if (signInMenu) location.reload();
      }
    });

    // Enable any and all tooltips.
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map((tooltipTriggerEl) => new bootstrap.Tooltip(tooltipTriggerEl) );

  },

  signOut: signOut,

  
  search() {
    /*
     * General search function to query the entire app and return the most
     * relevant page.
     */
    console.log('Searching...');
    const searchTerms = document.getElementById('navigation-search').value;
    // const urlParams = new URLSearchParams(window.location.search);
    // urlParams.set('q', searchTerms);
    // window.location.search = urlParams;
    // window.location.href = '/search';
    setGetParameter('q', searchTerms)
    // const query = URLSearchParams(window.location.search).get('q');
    // console.log(query);
  },

}


function setGetParameter(paramName, paramValue)
{
    var url = window.location.href;
    var hash = location.hash;
    url = url.replace(hash, '');
    if (url.indexOf(paramName + "=") >= 0)
    {
        var prefix = url.substring(0, url.indexOf(paramName + "=")); 
        var suffix = url.substring(url.indexOf(paramName + "="));
        suffix = suffix.substring(suffix.indexOf("=") + 1);
        suffix = (suffix.indexOf("&") >= 0) ? suffix.substring(suffix.indexOf("&")) : "";
        url = prefix + paramName + "=" + paramValue + suffix;
    }
    else
    {
    if (url.indexOf("?") < 0)
        url += "?" + paramName + "=" + paramValue;
    else
        url += "&" + paramName + "=" + paramValue;
    }
    window.location.href = `\\search\\${url}${hash}`;
}


function initializeUserUI(user) {
  /*
   * Setup user's UI based on their preferences and claims.
   */
  const organization = user.organization || 'Cannlytics';
  const navPhoto = document.getElementById('userPhotoNav');
  const menuPhoto = document.getElementById('userPhotoMenu');
  if (user.photoURL) {
    navPhoto.src = user.photoURL;
    menuPhoto.src = user.photoURL;
  }
  else {
    const robohash = `https://robohash.org/${user.email}?set=set5`;
    navPhoto.src = robohash;
    menuPhoto.src = robohash;
  }
  document.getElementById('anonymous-signup').classList.add('d-none');
  document.getElementById('userEmail').textContent = user.email;
  document.getElementById('userName').textContent = user.displayName;
  // TODO: Show Personalize your account button
  if (!user.displayName) {
    document.getElementById('personalize-account').classList.remove('d-none');
  }
  document.title = `${document.title.split('|')[0]} | ${organization}`;
  if (document.title.startsWith('|')) document.title = `Dashboard ${document.title}`;
}

