/**
 * App JavaScript | Cannlytics Console
 * Copyright (c) 2021-2022 Cannlytics
 * 
 * Authors: Keegan Skeate <https://github.com/keeganskeate>
 * Created: 12/7/2020
 * Updated: 1/13/2022
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

    // Create a session when a user is detected, checking
    // if any Google credentials may have been passed.
    onAuthChange(async (user) => {
      if (user) {
        if (user.metadata.createdAt == user.metadata.lastLoginAt) {
          const { email } = user;
          const defaultPhoto = `https://cannlytics.com/robohash/${user.email}?width=60&height=60`;
          const data = { email, photo_url: defaultPhoto };
          await authRequest('/api/users', data);
        }
        const currentSession = this.getSessionCookie();
        // if (currentSession === 'None')
        await authRequest('/src/auth/login');
        if (redirect) window.location.href = window.location.origin;
      } else {
        checkForCredentials();
        // FIXME: If the user has not persisted their session, may need
        // to log out the user of their Django session with /src/logout
      }
    });

    // Hide the sidebar on small screens.
    try {
      navigationHelpers.toggleSidebar('sidebar-menu');
    } catch(error) { /* User not signed in. */}

  },

  getSessionCookie(nullValue='None') {
    /** Gets the session cookie, returning 'None' by default if the cookie is null. */
    return (document.cookie.match(/^(?:.*;)?\s*__session\s*=\s*([^;]+)(?:.*)?$/)||[,nullValue])[1];
  },

}
