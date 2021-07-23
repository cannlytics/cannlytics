/**
 * Authentication JavaScript | Cannlytics Console
 * Author: Keegan Skeate
 * Created: 12/4/2020
 * Updated: 6/23/2021
 */

import { apiRequest, authRequest, showNotification } from '../utils.js';


export const auth = {


  currentUser() { return firebase.auth().currentUser },


  anonymousSignIn() {
    /*
     * Anonymously sign-in a user.
     */
    return new Promise((resolve, reject) => {
      firebase.auth().signInAnonymously()
        .then(() => {
          resolve();
        })
        .catch((error) => {
          reject(error)
        });
    });
  },


  googleSignIn() {
    /*
     * Sign in a user with Google.
     */
    var provider = new firebase.auth.GoogleAuthProvider();
    firebase.auth().signInWithRedirect(provider);
  },


  googleSignInRedirect() {
    /*
     * Signs in a user after a successful Google sign-in redirect.
     */
    // FIXME: Login on redirect does not work
    console.log('Checking for Google redirect...')
    firebase.auth().getRedirectResult().then((result) => {
      if (result.credential) {
        // This gives you a Google Access Token. You can use it to access the Google API.
        // var token = result.credential.accessToken;
        // window.location.href = '/';
      }
      // The signed-in user info.
      var user = result.user;
      console.log('User:', user);
    }).catch((error) => {
      // Handle Errors here.
      var errorCode = error.code;
      var errorMessage = error.message;
      // The email of the user's account used.
      var email = error.email;
      // The firebase.auth.AuthCredential type that was used.
      var credential = error.credential;
      // ...
      console.log('Error:', errorMessage);
    });
  },


  resetPassword() {
    /*
     * Reset a user's password.
     */
    var auth = firebase.auth();
    var email = document.getElementById('login-email').value;
    auth.sendPasswordResetEmail(email).then(function() {
      window.location.href = '/account/password-reset-done';
    }).catch(function(error) {
      showNotification('Reset password error', error.message, { type: 'error' });
    });
  },


  resetPasswordCodeCheck() {
    /*
     * Check if the password reset code is valid.
     */
    const url = new URL(window.location.href);
    const code = url.searchParams.get('oobCode');
    firebase.auth().verifyPasswordResetCode(code)
      .then((email) => {
        document.getElementById('user-email').value = email;
      })
      .catch(()  => {
        const invalidMessage = document.getElementById('password-reset-code-invalid-message');
        const passwordResetForm = document.getElementById('password-reset-form');
        passwordResetForm.classList.add('d-none');
        invalidMessage.classList.remove('d-none');
      });
  },


  resetPasswordConfirm() {
    /*
     * Confirm a password reset.
     */
    const newPassword = document.getElementById('login-password').value;
    const newPasswordConfirmation = document.getElementById('login-password-confirmation').value;
    if (newPassword !== newPasswordConfirmation) {
      const message = 'The passwords you entered are not the same, please confirm your password.';
      showNotification('Passwords do not match', message, { type: 'error' });
      return;
    }
    firebase.auth().confirmPasswordReset(code, newPassword)
      .then(() => {
        window.location.href = '/account/password-reset-complete';
      })
      .catch(() => {
        const message = 'The password reset link that you used is invalid. Please request a new password reset link.';
        showNotification('Password reset error', message, { type: 'error' });
      });
  },


  signIn(event) {
    /*
     * Sign in a user.
     */
    event.preventDefault();
    var email = document.getElementById('login-email').value;
    var password = document.getElementById('login-password').value;
    document.getElementById('sign-in-button').classList.add('d-none');
    document.getElementById('sign-in-loading-button').classList.remove('d-none');
    firebase.auth().signInWithEmailAndPassword(email, password).then((user) => {
      return authRequest('/login').then((response) => {
        window.location.href = window.location.origin;
      })
      .catch((error) => {
        console.log(error);
        // Optional: Fix error returned by successful login.
        window.location.href = window.location.origin;
        // const message = 'Platform down for maintenance. Thank you for your patience.'
        // showNotification('Sign in error', message, { type: 'error' });
      });
    })
    // Optional: Determine if it's okay to stay signed in.
    // The Firestore docs show to sign out when using session cookies,
    // but this means that all requests to Firestore have to go through the API.
    // It is still nice to be able to interact with Firestore from client-side JavaScript.
    // .then(() => {
    //   // return firebase.auth().signOut();
    // }).then(() => {
    //   // window.location.href = window.location.origin;
    //   // window.location.assign('/');
    // })
    .catch((error) => {
      showNotification('Sign in error', error.message, { type: 'error' });
    }).finally(() => {
      document.getElementById('sign-in-button').classList.remove('d-none');
      document.getElementById('sign-in-loading-button').classList.add('d-none');
    });
  },
  
  
  signUp(event) {
    /*
     * Sign up a user.
     */
    event.preventDefault();
    const terms = document.getElementById('login-terms-accepted');
    if (!terms.checked) {
      const message = 'Please agree with our terms of service and read our privacy policy to create an account.';
      showNotification('Terms not accepted', message, { type: 'error' });
      terms.classList.add('is-invalid');
      return;
    } else {
      terms.classList.remove('is-invalid');
    }
    const email = document.getElementById('login-email').value;
    const password = document.getElementById('login-password').value;
    document.getElementById('sign-up-button').classList.add('d-none');
    document.getElementById('sign-up-loading-button').classList.remove('d-none');
    // FIXME: Ensure that sign-up works with user sessions.
    firebase.auth().createUserWithEmailAndPassword(email, password)
      .then(() => {
        // Optional: Handle error more elegantly.
        return authRequest('/login').then((response) => {
          this.postSignUp(email);
        })
        .catch((error) => {
          this.postSignUp(email);
        });
      })
      // .then(() => {
      //   apiRequest('/api/users', { email, photo_url: `https://robohash.org/${email}?set=set5` })
      //       .then(() => {
      //         window.location.href = window.location.origin;
      //       })
      //   // Optional: Implement user verification and don't send emails in development.
      //   // this.verifyUser();
      // })
      .catch((error) => {
        showNotification('Sign up error', error.message, { type: 'error' });
      })
      .finally(() => {
        document.getElementById('sign-up-button').classList.remove('d-none');
        document.getElementById('sign-up-loading-button').classList.add('d-none');
      });;
  },


  postSignUp(email) {
    /*
     * Post sign-up routine.
     */
    const data = { email, photo_url: `https://robohash.org/${email}?set=set5` };
    apiRequest('/api/users', data)
      .then(() => {
        window.location.href = window.location.origin;
      });
  },


  signOut() {
    /*
    * Sign a user out of Firebase and clear the session.
    */
    const baseURL = window.location.origin;
    console.log('Signing out....')
    authRequest('/logout')
      .then((response) => {
        console.log(response);
        document.location.href = `${window.location.origin}/account/sign-out`;
      })
      .catch((error) => {
        console.log(error);
        document.location.href = `${window.location.origin}/account/sign-out`;
      })
      .finally(() => {
        document.location.href = `${window.location.origin}/account/sign-out`;
      });
  },
  
  
  verifyUser() {
    /*
     * Send a user a verification email.
     */
    var user = firebase.auth().currentUser;
    user.sendEmailVerification().then(() => {
      showNotification('Verification email sent', error.message, { type: 'success' });
    }).catch(function(error) {
      console.log(error);
      showNotification('Verification error', error.message, { type: 'error' });
    });
  },


}
