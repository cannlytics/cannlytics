/**
 * Settings JavaScript | Cannlytics Website
 * Copyright (c) 2021-2022 Cannlytics
 * 
 * Authors: Keegan Skeate <https://github.com/keeganskeate>
 * Created: 11/28/2021
 * Updated: 11/28/2021
 * License: MIT License <https://github.com/cannlytics/cannlytics-website/blob/main/LICENSE>
 */
import { accountSettings } from './account.js';
import { apiSettings } from './api-keys.js';

export const settings = {
  ...accountSettings,
  ...apiSettings,
};
