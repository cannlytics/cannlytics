/**
 * store.js | Cannlytics Console (v1.0.0)
 * Licensed under GPLv3 (https://github.com/cannlytics/cannlytics_console/blob/main/LICENSE)
 * Author: Keegan Skeate
 * Created: 12/26/2020
 * Resources:
 *   https://www.npmjs.com/package/idb
 *   https://developer.mozilla.org/en-US/docs/Web/API/IndexedDB_API/Using_IndexedDB
 */

import { openDB } from 'idb';

// Initialize IndexedDB for local storage.
const idbPromise = openDB('cannlytics-store', 1, {
  upgrade(db) {
    db.createObjectStore('store');
  },
});

export const idbStore = {
  async get(key) {
    return (await idbPromise).get('store', key);
  },
  async set(key, val) {
    return (await idbPromise).put('store', val, key);
  },
  async delete(key) {
    return (await idbPromise).delete('store', key);
  },
  async clear() {
    return (await idbPromise).clear('store');
  },
  async keys() {
    return (await idbPromise).getAllKeys('store');
  },
};
