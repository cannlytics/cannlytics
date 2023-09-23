# <img height="32" alt="" src="https://cannlytics.com/static/cannlytics_website/images/logos/cannlytics_calyx_detailed.svg"> Cannlytics API

The Cannlytics API allows users to interface with cannabis data and statistics. Each API endpoints handle authentication, error handling, and identifying the precise logic to perform.

- [AI Recipes API](./ai/recipes.md)
- [COAs API](./data/coas.md)
- [Receipts API](./data/receipts.md)
- [Strains API](./data/strains.md)
- [Effects and Aromas API](./stats/skunkfx.md)
- [Metrc API](./metrc/readme.md)

## Getting Started with the Cannlytics API <a name="getting-started"></a>

Getting started making requests to the Cannlytics API can be done in 3 quick steps.

1. First, [create a Cannlytics account](https://cannlytics.com/account/sign-up).
2. Second, [create a Cannlytics API key](https://cannlytics.com/account/api-keys).
3. Third, begin making requests to the Cannlytics API with your API Key in an `Authorization: Bearer <cannlytics_api_key>` header.

You can make requests through the API passing your API key as a bearer token in the authorization header. Below is an example reading an API key from a local `.env` file.

=== "Python"

    ```py
    from dotenv import load_dotenv
    import os
    import requests

    # Load your API key.
    load_dotenv('.env')
    API_KEY = os.getenv('CANNLYTICS_API_KEY')

    # Pass your API key through the authorization header as a bearer token.
    HEADERS = {
        'Authorization': 'Bearer %s' % API_KEY,
        'Content-type': 'application/json',
    }

    # Parse a COA through the API.
    url = 'https://cannlytics.page.link/test-coa'
    data = {'urls': [url]}
    response = requests.post(url, headers=headers, json=data)
    extracted = response.json()
    print(extracted["data"])
    ```


=== "Node.js"

    ```js
    const axios = require('axios');
    require('dotenv').config();

    // Pass API key through the authorization header as a bearer token.
    const apiKey = process.env.CANNLYTICS_API_KEY;
    const options = {
      headers: {
        'Content-Type': 'application/json',
        'Authorization' : `Bearer ${apiKey}`
      }
    };

    // Parse a COA through the API.
    const url = 'https://cannlytics.page.link/test-coa';
    const data = { urls: [url] };

    axios.post(url, data, options)
      .then((response) => {
        const extracted = response.data;
        console.log(extracted["data"]);
      })
      .catch((error) => {
        console.error("Error:", error);
      });
    ```

<!-- 
FUTURE WORK:

## Data API Endpoints <a name="data-api-endpoints"></a>

You can get all of the open data curated by Cannlytics through the `data` API endpoints described below.

| Endpoint | Methods | Description |
| -------- | ------- | ----------- |
| `\data\analyses` | `GET` |   |
| `\data\analytes` | `GET` |   |
| `\data\coas` | `GET` |   |
| `\data\labs` | `GET` | Get the data of labs that test cannabis. Append a URL-escaped `<lab>` or `<lab_license_number>` to query a specific lab. |
| `\data\regulations` | `GET` | Get regulation data for permitted cannabis markets. Append a `<state>` to query regulation data for a specific state. The regulations include the `limits` used in quality control testing. |
| `\data\states` | `GET` | Get data for states that permit adult-use / recreational or medicinal cannabis. Append a `<state>` path to get data for a specific state. |
| `\data\strains` | `GET` | Get data for documented cannabis strains. Append a `<strain_name>` to query a specific strain. | -->

<!-- TODO: Implement data API endpoints for:
  - [ ] Licensee data.
  - [ ] Patent data.
-->
<!-- 

TODO: MOVE THESE.

## Stats API Endpoints <a name="stats-api-endpoints"></a>

You can interface with various statistical models through the `stats` API endpoints listed in the table below. The `stats` API endpoints are clever mechanisms for you to capitalize on state-of-the-line statistics privately in the cloud. 

| Endpoint | Methods | Description |
| -------- | ------- | ----------- |
| `\stats\effects` | `GET`, `POST` | Get predicted effects or append `actual` to the path to post actual effects for a particular cannabis strain. You can also query by appending the `<strain>` as a URL-escaped path. |
| `\stats\personality` | `GET`, `POST` | Get the Big 5 personality test questions and rubric. Post your completed test to get the Big 5 personality trait metrics on a 0 to 1 scale. | -->

<!-- TODO:
  - [ ] Patent prediction API
  - [ ] Product recommendations API
-->
<!-- 

DEPRECATED:

## LIMS API Endpoints <a name="lims-api-endpoints"></a>

The `lims` API endpoints allows all actions necessary for managing a laboratory that tests cannabis, from sample reception to the publication of results to invoicing and the scheduling of the next test.

| Endpoint | Methods | Description |
| -------- | ------- | ----------- |
| `\lims\analyses` | `GET`, `POST`, `DELETE` | Manage analyses. Append `analysis_id` to query a specific analysis. |
| `\lims\analytes` | `GET`, `POST`, `DELETE` | Manage analyses. Append `analyte_id` to query a specific analyte. |
| `\lims\areas` | `GET`, `POST`, `DELETE` | Manage lab spaces. Append `area_id` to query a specific area. |
| `\lims\certificates` | `GET`, `POST`, `DELETE` | Manage certificates of analysis (COAs). Append `generate`, `review`, `approve`, `post`, or `release` paths for your desired action. |
| `\lims\contacts` | `GET`, `POST`, `DELETE` | Manage contacts. Append `contact_id` to query a specific contact. |
| `\lims\instruments` | `GET`, `POST`, `DELETE` | Manage instruments. |
| `\lims\inventory` | `GET`, `POST`, `DELETE` | Manage inventory items. Append `inventory_id` to query a specific inventory item. |
| `\lims\invoices` | `GET`, `POST`, `DELETE` | Manage invoices. Append `invoice_id` to query a specific invoice. |
| `\lims\measurements` | `GET`, `POST`, `DELETE` | Manage measurements. Append `measurement_id` to query a specific measurement. |
| `\lims\projects` | `GET`, `POST`, `DELETE` | Manage projects. Append `projecT_id` to query a specific project |
| `\lims\results` | `GET`, `POST`, `DELETE` | Manage results. Append `result_id` to query a specific result |
| `\lims\samples` | `GET`, `POST`, `DELETE` | Manage samples. Append `sample_id` to query a specific sample |
| `\lims\templates` | `GET`, `POST`, `DELETE` | Manage templates. Append `template_id` to query a specific template |
| `\lims\transfers` | `GET`, `POST`, `DELETE` | Manage transfers. Append `transfer_id` to query a specific transfer |
| `\lims\transporters` | `GET`, `POST`, `DELETE` | Manage transporters. Append `transporter_id` to query a specific transporter |
| `\lims\vehicles` | `GET`, `POST`, `DELETE` | Manage vehicles. Append `vehicle_id` to query a specific vehicle |
| `\lims\waste` | `GET`, `POST` | Manage waste data. Append `waste_item_id` to query a specific wasted item. | -->

<!-- 

DEPRECATED:

## Traceability API Endpoints <a name="traceability-api-endpoints"></a>

The `traceability` API endpoints are primarily used to add track and trace functionality to the Cannlytics Console, however, you are welcome to use the `traceability` endpoints in the table below to create your own custom workflows.

| Endpoint | Methods | Description |
| -------- | ------- | ----------- |
| `\traceability\employees` | `GET`, `POST`, `DELETE` | Manage tracked employees. |
| `\traceability\items` | `GET`, `POST`, `DELETE` | Manage tracked items. |
| `\traceability\results` | `GET`, `POST`, `DELETE` | Manage tracked lab tests. |
| `\traceability\locations` | `GET`, `POST`, `DELETE` | Manage tracked locations. |
| `\traceability\packages` | `GET`, `POST`, `DELETE` | Manage tracked packages. |
| `\traceability\strains` | `GET`, `POST`, `DELETE` | Manage tracked strains. |
| `\traceability\transfers` | `GET`, `POST`, `DELETE` | Manage tracked transfers. | -->

<!--

DEPRECATED:

## Organizations API Endpoints <a name="organizations-api-endpoints"></a>

You can manage your Cannlytics organizations through the `organizations` API endpoints listed in the table below.

| Endpoint | Methods | Description |
| -------- | ------- | ----------- |
| `\organizations\<organization_id>` | `GET`, `POST` | Get an organization's details. Must be an organization owner or authorized team member to change the organization details. |
| `\organizations\<organization_id>\settings` | `GET`, `POST` | Get an organization's settings. Must be the organization's owner or team member to get the settings and must be the owner or an authorized team member to change the settings. |
| `\organizations\<organization_id>\team` | `GET` | Get an organization's team. |
| `\organizations\<organization_id>\team\<user_ud>` | `GET` | Get an organization team member details. | -->

