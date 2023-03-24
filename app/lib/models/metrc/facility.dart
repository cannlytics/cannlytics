// Cannlytics App
// Copyright (c) 2023 Cannlytics

// Authors:
//   Keegan Skeate <https://github.com/keeganskeate>
// Created: 2/20/2023
// Updated: 3/23/2023
// License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

// Project imports:
import 'package:cannlytics_app/utils/string_utils.dart';

typedef FacilityId = String;

/// Model representing an organization.
class Facility {
  // Initialization.
  const Facility({
    required this.id,
    this.alias = '',
    this.credentialedDate = '',
    this.displayName = '',
    this.facilityType = const {},
    this.hireDate = '',
    this.isManager = false,
    this.isOwner = false,
    this.licenseEndDate = '',
    this.licenseNumber = '',
    this.licenseStartDate = '',
    this.licenseType = '',
    this.name = '',
    this.occupations = const [],
    this.supportActivationDate = '',
    this.supportExpirationDate = '',
    this.supportLastPaidDate = '',
    this.permissions = const Permissions(),
  });

  // Properties.
  final FacilityId id;
  final String alias;
  final String credentialedDate;
  final String displayName;
  final String hireDate;
  final Map facilityType;
  final bool isManager;
  final bool isOwner;
  final String licenseEndDate;
  final String licenseNumber;
  final String licenseStartDate;
  final String licenseType;
  final String name;
  final List<dynamic> occupations;
  final String supportActivationDate;
  final String supportExpirationDate;
  final String supportLastPaidDate;
  final Permissions permissions;

  // Create model.
  factory Facility.fromMap(Map<dynamic, dynamic> data) {
    return Facility(
      id: Format.slugify(data['display_name']),
      alias: data['alias'] ?? '',
      credentialedDate: data['credentialed_date'] ?? '',
      displayName: data['display_name'] ?? '',
      facilityType: data['facility_type'] ?? {},
      hireDate: data['hire_date'] ?? '',
      isManager: data['is_manager'] ?? false,
      isOwner: data['is_owner'] ?? false,
      licenseEndDate: data['license']['end_date'] ?? '',
      licenseNumber: data['license']['number'] ?? '',
      licenseStartDate: data['license']['start_date'] ?? '',
      licenseType: data['license']['type'] ?? '',
      name: data['name'] ?? '',
      // occupations: List<dynamic>.from(data['occupations'] ?? const []),
      supportActivationDate: data['support_activation_date'] ?? '',
      supportExpirationDate: data['support_expiration_date'] ?? '',
      supportLastPaidDate: data['support_last_paid_date'] ?? '',
      // permissions: Permissions.fromMap(data['facility_type']),
    );
  }

  // Create JSON.
  Map<String, dynamic> toMap() {
    return <String, dynamic>{
      'id': id,
      'alias': alias,
      'credentialed_date': credentialedDate,
      'display_name': displayName,
      'facility_type': facilityType,
      'hire_date': hireDate,
      'is_manager': isManager,
      'is_owner': isOwner,
      'license': {
        'end_date': licenseEndDate,
        'number': licenseNumber,
        'start_date': licenseStartDate,
        'type': licenseType,
      },
      'name': name,
      'occupations': occupations,
      'support_activation_date': supportActivationDate,
      'support_expiration_date': supportExpirationDate,
      'support_last_paid_date': supportLastPaidDate,
    };
  }
}

