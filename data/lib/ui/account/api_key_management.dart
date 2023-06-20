// Cannlytics Data
// Copyright (c) 2023 Cannlytics

// Authors:
//   Keegan Skeate <https://github.com/keeganskeate>
// Created: 5/4/2023
// Updated: 6/19/2023
// License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

// Flutter imports:
import 'package:flutter/material.dart';

// Package imports:
import 'package:flutter_riverpod/flutter_riverpod.dart';

// Project imports:
import 'package:cannlytics_data/common/cards/wide_card.dart';

/// API key management.
class APIKeyManagement extends ConsumerWidget {
  const APIKeyManagement({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    // Dynamic screen width.
    // final screenWidth = MediaQuery.of(context).size.width;

    // Render the widget.
    return WideCard(
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              // Title.
              Text(
                'API Keys',
                style: Theme.of(context).textTheme.titleLarge,
              ),
              SizedBox(height: 8),

              // FIXME: Table of API keys.
              // ApiKeysTable(),
            ],
          ),
        ],
      ),
    );
  }
}

/// API keys table.
class ApiKeysTable extends StatelessWidget {
  final GlobalKey<FormState> _formKey = GlobalKey<FormState>();
  final TextEditingController _keyNameController = TextEditingController();
  final TextEditingController _expirationController = TextEditingController();
  final TextEditingController _permissionsController = TextEditingController();

  @override
  Widget build(BuildContext context) {
    // final apiKeyService = Provider.of<APIKeyService>(context, listen: false);

    return Container(
      width: 504,
      height: 620,
      child: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          children: [
            Form(
              key: _formKey,
              child: Column(
                children: [
                  TextFormField(
                    controller: _keyNameController,
                    decoration: InputDecoration(labelText: 'Key name'),
                  ),
                  TextFormField(
                    controller: _expirationController,
                    decoration: InputDecoration(labelText: 'Expiration'),
                  ),
                  TextFormField(
                    controller: _permissionsController,
                    decoration: InputDecoration(labelText: 'Permissions'),
                  ),
                  ElevatedButton(
                    onPressed: () async {
                      // Create the API key
                      // await apiKeyService.createAPIKey();
                      // Clear the form
                      // _formKey.currentState.reset();
                    },
                    child: Text('Create key'),
                  ),
                ],
              ),
            ),
            Expanded(
              child: FutureBuilder<List>(
                // future: apiKeyService.getAPIKeys(),
                builder: (context, snapshot) {
                  if (snapshot.connectionState == ConnectionState.waiting) {
                    return CircularProgressIndicator();
                  } else if (snapshot.hasError) {
                    return Text('Error: ${snapshot.error}');
                  } else {
                    return ListView.builder(
                      itemCount: snapshot.data?.length,
                      itemBuilder: (context, index) {
                        return ListTile(
                          title: Text(snapshot.data?[index]['name']),
                          subtitle: Text(snapshot.data?[index]['permissions']),
                          trailing: IconButton(
                            icon: Icon(Icons.delete),
                            onPressed: () {
                              // apiKeyService.deleteAPIKey();
                            },
                          ),
                        );
                      },
                    );
                  }
                },
              ),
            ),
          ],
        ),
      ),
    );
  }
}

/// API key dialog?
// class ApiKeyPage extends StatelessWidget {
//   final GlobalKey<FormState> _formKey = GlobalKey<FormState>();
//   final TextEditingController _keyNameController = TextEditingController();
//   final TextEditingController _createdAtController = TextEditingController();
//   final TextEditingController _expirationController = TextEditingController();
//   final TextEditingController _permissionsController = TextEditingController();

//   @override
//   Widget build(BuildContext context) {
//     final apiKeyService = Provider.of<APIKeyService>(context, listen: false);

//     return Scaffold(
//       appBar: AppBar(
//         title: Text('API Key'),
//       ),
//       body: Padding(
//         padding: const EdgeInsets.all(16.0),
//         child: Column(
//           children: [
//             Form(
//               key: _formKey,
//               child: Column(
//                 children: [
//                   TextFormField(
//                     controller: _keyNameController,
//                     decoration: InputDecoration(labelText: 'Key name'),
//                     enabled: false,
//                   ),
//                   TextFormField(
//                     controller: _createdAtController,
//                     decoration: InputDecoration(labelText: 'Created At'),
//                     enabled: false,
//                   ),
//                   TextFormField(
//                     controller: _expirationController,
//                     decoration: InputDecoration(labelText: 'Expiration'),
//                     enabled: false,
//                   ),
//                   TextFormField(
//                     controller: _permissionsController,
//                     decoration: InputDecoration(labelText: 'Permissions'),
//                     enabled: false,
//                   ),
//                   ElevatedButton(
//                     onPressed: () async {
//                       // Delete the API key
//                       await apiKeyService.deleteAPIKey();
//                       // Clear the form
//                       _formKey.currentState.reset();
//                     },
//                     child: Text('Delete key'),
//                   ),
//                 ],
//               ),
//             ),
//           ],
//         ),
//       ),
//     );
//   }
// }

/// New API key dialog.

