// Cannlytics App
// Copyright (c) 2023 Cannlytics

// Authors:
//   Keegan Skeate <https://github.com/keeganskeate>
// Created: 2/18/2023
// Updated: 3/9/2023
// License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>
// Dart imports:

// Project imports:
import 'package:cannlytics_app/routing/app_router.dart';
import 'package:cannlytics_app/ui/account/licenses/add_license_screen.dart';
import 'package:cannlytics_app/ui/account/licenses/licenses_screen.dart';
import 'package:cannlytics_app/ui/account/organizations/organization_screen.dart';
import 'package:cannlytics_app/ui/account/organizations/organizations_screen.dart';
import 'package:cannlytics_app/ui/account/sign-in/sign_in_screen.dart';
import 'package:cannlytics_app/ui/account/sign-in/sign_in_text.dart';
import 'package:cannlytics_app/ui/account/user/account_screen.dart';
import 'package:cannlytics_app/ui/account/user/reset_password_screen.dart';
import 'package:cannlytics_app/ui/business/deliveries/deliveries_screen.dart';
import 'package:cannlytics_app/ui/business/deliveries/delivery_screen.dart';
import 'package:cannlytics_app/ui/business/employees/employee_screen.dart';
import 'package:cannlytics_app/ui/business/employees/employees_screen.dart';
import 'package:cannlytics_app/ui/business/facilities/facilities_screen.dart';
import 'package:cannlytics_app/ui/business/facilities/facility_screen.dart';
import 'package:cannlytics_app/ui/business/items/item_screen.dart';
import 'package:cannlytics_app/ui/business/items/items_screen.dart';
import 'package:cannlytics_app/ui/business/locations/location_screen.dart';
import 'package:cannlytics_app/ui/business/locations/locations_screen.dart';
import 'package:cannlytics_app/ui/business/packages/package_items_screen.dart';
import 'package:cannlytics_app/ui/business/packages/packages_screen.dart';
import 'package:cannlytics_app/ui/business/patients/patient_screen.dart';
import 'package:cannlytics_app/ui/business/patients/patients_screen.dart';
import 'package:cannlytics_app/ui/business/plants/plant_batch_screen.dart';
import 'package:cannlytics_app/ui/business/plants/plant_batches_screen.dart';
import 'package:cannlytics_app/ui/business/plants/plant_harvest_screen.dart';
import 'package:cannlytics_app/ui/business/plants/plant_harvests_screen.dart';
import 'package:cannlytics_app/ui/business/plants/plant_screen.dart';
import 'package:cannlytics_app/ui/business/plants/plants_screen.dart';
import 'package:cannlytics_app/ui/business/results/result_screen.dart';
import 'package:cannlytics_app/ui/business/results/results_screen.dart';
import 'package:cannlytics_app/ui/business/sales/receipt_screen.dart';
import 'package:cannlytics_app/ui/business/sales/receipts_screen.dart';
import 'package:cannlytics_app/ui/business/sales/transaction_screen.dart';
import 'package:cannlytics_app/ui/business/sales/transactions_screen.dart';
import 'package:cannlytics_app/ui/business/strains/strain_screen.dart';
import 'package:cannlytics_app/ui/business/strains/strains_screen.dart';
import 'package:cannlytics_app/ui/business/transfers/transfer_screen.dart';
import 'package:cannlytics_app/ui/business/transfers/transfers_screen.dart';
import 'package:cannlytics_app/ui/main/dashboard.dart';
import 'package:cannlytics_app/ui/layout/search_screen.dart';

