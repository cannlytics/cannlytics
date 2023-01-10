# Cannlytics Metrc SDK

SDK reference for the `cannlytics.metrc.client.Metrc` class.

<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th>Function</th>
      <th>Description</th>
      <th>Args</th>
      <th>Returns</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>`__init__`</td>
      <td>Initialize a Metrc API client.</td>
      <td>vendor_api_key (str): Required Metrc API key, obtained from Metrc        upon successful certification. The vendor API key is the        software provider's secret used in every instance, regardless        of location or licensee.    user_api_key (str): Required user secret obtained        from a licensee's Metrc user interface. The user's permissions        determine the level of access to the Metrc API.    logs (bool): Whether or not to log Metrc API requests, True by default.    primary_license (str): A license to use if no license is provided        on individual requests.    state (str): The state of the licensee, Oklahoma (ok) by default.    test (bool): Whether or not to use the test sandbox, True by default.Example:```pytrack = metrc.Client(    vendor_api_key='abc',    user_api_key='xyz',    primary_license='123',    state='ma')```</td>
      <td></td>
    </tr>
    <tr>
      <td>`change_package_items`</td>
      <td>Update package items.</td>
      <td>data (list): A list of package items (dict) to update.    license_number (str): A specific license number.</td>
      <td></td>
    </tr>
    <tr>
      <td>`complete_deliveries`</td>
      <td>Complete home delivery(ies).</td>
      <td>data (list): A list of deliveries (dict) to complete.    license_number (str): A specific license number.</td>
      <td></td>
    </tr>
    <tr>
      <td>`create_deliveries`</td>
      <td>Create home deliver(ies).</td>
      <td>data (list): A list of deliveries (dict) to create.    license_number (str): A specific license number.</td>
      <td></td>
    </tr>
    <tr>
      <td>`create_harvest_packages`</td>
      <td>Create packages from a harvest.</td>
      <td>data (list): A list of packages (dict) to create.    license_number (str): A specific license number.</td>
      <td></td>
    </tr>
    <tr>
      <td>`create_harvest_testing_packages`</td>
      <td>Create packages from a harvest for testing.</td>
      <td>data (list): A list of testing packages (dict) to create.    license_number (str): A specific license number.</td>
      <td></td>
    </tr>
    <tr>
      <td>`create_item`</td>
      <td>Create an item.</td>
      <td>data (dict): An item to create.    license_number (str): A specific license number.    return_obs (bool): Whether or not to get and return the newly created item.</td>
      <td></td>
    </tr>
    <tr>
      <td>`create_items`</td>
      <td>Create items.</td>
      <td>data (list): A list of items (dict) to create.    license_number (str): A specific license number.    return_obs (bool): Whether or not to get and return the newly created items.</td>
      <td></td>
    </tr>
    <tr>
      <td>`create_location`</td>
      <td>Create location.</td>
      <td>name (str): A location name.    location_type (str): An optional location type:        `default`, `planting`, or `packing`.        `default` is assigned by default.    license_number (str): Optional license number filter.</td>
      <td></td>
    </tr>
    <tr>
      <td>`create_locations`</td>
      <td>Create location(s).</td>
      <td>names (list): A list of locations (dict) to create.    types (list): An optional list of location types:        `default`, `planting`, or `packing`.        `default` is assigned by default.    license_number (str): Optional license number filter.</td>
      <td></td>
    </tr>
    <tr>
      <td>`create_log`</td>
      <td>Create a log given an HTTP response.</td>
      <td>response (HTTPResponse): An HTTP request response.</td>
      <td></td>
    </tr>
    <tr>
      <td>`create_package`</td>
      <td>Create a single package.</td>
      <td></td>
      <td></td>
    </tr>
    <tr>
      <td>`create_packages`</td>
      <td>Create packages.</td>
      <td>data (list): A list of packages (dict) to create.    license_number (str): A specific license number.    qa (bool): If the packages are for QA testing.    plantings (bool): If the packages are for planting.</td>
      <td></td>
    </tr>
    <tr>
      <td>`create_patient`</td>
      <td>Create a given patient.</td>
      <td></td>
      <td></td>
    </tr>
    <tr>
      <td>`create_patients`</td>
      <td>Create patient(s).</td>
      <td>data (list): A list of patient (dict) to add.</td>
      <td></td>
    </tr>
    <tr>
      <td>`create_plant`</td>
      <td>Create a plant.</td>
      <td>data (dict): A plant to create.    license_number (str): A specific license number.    return_obs (bool): Whether or not to get and return the created        plant.</td>
      <td>(Plant): Returns a plant batch class.</td>
    </tr>
    <tr>
      <td>`create_plant_batch`</td>
      <td>Create a plant batch.</td>
      <td>data (dict): A plant batch to create.    license_number (str): A specific license number.    return_obs (bool): Whether or not to get and return the created        plant batch.</td>
      <td>(PlantBatch): Returns a plant batch class.</td>
    </tr>
    <tr>
      <td>`create_plant_batches`</td>
      <td>Create plant batches.</td>
      <td>data (list): A list of plant batches (dict) to create.    license_number (str): A specific license number.    return_obs (bool): Whether or not to get and return the created        plant batches.</td>
      <td>(list): Returns a list of plant batch (PlantBatch) classes.</td>
    </tr>
    <tr>
      <td>`create_plant_package_from_batch`</td>
      <td>Create a plant package from a batch.</td>
      <td>data (dict): The plant package data.    license_number (str): A specific license number.</td>
      <td></td>
    </tr>
    <tr>
      <td>`create_plant_packages`</td>
      <td>Create plant packages.</td>
      <td>data (list): A list of plant packages (dict) to create.    license_number (str): A specific license number.</td>
      <td></td>
    </tr>
    <tr>
      <td>`create_plants`</td>
      <td>Use a plant to create an immature plant batch.</td>
      <td>data (list): A list of plants (dict) to create.    license_number (str): A specific license number.    return_obs (bool): Whether or not to get and return the created        plants.</td>
      <td>(list): Returns a list of plants (Plants) classes.</td>
    </tr>
    <tr>
      <td>`create_receipt`</td>
      <td>Create a receipt.</td>
      <td>data (dict): A receipts (dict) to create.    license_number (str): A specific license number.</td>
      <td></td>
    </tr>
    <tr>
      <td>`create_receipts`</td>
      <td>Create receipt(s).</td>
      <td>data (list): A list of receipts (dict) to create.    license_number (str): A specific license number.</td>
      <td></td>
    </tr>
    <tr>
      <td>`create_strain`</td>
      <td>Create a strain.</td>
      <td>data (dict): A strain to create.    license_number (str): A specific license number.    return_obs (bool): Whether or not to get and return the created        strain (Strain).</td>
      <td>(Strain): Returns a strain class.</td>
    </tr>
    <tr>
      <td>`create_strains`</td>
      <td>Create strain(s).</td>
      <td>data (list): A list of strains (dict) to create.    license_number (str): A specific license number.    return_obs (bool): Whether or not to get and return the created        strains (Strain).</td>
      <td>(list): Returns a list of strains (Strains) classes.</td>
    </tr>
    <tr>
      <td>`create_transactions`</td>
      <td>Create transaction(s).</td>
      <td>data (list): A list of transactions (dict) to create.    date (str): An ISO 8601 formatted string of the transaction date.    license_number (str): A specific license number.Return:    (Transaction): Return the created transaction if `return_obs=True`.</td>
      <td></td>
    </tr>
    <tr>
      <td>`create_transfer`</td>
      <td>Create a transfer.</td>
      <td>data (dict): A transfer to create.    license_number (str): A specific license number.    return_obs (bool): Whether or not to get and return the created        transfer.</td>
      <td>(Transfer): Returns the created transfer.</td>
    </tr>
    <tr>
      <td>`create_transfer_templates`</td>
      <td>Create transfer_template(s).</td>
      <td>data (list): A list of transfer templates (dict) to create.</td>
      <td></td>
    </tr>
    <tr>
      <td>`create_transfers`</td>
      <td>Create transfer(s).</td>
      <td>data (list): A list of transfers (dict) to create.    license_number (str): A specific license number.    return_obs (bool): Whether or not to get and return the created        transfer.</td>
      <td>(list): Returns a list of transfers (Transfer).</td>
    </tr>
    <tr>
      <td>`delete_delivery`</td>
      <td>Delete a home delivery.</td>
      <td>uid (str): The UID of a home delivery to delete.    license_number (str): A specific license number.</td>
      <td></td>
    </tr>
    <tr>
      <td>`delete_item`</td>
      <td>Delete item.</td>
      <td>uid (str): The UID of an item to delete.    license_number (str): A specific license number.</td>
      <td></td>
    </tr>
    <tr>
      <td>`delete_location`</td>
      <td>Delete location.</td>
      <td>uid (str): The UID of a location to delete.    license_number (str): Optional license number filter.</td>
      <td></td>
    </tr>
    <tr>
      <td>`delete_package`</td>
      <td>Delete a package.</td>
      <td>uid (str): The UID of a package to delete.    license_number (str): A specific license number.</td>
      <td></td>
    </tr>
    <tr>
      <td>`delete_patient`</td>
      <td>Delete patient.</td>
      <td>uid (str): The UID of a patient to delete.</td>
      <td></td>
    </tr>
    <tr>
      <td>`delete_receipt`</td>
      <td>Delete receipt.</td>
      <td>uid (str): The UID of a receipt to delete.    license_number (str): A specific license number.</td>
      <td></td>
    </tr>
    <tr>
      <td>`delete_strain`</td>
      <td>Delete strain.</td>
      <td>uid (str): The UID of a strain to delete.    license_number (str): A specific license number.</td>
      <td></td>
    </tr>
    <tr>
      <td>`delete_transfer`</td>
      <td>Delete transfer.</td>
      <td>uid (str): The UID of a transfer to delete.    license_number (str): A specific license number.</td>
      <td></td>
    </tr>
    <tr>
      <td>`delete_transfer_template`</td>
      <td>Delete transfer template.</td>
      <td>uid (str): The UID of a transfer template to delete.</td>
      <td></td>
    </tr>
    <tr>
      <td>`destroy_plants`</td>
      <td>Move multiple plants.</td>
      <td></td>
      <td></td>
    </tr>
    <tr>
      <td>`finish_harvests`</td>
      <td>Finish harvests.</td>
      <td>data (list): A list of harvests (dict) to finish.    license_number (str): A specific license number.</td>
      <td></td>
    </tr>
    <tr>
      <td>`format_params`</td>
      <td>Format Metrc request parameters.</td>
      <td></td>
      <td>(dict): Returns the parameters as a dictionary.</td>
    </tr>
    <tr>
      <td>`get_adjustment_reasons`</td>
      <td>Get reasons for adjusting packages.</td>
      <td></td>
      <td></td>
    </tr>
    <tr>
      <td>`get_batch`</td>
      <td>Get a given plant batch.</td>
      <td></td>
      <td></td>
    </tr>
    <tr>
      <td>`get_batch_types`</td>
      <td>Get plant batch types.</td>
      <td>license_number (str): A specific license number.</td>
      <td></td>
    </tr>
    <tr>
      <td>`get_batches`</td>
      <td>Get plant batches(s).</td>
      <td>uid (str): The UID for a plant batch.    action (str): The action to apply to the plants, with options:        `active`, `inactive`, `types`.    license_number (str): A specific license number.    start (str): An ISO 8601 formatted string to restrict the start        by the last modified time.    end (str): An ISO 8601 formatted string to restrict the end        by the last modified time.</td>
      <td></td>
    </tr>
    <tr>
      <td>`get_customer_types`</td>
      <td>Get all customer types.</td>
      <td>license_number (str): A specific license number.</td>
      <td>(list): Returns a list of customer types (dict).</td>
    </tr>
    <tr>
      <td>`get_deliveries`</td>
      <td>Get sale(s).</td>
      <td>uid (str): The UID for a delivery.    action (str): The action to apply to the delivery, with options:        `active` or `inactive`.    license_number (str): A specific license number.    start (str): An ISO 8601 formatted string to restrict the start        by the last modified time.    end (str): An ISO 8601 formatted string to restrict the end        by the last modified time.    sales_start (str): An ISO 8601 formatted string to restrict the start        by the sales time.    sales_end (str): An ISO 8601 formatted string to restrict the end        by the sales time.</td>
      <td>(list): Returns a list of Receipts.</td>
    </tr>
    <tr>
      <td>`get_delivery`</td>
      <td>Get a home delivery.</td>
      <td></td>
      <td></td>
    </tr>
    <tr>
      <td>`get_employees`</td>
      <td>Get all employees.</td>
      <td>license_number (str): A licensee's license number.</td>
      <td></td>
    </tr>
    <tr>
      <td>`get_facilities`</td>
      <td>Get all facilities.</td>
      <td></td>
      <td></td>
    </tr>
    <tr>
      <td>`get_facility`</td>
      <td>Get a given facility by its license number.</td>
      <td></td>
      <td></td>
    </tr>
    <tr>
      <td>`get_harvests`</td>
      <td>Get harvests.</td>
      <td>uid (str): The UID of a harvest, takes precedent over action.    action (str): A specific filter to apply, including:        `active`, `onhold`, `inactive`, `waste/types`.    license_number (str): The licensee's license number.    start (str): An ISO 8601 formatted string to restrict the start        by the last modified time.    end (str): An ISO 8601 formatted string to restrict the end        by the last modified time.</td>
      <td></td>
    </tr>
    <tr>
      <td>`get_item`</td>
      <td>Get an item.</td>
      <td>uid (str): The UID of an item.    action (str): A specific type of item to filter by:        `active`, `categories`, `brands`.    license_number (str): A specific license number.</td>
      <td>(Item): Returns a an item.</td>
    </tr>
    <tr>
      <td>`get_item_categories`</td>
      <td>Get all item categories.</td>
      <td>license_number (str): A specific license number.</td>
      <td>(list): Returns a list of item categories (Category).</td>
    </tr>
    <tr>
      <td>`get_items`</td>
      <td>Get items.</td>
      <td>uid (str): The UID of an item.    action (str): A specific type of item to filter by:        `active`, `categories`, `brands`.    license_number (str): A specific license number.</td>
      <td>(list): Returns a list of items (Item).</td>
    </tr>
    <tr>
      <td>`get_lab_result`</td>
      <td>Get lab results.</td>
      <td>uid (str): The UID of a lab result.    license_number (str): A specific license number.</td>
      <td>(LabResult): Returns a a lab result.</td>
    </tr>
    <tr>
      <td>`get_lab_results`</td>
      <td>Get lab results.</td>
      <td>uid (str): The UID for a package.    license_number (str): A specific license number.</td>
      <td></td>
    </tr>
    <tr>
      <td>`get_location`</td>
      <td>Get a location.</td>
      <td>uid (str): The UID of a location.    license_number (str): A specific license number.</td>
      <td>(Location): Returns a a lab result.</td>
    </tr>
    <tr>
      <td>`get_location_types`</td>
      <td>Get all location types for a given license.</td>
      <td>license_number (str): A specific license number.</td>
      <td></td>
    </tr>
    <tr>
      <td>`get_locations`</td>
      <td>Get locations.</td>
      <td>uid (str): The UID of a location, takes precedent over action.    action (str): A specific filter to apply, with options:        `active`, `types`.    license_number (str): A specific license number.</td>
      <td></td>
    </tr>
    <tr>
      <td>`get_package`</td>
      <td>Get a package.</td>
      <td>uid (str): The UID of an item.    label (str): The tag label for a package.    action (str): A specific type of item to filter by:        `active`, `categories`, `brands`.    license_number (str): A specific license number.</td>
      <td>(Item): Returns an item (Item).</td>
    </tr>
    <tr>
      <td>`get_package_statuses`</td>
      <td>Get all package status choices.</td>
      <td>license_number (str): A specific license number.</td>
      <td>(list): Returns package statuses (dict).</td>
    </tr>
    <tr>
      <td>`get_package_types`</td>
      <td>Get all facilities.</td>
      <td>license_number (str): A specific license number.</td>
      <td></td>
    </tr>
    <tr>
      <td>`get_packages`</td>
      <td>Get package(s).</td>
      <td>uid (str): The UID for a package.    label (str): The tag label for a package.    license_number (str): A specific license number.    action (str): `active`, `onhold`, `inactive`, `types`,        `adjust/reasons`.    start (str): Optional ISO date to restrict earliest modified transfers.    end (str): Optional ISO date to restrict latest modified transfers.</td>
      <td>(list): Returns a list of packages (Packages).</td>
    </tr>
    <tr>
      <td>`get_patients`</td>
      <td>Get licensee member patients.</td>
      <td>uid (str): A UID for a patient.    action (str): An optional filter to apply: `active`.    license_number (str): A licensee's license number to filter by.</td>
      <td></td>
    </tr>
    <tr>
      <td>`get_plants`</td>
      <td>Get plant(s).</td>
      <td>uid (str): The UID for a plant.    label (str): The label for a given plant.    action (str): A specific filter to apply, with options:        `vegetative`, `flowering`, `onhold`,        `inactive`, `additives`, `additives/types`,        `growthphases`, `waste/methods`, `waste/reasons`.    license_number (str): A specific license number.    start (str): An ISO 8601 formatted string to restrict the start        by the last modified time.    end (str): An ISO 8601 formatted string to restrict the end        by the last modified time.</td>
      <td></td>
    </tr>
    <tr>
      <td>`get_receipts`</td>
      <td>Get sale(s).</td>
      <td>uid (str): The UID for a plant batch.    action (str): The action to apply to the plants, with options:        `active` or `inactive`    license_number (str): A specific license number.    start (str): An ISO 8601 formatted string to restrict the start        by the last modified time.    end (str): An ISO 8601 formatted string to restrict the end        by the last modified time.    sales_start (str): An ISO 8601 formatted string to restrict the start        by the sales time.    sales_end (str): An ISO 8601 formatted string to restrict the end        by the sales time.</td>
      <td>(list): Returns a list of Receipts or a singular Receipt.</td>
    </tr>
    <tr>
      <td>`get_return_reasons`</td>
      <td>Get the possible return reasons for home delivery items.</td>
      <td>license_number (str): A specific license number.</td>
      <td>(list): A list of return reasons.</td>
    </tr>
    <tr>
      <td>`get_strains`</td>
      <td>Get strains.</td>
      <td>uid (str): A UID for a strain.    action (str): An optional filter to apply: `active`.    license_number (str): A licensee's license number to filter by.</td>
      <td></td>
    </tr>
    <tr>
      <td>`get_test_statuses`</td>
      <td>Get pre-defined lab statuses.</td>
      <td>license_number (str): A specific license number.</td>
      <td></td>
    </tr>
    <tr>
      <td>`get_test_types`</td>
      <td>Get required quality assurance analyses.</td>
      <td>license_number (str): A specific license number.</td>
      <td></td>
    </tr>
    <tr>
      <td>`get_transactions`</td>
      <td>Get transaction(s).</td>
      <td>license_number (str): A specific license number.    start (str): An ISO 8601 formatted string to restrict the start        by the sales time.    end (str): An ISO 8601 formatted string to restrict the end        by the sales time.</td>
      <td>(list): Returns either a list of Transactions or a singular Transaction.</td>
    </tr>
    <tr>
      <td>`get_transfer_packages`</td>
      <td>Get shipments.</td>
      <td>uid (str): Required UID of a shipment.    license_number (str): A specific license number.    action (str): The filter to apply to transfers:        `packages`, `packages/wholesale`, `requiredlabtestbatches`.</td>
      <td></td>
    </tr>
    <tr>
      <td>`get_transfer_templates`</td>
      <td>Get transfer template(s).</td>
      <td>uid (str): A UID for a transfer template.    action (str): An optional filter to apply: `deliveries`, `packages`.    license_number (str): A specific license number.    start (str): An ISO 8601 formatted string to restrict the start        by the sales time.    end (str): An ISO 8601 formatted string to restrict the end        by the sales time.</td>
      <td></td>
    </tr>
    <tr>
      <td>`get_transfer_types`</td>
      <td>Get all transfer types.</td>
      <td>license_number (str): A specific license number.</td>
      <td>(list): Returns transfer types (dict).</td>
    </tr>
    <tr>
      <td>`get_transfers`</td>
      <td>Get transfers.</td>
      <td>uid (str): The UID for a transfer, takes precedent in query.    transfer_type (str): The type of transfer:        `incoming`, `outgoing`, or `rejected`.    license_number (str): A specific license number.    start (str): Optional ISO date to restrict earliest modified transfers.    end (str): Optional ISO date to restrict latest modified transfers.</td>
      <td></td>
    </tr>
    <tr>
      <td>`get_transporter_details`</td>
      <td>Get the details of the transporter driver and vehicle.</td>
      <td>uid (str): The ID of the shipment delivery.</td>
      <td></td>
    </tr>
    <tr>
      <td>`get_transporters`</td>
      <td>Get the data for a transporter.</td>
      <td>uid (str): The ID of the shipment delivery.</td>
      <td></td>
    </tr>
    <tr>
      <td>`get_units_of_measure`</td>
      <td>Get all units of measurement.</td>
      <td>license_number (str): A specific license number.</td>
      <td>(list): Returns a list of units of measure (dict).</td>
    </tr>
    <tr>
      <td>`get_waste_methods`</td>
      <td>Get all waste methods for a given license.</td>
      <td>license_number (str): A specific license number.</td>
      <td></td>
    </tr>
    <tr>
      <td>`get_waste_reasons`</td>
      <td>Get all waste reasons for plants for a given license.</td>
      <td>license_number (str): A specific license number.</td>
      <td></td>
    </tr>
    <tr>
      <td>`get_waste_types`</td>
      <td>Get all waste types for harvests for a given license.</td>
      <td>license_number (str): A specific license number.</td>
      <td></td>
    </tr>
    <tr>
      <td>`harvest_plants`</td>
      <td>Move multiple plants.</td>
      <td></td>
      <td></td>
    </tr>
    <tr>
      <td>`import_tags`</td>
      <td>Import plant and package tags.</td>
      <td>file_path (str): The file location of the tags.    row_start (int): The row at which to begin importing tags.    row_end (int): The row at which to end importing tags.    number (int): The number of tags to import.</td>
      <td>(dict): Returns the tags as a dictionary.</td>
    </tr>
    <tr>
      <td>`initialize_logs`</td>
      <td>Initialize Metrc logs.</td>
      <td></td>
      <td></td>
    </tr>
    <tr>
      <td>`manage_batches`</td>
      <td>Manage plant batch(es) by applying a given action.</td>
      <td>data (list): A list of plants (dict) to manage.    action (str): The action to apply to the plants, with options:        `createplantings`, `createpackages`, `split`,        `/create/packages/frommotherplant`, `changegrowthphase`,        `additives`, `destroy`.    from_mother (bool): An optional parameter for the        `createpackages` action.</td>
      <td></td>
    </tr>
    <tr>
      <td>`manage_packages`</td>
      <td>Adjust package(s).</td>
      <td>data (list): A list of packages (dict) to manage.    license_number (str): A specific license number.    action (str): The action to apply to the packages, with options:        `adjust`, `finish`, `unfinish`, `remediate`.</td>
      <td></td>
    </tr>
    <tr>
      <td>`manage_plants`</td>
      <td>Manage plant(s) by applying a given action.</td>
      <td>data (list): A list of plants (dict) to manage.    action (str): The action to apply to the plants, with options:        `moveplants`, `changegrowthphases`, `destroyplants`,        `additives`, `additives/bylocation`,        `create/plantings`, `create/plantbatch/packages`,        `manicureplants`, `harvestplants`.    license_number (str): A specific license number.</td>
      <td></td>
    </tr>
    <tr>
      <td>`manicure_plants`</td>
      <td>Move multiple plants.</td>
      <td></td>
      <td></td>
    </tr>
    <tr>
      <td>`move_batch`</td>
      <td>Move plant batch(es).</td>
      <td>data (list): A list of plant batches (dict) to move.</td>
      <td></td>
    </tr>
    <tr>
      <td>`move_harvests`</td>
      <td>Move a harvests.</td>
      <td>data (list): A list of harvests (dict) to move.    license_number (str): A specific license number.</td>
      <td></td>
    </tr>
    <tr>
      <td>`move_plants`</td>
      <td>Move multiple plants.</td>
      <td>data (list): A list of plant move data (dict).    license_number (str): A specific license number.</td>
      <td></td>
    </tr>
    <tr>
      <td>`post_lab_results`</td>
      <td>Post lab result(s).</td>
      <td>data (list): A list of lab results (dict) to create or update.    license_number (str): A specific license number.</td>
      <td></td>
    </tr>
    <tr>
      <td>`release_lab_results`</td>
      <td>Release lab result(s).</td>
      <td>data (list): A list of package labels (dict) to release lab results.    license_number (str): A specific license number.</td>
      <td></td>
    </tr>
    <tr>
      <td>`remove_waste`</td>
      <td>Remove's waste from a harvest.</td>
      <td>data (list): A list of waste (dict) to unfinish.    license_number (str): A specific license number.</td>
      <td></td>
    </tr>
    <tr>
      <td>`request`</td>
      <td>Make a request to the Metrc API.</td>
      <td></td>
      <td></td>
    </tr>
    <tr>
      <td>`split_batch`</td>
      <td>Split a given batch.</td>
      <td>data (dict): Batch split data.    license_number (str): A specific license number.</td>
      <td></td>
    </tr>
    <tr>
      <td>`split_batches`</td>
      <td>Split multiple batches.</td>
      <td>data (list): A list of batch splits (dict).    license_number (str): A specific license number.</td>
      <td></td>
    </tr>
    <tr>
      <td>`unfinish_harvests`</td>
      <td>Unfinish harvests.</td>
      <td>data (list): A list of harvests (dict) to unfinish.    license_number (str): A specific license number.</td>
      <td></td>
    </tr>
    <tr>
      <td>`update_deliveries`</td>
      <td>Update home delivery(ies).</td>
      <td>data (list): A list of deliveries (dict) to create.    license_number (str): A specific license number.</td>
      <td></td>
    </tr>
    <tr>
      <td>`update_item`</td>
      <td>Update an item.</td>
      <td>data (dict): An item to update.    license_number (str): A specific license number.</td>
      <td></td>
    </tr>
    <tr>
      <td>`update_items`</td>
      <td>Update items.</td>
      <td>data (list): A list of items (dict) to update.    license_number (str): A specific license number.</td>
      <td></td>
    </tr>
    <tr>
      <td>`update_locations`</td>
      <td>Update location(s).</td>
      <td>data (list): A list of locations (dict) to update.    license_number (str): Optional license number filter.</td>
      <td></td>
    </tr>
    <tr>
      <td>`update_package`</td>
      <td>Update a given package.</td>
      <td></td>
      <td></td>
    </tr>
    <tr>
      <td>`update_package_item_locations`</td>
      <td>Update package item location(s).</td>
      <td>data (list): A list of package items (dict) to move.    license_number (str): A specific license number.</td>
      <td></td>
    </tr>
    <tr>
      <td>`update_package_notes`</td>
      <td>Update package note(s).</td>
      <td>data (list): A list of package notes (dict) to update.    license_number (str): A specific license number.</td>
      <td></td>
    </tr>
    <tr>
      <td>`update_packages`</td>
      <td>Update packages.</td>
      <td>data (list): A list of packages (dict) to update.    license_number (str): A specific license number.</td>
      <td></td>
    </tr>
    <tr>
      <td>`update_patients`</td>
      <td>Update strain(s).</td>
      <td>data (list): A list of patients (dict) to update.</td>
      <td></td>
    </tr>
    <tr>
      <td>`update_receipts`</td>
      <td>Update receipt(s).</td>
      <td>data (list): A list of receipts (dict) to update.    license_number (str): A specific license number.</td>
      <td></td>
    </tr>
    <tr>
      <td>`update_strain`</td>
      <td>Update strain.</td>
      <td>data (list): A strain (dict) to update.    license_number (str): A specific license number.    return_obs (bool): Whether or not to get and return the created strains.</td>
      <td>(Strain): Returns the updated strain.</td>
    </tr>
    <tr>
      <td>`update_strains`</td>
      <td>Update strain(s).</td>
      <td>data (list): A list of strains (dict) to update.    license_number (str): A specific license number.    return_obs (bool): Whether or not to get and return the created strains.</td>
      <td>(list): Returns a list of strains (Strain) classes.</td>
    </tr>
    <tr>
      <td>`update_transactions`</td>
      <td>Update transaction(s).</td>
      <td>data (list): A list of transactions (dict) to update.    date (str): An ISO 8601 formatted string of the transaction date.    license_number (str): A specific license number.Return:    (list): Return a list of transactions (Transaction) if `return_obs=True`.</td>
      <td></td>
    </tr>
    <tr>
      <td>`update_transfer`</td>
      <td>Update a given transfer.</td>
      <td>data (dict): A transfer to update.    license_number (str): A specific license number.    return_obs (bool): Whether or not to get and return the created transfer.</td>
      <td>(Transfer): Returns transfer class.</td>
    </tr>
    <tr>
      <td>`update_transfer_templates`</td>
      <td>Update transfer template(s).</td>
      <td>data (list): A list of transfer templates (dict) to update.</td>
      <td></td>
    </tr>
    <tr>
      <td>`update_transfers`</td>
      <td>Update transfer(s).</td>
      <td>data (list): A list of transfers (dict) to update.    license_number (str): A specific license number.    return_obs (bool): Whether or not to get and return the updated transfers.</td>
      <td>(list): Returns a list of transfers (Transfer).</td>
    </tr>
    <tr>
      <td>`upload_coas`</td>
      <td>Upload lab result CoA(s).</td>
      <td>data (list): A list of CoAs (dict) to upload.    license_number (str): A specific license number.</td>
      <td></td>
    </tr>
  </tbody>
</table>
