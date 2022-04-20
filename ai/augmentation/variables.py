"""
Defined Washington State Leaf Data Systems dataset fields.
Cannabis Data Science Meetup Group
Copyright (c) 2022 Cannlytics

Authors: Keegan Skeate <keegan@cannlytics.com>
Created: 1/18/2022
Updated: 1/19/2022
License: MIT License <https://opensource.org/licenses/MIT>
"""

#------------------------------------------------------------------------------
# Lab result fields.
#------------------------------------------------------------------------------

lab_result_fields = {
    'global_id': 'string',
    'mme_id': 'string',
    'intermediate_type': 'category',
    'status': 'category',
    'global_for_inventory_id': 'string',
    'cannabinoid_status': 'category',
    'cannabinoid_cbc_percent': 'float',
    'cannabinoid_cbc_mg_g': 'float',
    'cannabinoid_cbd_percent': 'float',
    'cannabinoid_cbd_mg_g': 'float',
    'cannabinoid_cbda_percent': 'float',
    'cannabinoid_cbda_mg_g': 'float',
    'cannabinoid_cbdv_percent': 'float',
    'cannabinoid_cbdv_mg_g': 'float',
    'cannabinoid_cbg_percent': 'float',
    'cannabinoid_cbg_mg_g': 'float',
    'cannabinoid_cbga_percent': 'float',
    'cannabinoid_cbga_mg_g': 'float',
    'cannabinoid_cbn_percent': 'float',
    'cannabinoid_cbn_mg_g': 'float',
    'cannabinoid_d8_thc_percent': 'float',
    'cannabinoid_d8_thc_mg_g': 'float',
    'cannabinoid_d9_thca_percent': 'float',
    'cannabinoid_d9_thca_mg_g': 'float',
    'cannabinoid_d9_thc_percent': 'float',
    'cannabinoid_d9_thc_mg_g': 'float',
    'cannabinoid_thcv_percent': 'float',
    'cannabinoid_thcv_mg_g': 'float',
    'solvent_status': 'category',
    'solvent_acetone_ppm': 'float',
    'solvent_benzene_ppm': 'float',
    'solvent_butanes_ppm': 'float',
    'solvent_chloroform_ppm': 'float',
    'solvent_cyclohexane_ppm': 'float',
    'solvent_dichloromethane_ppm': 'float',
    'solvent_ethyl_acetate_ppm': 'float',
    'solvent_heptane_ppm': 'float',
    'solvent_hexanes_ppm': 'float',
    'solvent_isopropanol_ppm': 'float',
    'solvent_methanol_ppm': 'float',
    'solvent_pentanes_ppm': 'float',
    'solvent_propane_ppm': 'float',
    'solvent_toluene_ppm': 'float',
    'solvent_xylene_ppm': 'float',
    'foreign_matter': 'bool',
    'foreign_matter_stems': 'float',
    'foreign_matter_seeds': 'float',
    'microbial_status': 'category',
    'microbial_bile_tolerant_cfu_g': 'float',
    'microbial_pathogenic_e_coli_cfu_g': 'float',
    'microbial_salmonella_cfu_g': 'float',
    'moisture_content_percent': 'float',
    'moisture_content_water_activity_rate': 'float',
    'mycotoxin_status': 'category',
    'mycotoxin_aflatoxins_ppb': 'float',
    'mycotoxin_ochratoxin_ppb': 'float',
    'thc_percent': 'float',
    'notes': 'string',
    'testing_status': 'category',
    'type': 'category',
    'inventory_id': 'string',
    'batch_id': 'string',
    'parent_lab_result_id': 'string',
    'og_parent_lab_result_id': 'string',
    'copied_from_lab_id': 'string',
    'external_id': 'string',
    'lab_user_id': 'string',
    'user_id': 'string',
    'cannabinoid_editor': 'string',
    'microbial_editor': 'string',
    'mycotoxin_editor': 'string',
    'solvent_editor': 'string',
}

