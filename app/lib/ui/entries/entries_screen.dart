import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:cannlytics_app/constants/strings.dart';
import 'package:cannlytics_app/models/entries_list_tile_model.dart';
import 'package:cannlytics_app/services/entries_service.dart';
import 'package:cannlytics_app/widgets/list_items_builder.dart';

class EntriesScreen extends ConsumerWidget {
  const EntriesScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    return Scaffold(
      appBar: AppBar(
        title: const Text(Strings.entries),
      ),
      body: Consumer(
        builder: (context, ref, child) {
          final entriesTileModelStream =
              ref.watch(entriesTileModelStreamProvider);
          return ListItemsBuilder<EntriesListTileModel>(
            data: entriesTileModelStream,
            itemBuilder: (context, model) => EntriesListTile(model: model),
          );
        },
      ),
    );
  }
}

class EntriesListTile extends StatelessWidget {
  const EntriesListTile({super.key, required this.model});
  final EntriesListTileModel model;

  @override
  Widget build(BuildContext context) {
    const fontSize = 16.0;
    return Container(
      color: model.isHeader ? Colors.indigo[100] : null,
      padding: const EdgeInsets.symmetric(vertical: 8.0, horizontal: 16.0),
      child: Row(
        children: <Widget>[
          Text(model.leadingText, style: const TextStyle(fontSize: fontSize)),
          Expanded(child: Container()),
          if (model.middleText != null)
            Text(
              model.middleText!,
              style: TextStyle(color: Colors.green[700], fontSize: fontSize),
              textAlign: TextAlign.right,
            ),
          SizedBox(
            width: 60.0,
            child: Text(
              model.trailingText,
              style: const TextStyle(fontSize: fontSize),
              textAlign: TextAlign.right,
            ),
          ),
        ],
      ),
    );
  }
}
