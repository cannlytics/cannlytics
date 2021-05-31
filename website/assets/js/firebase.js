/**
 * firebase.js | Cannlytics Website
 * Created: 12/22/2020
 */
import * as firebase from 'firebase/app';
import 'firebase/analytics';
import 'firebase/auth';
import 'firebase/firestore';
import 'firebase/performance';
import 'firebase/storage';


// Initialize Firebase.
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


// Define frequently used Firebase modules.
const analytics = firebase.analytics();
const auth = firebase.auth();
const db = firebase.firestore();
const performance = firebase.performance();
const storage = firebase.storage();


// Define useful Firebase objects.
const { firestore } = firebase;
const GoogleAuthProvider = firebase.auth.GoogleAuthProvider;


const getCollection = (path, limit=null, orderBy=null, desc=false, filters=[]) => new Promise((resolve) => {
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


export {
  analytics,
  auth,
  db,
  firestore,
  performance,
  storage,
  getCollection,
  getDocument,
  updateDocument,
  GoogleAuthProvider,
};
