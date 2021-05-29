"""
Leaf Integration Test | Cannlytics

Author: Keegan Skeate
Contact: keegan@cannlytics.com
Created: Thu Mar 18 16:08:18 2021
License: MIT License

Description:

    This script performs the required tests to become a
    Leaf Data Systems approved integrator. The test completes
    at least one request for each required endpoint.
    The global ID and created at timestamp are printed out.
    
Resources:

    [Leaf Docs](https://s3-us-gov-west-1.amazonaws.com/leafdata-wa-prod/help/Addendum+C--API+Documentation.pdf)

"""

# External imports
import os
from datetime import datetime
from dotenv import dotenv_values

# Local imports
import sys
sys.path.insert(0, os.path.abspath('../../'))
from cannlytics.traceability import leaf # pylint: disable=no-name-in-module, import-error
from cannlytics.traceability.leaf.exceptions import APIError # pylint: disable=no-name-in-module, import-error
from cannlytics.traceability.leaf.utils import get_time_string # pylint: disable=no-name-in-module, import-error
from cannlytics.traceability.leaf.models import ( # pylint: disable=no-name-in-module, import-error
    Inventory,
    InventoryAdjustment,
    Plant,
    Disposal,
) 

if __name__ == '__main__':
    
    #------------------------------------------------------------------
    # Initialization
    #------------------------------------------------------------------
    
    # Initialize the current time.
    now = datetime.now()
    current_time = now.isoformat()
    current_date = now.strftime('%m/%d/%Y')
    today = current_time[:10]

    # Load credentials.
    config = dotenv_values('../../.env')
    api_key = config['LEAF_TEST_API_KEY']
    cultivator_mme_code = config['LEAF_TEST_CULTIVATOR_MME_CODE']
    producer_mme_code = config['LEAF_TEST_PRODUCER_MME_CODE']
    lab_mme_code = config['LEAF_TEST_LAB_MME_CODE']
    retailer_mme_code = config['LEAF_TEST_RETAILER_MME_CODE']

    # Initialize the main producer Leaf client.
    track = leaf.authorize(api_key=api_key, mme_code=producer_mme_code)

    print('--------------------------------------------')
    print('Performing Leaf Data Systems Validation Test')
    print(current_time)
    print('--------------------------------------------')

    #------------------------------------------------------------------
    # Facilities ✓
    #------------------------------------------------------------------

    # Get the users for the facilities with the '/user' endpoint.
    users = track.get_users()
    user = users[0]
    print('User:', user.global_id)

    # Get licensee data.
    cultivator = track.get_licensees(mme_code=cultivator_mme_code)[0]
    producer = track.get_licensees(mme_code=producer_mme_code)[0]
    lab = track.get_licensees(mme_code=lab_mme_code)[0]
    retailer = track.get_licensees(mme_code=retailer_mme_code)[0]

    #------------------------------------------------------------------
    # Areas ✓
    #------------------------------------------------------------------

    # Create areas.
    areas = [
        {
            'name': 'Seed Vault',
            'type': 'non-quarantine',
            'external_id': 'area-1'
        },
        {
            'name': 'Waste Room',
            'type': 'quarantine',
            'external_id': 'area-2'
        },
        {
            'name': 'Drying Room',
            'type': 'quarantine',
            'external_id': 'area-3'
        },
    ]
    try:
        areas = track.create_areas(areas)
    except APIError:
        pass
    areas = track.get_areas()
    print('Area:', areas[0].global_id)

    #------------------------------------------------------------------
    # Batches ✓
    #------------------------------------------------------------------

    # Create a strain.
    strains = [{'name': 'Old-Time Moonshine'}]
    try:
        strains = track.create_strains(strains)
    except APIError:
        pass
    strains = track.get_strains()
    strain = strains[0]

    # Create a plant batch with the '/batches' endpoint.
    # Requires the previous creation of strain and area.
    batches = [{
        'type': 'propagation material',
        'origin': 'seed',
        'global_area_id': areas[0].global_id,
        'global_strain_id': strains[0].global_id,
        'num_plants': '33'
    }]
    try:
        batches = track.create_batches(batches)
    except APIError:
        pass
    batches = track.get_batches()
    batch = batches[0]
    print('Batch:', batch.global_id, 'Created:', batch.created_at)

    #------------------------------------------------------------------
    # Plants ✓
    #------------------------------------------------------------------

    # Create a plant and add it to the batch using: '/plants'
    plant_data = {'batch_id': batch.global_id}
    try:
        plant = Plant.create_from_json(track, plant_data)
    except APIError:
        pass
    plants = track.get_plants()
    plant = plants[0]
    print('Plant:', plant.global_id, 'Created:', plant.created_at)

    #------------------------------------------------------------------
    # Disposals ✓
    #------------------------------------------------------------------
    
    # Create a partial disposal from rgw batch with the '/disposals' endpoint.
    # Requires the previous creation of inventory lot, batch, or plant.
    disposal_data = {
        'external_id': 'disposal-1',
        'reason': 'mandated',
        'qty': 13,
        'uom': 'ea',
        'source': 'batch',
        'global_batch_id': batch.global_id,
        'global_area_id': areas[1].global_id, # Area for waste.
    }
    try:
        disposal = Disposal.create_from_json(track, disposal_data)
    except APIError:
        pass
    disposal = track.get_disposals()[0]
    print('Disposal:', disposal.global_id, 'Created:', disposal.created_at)
    
    #------------------------------------------------------------------
    # Harvests ✓
    #------------------------------------------------------------------

    # Create harvest batch with the '/plants/harvest_plants' endpoint.
    # Requires the previous creation of batch of plants.
    harvested_at = now.strftime('%m/%d/%Y %h:%m')
    harvested_at = now.isoformat()
    harvest = track.harvest_plants(
        area_id=areas[0].global_id,
        destination_id=areas[0].global_id,
        plant_ids=[plant.global_id],
        batch_id=batch.global_id,
        external_id='harvest-1',
        harvested_at=get_time_string(),
        flower_wet_weight=33,
        other_wet_weight=3.33,
        uom='gm'
    )
    print('Harvest:', harvest.global_id, 'Created:', harvest.created_at)

    #------------------------------------------------------------------
    # Inventory ✓
    #------------------------------------------------------------------

    # Create an inventory type.
    type_data = {
        'external_id': 'type-1',
        'name': 'Old-Time Moonshine Teenth',
        'type': 'end_product',
        'intermediate_type': 'usable_marijuana',
        'weight': '1.75',
        'uom': 'ea'
    }
    # inventory_type = InventoryType.create_from_json(track, type_data)
    inventory_types = track.get_inventory_types()
    inventory_type = inventory_types[1]

    # Create inventory lots with the '/inventories' endpoint.
    # Requires previous creation of area, strain, batch, and inventory type.
    inventory_data = {
        'external_id': 'inventory-1',
        'is_initial_inventory': 0,
        'is_active': 1,
        'inventory_created_at': get_time_string(),
        'inventory_packaged_at': get_time_string(),
        'medically_compliant': 0,
        'qty': '4',
        'uom': 'eq',
        'global_batch_id': batch.global_id,
        'global_area_id':  areas[2].global_id,
        'global_strain_id': strain.global_id,
        'global_inventory_type_id': inventory_type.global_id,
    }
    try:
        inventory = Inventory.create_from_json(track, inventory_data)
    except APIError:
        pass
    print('Inventory:', inventory.global_id, 'Created:', inventory.created_at)
    inventory_items = track.get_inventory()
    inventory_item = inventory_items[0]

    # Create an inventory adjustment with the '/inventory_adjustments' endpoint.
    # Requires the previous creation of an inventory lot.
    adj_data = {
        'external_id': 'adjustment-1',
        'adjusted_at': get_time_string(),
        'qty': '-2',
        'uom': 'ea',
        'reason': 'internal_qa_sample',
        'memo': 'Saving a copy of the QA sample.',
        'global_inventory_id': inventory_item.global_id,
        'global_adjusted_by_user_id': user.global_id
    }
    try:
        inventory_adjustment = InventoryAdjustment.create_from_json(adj_data)
        adjustments = track.create_inventory_adjustments([adj_data])
        adj = adjustments[0]
        print('Inventory adjustment:', adj.global_id, 'Created:', adj.created_at)
    except:
        pass

    # Create an inventory transfer with the '/inventory_transfers' endpoint.
    # Requires the previous creation of an inventory lot.
    transfer_data= {
        'manifest_type': 'delivery',
        'multi_stop': '0',
        'external_id': '12345',
        'est_departed_at': get_time_string(),
        'est_arrival_at': get_time_string(future=360),
        'vehicle_description': 'Smoke-grey Tesla',
        'vehicle_license_plate': 'Vonderful',
        'vehicle_vin': 'J1234567890',
        'global_to_mme_id': lab.global_id,
        'transporter_name1': 'Arthur',
        'transporter_name2': 'Dent',
        'inventory_transfer_items': [{
            'external_id': inventory_item.external_id,
            'is_sample': 1,
            'sample_type': 'lab_sample',
            # 'product_sample_type': 'budtender_sample',
            'retest': 0,
            'qty': '1.00',
            'uom': 'gm',
            'global_inventory_id': inventory_item.global_id
        }]
    }

    try:
        # Create the transfer.
        transfers = track.create_transfer(transfer_data)
        transfer = transfers[0]
        print('Transfer:', transfer.global_id, 'Created:', transfer.created_at)

        # Change transfer to in-transit.
        track.transit_transfer(transfer.global_id)
    except APIError:
        pass


    #------------------------------------------------------------------
    # Lab results ✓
    #------------------------------------------------------------------

    # Initialize lab Leaf client.
    lab_track = leaf.authorize(api_key=api_key, mme_code=lab_mme_code)

    # Create lab area.
    lab_area_data = {
        'name': 'Laboratory B',
        'type': 'quarantine',
        'external_id': 'lab-1'
    }
    try:
        lab_track.create_areas([lab_area_data])
    except APIError:
        pass

    # Get lab area.
    lab_area = lab_track.get_areas()[0]

    # Get transfers at the lab.
    lab_transfers = lab_track.get_transfers(global_id=transfer.global_id)
    lab_transfer = lab_transfers[0]

    # Receive the transfer
    try:
        lab_transfer = lab_track.receive_transfer(
            lab_transfer.global_id,
            area_id=lab_area.global_id
        )
    except APIError:
        pass

    # Get a sample.
    item = lab_transfer.inventory_transfer_items[0]

    # Create a lab result for a sample transferred to a lab with
    # the '/lab_result' endpoint.
    # Requires the previous creation of an inventory transfer, a lab user, 
    # and an inventory lot.
    lab_result_data = {
        'external_id': 'lab-test-1',
        'tested_at': get_time_string(),
        'testing_status': 'completed',
        'notes': "Don't forget to bring a towel.",
        'received_at': get_time_string(past=360),
        'type': item['sample_type'],
        'intermediate_type': item['intermediate_type'],
        'moisture_content_percent': '0.007',
        'moisture_content_water_activity_rate': '0.337',
        'cannabinoid_editor': user.global_id,
        'cannabinoid_status': 'completed',
        'cannabinoid_d9_thca_percent': '0.04',
        'cannabinoid_d9_thca_mg_g': 0,
        'cannabinoid_d9_thc_percent': '0.12',
        'cannabinoid_d9_thc_mg_g': 0,
        'cannabinoid_cbd_percent': '19.92',
        'cannabinoid_cbd_mg_g': 0,
        'cannabinoid_cbda_percent': '0.01',
        'cannabinoid_cbda_mg_g': 0,
        'microbial_editor': user.global_id,
        'microbial_status': 'completed',
        'microbial_bile_tolerant_cfu_g': '0.00',
        'microbial_pathogenic_e_coli_cfu_g': '0.00',
        'microbial_salmonella_cfu_g': '0.00',
        'mycotoxin_editor': user.global_id,
        'mycotoxin_status': 'completed',
        'mycotoxin_aflatoxins_ppb': '5',
        'mycotoxin_ochratoxin_ppb': '4',
        'metal_editor': '',
        'metal_status': 'not_started',
        'metal_arsenic_ppm': 0,
        'metal_cadmium_ppm': 0,
        'metal_lead_ppm': 0,
        'metal_mercury_ppm': 0,
        'pesticide_editor': '',
        'pesticide_status': 'not_started',
        'pesticide_abamectin_ppm': 0,
        'pesticide_acephate_ppm': 0,
        'pesticide_acequinocyl_ppm': 0,
        'pesticide_acetamiprid_ppm': 0,
        'pesticide_aldicarb_ppm': 0,
        'pesticide_azoxystrobin_ppm': 0,
        'pesticide_bifenazate_ppm': 0,
        'pesticide_bifenthrin_ppm': 0,
        'pesticide_boscalid_ppm': 0,
        'pesticide_carbaryl_ppm': 0,
        'pesticide_carbofuran_ppm': 0,
        'pesticide_chlorantraniliprole_ppm': 0,
        'pesticide_chlorfenapyr_ppm': 0,
        'pesticide_chlorpyrifos_ppm': 0,
        'pesticide_clofentezine_ppm': 0,
        'pesticide_cyfluthrin_ppm': 0,
        'pesticide_cypermethrin_ppm': 0,
        'pesticide_daminozide_ppm': 0,
        'pesticide_ddvp_dichlorvos_ppm': 0,
        'pesticide_diazinon_ppm': 0,
        'pesticide_dimethoate_ppm': 0,
        'pesticide_ethoprophos_ppm': 0,
        'pesticide_etofenprox_ppm': 0,
        'pesticide_etoxazole_ppm': 0,
        'pesticide_fenoxycarb_ppm': 0,
        'pesticide_fenpyroximate_ppm': 0,
        'pesticide_fipronil_ppm': 0,
        'pesticide_flonicamid_ppm': 0,
        'pesticide_fludioxonil_ppm': 0,
        'pesticide_hexythiazox_ppm': 0,
        'pesticide_imazalil_ppm': 0,
        'pesticide_imidacloprid_ppm': 0,
        'pesticide_kresoxim_methyl_ppm': 0,
        'pesticide_malathion_ppm': 0,
        'pesticide_metalaxyl_ppm': 0,
        'pesticide_methiocarb_ppm': 0,
        'pesticide_methomyl_ppm': 0,
        'pesticide_methyl_parathion_ppm': 0,
        'pesticide_mgk_264_ppm': 0,
        'pesticide_myclobutanil_ppm': 0,
        'pesticide_naled_ppm': 0,
        'pesticide_oxamyl_ppm': 0,
        'pesticide_paclobutrazol_ppm': 0,
        'pesticide_permethrinsa_ppm': 0,
        'pesticide_phosmet_ppm': 0,
        'pesticide_piperonyl_butoxideb_ppm': 0,
        'pesticide_prallethrin_ppm': 0,
        'pesticide_propiconazole_ppm': 0,
        'pesticide_propoxur_ppm': 0,
        'pesticide_pyrethrinsbc_ppm': 0,
        'pesticide_pyridaben_ppm': 0,
        'pesticide_spinosad_ppm': 0,
        'pesticide_spiromesifen_ppm': 0,
        'pesticide_spirotetramat_ppm': 0,
        'pesticide_spiroxamine_ppm': 0,
        'pesticide_tebuconazole_ppm': 0,
        'pesticide_thiacloprid_ppm': 0,
        'pesticide_thiamethoxam_ppm': 0,
        'pesticide_trifloxystrobin_ppm': 0,
        'solvent_editor': user.global_id,
        'solvent_status': 'completed',
        'solvent_acetone_ppm': 0,
        'solvent_benzene_ppm': 0,
        'solvent_butanes_ppm': 0,
        'solvent_cyclohexane_ppm': 0,
        'solvent_chloroform_ppm': 0,
        'solvent_dichloromethane_ppm': 0,
        'solvent_ethyl_acetate_ppm': 0,
        'solvent_heptane_ppm': 0,
        'solvent_hexanes_ppm': 0,
        'solvent_isopropanol_ppm': 0,
        'solvent_methanol_ppm': 0,
        'solvent_pentanes_ppm': 0,
        'solvent_propane_ppm': 0,
        'solvent_toluene_ppm': 0,
        'solvent_xylene_ppm': 0,
        'foreign_matter_stems': '1',
        'foreign_matter_seeds': '0',
        'test_for_terpenes': '0',
        'global_for_mme_id': cultivator.global_id,
        'global_inventory_id': item['global_received_inventory_id']
    }

    try:
        lab_results = lab_track.create_lab_results([lab_result_data])
        lab_result = lab_results[0]
        print('Lab result:', lab_result.global_id, 'Created:', lab_result.created_at)
    except APIError:
        pass

    #------------------------------------------------------------------
    # Sale ✓
    #------------------------------------------------------------------

    # Transfer tested product from the cultivator to the retailer.
    transfer_data= {
        'manifest_type': 'delivery',
        'global_to_mme_id': retailer.global_id,
        'multi_stop': '0',
        'external_id': '12345',
        'est_departed_at': get_time_string(),
        'est_arrival_at': get_time_string(future=360),
        'vehicle_description': 'Smoke-grey Tesla',
        'vehicle_license_plate': 'Vonderful',
        'vehicle_vin': 'J1234567890',
        'transporter_name1': 'Arthur',
        'transporter_name2': 'Dent',
        'inventory_transfer_items': [{
            'external_id': inventory_item.external_id,
            'is_sample': 1,
            'sample_type': 'product_sample',
            'product_sample_type': 'budtender_sample',
            'retest': 0,
            'qty': '1',
            'uom': 'ea',
            'global_inventory_id': inventory_item.global_id
        }]
    }
    retail_transfers = track.create_transfer(transfer_data)
    track.transit_transfer(retail_transfers[0].global_id)

    # Initialize retailer traceability
    retailer_track = leaf.authorize(api_key=api_key, mme_code=retailer_mme_code)

    # Create an area at the retailer.
    retail_area_data = {
        'name': 'Salesfloor',
        'type': 'quarantine',
        'external_id': 'sales-room-1'
    }
    try:
        retailer_track.create_areas([retail_area_data])
    except APIError:
        pass
    retail_area = retailer_track.get_areas()[0]

    # Receive the transfer at the retailer. (Optional?)
    retailer_transfers = retailer_track.get_transfers()
    retailer_transfer = retailer_transfers[0]

    try:
        retailer_transfer = retailer_track.receive_transfer(
            retailer_transfer.global_id,
            area_id=retail_area.global_id
        )
    except APIError:
        pass

    # Get the inventory item at the retailer
    retail_inventories = retailer_track.get_inventory()
    retail_inventory = retail_inventories[0]

    # Create a sale with the '/sales' endpoint.
    # Requires the previous creation of an area, batch, and inventory item.
    sale_data = {
        'external_id': 'sale-1',
        'type': 'retail_recreational',
        'patient_medical_id': '',
        'caregiver_id': '',
        'sold_at': get_time_string(),
        'price_total': '50.00',
        'status': 'sale',
        'global_sold_by_user_id': user.global_id,
        'sale_items': [
            {
                'external_id': 'sale-item-1',
                'type': 'sale',
                'sold_at': get_time_string(),
                'qty': '1.00',
                'uom': 'ea',
                'unit_price': '25.00',
                'price_total': '50.00',
                'name': 'Old-Time Moonshine',
                'global_batch_id': retail_inventory.global_batch_id,
                'global_inventory_id': retail_inventory.global_id
            }
        ]
    }

    try:
        sales = retailer_track.create_sales([sale_data])
        sale = sales[0]
        print('Sale:', sale.global_id, 'Created:', sale.created_at)
    except APIError:
        pass

