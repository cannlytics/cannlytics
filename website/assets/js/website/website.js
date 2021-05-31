/**
 * website.js | Cannlytics Website
 * Created: 12/3/2020
 */
import { auth } from '../firebase.js';


export const website = {


  initialize() {
    /*
     * Initialize the website's features and functionality.
     */
    
    // Initialize icons.
    feather.replace();

    // Initialize toasts.
    // this.initializeToasts();
    this.acceptCookiesCheck();

    // Set the theme.
    this.setInitialTheme();

    // Scroll to any hash's anchor.
    this.scrollToHash();

    // Keep track of user
    auth.onAuthStateChanged((user) => {
      if (user) {
        document.getElementById('user-email').textContent = user.email;
        document.getElementById('user-name').textContent = user.displayName;
        if (user.photoURL) {
          document.getElementById('user-photo').src = user.photoURL;
        } else {
          document.getElementById('user-photo').src = `/robohash/${user.email}/?width=60&height=60`
        }
        this.toggleAuthenticatedMaterial(true);
        // Save cookie.
      } else {
        this.toggleAuthenticatedMaterial(false);
      }
    });

  },


  initializeToasts() {
    /*
     * Initialize Bootstrap toasts.
     */
    var toast = document.getElementById('cookie-toast');
    new bootstrap.Toast(toast, { autohide: false });
  },


  acceptCookies() {
    /* Save choice that user accepted cookies. */
    localStorage.setItem('acceptCookies', true);
    var toast = document.getElementById('accept-cookies');
    toast.style.display = 'none';
    toast.style.opacity = 0;
    // TODO: Make entry in Firestore for cookie accepted?
  },


  acceptCookiesCheck() {
    /* Checks if a user needs to accept cookies. */
    var acceptCookies = localStorage.getItem('acceptCookies');
    if (!acceptCookies) {
      var toast = document.getElementById('accept-cookies');
      toast.style.display = 'block';
      toast.style.opacity = 1;
    }
  },


  changeTheme() {
    /* Change the website's theme. */
    var theme = localStorage.getItem('theme');
    if (!theme) {
      var hours = new Date().getHours();
      var dayTime = hours > 6 && hours < 20;
      theme = dayTime ? 'light' : 'dark';
    }
    var newTheme = (theme === 'light') ? 'dark' : 'light';
    this.setTheme(newTheme);
    localStorage.setItem('theme', newTheme);
  },


  setInitialTheme() {
    /* Set the theme when the website loads. */
    if (typeof(Storage) !== 'undefined') {
      var theme = localStorage.getItem('theme');
      if (!theme) {
        var hours = new Date().getHours();
        var dayTime = hours > 6 && hours < 20;
        if (!dayTime) this.setTheme('dark');
        return;
      }
      this.setTheme(theme);
      localStorage.setItem('theme', theme);
    } else {
      document.getElementById('theme-toggle').style.display = 'none';
    }
  },


  setTheme(theme) {
    /* Set the website's theme. */
    if (theme === 'light') {
      document.body.className = 'base';
    } else if (! this.hasClass(document.body, 'dark')) {
      document.body.className += ' dark';
    }
  },


  hasClass(element, className) {
    /* Check if an element has a class. */
    return (' ' + element.className + ' ').indexOf(' ' + className + ' ') > -1;
  },


  scrollToHash () {
    /* Scroll to any an from any hash in the URL. */
    var hash = window.location.hash.substring(1);
    var element = document.getElementById(hash);
    if (element) {
      element.scrollIntoView();
    }
  },


  copyToClipboard(text) {
    /* Prompt a user to copy a block of code to their clipboard. */
    // Optional: Improve getting only text from between tags.
    // https://aaronluna.dev/blog/add-copy-button-to-code-blocks-hugo-chroma/
    var tags = [
      /<span class="p">/g,
      /<\/span>/g,
      /<span class="nx">/g,
      /<span class="o">/g,
      /<span class="s2">/g,
      /<span class="kn">/g,
      /<span class="n">/g,
      /<span class="nn">/g,
    ];
    tags.forEach((tag) => {
      text = text.replace(tag, '');
    });
    window.prompt('Copy to clipboard: Press Ctrl+C, then Enter', text);
  },


  subscribe() {
    /* Subscribe to newsletter functionality. */
    var emailInput = document.getElementById('email-input');
    var subscribeBtn = document.getElementById('subscribe-button');
    var email = emailInput.value;
    if (!email) return; // TODO: Check if email is valid and notify user of error.
    subscribeBtn.disabled = true;
    var xhr = new XMLHttpRequest();
    xhr.addEventListener('readystatechange', function() {
      if (this.readyState === 4) {
        var jsonResponse = JSON.parse(this.responseText);
        var success = jsonResponse.message.success;
        if (success) {
          emailInput.value = '';
          document.location.href = '/subscribed';
        }
        else {
          // FIXME: Show success dismiss-able alert
          alert('Error subscribing. Please check that your email is valid and that you have a healthy internet connection.');
        }
        subscribeBtn.disabled = false;
      }
    });
    xhr.open('POST', '/subscribe');
    xhr.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded');
    xhr.send(`email=${email}`);
  },


  toggleAuthenticatedMaterial(authenticated=false) {
    /*
     * Show any material that requires authentication.
     */
    const indicatesAuth = document.getElementsByClassName('indicates-auth');
    const requiresAuth = document.getElementsByClassName('requires-auth');
    for (var i = 0; i < indicatesAuth.length; i++) {
      if (authenticated) indicatesAuth.item(i).classList.add('visually-hidden');
      else indicatesAuth.item(i).classList.remove('visually-hidden');
    }
    for (var i = 0; i < requiresAuth.length; i++) {
      if (authenticated) requiresAuth.item(i).classList.remove('visually-hidden');
      else requiresAuth.item(i).classList.add('visually-hidden');
    }
  },


  logPromo() {
    /*
     * Log a promotional event.
     */
    var code = this.getUrlParameter('source');
    if (!code) return;
    var data = { 'promo_code': code };
    fetch('/promotions/', {
      method: 'POST', 
      body: JSON.stringify(data),
      headers: { 'Accept': 'application/json' },
    });
  },


  getUrlParameter(name) {
    name = name.replace(/[\[]/, '\\[').replace(/[\]]/, '\\]');
    var regex = new RegExp('[\\?&]' + name + '=([^&#]*)');
    var results = regex.exec(location.search);
    return results === null ? '' : decodeURIComponent(results[1].replace(/\+/g, ' '));
  },


}
