/**
 * Cannlytics Console JavaScript Module
 * Copyright (c) 2021-2022 Cannlytics
 * 
 * Authors: Keegan Skeate <https://github.com/keeganskeate>
 * Created: 12/3/2020
 * Updated: 2/6/2022
 * License: MIT License <https://github.com/cannlytics/cannlytics-console/blob/main/LICENSE>
 */
import { analyses } from './analyses/analyses.js';
import { api } from './api/api.js';
import { app } from './app/app.js';
import { areas } from './areas/areas.js';
import { auth } from './auth/auth.js';
import { certificates } from './certificates/certificates.js';
import { dashboard } from './dashboard/dashboard.js';
import * as firebase from './firebase.js';
import { intake } from './intake/intake.js';
import { inventory } from './inventory/inventory.js';
import { payments } from './settings/payments.js';
import { projects } from './projects/projects.js';
import { results } from './results/results.js';
import { samples } from './samples/samples.js';
import { settings } from './settings/settings.js';
import { theme } from './settings/theme.js';
import { traceability } from './traceability/traceability.js';
import { transfers } from './transfers/transfers.js';
import { ui } from './ui/ui.js';
import { utils } from './utils.js';
import { waste } from './waste/waste.js';

// Stylesheets
import '../css/cannlytics.scss';
import '../css/console.scss';
import '../css/login.scss';

export {
  analyses,
  api,
  app,
  auth,
  areas,
  certificates,
  dashboard,
  firebase,
  intake,
  inventory,
  payments,
  projects,
  results,
  samples,
  traceability,
  transfers,
  settings,
  theme,
  ui,
  utils,
  waste,
}
