/**
 * Settings JavaScript | Cannlytics Console
 * Author: Keegan Skeate
 * Created: 12/3/2020
 * Updated: 7/13/2021
 */

import { apiSettings } from './api.js';
import { errorSettings } from './errors.js';
import { helpSettings } from './help.js';
import { organizationSettings } from './organizations.js';
import { userSettings } from './user.js';


export const settings = {
  ...apiSettings,
  ...errorSettings,
  ...helpSettings,
  ...organizationSettings,
  ...userSettings,
};
