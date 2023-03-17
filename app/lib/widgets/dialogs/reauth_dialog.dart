part of alert_dialogs;

/// Show an alert dialog with an option to reauthenticate the user with Firebase.
Future<bool?> showReauthDialog({
  required BuildContext context,
  required String title,
  String? content,
  String? cancelActionText,
  required String defaultActionText,
  required FirebaseAuth auth,
}) async {
  return showDialog(
    context: context,
    builder: (context) => AlertDialog(
      title: Text(title),
      content: content != null ? Text(content) : null,
      actions: <Widget>[
        if (cancelActionText != null)
          TextButton(
            child: Text(
              cancelActionText,
              style: Theme.of(context)
                  .textTheme
                  .titleSmall!
                  .copyWith(color: AppColors.neutral4),
            ),
            onPressed: () => Navigator.of(context).pop(false),
          ),
        TextButton(
          child: Text(defaultActionText),
          onPressed: () async {
            // Reauthenticate the user with Firebase
            try {
              var user = await FirebaseAuth.instance.currentUser!;
              await user.reauthenticateWithCredential(
                EmailAuthProvider.credential(
                  email: user.email!,
                  password: 'TODO: GET PASSWORD!',
                ),
              );
              Navigator.of(context).pop(true);
            } catch (e) {
              print('Error reauthenticating user: $e');
            }
          },
        ),
      ],
    ),
  );
}
