// Cannlytics Data
// Copyright (c) 2023 Cannlytics

// Authors:
//   Keegan Skeate <https://github.com/keeganskeate>
// Created: 5/18/2023
// Updated: 5/18/2023
// License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

// Dart imports:
import 'dart:html' as html if (dart.library.io) 'dart:io';
import 'dart:ui' as ui;

// Flutter imports:
import 'package:flutter/cupertino.dart';

// Package imports:
import 'package:google_maps/google_maps.dart';

/// Web map.
class WebMap extends StatefulWidget {
  WebMap({
    Key? key,
    required this.latitude,
    required this.longitude,
    required this.title,
  }) : super(key: key);

  // Properties.
  final double latitude;
  final double longitude;
  final String title;

  @override
  State<WebMap> createState() => WebMapState();
}

/// Web map state.
class WebMapState extends State<WebMap> {
  @override
  Widget build(BuildContext context) {
    return getMap(
      widget.latitude,
      widget.longitude,
      widget.title,
    );
  }
}

/// Map initialization.
Widget getMap(double latitude, double longitude, String title) {
  // Properties.
  String htmlId = 'licensee-map';

  // ignore: undefined_prefixed_name
  ui.platformViewRegistry.registerViewFactory(htmlId, (int viewId) {
    // Map options.
    final mapOptions = new MapOptions()
      ..zoom = 16
      ..center = new LatLng(latitude, longitude);

    // Map style.
    final elem = html.DivElement()
      ..id = htmlId
      ..style.width = '100%'
      ..style.height = '100%'
      ..style.border = 'none';

    // Create map.
    final map = GMap(elem, mapOptions);

    // Add map marker.
    Marker(MarkerOptions()
      ..position = new LatLng(latitude, longitude)
      ..map = map
      ..title = title);

    return elem;
  });

  return HtmlElementView(viewType: htmlId);
}
