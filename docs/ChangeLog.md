### Unreleased

BACKWARDS INCOMPATIBILITIES / NOTES:

* The 'Log File' config option is now baked into the application config and cannot be set in the API/UI/database. Use `python manage.py setlogfile <path>` or edit config.py to change the log file location. See [GH-128].
* `python manage.py createdb` has been replaced with `python manage.py upgradedb` [GH-138]

Features:

* Added the ability to install PostMaster via a deb package [GH-111]
* Database upgrades/migrations are automatic during ugrades via the deb package and Docker [GH-138]

Improvements:

* Database migrations are now tracked via source control to ensure consistency across installations [GH-138]
* Added additional documentation [GH-115]
* Improved Active Directory authentication performance [GH-118]
* Cleaned up JavaScript event listeners [GH-120]
* Vagrant now uses Ansible for configuration instead of a bash script [GH-111]
* Updated the Python packages to the latest versions [GH-135]

Bug Fixes:

* Fixed an issue where error logs were attempting to be written before the log file path was defined [GH-109]


### v1.0.0 - Abbey Road

Features:

* Published first release of Postmaster
