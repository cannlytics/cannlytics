/**
 * Account JavaScript | Cannlytics Console
 * Author: Keegan Skeate
 * Created: 1/2/2021
 * Updated: 6/3/2021
 */


export const accountSettings = {


  saveAccount(data) {
    /* 
    * Saves a user's account fields.
    */
    console.log('Todo: Save user fields to firestore!');
  },


  exportAccount(data) {
    /* 
    * Exports a user's data.
    */
    console.log('Export all of a users data to Excel.');
  },


  createPin(data) {
    /* 
    * Create a pin for a user.
    */
   console.log('Todo: Create a pin!');
  },


  uploadSignature(data) {
    /* 
    * Upload a signature for a user.
    */
    const collection = db.collection('organizations');
    return collection.add(data);
  },


  deleteSignature(data) {
    /* 
    * Remove a signature from a user.
    */
    const collection = db.collection('organizations');
    return collection.add(data);
  },


};
