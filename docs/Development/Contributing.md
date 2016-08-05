### Types of Contributions

#### Bug Reports

Report bugs and issues at [https://github.com/StackFocus/PostMaster/issues](https://github.com/StackFocus/PostMaster/issues).

If you are reporting a bug, please include the following:

 - The version of PostMaster that you are running
 - The operating system name and version that is running the application
 - The version of Python that is running the application (`python -V`)
 - The installation method used (package or manual)
 - Detailed steps to reproduce the bug
 - Any details about your specific environment that might be helpful for troubleshooting


#### Bug Fixes

Look through the GitHub issues for bugs.
Anything tagged with "bug" and is unassigned is open to whoever wants to implement it.
Any changes made should be documented in docs/ChangeLog.md.

#### Features

Look through the GitHub issues for features.
Anything tagged with "feature" and is unassigned is open to whoever wants to implement it.
Any changes made should be documented in "docs/ChangeLog.md".

#### Documentation

PostMaster documentation is written in Markdown and then deployed to GitHub pages via mkdocs by a StackFocus administrator.
To update documentation, directly modify the Markdown files in the "docs" folder. Once the changes are merged,
a StackFocus administrator will update GitHub pages.

#### Feedback

The best way to send feedback is to file an issue at [https://github.com/StackFocus/PostMaster/issues](https://github.com/StackFocus/PostMaster/issues).

If you are proposing a feature:

 - Explain in detail how it would work and why it would be beneficial
 - Keep the scope as narrow as possible to make it easier to implement

### How To Contribute Code

 1. Fork the project
 2. Create a branch related to the issue (ex. ft-adds_2factor-123)
 3. Make changes to the code
 4. Write unit tests to test the new code
 5. Run `$ python pylint-check.py` to verify that you are complying to PEP8 coding standards
 6. Run `$ py.test tests` to verify the unit tests pass
 7. Commit and push the changed files
 8. Open a pull request and describe what was changed (try to squash your commits when possible)


### Coding Standards
We use standard [PEP8](https://www.python.org/dev/peps/pep-0008/).
Our specific exceptions are in the `.pylintrc` file.

Code will not be accepted if it fails the pylint test. To run pylint:
`$ python pylint-check.py`

There is a paradigm we've been using for Flask:

 - Keep the code in the routes as minimal as possible by using decorators and helper functions
 - Use Ajax to an API route for data as much as possible
 - Use modern Flask and SQLAlchemy functions for API routes (ex. get_or_404)
