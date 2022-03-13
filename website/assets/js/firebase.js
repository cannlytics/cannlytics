/**
 * Firebase JavaScript | Cannlytics Website
 * Copyright (c) 2021-2022 Cannlytics
 * 
 * Authors: Keegan Skeate <keegan@cannlytics.com>
 * Created: 12/22/2020
 * Updated: 1/21/2022
 * License: MIT License <https://github.com/cannlytics/cannlytics-website/blob/main/LICENSE>
 */
import { initializeApp } from 'firebase/app';
// import { getAnalytics, logEvent } from 'firebase/analytics';
import {
  browserSessionPersistence,
  confirmPasswordReset,
  createUserWithEmailAndPassword,
  deleteUser,
  getAuth,
  getRedirectResult,
  GoogleAuthProvider,
  inMemoryPersistence,
  onAuthStateChanged,
  updatePassword,
  updateProfile,
  reauthenticateWithCredential,
  sendEmailVerification,
  sendPasswordResetEmail,
  setPersistence,
  signInWithCustomToken,
  signInWithEmailAndPassword,
  signInWithRedirect,
  signOut,
  verifyPasswordResetCode,
} from 'firebase/auth';
import {
  arrayRemove,
  arrayUnion,
  getFirestore,
  getDoc,
  getDocs,
  setDoc,
  deleteField,
  deleteDoc,
  collection,
  doc,
  query,
  where,
  orderBy,
  limit,
  onSnapshot,
  updateDoc,
} from 'firebase/firestore';
import {
  getStorage,
  getDownloadURL,
  ref,
  uploadBytes,
  uploadString,
  deleteObject,
} from 'firebase/storage';

// Initialize Firebase.
const firebaseApp = initializeApp({
  apiKey: process.env.FIREBASE_API_KEY,
  authDomain: process.env.FIREBASE_AUTH_DOMAIN,
  databaseURL: process.env.FIREBASE_DATABASE_URL,
  projectId: process.env.FIREBASE_PROJECT_ID,
  storageBucket: process.env.FIREBASE_STORAGE_BUCKET,
  messagingSenderId: process.env.FIREBASE_MESSAGING_SENDER_ID,
  appId: process.env.FIREBASE_APP_ID,
  // measurementId: process.env.FIREBASE_MEASUREMENT_ID,
});

// Get core modules.
// const analytics = getAnalytics(firebaseApp);
const auth = getAuth(firebaseApp);
const db = getFirestore(firebaseApp);
const storage = getStorage(firebaseApp);
 
/*------------------------------------------------------------------------------
 * Firestore Interface
 *----------------------------------------------------------------------------*/

const addToArray = async (path, field, value) => {
  /**
  * Add a value to an array field in a Firestore document.
  * @param {String} path The path to the document.
  * @param {String} field An array field in the document.
  * @param {Dynamic} value A value to be added to the array.
  */
  const documentRef = createDocumentReference(path);
  const update = {};
  update[field] = arrayUnion(value);
  await updateDoc(documentRef, update);
};

const removeFromArray = async (path, field, value) => {
  /**
  * Remove a value from an array field in a Firestore document.
  * @param {String} path The path to the document.
  * @param {String} field An array field in the document.
  * @param {Dynamic} value A value to be removed from the array.
  */
  const documentRef = createDocumentReference(path);
  const update = {};
  update[field] = arrayRemove(value);
  await updateDoc(documentRef, update);
};

