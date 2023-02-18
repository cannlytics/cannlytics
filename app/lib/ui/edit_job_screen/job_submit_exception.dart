// Cannlytics App
// Copyright (c) 2023 Cannlytics

// Authors:
//   Keegan Skeate <https://github.com/keeganskeate>
// Created: 2/18/2023
// Updated: 2/18/2023
// License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>
class JobSubmitException {
  String get title => 'Name already used';
  String get description => 'Please choose a different job name';

  @override
  String toString() {
    return '$title. $description.';
  }
}
