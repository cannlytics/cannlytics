/**
 * firebase.js | Cannlytics Website
 * Created: 12/22/2020
 * Updated: 5/9/2021
 */

// Initialize Firebase
firebase.initializeApp({
  apiKey: process.env.FIREBASE_API_KEY,
  authDomain: process.env.FIREBASE_AUTH_DOMAIN,
  databaseURL: process.env.FIREBASE_DATABASE_URL,
  projectId: process.env.FIREBASE_PROJECT_ID,
  storageBucket: process.env.FIREBASE_STORAGE_BUCKET,
  messagingSenderId: process.env.FIREBASE_MESSAGING_SENDER_ID,
  appId: process.env.FIREBASE_APP_ID,
  measurementId: process.env.FIREBASE_MEASUREMENT_ID,
});

// FIXME: As session cookies are to be used, do not persist any state client side.
// firebase.auth().setPersistence(firebase.auth.Auth.Persistence.NONE);

// Core modules
const auth = firebase.auth();
const db = firebase.firestore();
const storage = firebase.storage();
const { firestore } = firebase;
const GoogleAuthProvider = firebase.auth.GoogleAuthProvider;


/*
 * Auth interface
 */


const changePhotoURL = (file) => new Promise((resolve, reject) => {
  /* 
  * Upload an image to Firebase Storage to use for a user's photo URL,
  * listening for state changes, errors, and the completion of the upload.
  */
  const uid = auth.currentUser.uid;
  const storageRef = storage.ref();
  const metadata = { contentType: 'image/jpeg' };
  const fileName = `users/${uid}/user_photos/${file.name}`;
  const uploadTask = storageRef.child(fileName).put(file, metadata);
  uploadTask.on(firebase.storage.TaskEvent.STATE_CHANGED,
    (snapshot) => {
      const progress = (snapshot.bytesTransferred / snapshot.totalBytes) * 100;
      switch (snapshot.state) {
        case firebase.storage.TaskState.PAUSED:
          break;
        case firebase.storage.TaskState.RUNNING:
          break;
      }
    }, 
    (error) => {
      reject(error);
    },
    () => {
      uploadTask.snapshot.ref.getDownloadURL().then((downloadURL) => {
        auth.currentUser.updateProfile({ photoURL: downloadURL });
        resolve(downloadURL);
      });
    }
  );
});


const getUserToken = (refresh=false) => new Promise((resolve, reject) => {
  /*
   * Get an auth token for a given user.
   */
  if (!auth.currentUser) {
    auth.onAuthStateChanged((user) => {
      if (user) {
        user.getIdToken(refresh).then((idToken) => {
          resolve(idToken)
        }).catch((error) => {
          reject(error);
        });
      }
    });
  } else {
    auth.currentUser.getIdToken(refresh).then((idToken) => {
      resolve(idToken)
    }).catch((error) => {
      reject(error);
    });
  }
});


function signOut() {
  /*
   * Sign a user out of Firebase and clear the session.
   */
  try {
    firebase.auth().currentUser.getIdToken().then((idToken) => {
      const headers = new Headers({
        'Content-Type': 'text/plain',
        'Authorization': `Bearer ${idToken}`,
      });
      fetch('/api/auth/sign-out', { headers }).then(() => {
        firebase.auth().signOut().then(() => {
          document.location.href = '/account/sign-out';
        }).catch((error) => {
          document.location.href = '/account/sign-out';
        }); 
      });
    })
  } catch(error) {
    document.location.href = '/account/sign-out';
  }
}


/*
 * Firestore interface
 */


const getCollection = (
  path,
  limit=null,
  orderBy=null,
  desc=false,
  filters=[],
) => new Promise((resolve) => {
  /*
   * Get documents from a collection in Firestore.
   */
  let ref = getReference(path);
  filters.forEach((filter) => {
    ref = ref.where(filter.key, filter.operation, filter.value);
  });
  if (orderBy && desc) ref = ref.orderBy(orderBy, 'desc');
  else if (orderBy) ref = ref.orderBy(orderBy);
  if (limit) ref = ref.limit(limit);
  ref.get().then((snapshot) => {
    const docs = [];
    snapshot.forEach((doc) => {
      docs.push(doc.data());
    });
    resolve(docs);
  }).catch((error) => {
    console.log('Error getting documents: ', error);
  });
});


const getDocument = (path) => new Promise((resolve) => {
  /*
   * Get a document from Firestore.
   */
  const ref = getReference(path);
  ref.get().then((doc) => {
    resolve(doc.data());
  });
});


const getReference = (path) => {
  /*
   * Create a collection or a document Firestore reference.
   */
  let ref = db;
  const parts = path.split('/');
  parts.forEach((part, index) => {
    if (index % 2) ref = ref.doc(part);
    else ref = ref.collection(part);
  });
  return ref;
};


const updateDocument = (path, data) => new Promise((resolve) => {
  /*
   * Update or create a document in Firestore.
   */
  const ref = getReference(path);
  ref.set(data, { merge: true }).then((doc) => {
    resolve(doc.data());
  });
});


/*
 * Storage interface
 */


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
  db,
  firestore,
  storageErrors,
  GoogleAuthProvider,
  changePhotoURL,
  getUserToken,
  signOut,
  getDocument,
  updateDocument,
  getCollection,
};
