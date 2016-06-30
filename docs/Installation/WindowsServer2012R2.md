### Prerequisites
1. An Ubuntu 14.04 mail server configured with the guide from [DigitalOcean](https://www.digitalocean.com/community/tutorials/how-to-configure-a-mail-server-using-postfix-dovecot-mysql-and-spamassassin) or [Linode](https://www.linode.com/docs/email/postfix/email-with-postfix-dovecot-and-mysql).
Any other MySQL configuration requires edits to PostMaster's database models. Paid support for this is available.
2. A clean Windows Server 2012 R2 installation with Administrative access

### MySQL Preparation
1. Start by logging into the MySQL server that your mail server uses:

        mysql -u root -p

2. Once you've logged into MySQL, create a PostMaster MySQL user that has privileges to edit the tables for the servermail database.
If you are installing PostMaster on a server other than where your mail server's MySQL server is installed,
replace '127.0.0.1' with the server's IP address or DNS that is going to host PostMaster:

        GRANT ALL PRIVILEGES ON servermail.* TO 'postmasteruser'@'127.0.0.1' IDENTIFIED BY 'password_changeme';

3. Exit from MySQL:

        exit

4. If you are installing PostMaster on a server other than where your mail server's MySQL server is installed, make sure that
bind-address is set 0.0.0.0 and not 127.0.0.1 in:

        /etc/mysql/my.cnf

### Installation
1. To install IIS and FastCGI, open an Administrative PowerShell window and run the following commands:

        Import-Module ServerManager
        Install-WindowsFeature Web-Server, Web-CGI, Web-Mgmt-Console

2. To install Python and WFastCGI, Microsoft Web Platform Installer is required. To download it, run the following command:

        Invoke-WebRequest -Uri 'http://download.microsoft.com/download/C/F/F/CFF3A0B8-99D4-41A2-AE1A-496C08BEB904/WebPlatformInstaller_amd64_en-US.msi' -OutFile "$env:SystemDrive\WebPlatformInstaller_amd64_en-US.msi"

3. Install Microsoft Web Platform Installer:

        Start-Process -FilePath 'msiexec.exe' -ArgumentList "/i $env:SystemDrive\WebPlatformInstaller_amd64_en-US.msi /quiet" -Wait

4. Using Microsoft Web Platform Installer, install Python 2.7 and WFastCGI:

        Invoke-Expression "& '$env:ProgramFiles\Microsoft\Web Platform Installer\WebpiCmd.exe' /Install /Products:WFastCgi_21_279 /AcceptEula"

5. Delete the Microsoft Web Platform Installer installation file:

        Remove-Item "$env:SystemDrive\WebPlatformInstaller_amd64_en-US.msi" -Force

6. In order to download the source code for PostMaster, a git client is required. To download git, run the following command:

        Invoke-WebRequest -Uri 'https://github.com/git-for-windows/git/releases/download/v2.7.2.windows.1/Git-2.7.2-64-bit.exe' -OutFile "$env:SystemDrive\Git-2.7.2-64-bit.exe"

7. Install git:

        Start-Process -FilePath "$env:SystemDrive\Git-2.7.2-64-bit.exe" -ArgumentList '/VERYSILENT' -Wait

8. Delete the git installation file:

        Remove-Item "$env:SystemDrive\Git-2.7.2-64-bit.exe" -Force

9. Create a directory to contain PostMaster:

        New-Item "$env:SystemDrive\PostMaster" -Type Directory

9. Create a directory to contain PostMaster logs:

        New-Item "$env:SystemDrive\PostMaster\logs" -Type Directory

10. Download the PostMaster source code:

        & "$env:ProgramFiles\Git\bin\git.exe" clone 'https://github.com/StackFocus/PostMaster.git' "$env:SystemDrive\PostMaster\git"

11. PostMaster will write logs to C:\PostMaster\logs\postmaster.log, but since IIS does not have access to create that file, it must be done manually with the following command:

        New-Item "$env:SystemDrive\PostMaster\logs\postmaster.log" -Type File

12. In order for PostMaster's files to be secured, the proper permissions must be set. The following command will grant only IIS read access,
and Administrators full control on PostMaster's files:

        cmd.exe /C "icacls $env:SystemDrive\PostMaster /inheritance:r /grant BUILTIN\IIS_IUSRS:(OI)(CI)(RX) /grant BUILTIN\Administrators:(OI)(CI)F /grant SYSTEM:(OI)(CI)(F)"

13. In order for PhoenixPass to be able to write to the log file created earlier, IIS requires write access. To do so, use the following command:

        cmd.exe /C "icacls $env:SystemDrive\PostMaster\logs\postmaster.log /grant BUILTIN\IIS_IUSRS:(M)"

14. A python virtual environment is now required. This allows you to separate the system installed python packages from PostMaster's required python packages.
This is done with the following command:

        & "$env:SystemDrive\Python27\Scripts\pip.exe" install virtualenv

15. Create a Python virtualenv for PostMaster:

        & "$env:SystemDrive\Python27\Scripts\virtualenv.exe" -p "$env:SystemDrive\Python27\python.exe" "$env:SystemDrive\PostMaster\env"

16. To use the newly created virtual environment in your PowerShell window, run the following command:

        & "$env:SystemDrive\PostMaster\env\Scripts\activate.ps1"

17. PostMaster requires the Python module "python-ldap". Because it is difficult to compile it manually on Windows, this tutorial will use a precompiled version. To download it, use the following command:

        Invoke-WebRequest -Uri 'https://pypi.python.org/packages/2.7/p/python-ldap/python_ldap-2.4.25-cp27-none-win32.whl#md5=aef7058690dd740d9333af35c270d03a' -OutFile "$env:SystemDrive\python_ldap-2.4.25-cp27-none-win32.whl"

18. Install "python-ldap":

        pip install "$env:SystemDrive\python_ldap-2.4.25-cp27-none-win32.whl"

19. Remove the "python-ldap" installation file:

        Remove-Item "$env:SystemDrive\python_ldap-2.4.25-cp27-none-win32.whl" -Force

19. PostMaster requires the Python module "mysqlclient". Because it is difficult to compile it manually on Windows, this tutorial will use a precompiled version. To download it, use the following command:

        Invoke-WebRequest -Uri 'https://pypi.python.org/packages/cp27/m/mysqlclient/mysqlclient-1.3.7-cp27-none-win32.whl#md5=e9e726fd6f1912af78e2bf6ab56c02f3' -OutFile "$env:SystemDrive\mysqlclient-1.3.7-cp27-none-win32.whl"

20. Install "mysqlclient":

        pip install "$env:SystemDrive\mysqlclient-1.3.7-cp27-none-win32.whl"

19. Remove the "mysqlclient" installation file:

        Remove-Item "$env:SystemDrive\mysqlclient-1.3.7-cp27-none-win32.whl" -Force

20. Install the Python packages that PostMaster requires:

        pip install -r "$env:SystemDrive\PostMaster\git\requirements.txt"

21. Copy wfastcgi.py, created by Microsoft Web Platform Installer earlier, to C:\PostMaster\git:

        Copy-Item -Path "$env:SystemDrive\Python27\Scripts\wfastcgi.py" "$env:SystemDrive\PostMaster\git"

22. At this point, PostMaster requires an IIS site. You can either use the "Default Web Site" and change the virtual directory to C:\PostMaster\git,
or create a new site that points to that directory. This tutorial will use the Default Web Site. To change the virtual directory, use the following commands:

        Import-Module WebAdministration
        Set-ItemProperty 'IIS:\Sites\Default Web Site\' -Name physicalPath -Value "$env:SystemDrive\PostMaster\git"

23. Now, IIS needs to know how to run PostMaster. The following commands configure FastCGI to be able to use the Python virtual environment created earlier and run PostMaster
(If you are using a site other than "Default Web Site", change that value in the commands below):

        Import-Module WebAdministration
        Set-WebConfiguration -Filter '/system.webServer/handlers/@AccessPolicy' -Value 'Read, Script' -PSPath 'IIS:\' -Location 'Default Web Site'
        Add-WebConfiguration -Filter '/system.webServer/handlers' -Value @{name='PythonHandler'; path='*'; verb='*'; modules='FastCgiModule'; scriptProcessor="$env:SystemDrive\PostMaster\env\Scripts\python.exe|$env:SystemDrive\PostMaster\git\wfastcgi.py"; resourceType='Unspecified'} -PSPath 'IIS:\' -Location 'Default Web Site'
        Add-WebConfiguration -Filter '/system.webServer/fastCgi' -Value @{fullPath="$env:SystemDrive\PostMaster\env\Scripts\python.exe"; arguments="$env:SystemDrive\PostMaster\git\wfastcgi.py"}
        Add-WebConfiguration -Filter "/system.webServer/fastCgi/application[@fullPath='$env:SystemDrive\PostMaster\env\Scripts\python.exe' and @arguments='$env:SystemDrive\PostMaster\git\wfastcgi.py']/environmentVariables" -Value @{name='PYTHONPATH'; value="$env:SystemDrive\PostMaster\git"} -AtIndex 0
        Add-WebConfiguration -Filter "/system.webServer/fastCgi/application[@fullPath='$env:SystemDrive\PostMaster\env\Scripts\python.exe' and @arguments='$env:SystemDrive\PostMaster\git\wfastcgi.py']/environmentVariables" -Value @{name='WSGI_HANDLER'; value='app.app'} -AtIndex 1

24. PostMaster needs to be configured to connect to the MySQL database using the MySQL user created in step 2 of MySQL Preparation.
Make sure to replace "password_changeme" and "127.0.0.1' with the actual values supplied in step 2 of MySQL Preparation, and if needed,
replace '127.0.0.1' with the IP address or DNS specified in step 2 of MySQL Preparation:

        cd C:\Postmaster\git
        python manage.py setdburi 'mysql://postmasteruser:password_changeme@127.0.0.1:3306/servermail'

25. PostMaster needs to create a few tables under the servermail database. This is done via a database migration,
which means that only the necessary changes to the database are made, and these changes are reversible if something went wrong.
To start the migration, run the following command:

        python manage.py createdb

 - If you are coming from an existing database with `virtual_users`, `virtual_domains`, and `virtual_aliases` tables (you followed the mailserver setup guides at the top), then run this command instead of the above:  
   `python manage.py existingdb`  

26. PostMaster uses a secret key for certain cryptographic functions. To generate a random key, run the following command:

        python manage.py generatekey

27. By deafult, PostMaster logs to a Linux based path, run the following command to change the log to the text file created in step 11:

        python manage.py setlogfile "$env:SystemDrive\PostMaster\logs\postmaster.log"

28. You may now exit the Python virtual environment:

        deactivate

29. Restart IIS to make sure all the changes take effect:

        iisreset

30. At this point it is highly recommended that you implement SSL before using PostMaster in production.

31. PostMaster should now be running. Simply use the username "admin" and the password "PostMaster" to login.
You can change your username and password from Manage -> Administrators.

32. Please keep in mind that the C:\PostMaster\git\db\migrations folder should be backed up after installation/updates.
This is because PostMaster uses database migrations to safely upgrade the database schema,
and this folder contains auto-generated database migration scripts that allow you to revert back if a database migration ever failed.
If this folder is missing, PostMaster can't tell what state your database is in, and therefore, cannot revert back.
