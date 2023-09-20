# Change Log

## 2023-09-19 v0.0.16

- Continued work on the organization screens in the app.
- Made significant progress on data collection and app.
- WA CCRS sales and strains data curation.
- Designed a data dashboard console and refactored app imports.
- Development of data dashboard and Cannlytics data archive.
- Added AI models, datasets, and sales curation features.
- Worked on API with an OpenAPI specification.
- Made updates to the data archive and developed cannabis license curation algorithms.
- Fixed GIS data and implemented data algorithms for multiple states.
- Resumed development of data app, specifically on subscription management and dashboard features.
- Implemented download state license data functionality.
- Outlined and began generating code for AI data tools.
- Refactored the data app dashboard and worked on CoADoc user interface.
- Implemented receipt parser UI, API, and stabilized website requirements.
- Continued work on licensing features, lab results data availability, and data app map features.
- Began work on FL COA parsing algorithms and made lab results accessible through the data app.
- Implemented lab result search and made various data app improvements.
- Began the algorithm to archive CA producer lab results.
- Refactored the website and the data app.
- Worked on Kaycha Labs COA parsing and refactored documentation.
- Worked on COA PDF parsing and carried out tests.
- Refactored `CannPatent` - Cannabis Strain Identifier.
- Refactored various components of the app, including data app, archive, tests, API, and AI.
- Implemented QR code scan and began parsing COA with AI.
- Integrated COA AI with data app through the API and published it.
- Implemented & tested `BudSpender` AI receipt parser and UI.
- Worked on COA and receipt parsers.
- Focused on uploading receipts and COAs and improving CRUD operations.
- Began implementing payments, tokens, and subscription plans in the app.

## 2023-07-04 v0.0.15

- Added starter Flutter architecture for the app.
- Refactored app while preserving core functionality.
- Refactor of app onboarding and sign-in logic/names.
- Architecture for screens & started implementing routing.
- Refactoring of various app screens and added API service.
- Refactored app menu and began implementing app models.
- Added footer and PNG images for the app.
- Various styling and theming updates, including dashboard, footer, and menu style.
- Implementation and refactoring of Metrc service functions for the app.
- Added license functionality and implemented UI controllers for various app screens.
- Continuous work on the app's Metrc screens, account screens, organization screens, and licenses.
- Refactored app routes and started implementing model CRUDs.
- Implemented Metrc actions in the app and various refactors.
- Added app authentication features for smooth sign-in.
- Implemented app location sorting and started adding search functionality.
- Improved app locations table functionality and other enhancements.
- Implemented checkboxes for location form and added location type selection features.
- Improved app's data curation and organization screen features.
- Refactor of app facilities and improvements to `CoADoc` algorithms.
- Refactored Metrc API authentication.
- Implemented Metrc sync and refactored app theme.
- Made updates to app theme and colors.
- Implemented the 'join organization' feature in the app.
- Released app to production.

## 2023-02-17 v0.0.13

Updated requirements and made minor refactors to allow `cannlytics` to run nicely on various systems.

## 2022-03-13 v0.0.11

Unified the entire codebase, cleaning and organizing code that was marked for refactoring. Added placeholders for planned future development.

Products:

- AI
- API
- `cannlytics` (Python SDK)
- Console
- Docs
- Website

Planned:

- QuickBooks (`quickbooks.py`) module for the `cannlytics` Python SDK.

## 2021-12-21 v0.0.9

- Major refactor of the entire `cannlytics` module.
- Minor refactor of the `firestore` module, removing redundant wrapper functions. Firestore functions can now optionally be passed a Firestore Client, `database`, to create an opportunity for further performance optimization.
- LIMS features and functionality are beginning to be tested and standardized.
- A `Cannlytics` class has been added to serve as an interface to all `firebase`, `metrc`, and `lims` functionality.
- Authentication functionality in `cannlytics.auth.auth.py` has been standardized to support the Cannlytics Console and API.

## 2021-08-21 v0.0.8

- Major refactor of the Metrc module, improving performance and ease-of-use.
- Beginning to add laboratory information management system (LIMS) features and functionality.

## 4/20/2021 v0.0.6

- Refactored code and ensured that all code is licensed under GPLv3.

## 4/16/2021 v0.0.5

- Added complete Metrc and Leaf Data Systems API modules.

## 3/18/2021 v0.0.4

- Started Leaf Data Systems traceability module.

## 2/14/2021 v0.0.1 - v0.0.3

- Added Firebase functionality.
