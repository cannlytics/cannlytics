// Cannlytics Data
// Copyright (c) 2023 Cannlytics

// Authors:
//   Keegan Skeate <https://github.com/keeganskeate>
// Created: 5/16/2023
// Updated: 5/16/2023
// License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

import 'dart:async';
import 'package:flutter/material.dart';
import 'package:google_maps_flutter/google_maps_flutter.dart';

/// Licensee map.
class LicenseeMap extends StatefulWidget {
  const LicenseeMap({super.key});

  @override
  State<LicenseeMap> createState() => LicenseeMapState();
}

/// Licensee map state.
class LicenseeMapState extends State<LicenseeMap> {
  final Completer<GoogleMapController> _controller =
      Completer<GoogleMapController>();

  // TODO: Get the licensee's location.
  // _locationServices=Provider.of<LocationServices>(context);
  Set<Marker> allMapMarkers = {
    Marker(
      markerId: MarkerId('Licensee'),
      draggable: false,
      position: LatLng(37.43296265331129, -122.08832357078792),
      // onTap: () {},
    ),
  };

  // Camera position.
  static const CameraPosition _cameraPosition = CameraPosition(
    target: LatLng(37.42796133580664, -122.085749655962),
    zoom: 14.4746,
  );

  @override
  Widget build(BuildContext context) {
    return SafeArea(
      child: Stack(
        children: [
          GoogleMap(
            compassEnabled: false,
            zoomControlsEnabled: false,
            markers: allMapMarkers,
            mapType: MapType.normal,
            initialCameraPosition: _cameraPosition,
            onMapCreated: (GoogleMapController controller) {
              _controller.complete(controller);
            },
          ),
        ],
      ),
    );
  }
}