// The main app routes.
class Routes {
  static List<AppRoute> mainRoutes = [
    // Sign in screen.
    AppRoute(
      path: '/sign-in',
      name: AppRoutes.signIn.name,
      builder: (context, state) => EmailPasswordSignInScreen(
        formType: SignInFormType.signIn,
      ),
    ),

    // User account screens.
    AppRoute(
      path: '/account',
      name: AppRoutes.account.name,
      builder: (context, state) => AccountScreen(),
      routes: [
        // Reset password screen.
        AppRoute(
          path: 'reset-password',
          name: AppRoutes.resetPassword.name,
          builder: (context, state) => ResetPasswordScreen(),
        ),
      ],
    ),

    // Organizations screen.
    AppRoute(
      path: '/organizations',
      name: AppRoutes.organizations.name,
      builder: (context, state) => OrganizationsScreen(),
      routes: [
        // Organization screen.
        AppRoute(
          path: 'add',
          name: AppRoutes.organization.name,
          builder: (context, state) => OrganizationScreen(),
        ),
      ],
    ),

    // License management screen.
    AppRoute(
      path: '/licenses',
      name: AppRoutes.licenses.name,
      builder: (context, state) => LicensesScreen(),
      routes: [
        // Delivery screen.
        AppRoute(
          path: 'add',
          name: AppRoutes.addLicense.name,
          builder: (context, state) => AddLicenseScreen(),
        ),
      ],
    ),

    // Dashboard screen.
    AppRoute(
      path: '/dashboard',
      name: AppRoutes.dashboard.name,
      builder: (context, state) => DashboardScreen(),
    ),

    // Search screen.
    AppRoute(
      path: '/search',
      name: AppRoutes.search.name,
      builder: (context, state) => SearchScreen(),
    ),

    /* Business screens */

    // Deliveries screens.
    AppRoute(
      path: '/deliveries',
      name: AppRoutes.deliveries.name,
      builder: (context, state) => DeliveriesScreen(),
      routes: [
        AppRoute(
          path: ':id',
          name: AppRoutes.delivery.name,
          builder: (context, state) {
            final id = state.params['id']!;
            return DeliveryScreen(jobId: id);
          },
        ),
      ],
    ),

    // Employees screens.
    AppRoute(
      path: '/employees',
      name: AppRoutes.employees.name,
      builder: (context, state) => EmployeesScreen(),
      routes: [
        AppRoute(
          path: ':id',
          name: AppRoutes.employee.name,
          builder: (context, state) {
            final id = state.params['id']!;
            return EmployeeScreen(jobId: id);
          },
        ),
      ],
    ),

    // Facilities screens.
    AppRoute(
      path: '/facilities',
      name: AppRoutes.facilities.name,
      builder: (context, state) => FacilitiesScreen(),
      routes: [
        AppRoute(
          path: ':id',
          name: AppRoutes.facility.name,
          builder: (context, state) {
            final id = state.params['id']!;
            return FacilityScreen(jobId: id);
          },
        ),
      ],
    ),

    // Locations screens.
    AppRoute(
      path: '/locations',
      name: AppRoutes.locations.name,
      builder: (context, state) => LocationsScreen(),
      routes: [
        AppRoute(
          path: ':id',
          name: AppRoutes.location.name,
          builder: (context, state) {
            final id = state.params['id']!;
            return LocationScreen(id: id);
          },
        ),
      ],
    ),

    // Patients screens.
    AppRoute(
      path: '/patients',
      name: AppRoutes.patients.name,
      builder: (context, state) => PatientsScreen(),
      routes: [
        AppRoute(
          path: ':id',
          name: AppRoutes.patient.name,
          builder: (context, state) {
            final id = state.params['id']!;
            return PatientScreen(jobId: id);
          },
        ),
      ],
    ),

    // Packages screens.
    AppRoute(
      path: '/packages',
      name: AppRoutes.packages.name,
      builder: (context, state) => PackagesScreen(),
      routes: [
        AppRoute(
          path: ':id',
          name: AppRoutes.package.name,
          builder: (context, state) {
            final id = state.params['id']!;
            return PackageScreen(jobId: id);
          },
        ),
      ],
    ),

    // Items screens.
    AppRoute(
      path: '/items',
      name: AppRoutes.items.name,
      builder: (context, state) => ItemsScreen(),
      routes: [
        AppRoute(
          path: ':id',
          name: AppRoutes.item.name,
          builder: (context, state) {
            final id = state.params['id']!;
            return ItemScreen(jobId: id);
          },
        ),
      ],
    ),

    // Plants screens.
    AppRoute(
      path: '/plants',
      name: AppRoutes.plants.name,
      builder: (context, state) => PlantsScreen(),
      routes: [
        AppRoute(
          path: ':id',
          name: AppRoutes.plant.name,
          builder: (context, state) {
            final id = state.params['id']!;
            return PlantScreen(jobId: id);
          },
        ),
      ],
    ),

    // Plant batches screens.
    AppRoute(
      path: '/batches',
      name: AppRoutes.plantBatches.name,
      builder: (context, state) => PlantBatchesScreen(),
      routes: [
        AppRoute(
          path: ':id',
          name: AppRoutes.plantBatch.name,
          builder: (context, state) {
            final id = state.params['id']!;
            return PlantBatchScreen(jobId: id);
          },
        ),
      ],
    ),

    // Harvests screens.
    AppRoute(
      path: '/harvests',
      name: AppRoutes.plantHarvests.name,
      builder: (context, state) => PlantHarvestsScreen(),
      routes: [
        AppRoute(
          path: ':id',
          name: AppRoutes.plantHarvest.name,
          builder: (context, state) {
            final id = state.params['id']!;
            return PlantHarvestScreen(jobId: id);
          },
        ),
      ],
    ),

    // Lab results screens.
    AppRoute(
      path: '/results',
      name: AppRoutes.results.name,
      builder: (context, state) => ResultsScreen(),
      routes: [
        AppRoute(
          path: ':id',
          name: AppRoutes.result.name,
          builder: (context, state) {
            final id = state.params['id']!;
            return ResultScreen(jobId: id);
          },
        ),
      ],
    ),

    // Sales receipts
    AppRoute(
      path: '/receipts',
      name: AppRoutes.receipts.name,
      builder: (context, state) => ReceiptsScreen(),
      routes: [
        AppRoute(
          path: ':id',
          name: AppRoutes.receipt.name,
          builder: (context, state) {
            final id = state.params['id']!;
            return ReceiptScreen(jobId: id);
          },
        ),
      ],
    ),

    // Sales transactions
    AppRoute(
      path: '/transactions',
      name: AppRoutes.transactions.name,
      builder: (context, state) => TransactionsScreen(),
      routes: [
        AppRoute(
          path: ':id',
          name: AppRoutes.transaction.name,
          builder: (context, state) {
            final id = state.params['id']!;
            return TransactionScreen(jobId: id);
          },
        ),
      ],
    ),

    // Strains screens.
    AppRoute(
      path: '/strains',
      name: AppRoutes.strains.name,
      builder: (context, state) => StrainsScreen(),
      routes: [
        AppRoute(
          path: ':id',
          name: AppRoutes.strain.name,
          builder: (context, state) {
            final id = state.params['id']!;
            return StrainScreen(jobId: id);
          },
        ),
      ],
    ),

    // Transfers screens.
    AppRoute(
      path: '/transfers',
      name: AppRoutes.transfers.name,
      builder: (context, state) => TransfersScreen(),
      routes: [
        AppRoute(
          path: ':id',
          name: AppRoutes.transfer.name,
          builder: (context, state) {
            final id = state.params['id']!;
            return TransferScreen(jobId: id);
          },
        ),
      ],
    ),

    // TODO: Transfer templates screen.

    /* Consumer screens */

    // TODO: homegrow

    // TODO: products

    // TODO: retailers

    // TODO: brands

    // TODO: spending
  ];
}

