/**
 * Website JavaScript | Cannlytics Website
 * Copyright (c) 2021-2022 Cannlytics
 * 
 * Authors: Keegan Skeate <keegan@cannlytics.com>
 * Created: 12/3/2020
 * Updated: 1/5/2022
 * License: MIT License <https://github.com/cannlytics/cannlytics-website/blob/main/LICENSE>
 */
import { checkGoogleLogIn, onAuthChange } from '../firebase.js';
import { setTableTheme } from '../ui/ui.js';
import { authRequest, hasClass } from '../utils.js';
import { contact } from './contact.js';

export const website = {

  ...contact,

  initialize() {
    /**
     * Initialize the website's features and functionality.
     */

    // Set the theme.
    this.setInitialTheme();

    // Scroll to any hash's anchor.
    this.scrollToHash();

    // Check if a user is signed in.
    onAuthChange(async user => {
      if (user) {
        document.getElementById('user-email').textContent = user.email;
        document.getElementById('user-name').textContent = user.displayName;
        if (user.photoURL) {
          document.getElementById('user-photo').src = user.photoURL;
        } else {
          const robohash = `${window.location.origin}/robohash/${user.email}/?width=60&height=60`;
          document.getElementById('user-photo').src = robohash;
        }
        this.toggleAuthenticatedMaterial(true);
        await authRequest('/src/auth/login');
        if (user.metadata.createdAt == user.metadata.lastLoginAt) {
          const { email } = user;
          const defaultPhoto = `${window.location.origin}/robohash/${user.email}/?width=60&height=60`;
          const data = { email, photo_url: defaultPhoto };
          await apiRequest('/api/users', data);
        }
      } else {
        this.toggleAuthenticatedMaterial(false);
        checkForCredentials();
      }
    });

  },

  acceptCookies() {
    /**
     * Save the user's choice to accept cookies.
     */
    localStorage.setItem('cannlytics_cookies', true);
    const toast = document.getElementById('accept-cookies');
    toast.style.display = 'none';
    toast.style.opacity = 0;
  },

  acceptCookiesCheck() {
    /**
     * Checks if a user has or has not accepted cookies.
     */
    const acceptCookies = localStorage.getItem('cannlytics_cookies');
    if (!acceptCookies) {
      const toast = document.getElementById('accept-cookies');
      toast.style.display = 'block';
      toast.style.opacity = 1;
    }
  },

  changeTheme() {
    /**
     * Change the website's theme.
     */
    let theme = localStorage.getItem('cannlytics_theme');
    if (!theme) {
      const hours = new Date().getHours();
      const dayTime = hours > 6 && hours < 20;
      theme = dayTime ? 'light' : 'dark';
    }
    const newTheme = (theme === 'light') ? 'dark' : 'light';
    this.setTheme(newTheme);
    setTableTheme();
    localStorage.setItem('cannlytics_theme', newTheme);
  },

  setInitialTheme() {
    /**
     * Set the theme when the website loads.
     */
    if (typeof(Storage) !== 'undefined') {
      let theme = localStorage.getItem('cannlytics_theme');
      if (!theme) {
        const hours = new Date().getHours();
        const dayTime = hours > 6 && hours < 20;
        if (!dayTime) this.setTheme('dark');
        return;
      }
      this.setTheme(theme);
      localStorage.setItem('cannlytics_theme', theme);
    } else {
      document.getElementById('theme-toggle').style.display = 'none';
    }
  },

  setTheme(theme) {
    /**
     * Set the website's theme.
     * @param {String} theme The theme to set: `light` or `dark`.
     */
    if (theme === 'light') document.body.className = 'base';
    else if (!hasClass(document.body, 'dark')) document.body.className += ' dark';
  },

  scrollToHash () {
    /**
     * Scroll to any an from any hash in the URL.
     */
    const hash = window.location.hash.substring(1);
    const element = document.getElementById(hash);
    if (element) element.scrollIntoView();
  },

  toggleAuthenticatedMaterial(authenticated = false) {
    /**
     * Show any material that requires authentication.
     * @param {bool} authenticated Whether or not the user is authenticated.
     */
    const indicatesAuth = document.getElementsByClassName('indicates-auth');
    const requiresAuth = document.getElementsByClassName('requires-auth');
    for (let i = 0; i < indicatesAuth.length; i++) {
      if (authenticated) indicatesAuth.item(i).classList.add('visually-hidden');
      else indicatesAuth.item(i).classList.remove('visually-hidden');
    }
    for (let i = 0; i < requiresAuth.length; i++) {
      if (authenticated) requiresAuth.item(i).classList.remove('visually-hidden');
      else requiresAuth.item(i).classList.add('visually-hidden');
    }
  },

}

async function checkForCredentials() {
  /**
   * Check if a user has signed in through a redirect from
   * an authentication provider, such as Google.
   */
  try {
    await checkGoogleLogIn();
    await authRequest('/api/internal/login');
  } catch(error) {
    // No Google sign-in token.
  }
}