lab_result_date_fields = [
    'created_at',
    'deleted_at',
    'updated_at',
    'received_at',
]

#------------------------------------------------------------------------------
# Licensees fields.
#------------------------------------------------------------------------------

licensee_fields = {
    'global_id': 'string',
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
    'created_at', # No records if issued before 2018-02-21.
    'updated_at',
    'deleted_at',
    'expired_at',
]

#------------------------------------------------------------------------------
# Inventories fields.
#------------------------------------------------------------------------------

inventory_fields = {
    'global_id': 'string',
    'strain_id': 'string',
    'inventory_type_id': 'string',
    'qty': 'float',
    'uom': 'string',
    'mme_id': 'string',
    'user_id': 'string',
    'external_id': 'string',
    'area_id': 'string',
    'batch_id': 'string',
    'lab_result_id': 'string',
    'lab_retest_id': 'string',
    'is_initial_inventory': 'bool',
    'created_by_mme_id': 'string',
    'additives': 'string',
    'serving_num': 'float',
    'sent_for_testing': 'bool',
    'medically_compliant': 'string',
    'legacy_id': 'string',
    'lab_results_attested': 'int',
    'global_original_id': 'string',
}

inventory_date_fields = [
    'created_at', # No records if issued before 2018-02-21.
    'updated_at',
    'deleted_at',
    'inventory_created_at',
    'inventory_packaged_at',
    'lab_results_date',
]

#------------------------------------------------------------------------------
# Inventory type fields.
#------------------------------------------------------------------------------

inventory_type_fields = {
    'global_id': 'string',
    'mme_id': 'string',
    'user_id': 'string',
    'external_id': 'string',
    'uom': 'string',
    'name': 'string',
    'intermediate_type': 'string',
}

inventory_type_date_fields = [
    'created_at',
    'updated_at',
    'deleted_at',
]

#------------------------------------------------------------------------------
# Strain fields.
#------------------------------------------------------------------------------

strain_fields = {
    'mme_id': 'string',
    'user_id': 'string',
    'global_id': 'string',
    'external_id': 'string',
    'name': 'string',
}
strain_date_fields = [
    'created_at',
    'updated_at',
    'deleted_at',
]


#------------------------------------------------------------------------------
# Sales fields.
# TODO: Parse Sales_0, Sales_1, Sales_2
#------------------------------------------------------------------------------

sales_fields = {
    'global_id': 'string',
    'external_id': 'string',
    'type': 'string', # wholesale or retail_recrational
    'price_total': 'float',
    'status': 'string',
    'mme_id': 'string',
    'user_id': 'string',
    'area_id': 'string',
    'sold_by_user_id': 'string',
}
sales_date_fields = [
    'created_at',
    'updated_at',
    'sold_at',
    'deleted_at',
]


#------------------------------------------------------------------------------
# Sales Items fields.
# TODO: Parse SalesItems_0, SalesItems_1, SalesItems_2, SalesItems_3
#------------------------------------------------------------------------------

sales_items_fields = {
    'global_id': 'string',
    'mme_id': 'string',
    'user_id': 'string',
    'sale_id': 'string',
    'batch_id': 'string',
    'inventory_id': 'string',
    'external_id': 'string',
    'qty': 'float',
    'uom': 'string',
    'unit_price': 'float',
    'price_total': 'float',
    'name': 'string',
}
sales_items_date_fields = [
    'created_at',
    'updated_at',
    'sold_at',
    'use_by_date',
]

#------------------------------------------------------------------------------
# Batches fields.
# TODO: Parse Batches_0
#------------------------------------------------------------------------------