// Routes.
enum AppRoutes {
  /* General pages */

  // Account management.
  account,
  dashboard,
  onboarding,
  resetPassword,
  signIn,

  // Organization pages.
  organizations,
  organization,

  // Utility pages.
  search,

  /* Business screens */

  // Licenses
  addLicense,
  licenses,

  // Deliveries
  deliveries,
  delivery,
  addDelivery,
  editDelivery,
  vehicles,
  vehicle,
  drivers,
  driver,

  // Employees
  employees,
  employee,
  addEmployee,
  editEmployee,

  // Facilities
  facilities,
  facility,
  addFacility,

  // Locations
  locations,
  location,
  addLocation,
  editLocation,

  // Patients
  patients,
  patient,
  addPatient,
  editPatient,

  // Plants
  plants,
  plant,
  addPlant,
  editPlant,

  // Plant batches
  plantBatches,
  plantBatch,

  // Harvests
  plantHarvests,
  plantHarvest,

  // Results
  results,
  result,
  addResult,
  editResult,

  // Sales
  receipts,
  receipt,
  addReceipt,
  editReceipt,
  transactions,
  transaction,
  addTransaction,
  editTransaction,

  // Strains
  strains,
  strain,
  addStrain,
  editStrain,

  // Transfers
  transfers,
  transfer,
  addTransfer,
  editTransfer,

