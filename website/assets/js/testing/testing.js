/**
 * Community Page JavaScript | Cannlytics Website
 * Copyright (c) 2021-2022 Cannlytics
 * 
 * Authors: Keegan Skeate <keegan@cannlytics.com>
 * Created: 1/17/2021
 * Updated: 1/9/2022
 * License: MIT License <https://github.com/cannlytics/cannlytics-website/blob/main/LICENSE>
 */
import { labMap } from './labMap.js';
import { labs } from './labs.js';
import { labAnalyses } from './analyses.js';
import { labRegulations } from './regulations.js';

export const testing = {
  ...labs,
  ...labAnalyses,
  ...labMap,
  ...labRegulations,
};
