import 'package:cannlytics_data/constants/design.dart';
import 'package:cannlytics_data/models/strain.dart';
import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';

/// A strain list item.
class StrainListItem extends StatelessWidget {
  StrainListItem({required this.strain});

  // Properties
  final Strain strain;

  @override
  Widget build(BuildContext context) {
    final screenWidth = MediaQuery.of(context).size.width;
    print('Building list item:');
    print(strain.toMap());
    return Card(
      margin: EdgeInsets.symmetric(horizontal: 24),
      elevation: 2,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(3)),
      color: Theme.of(context).scaffoldBackgroundColor,
      child: InkWell(
        onTap: () {
          context.go('/strains/${strain.id}/');
        },
        child: Container(
          margin: EdgeInsets.all(0),
          padding: EdgeInsets.all(16.0),
          decoration: BoxDecoration(borderRadius: BorderRadius.circular(3.0)),
          child: Row(
            children: [
              // Strain image.
              if (strain.imageUrl != null)
                Padding(
                  padding: EdgeInsets.only(right: 16.0),
                  child: Image.network(
                    strain.imageUrl!,
                    width: 64,
                    height: 64,
                  ),
                ),

              // Strain details.
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    // Strain name.
                    Text(
                      strain.name ?? 'Unknown',
                      style: Theme.of(context).textTheme.labelLarge,
                    ),
                    gapH8,

                    // Strain ID.
                    Text(
                      'ID: ${strain.id}',
                      style: Theme.of(context).textTheme.labelMedium,
                    ),
                  ],
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