  // Packages
  packages,
  package,
  addPackage,
  editPackage,

  // Items
  items,
  item,
  addItem,
  editItem,

  /* Consumer screens */

  // Homegrow
  garden,
  gardenPlant,
  addGardenPlant,
  editGardenPlant,

  // Products
  products,
  product,
  addProduct,
  editProduct,

  // Retailers and brands (licensees).
  retailers,
  retailer,
  brands,
  brand,

  // Spending
  spending,
  spend,
  addSpend,
  editSpend,
}

/// Data for each screen.
class ScreenData {
  const ScreenData({
    required this.imageName,
    required this.title,
    required this.description,
    required this.route,
  });
  final String imageName;
  final String title;
  final String description;
  final String route;

  // Business screens.
  static const businessScreens = [
    ScreenData(
      imageName: 'assets/images/icons/spending.png',
      title: 'Deliveries',
      description: 'Manage your deliveries to consumers.',
      route: 'deliveries',
    ),
    ScreenData(
      imageName: 'assets/images/icons/employees.png',
      title: 'Employees',
      description: 'Manage your employees and staff.',
      route: 'employees',
    ),
    ScreenData(
      imageName: 'assets/images/icons/facilities.png',
      title: 'Facilities',
      description: 'Manage your facilities and locations.',
      route: 'facilities',
    ),
    ScreenData(
      imageName: 'assets/images/icons/packages.png',
      title: 'Packages',
      description: 'Manage your packages and their items.',
      route: 'packages',
    ),
    ScreenData(
      imageName: 'assets/images/icons/item.png',
      title: 'Items',
      description: 'Manage your items.',
      route: 'items',
    ),
    ScreenData(
      imageName: 'assets/images/icons/locations.png',
      title: 'Locations',
      description: 'Manage your locations and addresses.',
      route: 'locations',
    ),
    ScreenData(
      imageName: 'assets/images/icons/patients.png',
      title: 'Patients',
      description: 'Manage your patients and customers.',
      route: 'patients',
    ),
    ScreenData(
      imageName: 'assets/images/icons/plant.png',
      title: 'Plants',
      description: 'Manage your plants and cultivation processes.',
      route: 'plants',
    ),
    ScreenData(
      imageName: 'assets/images/icons/chemistry.png',
      title: 'Results',
      description: 'Manage your test results and analyses.',
      route: 'results',
    ),
    ScreenData(
      imageName: 'assets/images/icons/sales.png',
      title: 'Sales',
      description: 'Manage your sale receipts, transactions, and revenue.',
      route: 'receipts',
    ),
    ScreenData(
      imageName: 'assets/images/icons/strains.png',
      title: 'Strains',
      description: 'Manage your strains and variety catalog.',
      route: 'strains',
    ),
    ScreenData(
      imageName: 'assets/images/icons/transfers.png',
      title: 'Transfers',
      description: 'Manage your transfers and shipments.',
      route: 'transfers',
    ),
  ];

  // Consumer screens.
  static const consumerScreens = [
    ScreenData(
      imageName: 'assets/images/icons/indoor.png',
      title: 'Homegrow',
      description: 'Manage your home cultivation.',
      route: 'garden',
    ),
    ScreenData(
      imageName: 'assets/images/icons/product.png',
      title: 'Products',
      description: 'Manage your cannabis products.',
      route: 'products',
    ),
    ScreenData(
      imageName: 'assets/images/icons/chemistry.png',
      title: 'Results',
      description: 'Explore lab results.',
      route: 'results',
    ),
    ScreenData(
      imageName: 'assets/images/icons/shop.png',
      title: 'Retailers',
      description: 'Find cannabis retailers.',
      route: 'retailers',
    ),
    ScreenData(
      imageName: 'assets/images/icons/award.png',
      title: 'Brands',
      description: 'Explore cannabis brands and their products.',
      route: 'brands',
    ),
    ScreenData(
      imageName: 'assets/images/icons/strains.png',
      title: 'Strains',
      description: 'Explore cannabis varieties.',
      route: 'strains',
    ),
    ScreenData(
      imageName: 'assets/images/icons/spending.png',
      title: 'Spending',
      description: 'Manage your cannabis spending.',
      route: 'spend',
    ),
  ];
}
