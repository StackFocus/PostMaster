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
 5. Run `$ flake8 --exclude=config.py,config.default.py` to verify that you are complying to PEP8 coding standards
 6. Run `$ py.test tests` to verify the unit tests pass
 7. Commit and push the changed files
 8. Open a pull request and describe what was changed (try to squash your commits when possible)


### Coding Standards
We use standard [PEP8](https://www.python.org/dev/peps/pep-0008/).

Code will not be accepted if it fails the flake8 test. To run flake8:
`$ flake8 --exclude=config.py,config.default.py`

There is a paradigm we've been using for Flask:

 - Keep the code in the routes as minimal as possible by using decorators and helper functions
 - Use Ajax to an API route for data as much as possible
 - Use modern Flask and SQLAlchemy functions for API routes (ex. get_or_404)


### How to Generate an Updated openAPI-spec.html

 1. Start in the root of the PostMaster git repository
 2. Install the required npm packages with `npm install -g bootprint bootprint-openapi html-inline`
 3. Create a temporary target for the generated HTML with `mkdir openapi-target`
 4. Generate the temporary HTML contents with `bootprint openapi docs/API/openAPI-spec.yml openapi-target`
 5. Consolidate the generated HTML folder to a single file with `html-inline openapi-target/index.html > docs/API/openAPI-spec.html`
 6. Delete the temporary HTML contents from step 4 with `rm -rf openapi-target`