batches_fields = {
    'external_id': 'string',
    'num_plants': 'float',
    'status': 'string',
    'qty_harvest': 'float',
    'uom': 'string',
    'is_parent_batch': 'int',
    'is_child_batch': 'int',
    'type': 'string',
    'harvest_stage': 'string',
    'qty_accumulated_waste': 'float',
    'qty_packaged_flower': 'float',
    'qty_packaged_by_product': 'float',
    'origin': 'string',
    'source': 'string',
    'qty_cure': 'float',
    'plant_stage': 'string',
    'flower_dry_weight': 'float',
    'waste': 'float',
    'other_waste': 'float',
    'flower_waste': 'float',
    'other_dry_weight': 'float',
    'flower_wet_weight': 'float',
    'other_wet_weight': 'float',
    'global_id': 'string',
    'global_area_id': 'string',
    'area_name': 'string',
    'global_mme_id': 'string',
    'mme_name': 'string',
    'mme_code': 'string',
    'global_user_id': 'string',
    'global_strain_id': 'string',
    'strain_name': 'string',
    'global_mother_plant_id': 'string',
    'global_flower_area_id': 'string',
    'global_other_area_id': 'string',
}
batches_date_fields = [
    'created_at',
    'updated_at',
    'planted_at',
    'harvested_at',
    'batch_created_at',
    'deleted_at',
    'est_harvest_at',
    'packaged_completed_at',
    'harvested_end_at',
]


#------------------------------------------------------------------------------
# Taxes fields.
# TODO: Parse Taxes_0
#------------------------------------------------------------------------------

taxes_fields = {

}
taxes_date_fields = [

]

#------------------------------------------------------------------------------
# Areas fields.
#------------------------------------------------------------------------------

areas_fields = {
    'external_id': 'string',
    'name': 'string',
    'type': 'string',
    'is_quarantine_area': 'bool',
    'global_id': 'string',
}
areas_date_fields = [
    'created_at',
    'updated_at',
    'deleted_at',
]

#------------------------------------------------------------------------------
# Inventory Transfer Items fields.
# TODO: Parse InventoryTransferItems_0
#------------------------------------------------------------------------------

inventory_transfer_items_fields = {
    'external_id': 'string',
    'is_sample': 'int',
    'sample_type': 'string',
    'product_sample_type': 'string',
    'description': 'string',
    'qty': 'float',
    'price': 'float',
    'uom': 'string',
    'received_qty': 'float',
    'retest': 'int',
    'global_id': 'string',
    'is_for_extraction': 'int',
    'propagation_source': 'string',
    'inventory_name': 'string',
    'intermediate_type': 'string',
    'strain_name': 'string',
    'global_mme_id': 'string',
    'global_user_id': 'string',
    'global_batch_id': 'string',
    'global_plant_id': 'string',
    'global_inventory_id': 'string',
    'global_lab_result_id': 'string',
    'global_received_area_id': 'string',
    'global_received_strain_id': 'string',
    'global_inventory_transfer_id': 'string',
    'global_received_batch_id': 'string',
    'global_received_inventory_id': 'string',
    'global_received_plant_id': 'string',
    'global_received_mme_id': 'string',
    'global_received_mme_user_id': 'string',
    'global_customer_id': 'string',
    'global_inventory_type_id': 'string',
    # Optional: Match with inventory type fields
    # "created_at": "09/11/2018 07:39am",
    # "updated_at": "09/12/2018 03:55am",
    # "external_id": "123425",
    # "name": "Charlotte's Web Pre-Packs - 3.5gm",
    # "description": "",
    # "storage_instructions": "",
    # "ingredients": "",
    # "type": "end_product",
    # "allergens": "",
    # "contains": "",
    # "used_butane": 0,
    # "net_weight": "2",
    # "packed_qty": null,
    # "cost": "0.00",
    # "value": "0.00",
    # "serving_num": 1,
    # "serving_size": 0,
    # "uom": "ea",
    # "total_marijuana_in_grams": "0.000000",
    # "total_marijuana_in_mcg": null,
    # "deleted_at": null,
    # "intermediate_type": "usable_marijuana",
    # "global_id": "WAG12.TY3DE",
    # "global_original_id": null,
    # "weight_per_unit_in_grams": "0.00"
    # "global_mme_id": "WASTATE1.MM30",
    # "global_user_id": "WASTATE1.US1I",
    # "global_strain_id": null
}
inventory_transfer_items_date_fields = [
    'created_at',
    'updated_at',
    'received_at',
    'deleted_at',
]

