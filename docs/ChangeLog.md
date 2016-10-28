### Unreleased

BACKWARDS INCOMPATIBILITIES / NOTES:

* The default MySQL Python connector of "mysqlclient" has been replaced with "pymysql" for a pure Python replacement.
Upgrades will be unaffected by this, but please note that reinstalls will require you to either install "mysqlclient"
([Ubuntu Instructions](https://github.com/PyMySQL/mysqlclient-python#install) or change the start of your database URI
with "mysql+pymysql://" instead of "mysql://" [GH-170].

### v1.1.0 - A Hard Day's Night

BACKWARDS INCOMPATIBILITIES / NOTES:

* The 'Log File' config option is now baked into the application config and cannot be set in the API/UI/database. Use `python manage.py setlogfile <path>` or edit config.py to change the log file location. [GH-128]
* `python manage.py createdb` has been replaced with `python manage.py upgradedb` [GH-138]
* On new installations of PostMaster, the ID of the configuration settings will change. Existing installations that will be upgraded will not be affected. [GH-142]
* The API error messages for HTTP 400 and 404 have been made friendlier. Any automation that keys in on these messages will be broken. [GH-142]

Features:

* Added the ability to install PostMaster via a deb package [GH-111]
* Adds the ability to lockout local accounts after x number of failed login attempts [GH-142]
* Database upgrades/migrations are automatic during ugrades via the deb package and Docker [GH-138]
* Adds the ability to unlock administrators and reset administrator passwords via the CLI [GH-145]
* Adds the `python manage.py version` command [GH-156]
* Adds the `python manage.py setkey` command [GH-161]

Improvements:

* Database migrations are now tracked via source control to ensure consistency across installations [GH-138]
* Added additional documentation [GH-115]
* Improved Active Directory authentication performance [GH-118]
* Cleaned up JavaScript event listeners [GH-120]
* Made the `python manage.py clean` function completely OS agnostic [GH-158]
* Vagrant now uses Ansible for configuration instead of a bash script [GH-111]
* Updated the Python packages to the latest versions [GH-135]
* Apache logs for PostMaster now default to /opt/postmaster/logs [GH-151]

Bug Fixes:

* Fixed an issue where error logs were attempting to be written before the log file path was defined [GH-109]
* The configuration file, config.py, is now named as config.default.py in the repository. During installation, the administrator must now copy or rename config.default.py to config.py.
This is so that config.py is not overwritten during package upgrades [GH-157].


### v1.0.0 - Abbey Road

Features:

* Published first release of Postmaster