/// Metrc permissions.
class Permissions {
  // Initialization.
  const Permissions({
    this.isMedical = false,
    this.isRetail = false,
    this.isHemp = false,
    this.restrictHarvestPlantRestoreTimeHours,
    this.totalMemberPatientsAllowed,
    this.canGrowPlants = false,
    this.canCreateOpeningBalancePlantBatches = false,
    this.canClonePlantBatches = false,
    this.canTagPlantBatches = false,
    this.canAssignLocationsToPlantBatches = false,
    this.plantsRequirePatientAffiliation = false,
    this.plantBatchesCanContainMotherPlants = false,
    this.canUpdatePlantStrains = false,
    this.canTrackVegetativePlants = false,
    this.canCreateImmaturePlantPackagesFromPlants = false,
    this.canPackageVegetativePlants = false,
    this.canPackageWaste = false,
    this.canReportHarvestSchedules = false,
    this.canSubmitHarvestsForTesting = false,
    this.canRequireHarvestSampleLabTestBatches = false,
    this.canReportStrainProperties = false,
    this.canCreateOpeningBalancePackages = false,
    this.canCreateDerivedPackages = false,
    this.canAssignLocationsToPackages = false,
    this.canUpdateLocationsOnPackages = false,
    this.packagesRequirePatientAffiliation = false,
    this.canCreateTradeSamplePackages = false,
    this.canDonatePackages = false,
    this.canSubmitPackagesForTesting = false,
    this.canCreateProcessValidationPackages = false,
    this.canRequirePackageSampleLabTestBatches = false,
    this.canRequestProductRemediation = false,
    this.canRemediatePackagesWithFailedLabResults = false,
    this.canInfuseProducts = false,
    this.canRecordProcessingJobs = false,
    this.canRecordProductForDestruction = false,
    this.canDestroyProduct = false,
    this.canTestPackages = false,
    this.testsRequireLabSample = false,
    this.canTransferFromExternalFacilities = false,
    this.canSellToConsumers = false,
    this.canSellToPatients = false,
    this.canSellToExternalPatients = false,
    this.canSellToCaregivers = false,
    this.canTakePlantBatchesOnTrip = false,
    this.canTakePlantsOnTrip = false,
    this.canTakeHarvestsOnTrip = false,
    this.canTakePackagesOnTrip = false,
    this.canSellFromPackagesOnTrip = false,
    this.advancedSales = false,
    this.salesRequirePatientNumber = false,
    this.salesRequireExternalPatientNumber = false,
    this.salesRequireExternalPatientIdentificationMethod = false,
    this.salesRequireCaregiverNumber = false,
    this.salesRequireCaregiverPatientNumber = false,
    this.canDeliverSalesToConsumers = false,
    this.salesDeliveryAllowPlannedRoute = false,
    this.salesDeliveryAllowAddress = false,
    this.salesDeliveryAllowCity = false,
    this.salesDeliveryAllowState = false,
    this.salesDeliveryAllowCounty = false,
    this.salesDeliveryAllowZip = false,
    this.salesDeliveryRequireConsumerId = false,
    this.canDeliverSalesToPatients = false,
    this.salesDeliveryRequirePatientNumber = false,
    this.salesDeliveryRequireRecipientName = false,
    this.isSalesDeliveryHub = false,
    this.canHaveMemberPatients = false,
    this.canReportPatientCheckIns = false,
    this.canSpecifyPatientSalesLimitExemption = false,
    this.canReportPatientsAdverseResponses = false,
    this.retailerDelivery = false,
    this.retailerDeliveryAllowTradeSamples = false,
    this.retailerDeliveryAllowDonations = false,
    this.retailerDeliveryRequirePrice = false,
    this.retailerDeliveryAllowPartialPackages = false,
    this.canCreatePartialPackages = false,
    this.canAdjustSourcePackagesWithPartials = false,
  });

