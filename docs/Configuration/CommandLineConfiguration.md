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

**createdb** runs a database migration, and configures the default configuration settings if they are missing on the database specified using the "setdburi" command.  
This is used during the installation of PostMaster.

**existingdb** marks the first revision complete, which
  is the revision that creates the virtual\_\* tables. It then upgrades the database from there.   
  This is used during the installation of PostMaster.   
  **WARNING**: Only use this function if you setup your mailserver database before this application and only have the virtual_* tables.

**upgradedb** upgrades the existing database to new state and adds default configurations if missing.

**generatekey** replaces the secret key in config.py which is used by Flask (the Python framework used for PostMaster) for cryptographic functions.
After the initial installation, this command should not be run again as all current logins would become invalid upon the next restart of the PostMaster.

**runserver -d -h 0.0.0.0** runs PostMaster in debug mode on port 5000. This is useful if you are having issues as it bypasses the webserver
and displays failing errors in HTML.

**db [command]** runs advanced database migration commands.
Most of the time it is better to use the wrapper commands we created above.  
For more information, visit the [Alembic API documentation](https://alembic.readthedocs.org/en/latest/api/commands.html).
