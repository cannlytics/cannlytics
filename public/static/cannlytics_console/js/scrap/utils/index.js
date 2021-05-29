/**
 * --------------------------------------------------------------------------
 * Cannlytics (v1.0.0): utils/index.js
 * Licensed under GPLv3 (https://github.com/cannlytics/cannlytics_console/blob/main/LICENSE)
 * --------------------------------------------------------------------------
 */

const TRANSITION_END = 'transitionend';

 /**
 * ------------------------------------------------------------------------
 * Helpers
 * ------------------------------------------------------------------------
 */

const getUID = prefix => {
  do {
    prefix += Math.floor(Math.random() * MAX_UID)
  } while (document.getElementById(prefix))
  return prefix
}

export {
  TRANSITION_END,
  getUID,
}