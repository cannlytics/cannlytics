# Augmenting Washington State Leaf Traceability Data

The Washington State Leaf Traceability datasets are disparate, yet contained rich, valuable data. This collection of scripts aims to be a standard mechanism of aggregating the datasets and augmenting them with other useful data. Augmenting the Leaf traceability data can be difficult due to the size of each dataset.

| Dataset | Zipped Size | Un-zipped Size |
|---------|-------------|----------------|
| Areas_0 | 9 MB |  81 MB |
| Batches_0 | 1.3 GB | 27 GB  |
| Disposals_0 | 788 MB | 10 GB  |
| Inventories_0 | 2.7 GB |  31.7 GB |
| InventoryTransferItems_0 | 1 GB | 15.2 GB |
| InventoryTransfers_0 | 80 MB | 702 MB |
| InventoryTypes_0 | 1.1 GB  | 14.8 GB |
| LabResults_0 |  | 1.2 GB |
| LabResults_1 |  |  1.1 GB |
| LabResults_2 |  | 135 MB |
| Licensees_0 |  | 1.2 MB |
| Plants_0 | 379 MB | 12.9 GB |
| Sales_0 | 2.8 GB |  31.1 GB |
| Sales_1 | 4.4 GB | 37.1 GB |
| Sales_2 | 1.2 GB | 10.7 GB |
| SaleItems_0 | 4.7 GB | 42.6 GB |
| SaleItems_1 | 5.7 GB | 48.2 GB |
| SaleItems_2 | 5.5 GB | 48.5 GB |
| SaleItems_3 | 4.6 GB | 41.9 GB |
| Strains_0 | 28 MB |  264 MB |
| Taxes_0 | 1 KB | 1 KB |
| Total |  | 375.9 GB |

## Augmenting Lab Results

Lab results are augmented with relevant fields from the licensees, inventories, inventory types, and strains datasets.

```py
lab_result_fields = {
    'global_id' : 'string',
    'mme_id' : 'string',
    'intermediate_type' : 'category',
    'status' : 'category',
    'global_for_inventory_id': 'string',
    .
    .
    .
    'testing_status' : 'category',
    'type' : 'category',
    'inventory_id' : 'string',
    'batch_id' : 'string',
    'parent_lab_result_id' : 'string',
    'og_parent_lab_result_id' : 'string',
    'copied_from_lab_id' : 'string',
    'external_id' : 'string',
    'lab_user_id' : 'string',
    'user_id' : 'string',
    'cannabinoid_editor' : 'float32',
    'microbial_editor' : 'string',
    'mycotoxin_editor' : 'string',
    'solvent_editor' : 'string',
}

lab_result_date_fields = [
    'created_at',
    'deleted_at',
    'updated_at',
    'received_at',
]
```

## Augmenting Licensees

Each licensee entry is augmented with latitude and longitude.

```py
licensee_fields = {
    'global_id' : 'string',
    'name': 'string',
    'type': 'string',
    'code': 'string',
    'address1': 'string',
    'address2': 'string',
    'city': 'string',
    'state_code': 'string',
    'postal_code': 'string',
    'country_code': 'string',
    'phone': 'string',
    'external_id': 'string',
    'certificate_number': 'string',
    'is_live': 'bool',
    'suspended': 'bool',
}

licensee_date_fields = [
    'created_at',
    'updated_at',
    'deleted_at',
    'expired_at',
]
```

> Note that there are no valid dates for `created_at` if the license was issued before 2018-02-21.

## Augmenting Sales


## Creating Summary Statistics