  final bool isMedical;
  final bool isRetail;
  final bool isHemp;
  final int? restrictHarvestPlantRestoreTimeHours;
  final int? totalMemberPatientsAllowed;
  final bool canGrowPlants;
  final bool canCreateOpeningBalancePlantBatches;
  final bool canClonePlantBatches;
  final bool canTagPlantBatches;
  final bool canAssignLocationsToPlantBatches;
  final bool plantsRequirePatientAffiliation;
  final bool plantBatchesCanContainMotherPlants;
  final bool canUpdatePlantStrains;
  final bool canTrackVegetativePlants;
  final bool canCreateImmaturePlantPackagesFromPlants;
  final bool canPackageVegetativePlants;
  final bool canPackageWaste;
  final bool canReportHarvestSchedules;
  final bool canSubmitHarvestsForTesting;
  final bool canRequireHarvestSampleLabTestBatches;
  final bool canReportStrainProperties;
  final bool canCreateOpeningBalancePackages;
  final bool canCreateDerivedPackages;
  final bool canAssignLocationsToPackages;
  final bool canUpdateLocationsOnPackages;
  final bool packagesRequirePatientAffiliation;
  final bool canCreateTradeSamplePackages;
  final bool canDonatePackages;
  final bool canSubmitPackagesForTesting;
  final bool canCreateProcessValidationPackages;
  final bool canRequirePackageSampleLabTestBatches;
  final bool canRequestProductRemediation;
  final bool canRemediatePackagesWithFailedLabResults;
  final bool canInfuseProducts;
  final bool canRecordProcessingJobs;
  final bool canRecordProductForDestruction;
  final bool canDestroyProduct;
  final bool canTestPackages;
  final bool testsRequireLabSample;
  final bool canTransferFromExternalFacilities;
  final bool canSellToConsumers;
  final bool canSellToPatients;
  final bool canSellToExternalPatients;
  final bool canSellToCaregivers;
  final bool canTakePlantBatchesOnTrip;
  final bool canTakePlantsOnTrip;
  final bool canTakeHarvestsOnTrip;
  final bool canTakePackagesOnTrip;
  final bool canSellFromPackagesOnTrip;
  final bool advancedSales;
  final bool salesRequirePatientNumber;
  final bool salesRequireExternalPatientNumber;
  final bool salesRequireExternalPatientIdentificationMethod;
  final bool salesRequireCaregiverNumber;
  final bool salesRequireCaregiverPatientNumber;
  final bool canDeliverSalesToConsumers;
  final bool salesDeliveryAllowPlannedRoute;
  final bool salesDeliveryAllowAddress;
  final bool salesDeliveryAllowCity;
  final bool salesDeliveryAllowState;
  final bool salesDeliveryAllowCounty;
  final bool salesDeliveryAllowZip;
  final bool salesDeliveryRequireConsumerId;
  final bool canDeliverSalesToPatients;
  final bool salesDeliveryRequirePatientNumber;
  final bool salesDeliveryRequireRecipientName;
  final bool isSalesDeliveryHub;
  final bool canHaveMemberPatients;
  final bool canReportPatientCheckIns;
  final bool canSpecifyPatientSalesLimitExemption;
  final bool canReportPatientsAdverseResponses;
  final bool retailerDelivery;
  final bool retailerDeliveryAllowTradeSamples;
  final bool retailerDeliveryAllowDonations;
  final bool retailerDeliveryRequirePrice;
  final bool retailerDeliveryAllowPartialPackages;
  final bool canCreatePartialPackages;
  final bool canAdjustSourcePackagesWithPartials;

