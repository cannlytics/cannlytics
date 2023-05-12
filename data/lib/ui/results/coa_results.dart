import 'package:cannlytics_data/ui/results/coa_doc_service.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';

/// COA results page.
class CoAResultsPage extends StatefulWidget {
  @override
  _CoAResultsPageState createState() => _CoAResultsPageState();
}

class _CoAResultsPageState extends State<CoAResultsPage> {
  List<CoAResult> results = [
    // Your initial list of CoA results
  ];

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: ListView.builder(
        itemCount: results.length,
        itemBuilder: (context, index) {
          return Card(
            child: ListTile(
              leading: Image.network("your_image_url"),
              title: Text(results[index].productName),
              subtitle: Text(
                  'Producer: ${results[index].producer}\nDate Tested: ${results[index].dateTested}'),
              trailing: IconButton(
                icon: Icon(Icons.delete),
                onPressed: () {
                  setState(() {
                    results.removeAt(index);
                  });
                },
              ),
            ),
          );
        },
      ),
    );
  }
}

/// COA data page.
class CoADataPage extends StatefulWidget {
  @override
  _CoADataPageState createState() => _CoADataPageState();
}

class _CoADataPageState extends State<CoADataPage> {
  // Your list of results would be defined here

  Future<void> postCoAData(Map<String, dynamic> data) async {
    final response = await http.post(
      Uri.parse('https://cannlytics/api/data/coas'),
      headers: <String, String>{
        'Content-Type': 'application/json; charset=UTF-8',
      },
      body: jsonEncode(data),
    );

    if (response.statusCode == 200) {
      // If the server returns a 200 OK response, parse the JSON.
      Map<String, dynamic> responseData = jsonDecode(response.body);
      if (responseData['success']) {
        setState(() {
          // Your renderCoAResults function would be called here
          // renderCoAResults(responseData['data']);
        });
      } else {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: const Text(
              'An error occurred when parsing the CoA. Please try again later or email support.',
            ),
            backgroundColor: Colors.red,
          ),
        );
      }
    } else {
      // If the server returns a response with a status code other than 200,
      // throw an exception.
      throw Exception('Failed to load API data');
    }
  }

  @override
  Widget build(BuildContext context) {
    return Container(); // Build your widget tree here
  }
}

/// Sample image.
class SampleImage extends StatelessWidget {
  final Map<String, dynamic> sample;

  SampleImage({required this.sample});

  @override
  Widget build(BuildContext context) {
    final defaultImage =
        'https://firebasestorage.googleapis.com/v0/b/cannlytics.appspot.com/o/public%2Fimages%2Fbackgrounds%2Fmisc%2Fsample-placeholder.png?alt=media&token=e8b96368-5d80-49ec-bbd0-3d21654b677f';

    String imageUrl;
    if (sample['images'] == null) {
      if (sample['image_data'] != null) {
        imageUrl = sample['image_data'];
      } else if (sample['image_url'] != null) {
        imageUrl = sample['image_url'];
      } else if (sample['lab_image_url'] != null) {
        imageUrl = sample['lab_image_url'];
      } else {
        imageUrl = defaultImage;
      }
    } else {
      try {
        if (sample['images'].length > 0) {
          imageUrl = sample['images'][0]['url'];
        } else {
          imageUrl = defaultImage;
        }
      } catch (error) {
        imageUrl = defaultImage;
      }
    }

    return Image.network(imageUrl);
  }
}

/// Sample details.
class SampleDetails extends StatelessWidget {
  final Map<String, dynamic> sample;

  SampleDetails({required this.sample});

  @override
  Widget build(BuildContext context) {
    // Here we assume that `sample` has been serialized into a Map
    return Column(
      children: <Widget>[
        SampleImage(sample: sample),
        Text(sample['product_name'] ?? ''),
        Text(sample['product_type'] ?? ''),
        Text(sample['producer'] ?? ''),
        Text(sample['date_tested'] ?? ''),
        // Add more fields as needed
        // You can add a download button and set its callback function to handle download
        ElevatedButton(
          onPressed: () {
            // Put download function here
          },
          child: Text('Download Sample Results'),
        ),
      ],
    );
  }
}

/// Sample results table.
class SampleResultsTable extends StatelessWidget {
  final List<Map<String, dynamic>> results;

  SampleResultsTable({required this.results});

  DataRow getRow(Map<String, dynamic> item) {
    return DataRow(
      cells: [
        DataCell(Text(item['analysis'] ?? '')),
        DataCell(Text(item['name'] ?? '')),
        DataCell(Text(item['value'].toString() ?? '')),
        DataCell(Text(item['units'] ?? '')),
        DataCell(Text(item['status'] ?? '')),
      ],
    );
  }

  @override
  Widget build(BuildContext context) {
    return DataTable(
      columns: const <DataColumn>[
        DataColumn(label: Text('Analysis')),
        DataColumn(label: Text('Compound')),
        DataColumn(label: Text('Result')),
        DataColumn(label: Text('Units')),
        DataColumn(label: Text('Status')),
      ],
      rows: results.map((item) => getRow(item)).toList(),
    );
  }
}

// Center(
//         child: Column(
//           mainAxisAlignment: MainAxisAlignment.center,
//           children: List.generate(5, (index) {
//             return ElevatedButton(
//               style: ElevatedButton.styleFrom(
//                 primary: selectedRating == index + 1 ? Colors.blue : Colors.grey,
//                 side: BorderSide(color: selectedRating == index + 1 ? Colors.black : Colors.transparent, width: 2),
//               ),
//               onPressed: () => selectRating(index + 1),
//               child: Text((index + 1).toString()),
//             );
//           }),
//         ),

// FIXME:
// class CoAResultCard extends StatelessWidget {
//   final CoAResult result;

//   CoAResultCard({required this.result});

//   @override
//   Widget build(BuildContext context) {
//     return Card(
//       child: Column(
//         children: <Widget>[
//           Text(result.productName),
//           Text(result.productType),
//           Text(result.producer),
//           Text(result.dateTested),
//           ElevatedButton(
//             child: Text('Remove'),
//             onPressed: () {
//               Provider.of<CoAResultsProvider>(context, listen: false)
//                   .removeResult(result.sampleId);
//             },
//           ),
//         ],
//       ),
//     );
//   }
// }

// class CoAResultsList extends StatelessWidget {
//   @override
//   Widget build(BuildContext context) {
//     return Consumer<CoAResultsProvider>(
//       builder: (context, coaResultsProvider, child) {
//         return ListView.builder(
//           itemCount: coaResultsProvider.results.length,
//           itemBuilder: (context, index) {
//             return CoAResultCard(result: coaResultsProvider.results[index]);
//           },
//         );
//       },
//     );
//   }
// }
