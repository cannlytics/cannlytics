# Change Log

## 2023-06-02 v0.0.15



## 2023-02-17 v0.0.13

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