const createDocumentReference = (path) => {
  /**
  * Create a Firestore document reference from a path.
  * @param {String} path The path to the document. 
  * @return {DocumentReference}
  */
  const parts = path.replace(/^\//g, '').split('/');
  return doc(db, ...parts);
};

const createCollectionReference = (path) => {
  /**
  * Create a Firestore collection reference from a path.
  * @param {String} path The path to the collection. 
  * @return {CollectionReference}
  */
  const parts = path.replace(/^\//g, '').split('/');
  return collection(db, ...parts);
};

const createCollectionQuery = (path, params) => {
  /**
  * Create a Firestore collection query from a path and parameters.
  * @param {String} path The path to the collection.
  * @param {Map} params Parameters for querying: `desc`, `filters`, `max`, `order`.
  * @return {Query}
  */
  const collectionRef = createCollectionReference(path);
  const args = [collectionRef];
  const { desc, filters=[], max, order } = params;
  filters.forEach((filter) => {
    args.push(where(filter.key, filter.operation, filter.value));
  });
  if (order && desc) args.push(orderBy(order, 'desc'));
  else if (order) args.push(orderBy(order));
  if (max) args.push(limit(max));
  return query(...args);
};

async function getCollection(path, params) {
  /**
  * Get documents from a collection in Firestore.
  * @param {String} path The path to the document.
  * @param {Map} params Parameters for querying: `desc`, `filters`, `max`, `order`.
  * @return {Array}
  */
  const q = createCollectionQuery(path, params);
  const snapshot = await getDocs(q);
  return snapshot.docs.map(doc => Object({ id: doc.id, ...doc.data() }));
}

async function getDocument(path) {
  /**
  * Get a document from Firestore.
  * @param {String} path The path to the document.
  * @return {Map}
  */
  const docRef = createDocumentReference(path);
  const docSnap = await getDoc(docRef);
  if (docSnap.exists()) {
    return { id: docRef.id, ...docSnap.data() };
  } else {
    return {}
  }
}

async function setDocument(path, data) {
  /**
  * Create or update a document in Firestore.
  * @param {String} path The path to the document.
  * @param {Map} path The path to the document.
  */
  const now = new Date().toISOString();
  const docRef = createDocumentReference(path);
  const entry = {...data, created_at: now, updated_at: now };
  await setDoc(docRef, entry, { merge: true });
  return { id: docRef.id, ...entry };
}

async function deleteDocument(path) {
  /**
  * Delete a document from Firestore.
  * @param {String} path The path to the document.
  */
  const docRef = createDocumentReference(path);
  await deleteDoc(docRef);
}

async function deleteDocumentField(path, key) {
  /**
  * Delete a field from a document in Firestore.
  * @param {String} path The path to the document.
  * @param {String} key The key of the field to delete.
  */
  const entry = {}
  entry[key] = deleteField();
  await setDocument(path, entry);
}

async function listenToDocument(path, callback, errorCallback = null) {
  /**
  * Listen to changes of a document in Firestore.
  * @param {String} path The path to the document.
  * @param {Function} callback A callback to execute when the document changes.
  * @param {Function} errorCallback A callback to execute if there is an error.
  * @returns {Function}
  */
  const docRef = createDocumentReference(path);
  return onSnapshot(docRef, (doc) => {
    callback({ id: doc.id, ...doc.data() });
  },
  (error) => {
    if (errorCallback) errorCallback(error);
  });
}

async function listenToCollection(
  path,
  params,
  queryCallback = null,
  addedCallback = null,
  modifiedCallback = null,
  removedCallback = null,
  errorCallback = null,
) {
  /**
  * Listen to changes of a document in Firestore.
  * @param {String} path The path to the collection.
  * @param {Map} params Parameters for querying: `desc`, `filters`, `max`, `order`.
  * @param {Function} queryCallback A callback to execute when documents in the collection change,
  *  overrides other callbacks. Leave as null or false to specify more specific callbacks.
  * @param {Function} addedCallback A callback to execute when documents in the collection are added.
  * @param {Function} modifiedCallback A callback to execute when documents in the collection are modified.
  * @param {Function} removedCallback A callback to execute when documents in the collection are removed.
  * @returns {Function}
  */
  const q = createCollectionQuery(path, params);
  if (queryCallback) return onSnapshot(q, queryCallback);
  return onSnapshot(q, (snapshot) => {
    snapshot.docChanges().forEach((change) => {
      if (change.type === 'added' && addedCallback) {
        addedCallback({ id: change.doc.id, ...change.doc.data() });
      }
      if (change.type === 'modified') {
        modifiedCallback({ id: change.doc.id, ...change.doc.data() })
      }
      if (change.type === 'removed') {
        removedCallback({ id: change.doc.id, ...change.doc.data() })
      }
    });
  },
  (error) => {
    if (errorCallback) errorCallback(error);
  });
}

/*------------------------------------------------------------------------------
 * Authentication Interface
 *----------------------------------------------------------------------------*/

async function changeEmail(email) {
  /**
  * Change the user's email and update their user data in Firestore.
  * @param {String} email The user's new email.
  */
  await updateEmail(auth.currentUser, email)
  await setDocument(`users/${auth.currentUser.uid}`, { email })
};

async function changePassword(newPassword) {
  /**
  * Change a user's password.
  * @param {String} newPassword The user's new password.
  */
  updatePassword(auth.currentUser, newPassword)
}

async function confirmPasswordChange(code, newPassword) {
  /**
  * Change the user's password using a valid action code and
  * a new password.
  * @param {String} code A password reset action code.
  * @param {String} newPassword The user's new password.
  * @returns {String}
  */
  return await confirmPasswordReset(auth, code, newPassword);
}

async function checkGoogleLogIn() {
  /**
  * Check if a user signed in through Google.
  * @returns {User}
  */
  const result = await getRedirectResult(auth);
  const credential = GoogleAuthProvider.credentialFromResult(result);
  return result.user;
}

async function createAccount(email, password) {
  /**
  * Sign a user up for a Firebase account with a username and password.
  * @param {String} email The user's email to be used as a username.
  * @param {String} password The user's password. Should be longer than 6 characters.
  * @returns {User}
  */
  const credentials = await createUserWithEmailAndPassword(auth, email, password);
  return credentials.user;
}

async function deleteCurrentUser() {
  /**
  * WARNING: Delete the current user's account.
  */   
  await deleteUser(auth.currentUser)
}

function getCurrentUser() {
  /**
  * Return the currently signed in user.
  * @returns {User}
  */
  return auth.currentUser;
}

async function getUserToken(refresh = false) {
  /**
  * Get an auth token for a given user.
  * @param {Boolean} refresh Whether or not the credentials of the ID token should be refreshed.
  */
  if (!auth.currentUser) {
    return await onAuthStateChanged(auth, async (user) => {
      if (user) return await user.getIdToken(refresh);
    });
  } else {
    return await auth.currentUser.getIdToken(refresh);
  }
}

async function googleLogIn(persistence = false) {
  /**
  * Sign a user in through Google.
  * @param {Boolean} persistence Whether or not to persist the user session,
  *    `false` by default.
  */
  if (!persistence) await setPersistence(auth, inMemoryPersistence);
  const provider = new GoogleAuthProvider();
  signInWithRedirect(auth, provider);
}

async function logIn(email, password, persistence = false) {
  /**
  * Sign a user in with username and password.
  * @param {String} email The user's login email.
  * @param {String} password The user's password.
  * @param {Boolean} persistence Whether or not to persist the user session,
  *    `false` by default.
  * @returns {User}
  */
  if (!persistence) await setPersistence(auth, browserSessionPersistence)
  const credentials = await signInWithEmailAndPassword(auth, email, password);
  return credentials.user;
}

async function logOut() {
  /**
  * Sign the current user out of their account.
  */
  await signOut(auth);
}

function onAuthChange(callback) {
  /**
  * Perform an action when a user sign in or sign out is detected.
  * @param {function} callback An action to perform when a user is detected.
  *    Passed a `User` object..
  */
  return onAuthStateChanged(auth, callback);
}

async function sendPasswordReset() {
  /**
  * Send the current user a password reset email.
  */
  await sendPasswordResetEmail(auth, auth.currentUser.email);
};

async function updateUserPhoto(file) {
  /**
  * Update a user's photo URL, listening for state changes, errors,
  * and the completion of the upload.
  * @param {File} file The image file to upload as the user's photo.
  * @returns {String} The download URL for the photo.
  */
  const fileName = `users/${auth.currentUser.uid}/user_photos/${file.name}`;
  await uploadFile(fileName, file);
  const downloadURL = await getFileURL(fileName);
  updateProfile(auth.currentUser, { photoURL: downloadURL });
  return downloadURL;
}

async function updateUserDisplayName(displayName) {
  /**
  * Update a user's display name.
  * @param {String} displayName The user's new display name.
  */
  await updateProfile(auth.currentUser, { displayName });
}

async function verifyUserToken(token) {
  /**
  * Verify an authentication token for a given user.
  * @param {String} token A Firebase user token.
  */
  await signInWithCustomToken(auth, token)
    .then((userCredential) => resolve(userCredential.user))
    .catch((error) => reject(error));
};

async function sendVerification() {
  /**
  * Send the current user a verification email.
  */
  await sendEmailVerification(auth.currentUser);
};

async function reAuthenticate(password) {
  /**
  * Re-authenticate the current user.
  * @param {String} password The user provided password.
  */
  const email = auth.currentUser.email;
  const credential = firebase.auth.EmailAuthProvider.credential(email, password);
  await reauthenticateWithCredential(user, credential);
};

async function verifyPasswordReset(code) {
  /**
  * Verify the action code to handle password reset and return the user's email.
  * @param {String} code A password reset action code.
  * @returns {String}
  */
  return await verifyPasswordResetCode(auth, code);
}

/*------------------------------------------------------------------------------
 * Storage Interface
 *----------------------------------------------------------------------------*/

async function deleteFile(path) {
  /**
  * Delete a given file from Firebase Storage.
  * @param {String} path The full path to the file.
  */
  const fileRef = ref(storage, path);
  await deleteObject(fileRef);
}

async function getFileURL(path) {
  /**
  * Get a download URL for a given file path in Firebase Storage.
  * @param {String} path The full path to the file.
  * @returns {String}
  */
  return await getDownloadURL(ref(storage, path));
}

async function downloadFile(ref, fileName) {
  /**
  * Download a file from Firebase Storage.
  * @param {String} ref The full path to the file.
  * @param {String} fileName The name of the download file.
  */
  if (!ref.startsWith('http')) ref = await getFileURL(ref);
  const response = await fetch(ref);
  const blob = await response.blob();
  const url = window.URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = url;
  link.style = 'display: none';
  link.setAttribute('download', fileName);
  document.body.appendChild(link);
  link.click();
  link.parentNode.removeChild(link);
  window.URL.revokeObjectURL(blob);
}

async function uploadFile(path, file, type = 'File') {
  /**
  * Upload an image to Firebase Storage given a file object or
  * another specified type: 'data_url', base64url', 'base64', or
  * null for a raw string.
  * @param {String} path The full path to the file.
  * @param {File} file The name of the download file.
  * @param {String} type The type of file to upload, 'File' by default.
  *    You can upload by string by specifying the type as:
  *    'data_url', base64url', 'base64', or null.
  */
  const storageRef = ref(storage, path);
  if (type === 'File') await uploadBytes(storageRef, file);
  else uploadString(storageRef, file, type)
};

const authErrors = {
  'auth/email-already-in-use': 'The provided email is already in use by an existing user. Each user must have a unique email.',
  'auth/email-already-exists': 'The provided email is already in use by an existing user. Each user must have a unique email.',
  'auth/internal-error': 'Unexpected error while trying to process the request. If the error persists, please report the problem to support@cannlytics.com',
  'auth/invalid-email':	'The provided email is invalid. It must be a valid email address.',
  'auth/invalid-password': 'The provided password is invalid.',
  'auth/weak-password': 'Your password must be 6 characters long or more.',
  'auth/wrong-password': 'The password provided is incorrect.',
  'network-request-failed': 'A network error (such as timeout, interrupted connection or unreachable host) has occurred.',
  'too-many-requests': 'We have blocked all requests from this device due to unusual activity. Try again later.',
  'user-not-found': 'There is no user record corresponding to this identifier. The user may have been deleted.',
  'user-disabled': 'The user account has been disabled by an administrator.',
  'weak-password': 'The password must be 6 characters long or more.',
  'web-storage-unsupported': 'This browser is not supported or 3rd party cookies and data may be disabled.',
}

const storageErrors = {
  'storage/unknown':	'An unknown error occurred.',
  'storage/object-not-found':	'No file exists at the desired reference.',
  'storage/bucket-not-found':	'Improper storage configuration.',
  'storage/project-not-found':	'Project is not configured for Cloud Storage.',
  'storage/quota-exceeded':	"Your storage quota has been exceeded. If you're on the free tier, upgrade to a paid plan. If you're on a paid plan, reach out to Cannlytics support.",
  'storage/unauthenticated':	'Unauthenticated, please authenticate and try again.',
  'storage/unauthorized':	"You are not authorized to perform the desired action, check your privileges to ensure that they are correct.",
  'storage/retry-limit-exceeded':	"The operation took too long to complete. Please try uploading again.",
  'storage/invalid-checksum':	"There is an error with the file. Please try uploading again.",
  'storage/canceled':	'Operation canceled.',
  'storage/invalid-url': "Invalid URL name.",
  'storage/cannot-slice-blob': "Your local file may have changed. Please try uploading again after verifying that the file hasn't changed.",
  'storage/server-file-wrong-size':	"Your file is too large. Please try uploading a different file.",
};

export {
  auth,
  authErrors,
  // analytics,
  addToArray,
  removeFromArray,
  changeEmail,
  changePassword,
  confirmPasswordChange,
  checkGoogleLogIn,
  createAccount,
  deleteCurrentUser,
  deleteDocument,
  deleteDocumentField,
  deleteFile,
  downloadFile,
  getCurrentUser,
  getCollection,
  getDocument,
  getFileURL,
  getUserToken,
  googleLogIn,
  listenToDocument,
  listenToCollection,
  // logEvent,
  logIn,
  logOut,
  onAuthChange,
  reAuthenticate,
  sendPasswordReset,
  sendVerification,
  setDocument,
  storageErrors,
  updateUserDisplayName,
  updateUserPhoto,
  uploadFile,
  verifyPasswordReset,
  verifyUserToken,
};
 