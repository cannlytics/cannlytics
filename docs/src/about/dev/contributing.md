# Contributing

## Become a Sponsor :octicons-heart-fill-16:{: .heart-throb}

Open source projects take time and money. Help support the project by becoming a sponsor. You can add your support at
any tier you feel comfortable with. No amount is too little. We also accept one time contributions via PayPal.

[:octicons-mark-github-16: GitHub Sponsors](https://github.com/sponsors/cannlytics){: .md-button .md-button--primary }
[:fontawesome-brands-paypal: PayPal](https://www.paypal.me/cannlytics){ .md-button}

## Bug Reports :material-bug:

1. Please **read the documentation** and **search the issue tracker** to try and find the answer to your question
  **before** posting an issue.

2. When creating an issue on the repository, please provide as much info as possible:

    - Version being used.
    - Operating system.
    - Version of Python.
    - Errors in console.
    - Detailed description of the problem.
    - Examples for reproducing the error.  You can post pictures, but if specific text or code is required to reproduce
      the issue, please provide the text in a plain text format for easy copy/paste.

    The more info provided, the greater the chance someone will take the time to answer, implement, or fix the issue.

3. Be prepared to answer questions and provide additional information if required.  Issues in which the creator refuses
  to respond to follow up questions will be marked as stale and closed.

## Reviewing Code :material-glasses:

Take part in reviewing pull requests and/or reviewing direct commits.  Make suggestions to improve the code and discuss
solutions to overcome weakness in the algorithm.

## Answer Questions in Issues :material-comment-question:

Take time and answer questions and offer suggestions to people who've created issues in the issue tracker. Often people
will have questions that you might have an answer for.  Or maybe you know how to help them accomplish a specific task
they are asking about. Feel free to share your experience to help others out.

## Pull Requests :octicons-git-pull-request-24:

Pull requests are welcome, and a great way to help fix bugs and add new features. If you you are interested in directly
contributing to the code, please check out [Development](./development.md) for more info on the environment and process.

## Documentation Improvements :material-pencil:

A ton of time has been spent not only creating and supporting this tool and related extensions, but also spent making
this documentation.  If you feel it is still lacking, show your appreciation for the tool and/or extensions by helping
to improve the documentation. Check out [Development](./development.md) for more info on documentation.

# Contributing

Interested in contributing to the Material for MkDocs? Want to report a bug?
Before you do, please read the following guidelines.

## Submission context

### Got a question or problem?

For quick questions there's no need to open an issue as you can reach us on
[gitter.im][1].

  [1]: https://gitter.im/squidfunk/mkdocs-material

### Found a bug?

If you found a bug in the source code, you can help us by submitting an issue
to the [issue tracker][2] in our GitHub repository. Even better, you can submit
a Pull Request with a fix. However, before doing so, please read the
[submission guidelines][3].

  [2]: https://github.com/squidfunk/mkdocs-material/issues
  [3]: #submission-guidelines

### Missing a feature?

You can request a new feature by submitting an issue to our GitHub Repository.
If you would like to implement a new feature, please submit an issue with a
proposal for your work first, to be sure that it is of use for everyone, as
the Material for MkDocs is highly opinionated. Please consider what kind of
change it is:

* For a **major feature**, first open an issue and outline your proposal so
  that it can be discussed. This will also allow us to better coordinate our
  efforts, prevent duplication of work, and help you to craft the change so
  that it is successfully accepted into the project.

* **Small features and bugs** can be crafted and directly submitted as a Pull
  Request. However, there is no guarantee that your feature will make it into
  the `master`, as it's always a matter of opinion whether if benefits the
  overall functionality of the project.

## Submission guidelines

### Submitting an issue

Before you submit an issue, please search the issue tracker, maybe an issue for
your problem already exists and the discussion might inform you of workarounds
readily available.

We want to fix all the issues as soon as possible, but before fixing a bug we
need to reproduce and confirm it. In order to reproduce bugs we will
systematically ask you to provide a minimal reproduction scenario using the
custom issue template. Please stick to the issue template.

Unfortunately we are not able to investigate / fix bugs without a minimal
reproduction scenario, so if we don't hear back from you we may close the issue.

### Submitting a Pull Request (PR)

Search GitHub for an open or closed PR that relates to your submission. You
don't want to duplicate effort. If you do not find a related issue or PR,
go ahead.

1. **Development**: Fork the project, set up the [development environment][4],
  make your changes in a separate git branch and add descriptive messages to
  your commits.

2. **Build**: Before submitting a pull requests, [build the theme][5]. This is
  a mandatory requirement for your PR to get accepted, as the theme should at
  all times be installable through GitHub.

3. **Pull Request**: After building the theme, commit the compiled output, push
  your branch to GitHub and send a PR to `mkdocs-material:master`. If we
  suggest changes, make the required updates, rebase your branch and push the
  changes to your GitHub repository, which will automatically update your PR.

After your PR is merged, you can safely delete your branch and pull the changes
from the main (upstream) repository.

  [4]: https://squidfunk.github.io/mkdocs-material/customization/#environment-setup
  [5]: https://squidfunk.github.io/mkdocs-material/customization/#build-process
