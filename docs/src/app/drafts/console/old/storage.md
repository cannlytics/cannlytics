# Storage

Cannlytics utilizes Firebase Storage for storing user and app files.

## Storage Rules

User's can upload their own profile pictures (< 5MB) to Firebase Storage. All users can view other users' profile pictures.

```js
// Only a user can upload their profile pictures, but anyone can view them.
// Only allows image uploads that are less than 5MB.
match /users/{uid}/user_photos/{photos=**} {
  allow read;
  allow write: if request.resource.size < 5 * 1024 * 1024
                && request.resource.contentType.matches('image/.*')
                && request.auth.uid == uid;
}
```


## Resources

- [Upload a file with JavaScript](https://developer.mozilla.org/en-US/docs/Web/API/File/Using_files_from_web_applications)
- [Upload file to Firebase Storage](https://firebase.google.com/docs/storage/web/upload-files)
- [Change user's photo URL](https://firebase.google.com/docs/auth/web/manage-users#update_a_users_profile)
- [Listen to data changes](https://firebase.google.com/docs/firestore/query-data/listen#web)
- [Firebase Storage Errors](https://firebase.google.com/docs/storage/web/handle-errors)
