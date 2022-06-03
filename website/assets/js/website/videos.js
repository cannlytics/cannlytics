/**
 * Videos JavaScript | Cannlytics Website
 * Copyright (c) 2021-2022 Cannlytics
 * 
 * Authors: Keegan Skeate <https://github.com/keeganskeate>
 * Created: 7/30/2021
 * Updated: 11/23/2021
 * License: MIT License <https://github.com/cannlytics/cannlytics-website/blob/main/LICENSE>
 */
 import { getDocument, onAuthChange } from '../firebase.js';


 export const videos = {

    authenticatePremiumVideo() {
      /**
       * Authenticate the user to view a premium video.
       */
       onAuthChange(user => {
        if (user) {
          // TODO: Implement premium videos.
          console.log('Current user:', user);
        } else {
          console.log('No user');
        }
      });
    },

    async getVideo(videoId) {
      /**
       * Get video data from Firestore.
       * @param {String} videoId The ID of the video to retrieve.
       * @returns {Object} The document object if found, otherwise an empty object.
       */
      const videoData = await getDocument(`public/videos/video_data/${videoId}`);
      return videoData;
    },

    async updateVideoViews(videoId) {
      /**
       * Increment video views for a given video in Firestore.
       * @param {string} videoId The ID of the video to increment views.
      */
      await updateDocument(`public/videos/video_data/${videoId}`);
    },

 };
