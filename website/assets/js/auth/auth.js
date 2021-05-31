/**
 * auth.js | Cannlytics Website
 * Created: 1/17/2021
 */

import { auth as fbAuth, GoogleAuthProvider } from '../firebase.js';

export const auth = {


  signIn() {
    /*
     * Sign in with username and password.
     */
    const email = document.getElementById('login-email').value;
    const password = document.getElementById('login-password').value;
    fbAuth.signInWithEmailAndPassword(email, password)
      .then((user) => {
        const dialog = document.getElementById('login-dialog');
        const modal = bootstrap.Modal.getInstance(dialog);
        modal.hide();
      })
      .catch((error) => {
        const errorCode = error.code;
        const errorMessage = error.message;
        // TODO: Show error
        console.log('Error:', errorMessage);
      });
  },


  signOut() {
    /*
     * Sign a user out of their account.
     */
    fbAuth.signOut();
  },


  googleSignIn() {
    /*
     * Sign in with Google.
     */
    const provider = GoogleAuthProvider();
    firebase.auth().signInWithRedirect(provider);
  },


  resetPassword() {
    const email = document.getElementById('email-input').value;
    fbAuth.sendPasswordResetEmail(email).then(() => {
      // window.location.href = '/account/password-reset-done';
      // TODO: Show reset email sent toast.
    }).catch((error) => {
      const errorCode = error.code;
      const errorMessage = error.message;
      // TODO: Show error
      console.log('Error:', errorMessage);
    });
  },

  // TODO: Sign up.


}
