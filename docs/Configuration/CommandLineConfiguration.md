### Before You Start
1. Logged into the server hosting PostMaster as root or as an administrator, enter the Python virtual environment (if necessary, replace the path with your install location):

        Linux:
        source /opt/postmaster/env/bin/activate
        Windows:
        C:\PostMaster\env\Scripts\activate.ps1

2. Once you've entered the Python virtual environment, navigate to the location of manage.py (replace /opt/postmaster/git with your install location):

        cd /opt/postmaster/git

3. You can now run command line configurations with the following:

        python manage.py [command]

4. Some of the commands modify files and may end up changing the ownership of the files on Linux/Unix operating systems.
Use the following commands to restore the proper permissions on the PostMaster files:

        chown -R www-data:www-data /opt/postmaster
        chmod -R 550 /opt/postmaster

### Command Line Commands

**setlogfile** sets the location of the logfile. The default is `/opt/postmaster/logs/postmaster.log`.

**setdburi** sets the MySQL database URI that PostMaster uses to connect to the MySQL server used by your mail server.

**upgradedb** upgrades the existing database to the latest schema version and adds the default configuration items if they are missing.

**generatekey** replaces the secret key in config.py which is used by Flask (the Python framework used for PostMaster) for cryptographic functions.
After the initial installation, this command should not be run again as all current logins would become invalid upon the next restart of the PostMaster.

**unlockadmin username** unlocks a locked out administrator (replace username with the actual value).

**resetadminpassword username password** resets an administrator's password to the desired value (replace user and password with the actual values)

**runserver -d -h 0.0.0.0** runs PostMaster in debug mode on port 5000. This is useful if you are having issues as it bypasses the webserver
and displays failing errors in HTML.

**db [command]** runs advanced database migration commands.
It is recommended to use the wrapper commands listed above instead, however, in rare and advanced circumstances, these sets of commands may be necessary.
For more information, visit the [Alembic API documentation](https://alembic.readthedocs.org/en/latest/api/commands.html).
