// Cannlytics App
// Copyright (c) 2023 Cannlytics

// Authors:
//   Keegan Skeate <https://github.com/keeganskeate>
// Created: 2/18/2023
// Updated: 2/18/2023
// License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:rxdart/rxdart.dart';
import 'package:cannlytics_app/services/auth_service.dart';
import 'package:cannlytics_app/models/app_user.dart';
import 'package:cannlytics_app/models/daily_jobs_details.dart';
import 'package:cannlytics_app/models/entry_job.dart';
import 'package:cannlytics_app/ui/business/inventory/packages/packages_service.dart';
import 'package:cannlytics_app/utils/strings/string_format.dart';
import 'package:cannlytics_app/models/entry.dart';
import 'package:cannlytics_app/models/job.dart';

class EntriesListTileModel {
  const EntriesListTileModel({
    required this.leadingText,
    required this.trailingText,
    this.middleText,
    this.isHeader = false,
  });
  final String leadingText;
  final String trailingText;
  final String? middleText;
  final bool isHeader;
}

// TODO: Clean up this code a bit more
class EntriesService {
  EntriesService({required this.database});
  final SpendingService database;

  /// combine List<Job>, List<Entry> into List<EntryJob>
  Stream<List<EntryJob>> _allEntriesStream(UserID uid) =>
      CombineLatestStream.combine2(
        database.watchEntries(uid: uid),
        database.watchJobs(uid: uid),
        _entriesJobsCombiner,
      );

  static List<EntryJob> _entriesJobsCombiner(
      List<Entry> entries, List<Job> jobs) {
    return entries.map((entry) {
      final job = jobs.firstWhere((job) => job.id == entry.jobId);
      return EntryJob(entry, job);
    }).toList();
  }

  /// Output stream
  Stream<List<EntriesListTileModel>> entriesTileModelStream(UserID uid) =>
      _allEntriesStream(uid).map(_createModels);

  static List<EntriesListTileModel> _createModels(List<EntryJob> allEntries) {
    if (allEntries.isEmpty) {
      return [];
    }
    final allDailyJobsDetails = DailyJobsDetails.all(allEntries);

    // total duration across all jobs
    final totalDuration = allDailyJobsDetails
        .map((dateJobsDuration) => dateJobsDuration.duration)
        .reduce((value, element) => value + element);

    // total pay across all jobs
    final totalPay = allDailyJobsDetails
        .map((dateJobsDuration) => dateJobsDuration.pay)
        .reduce((value, element) => value + element);

    return <EntriesListTileModel>[
      EntriesListTileModel(
        leadingText: 'All Entries',
        middleText: Format.currency(totalPay),
        trailingText: Format.hours(totalDuration),
      ),
      for (DailyJobsDetails dailyJobsDetails in allDailyJobsDetails) ...[
        EntriesListTileModel(
          isHeader: true,
          leadingText: Format.date(dailyJobsDetails.date),
          middleText: Format.currency(dailyJobsDetails.pay),
          trailingText: Format.hours(dailyJobsDetails.duration),
        ),
        for (JobDetails jobDuration in dailyJobsDetails.jobsDetails)
          EntriesListTileModel(
            leadingText: jobDuration.name,
            middleText: Format.currency(jobDuration.pay),
            trailingText: Format.hours(jobDuration.durationInHours),
          ),
      ]
    ];
  }
}

final entriesServiceProvider = Provider<EntriesService>((ref) {
  return EntriesService(database: ref.watch(databaseProvider));
});

final entriesTileModelStreamProvider =
    StreamProvider.autoDispose<List<EntriesListTileModel>>(
  (ref) {
    final user = ref.watch(authStateChangesProvider).value;
    if (user == null) {
      throw AssertionError('User can\'t be null when fetching entries');
    }
    final entriesService = ref.watch(entriesServiceProvider);
    return entriesService.entriesTileModelStream(user.uid);
  },
);