#------------------------------------------------------------------------------
# Inventory Transfers fields.
# TODO: Parse InventoryTransfers_0
#------------------------------------------------------------------------------

inventory_transfers_fields = {
    'number_of_edits': 'int',
    'external_id': 'string',
    'void': 'int',
    'multi_stop': 'int',
    'route': 'string',
    'stops': 'string',
    'vehicle_description': 'string',
    'vehicle_year': 'string',
    'vehicle_color': 'string',
    'vehicle_vin': 'string',
    'vehicle_license_plate': 'string',
    'notes': 'string',
    'transfer_manifest': 'string',
    'manifest_type': 'string',
    'status': 'string',
    'type': 'string',
    'transfer_type': 'string',
    'global_id': 'string',
    'test_for_terpenes': 'int',
    'transporter_name1': 'string',
    'transporter_name2': 'string',
    'global_mme_id': 'string',
    'global_user_id': 'string',
    'global_from_mme_id': 'string',
    'global_to_mme_id': 'string',
    'global_from_user_id': 'string',
    'global_to_user_id': 'string',
    'global_from_customer_id': 'string',
    'global_to_customer_id': 'string',
    'global_transporter_user_id': 'string',
}
inventory_transfers_date_fields = [
    'created_at',
    'updated_at',
    'hold_starts_at',
    'hold_ends_at',
    'transferred_at',
    'est_departed_at',
    'est_arrival_at',
    'deleted_at',
]

#------------------------------------------------------------------------------
# Disposals fields.
# Optional: Parse Disposals_0
#------------------------------------------------------------------------------

disposals_fields = {
    'external_id': 'string',
    'whole_plant': 'string',
    'reason': 'string',
    'method': 'string',
    'phase': 'string',
    'type': 'string',
    'qty': 'float',
    'uom': 'string',
    'source': 'string',
    'disposal_cert': 'string',
    'global_id': 'string',
    'global_mme_id': 'string',
    'global_user_id': 'string',
    'global_batch_id': 'string',
    'global_area_id': 'string',
    'global_plant_id': 'string',
    'global_inventory_id': 'string',
}
disposals_date_fields = [
    'created_at',
    'updated_at',
    'hold_starts_at',
    'hold_ends_at',
    'disposal_at',
    'deleted_at',
]

#------------------------------------------------------------------------------
# Inventory Adjustments fields.
# Optional: Parse InventoryAdjustments_0, InventoryAdjustments_1, InventoryAdjustments_2
#------------------------------------------------------------------------------

inventory_adjustments_fields = {
    'external_id': 'string',
    'qty': 'float',
    'uom': 'string',
    'reason': 'string',
    'memo': 'string',
    'global_id': 'string',
    'global_mme_id': 'string',
    'global_user_id': 'string',
    'global_inventory_id': 'string',
    'global_adjusted_by_user_id': 'string',
}
inventory_adjustments_date_fields = [
    'created_at',
    'updated_at',
    'adjusted_at',
    'deleted_at',
]

#------------------------------------------------------------------------------
# Plants fields.
#------------------------------------------------------------------------------

plants_fields = {
    'global_id': 'string',
    'mme_id': 'string',
    'user_id': 'string',
    'external_id': 'string',
    'inventory_id': 'string',
    'batch_id': 'string',
    'area_id': 'string',
    'mother_plant_id': 'string',
    'is_initial_inventory': 'string',
    'origin': 'string',
    'stage': 'string',
    'strain_id': 'string',
    'is_mother': 'string',
    'last_moved_at': 'string',
    'plant_harvested_end_at': 'string',
    'legacy_id': 'string',
}
plants_date_fields = [
    'created_at',
    'deleted_at',
    'updated_at',
    'plant_created_at',
    'plant_harvested_at',
    'plant_harvested_end_at'
]