  // Create model.
  factory Permissions.fromMap(Map<dynamic, dynamic> data) {
    return Permissions(
      // General
      isMedical: data['is_medical'],
      isRetail: data['is_retail'],
      isHemp: data['is_hemp'] ?? false,

      // Patients
      totalMemberPatientsAllowed: data['total_member_patients_allowed'],

      // Plants
      canGrowPlants: data['can_grow_plants'] ?? false,
      plantsRequirePatientAffiliation:
          data['plants_require_patient_affiliation'] ?? false,
      canUpdatePlantStrains: data['can_update_plant_strains'] ?? false,
      canTrackVegetativePlants: data['can_track_vegetative_plants'] ?? false,
      canCreateImmaturePlantPackagesFromPlants:
          data['can_create_immature_plant_packages_from_plants'] ?? false,
      canPackageVegetativePlants:
          data['can_package_vegetative_plants'] ?? false,

      // Plant batches
      canCreateOpeningBalancePlantBatches:
          data['can_create_opening_balance_plant_batches'] ?? false,
      canClonePlantBatches: data['can_clone_plant_batches'] ?? false,
      canTagPlantBatches: data['can_tag_plant_batches'] ?? false,
      canAssignLocationsToPlantBatches:
          data['can_assign_locations_to_plant_batches'] ?? false,

      plantBatchesCanContainMotherPlants:
          data['plant_batches_can_contain_mother_plants'] ?? false,

      // Harvests
      restrictHarvestPlantRestoreTimeHours:
          data['restrict_harvest_plant_restore_time_hours'],
      canReportHarvestSchedules: data['can_report_harvest_schedules'] ?? false,
      canSubmitHarvestsForTesting:
          data['can_submit_harvests_for_testing'] ?? false,
      canRequireHarvestSampleLabTestBatches:
          data['can_require_harvest_sample_lab_test_batches'] ?? false,

      // Packages
      canPackageWaste: data['can_package_waste'] ?? false,
      canCreateOpeningBalancePackages:
          data['can_create_opening_balance_packages'] ?? false,
      canCreateDerivedPackages: data['can_create_derived_packages'] ?? false,
      canAssignLocationsToPackages:
          data['can_assign_locations_to_packages'] ?? false,
      canUpdateLocationsOnPackages:
          data['can_update_locations_on_packages'] ?? false,
      packagesRequirePatientAffiliation:
          data['packages_require_patient_affiliation'] ?? false,
      canCreateTradeSamplePackages:
          data['can_create_trade_sample_packages'] ?? false,
      canDonatePackages: data['can_donate_packages'] ?? false,
      canSubmitPackagesForTesting:
          data['can_submit_packages_for_testing'] ?? false,
      canCreateProcessValidationPackages:
          data['can_create_process_validation_packages'] ?? false,

      // Strains
      canReportStrainProperties: data['can_report_strain_properties'] ?? false,

      // Lab testing
      canTestPackages: data['can_test_packages'] ?? false,
      testsRequireLabSample: data['tests_require_lab_sample'] ?? false,
      canRequirePackageSampleLabTestBatches:
          data['can_require_package_sample_lab_test_batches'] ?? false,
      canRequestProductRemediation:
          data['can_request_product_remediation'] ?? false,
      canRemediatePackagesWithFailedLabResults:
          data['can_remediate_packages_with_failed_lab_results'] ?? false,

      // Processing
      canInfuseProducts: data['can_infuse_products'] ?? false,
      canRecordProcessingJobs: data['can_record_processing_jobs'] ?? false,

      // Waste
      canRecordProductForDestruction:
          data['can_record_product_for_destruction'] ?? false,
      canDestroyProduct: data['can_destroy_product'] ?? false,

      // Transfers
      canTransferFromExternalFacilities:
          data['can_transfer_from_external_facilities'] ?? false,
      canTakePlantBatchesOnTrip:
          data['can_take_plant_batches_on_trip'] ?? false,
      canTakePlantsOnTrip: data['can_take_plants_on_trip'] ?? false,
      canTakeHarvestsOnTrip: data['can_take_harvests_on_trip'] ?? false,
      canTakePackagesOnTrip: data['can_take_packages_on_trip'] ?? false,
      canSellFromPackagesOnTrip:
          data['can_sell_from_packages_on_trip'] ?? false,

      // Sales
      advancedSales: data['advanced_sales'] ?? false,
      canSellToConsumers: data['can_sell_to_consumers'] ?? false,
      canSellToPatients: data['can_sell_to_patients'] ?? false,
      canSellToExternalPatients: data['can_sell_to_external_patients'] ?? false,
      canSellToCaregivers: data['can_sell_to_caregivers'] ?? false,
      salesRequirePatientNumber: data['sales_require_patient_number'] ?? false,
      salesRequireExternalPatientNumber:
          data['sales_require_external_patient_number'] ?? false,
      salesRequireExternalPatientIdentificationMethod:
          data['sales_require_external_patient_identification_method'] ?? false,
      salesRequireCaregiverNumber:
          data['sales_require_caregiver_number'] ?? false,
      salesRequireCaregiverPatientNumber:
          data['sales_require_caregiver_patient_number'] ?? false,

      // Deliveries
      canDeliverSalesToConsumers:
          data['can_deliver_sales_to_consumers'] ?? false,
      salesDeliveryAllowPlannedRoute:
          data['sales_delivery_allow_planned_route'] ?? false,
      salesDeliveryAllowAddress: data['sales_delivery_allow_address'] ?? false,
      salesDeliveryAllowCity: data['sales_delivery_allow_city'] ?? false,
      salesDeliveryAllowState: data['sales_delivery_allow_state'] ?? false,
      salesDeliveryAllowCounty: data['sales_delivery_allow_county'] ?? false,
      salesDeliveryAllowZip: data['sales_delivery_allow_zip'] ?? false,
      salesDeliveryRequireConsumerId:
          data['sales_delivery_require_consumer_id'] ?? false,
      canDeliverSalesToPatients: data['can_deliver_sales_to_patients'] ?? false,
      salesDeliveryRequirePatientNumber:
          data['sales_delivery_require_patient_number'] ?? false,
      salesDeliveryRequireRecipientName:
          data['sales_delivery_require_recipient_name'] ?? false,
    );
  }
}
