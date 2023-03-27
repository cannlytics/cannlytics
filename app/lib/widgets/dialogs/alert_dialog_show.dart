part of alert_dialogs;

/// Show an alert dialog.
Future<bool?> showAlertDialog({
  required BuildContext context,
  required String title,
  String? content,
  String? cancelActionText,
  required String defaultActionText,
}) async {
  if (kIsWeb || !Platform.isIOS) {
    return showDialog(
      context: context,
      builder: (context) => AlertDialog(
        // Title.
        title: Text(
          title,
          style: Theme.of(context).textTheme.titleLarge,
        ),

        // Content.
        content: content != null ? Text(content) : null,

        // Actions.
        actions: <Widget>[
          // Cancel action.
          if (cancelActionText != null)
            TextButton(
              child: Text(
                cancelActionText,
                style: Theme.of(context).textTheme.titleMedium!.copyWith(
                      color: Theme.of(context).textTheme.titleLarge!.color,
                    ),
              ),
              onPressed: () => Navigator.of(context).pop(false),
            ),

          // Confirm action.
          SecondaryButton(
            text: defaultActionText,
            onPressed: () => Navigator.of(context).pop(true),
          ),
        ],
      ),
    );
  }
  return showCupertinoDialog(
    context: context,
    builder: (context) => CupertinoAlertDialog(
      title: Text(title),
      content: content != null ? Text(content) : null,
      actions: <Widget>[
        if (cancelActionText != null)
          CupertinoDialogAction(
            child: Text(cancelActionText),
            onPressed: () => Navigator.of(context).pop(false),
          ),
        CupertinoDialogAction(
          child: Text(defaultActionText),
          onPressed: () => Navigator.of(context).pop(true),
        ),
      ],
    ),
  );
}
