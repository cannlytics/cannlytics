// Cannlytics App
// Copyright (c) 2023 Cannlytics

// Authors:
//   Keegan Skeate <https://github.com/keeganskeate>
// Created: 2/18/2023
// Updated: 2/22/2023
// License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

// Routes.
enum AppRoutes {
  /* General pages */

  // Account management.
  account,
  dashboard,
  onboarding,
  resetPassword,
  signIn,

  // Utility pages.
  search,

  /* Business screens */

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
