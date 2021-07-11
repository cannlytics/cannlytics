/**
 * Cannlytics Console JavaScript Module
 * Author: Keegan Skeate
 * Created: 12/3/2020
 * Updated: 6/18/2021
 */

import { analyses } from './analyses/analyses.js'
import { api } from './api/api.js';
import { app } from './app/app.js';
import { auth } from './auth/auth.js';
import { dashboard } from './dashboard/dashboard.js';
import * as firebase from './firebase.js';
import { intake } from './intake/intake.js';
import { inventory } from './inventory/inventory.js';
// import { organizations } from './organizations/organizations.js';
import { projects } from './projects/projects.js';
import { results } from './results/results.js';
import { samples } from './samples/samples.js';
import { settings } from './settings/settings.js';
import { theme } from './settings/theme.js';
import { traceability } from './traceability/traceability.js';
import { transfers } from './transfers/transfers.js';
import { ui } from './ui/ui.js';

export {
  analyses,
  api,
  app,
  auth,
  dashboard,
  firebase,
  intake,
  inventory,
  // organizations,
  projects,
  results,
  samples,
  traceability,
  transfers,
  settings,
  theme,
  ui,
}
