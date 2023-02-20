// Cannlytics App
// Copyright (c) 2023 Cannlytics

// Authors:
//   Keegan Skeate <https://github.com/keeganskeate>
// Created: 2/18/2023
// Updated: 2/18/2023
// License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:cannlytics_app/ui/business/inventory/packages/packages_service.dart';
import 'package:cannlytics_app/models/job.dart';
import 'package:cannlytics_app/widgets/list_items_builder.dart';
import 'package:cannlytics_app/ui/business/inventory/packages/packages_controller.dart';
import 'package:cannlytics_app/routing/app_router.dart';
import 'package:cannlytics_app/utils/dialogs/alert_dialog_ui.dart';

class PackagesScreen extends StatelessWidget {
  const PackagesScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Jobs'),
        actions: <Widget>[
          IconButton(
            icon: const Icon(Icons.add, color: Colors.white),
            onPressed: () => context.goNamed(AppRoute.addPackage.name),
          ),
        ],
      ),
      body: Consumer(
        builder: (context, ref, child) {
          ref.listen<AsyncValue>(
            jobsScreenControllerProvider,
            (_, state) => state.showAlertDialogOnError(context),
          );
          // * TODO: investigate why we get a dismissible error if we call
          // * ref.watch(jobsScreenControllerProvider) here
          final jobsAsyncValue = ref.watch(jobsStreamProvider);
          return ListItemsBuilder<Job>(
            data: jobsAsyncValue,
            itemBuilder: (context, job) => Dismissible(
              key: Key('job-${job.id}'),
              background: Container(color: Colors.red),
              direction: DismissDirection.endToStart,
              onDismissed: (direction) => ref
                  .read(jobsScreenControllerProvider.notifier)
                  .deleteJob(job),
              child: JobListTile(
                job: job,
                onTap: () => context.goNamed(
                  AppRoute.package.name,
                  params: {'id': job.id},
                ),
              ),
            ),
          );
        },
      ),
    );
  }
}

class JobListTile extends StatelessWidget {
  const JobListTile({Key? key, required this.job, this.onTap})
      : super(key: key);
  final Job job;
  final VoidCallback? onTap;

  @override
  Widget build(BuildContext context) {
    return ListTile(
      title: Text(job.name),
      trailing: const Icon(Icons.chevron_right),
      onTap: onTap,
    );
  }
}
