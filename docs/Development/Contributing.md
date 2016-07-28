# Contributing Guidelines

## Types of Contributions

### Report Bugs

Report bugs at [https://github.com/StackFocus/PostMaster/issues](https://github.com/StackFocus/PostMaster/issues).

If you are reporting a bug, please include:

 - Your operating system name and version.
 - Any details about your local setup that might be helpful in troubleshooting.
 - Detailed steps to reproduce the bug.


### Fix Bugs

Look through the GitHub issues for bugs. Anything tagged with "bug"
is open to whoever wants to implement it.

### Implement Features

Look through the GitHub issues for features. Anything tagged with "feature"
is open to whoever wants to implement it.

### Write Documentation

PostMaster could always use more documentation.

### Submit Feedback

The best way to send feedback is to file an issue at [https://github.com/StackFocus/PostMaster/issues](https://github.com/StackFocus/PostMaster/issues).

If you are proposing a feature:

 - Explain in detail how it would work.
 - Keep the scope as narrow as possible, to make it easier to implement.

## How to Contribute Code

 1. Fork the project
 2. Create a branch related to the issue (ex. ft-adds_2factor-123)
 3. Make changes to the code
 4. `$ python pylint-check.py`
 5. `$ py.test tests`
 6. Add, commit, and push
 7. Open pull request and describe what was changed


## Coding Standards
We use standard [PEP8](https://www.python.org/dev/peps/pep-0008/)  
Our specific exceptions are in the `.pylintrc` file

Code will not be accepted if it fails the pylint test.  
`$ python pylint-check.py`

There is a paradigm we've been using for Flask:

 - Keep the view as minimal as possible.
 - Use Ajax to an API route for data as much as possible
 - Use modern flask and sqlalchemy functions for API routes (ex. get_or_404)
