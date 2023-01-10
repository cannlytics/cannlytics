/**
 * App JavaScript | Cannlytics Console
 * Copyright (c) 2021-2023 Cannlytics
 * 
 * Authors: Keegan Skeate <https://github.com/keeganskeate>
 * Created: 12/7/2020
 * Updated: 1/8/2023
 * License: MIT License <https://github.com/cannlytics/cannlytics-console/blob/main/LICENSE>
 */
import { checkForCredentials } from '../auth/auth.js';
import { onAuthChange } from '../firebase.js';
import { authRequest } from '../utils.js';
import { initHelpers, navigationHelpers } from '../ui/ui.js';
import { dataTables } from './dataTables.js';
import { dataModels } from './dataModels.js';

export const app = {

  ...dataModels,
  ...dataTables,

  initialize(redirect=false) {
    /**
     * Initialize the console's features and functionality.
     * @param {Boolean} redirect Whether or not to redirect the user to the
     *    dashboard (optional).
     */

    // Enable any and all tooltips.
    initHelpers.initializeTooltips();

    // Create a user session if a user is detected.
    onAuthChange(async (user) => signInUser(user, redirect));

    // Hide the sidebar on small screens.
    try {
      navigationHelpers.toggleSidebar('sidebar-menu');
    } catch(error) { /* User not signed in. */}

  },

  // getSessionCookie(nullValue='None') {
  //   /** Gets the session cookie, returning 'None' by default if the cookie is null. */
  //   return (document.cookie.match(/^(?:.*;)?\s*__session\s*=\s*([^;]+)(?:.*)?$/)||[,nullValue])[1];
  // },

}

function getSessionCookie(nullValue='None') {
  /** Gets the session cookie, returning 'None' by default if the cookie is null. */
  return (document.cookie.match(/^(?:.*;)?\s*__session\s*=\s*([^;]+)(?:.*)?$/)||[,nullValue])[1];
}

async function signInUser(user, redirect=false) {
  /**
   * Create a session when a user is detected, checking
   * if any Google credentials may have been passed.
   */
  if (user) {

    console.log(`USER DETECTED: ${user.uid}`);

    // Set user data on first login.
    if (user.metadata.createdAt == user.metadata.lastLoginAt) {
      const { email } = user;
      const defaultPhoto = `https://cannlytics.com/robohash/${user.uid}?width=60&height=60`;
      const data = { email, photo_url: defaultPhoto };
      await authRequest('/api/users', data);
    }
    
    // Only authenticate with the server as needed.
    const currentSession = getSessionCookie();
    if (currentSession === 'None') await authRequest('/src/auth/login');
    if (redirect) window.location.href = window.location.origin;
    try {
      document.getElementById('splash').classList.add('d-none');
      document.getElementById('page').classList.remove('d-none');
    } catch(error) {
      // No splash page.
    }

  } else {

    console.log('NO USER');
    
    // If the user has not persisted their session, then log out of their
    // Django session, and redirect to the sign in page.
    await checkForCredentials();
    const currentSession = getSessionCookie();
    if (currentSession === 'None') await authRequest('/src/auth/logout');
    if (!window.location.href.includes('account')) {
      window.location.href = `${window.location.origin}\\account\\sign-in`;
      await page.waitForNavigation();
    }
    document.getElementById('page').classList.remove('d-none');
  
  }
}
