// Cannlytics App
// Copyright (c) 2023 Cannlytics

// Authors:
//   Keegan Skeate <https://github.com/keeganskeate>
// Created: 2/18/2023
// Updated: 2/18/2023
// License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

// Flutter imports:
import 'package:flutter/material.dart';

// Package imports:
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

// Project imports:
import 'package:cannlytics_app/models/consumer/job.dart';
import 'package:cannlytics_app/routing/app_router.dart';
import 'package:cannlytics_app/routing/routes.dart';
import 'package:cannlytics_app/ui/business/packages/package_items_list.dart';
import 'package:cannlytics_app/ui/business/packages/packages_service.dart';
import 'package:cannlytics_app/widgets/layout/async_value_widget.dart';

class PackageScreen extends ConsumerWidget {
  const PackageScreen({super.key, required this.jobId});
  final JobID jobId;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final jobAsync = ref.watch(jobStreamProvider(jobId));
    return ScaffoldAsyncValueWidget<Job>(
      value: jobAsync,
      data: (job) => JobEntriesPageContents(job: job),
    );
  }
}

class JobEntriesPageContents extends StatelessWidget {
  const JobEntriesPageContents({super.key, required this.job});
  final Job job;

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text(job.name),
        actions: <Widget>[
          IconButton(
            icon: const Icon(Icons.edit, color: Colors.white),
            onPressed: () => context.goNamed(
              AppRoutes.editPackage.name,
              params: {'id': job.id},
              extra: job,
            ),
          ),
        ],
      ),
      body: JobEntriesList(job: job),
      floatingActionButton: FloatingActionButton(
        child: const Icon(Icons.add, color: Colors.white),
        onPressed: () => context.goNamed(
          AppRoutes.addPackage.name,
          params: {'id': job.id},
          extra: job,
        ),
      ),
    );
  }
}
