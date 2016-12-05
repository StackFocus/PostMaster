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

2. To download Python, run the following command:

        Invoke-WebRequest -Uri 'https://www.python.org/ftp/python/3.5.2/python-3.5.2-amd64.exe' -OutFile "$env:SystemDrive\python-3.5.2-amd64.exe"

3. To install Python, run the following command:

        Start-Process "$env:SystemDrive\python-3.5.2-amd64.exe" -ArgumentList @('/quiet', 'InstallAllUsers=1', 'PrependPath=1', 'Include_test=0') -Wait

4. To remove the Python installation file, run the following command:

        Remove-Item "$env:SystemDrive\python-3.5.2-amd64.exe" -Force

5. To be able to run Python without specifying a path, add Python to your Path environment variable with the following command, or close and reopen PowerShell:

        if (-not ($env:Path -like "*$env:SystemDrive\Program Files\Python3*")) {$env:Path = "$env:SystemDrive\Program Files\Python35\Scripts\;$env:SystemDrive\Program Files\Python35\;" + $env:Path}

6. To create a directory for PostMaster, run the following command:

        New-Item "$env:SystemDrive\PostMaster" -Type 'Directory'

7. Find the URL to the latest zip file containing the PostMaster source code at:

        https://github.com/StackFocus/PostMaster/releases/latest

8. Then download PostMaster with the URL from the previous step, with the following command (replace the URL with the correct one):

        Invoke-WebRequest 'https://github.com/StackFocus/PostMaster/archive/[release version].zip' -OutFile "$env:SystemDrive\postmaster.zip"

9. Then unzip the downloaded zip file with the following commands:

        Add-Type -AssemblyName 'System.IO.Compression.FileSystem'
        [System.IO.Compression.ZipFile]::ExtractToDirectory("$env:SystemDrive\postmaster.zip", "$env:SystemDrive\PostMaster")

10. Rename the folder containing the downloaded source code to C:\PostMaster\git:

        $folder = Get-ChildItem "$env:SystemDrive\PostMaster" | Where-Object {$_.Name -like "*PostMaster-*"} | Select-Object -First 1
        Rename-Item $folder.FullName "$env:SystemDrive\PostMaster\git"

11. Delete the downloaded zip file:

        Remove-Item "$env:SystemDrive\postmaster.zip" -Force

12. Create a directory to contain PostMaster logs:

        New-Item "$env:SystemDrive\PostMaster\logs" -Type 'Directory'

13. PostMaster will write logs to C:\PostMaster\logs\postmaster.log, but since IIS does not have access to create that file, it must be done manually with the following command:

        New-Item "$env:SystemDrive\PostMaster\logs\postmaster.log" -Type 'File'

14. In order for PostMaster to be able to write to the log file created earlier, IIS requires write access. To do so, use the following command:

        cmd.exe /C "icacls $env:SystemDrive\PostMaster\logs\postmaster.log /grant BUILTIN\IIS_IUSRS:(M)"

15. In order for PostMaster's files to be secured, the proper permissions must be set. The following command will grant only IIS read access,
and Administrators full control on PostMaster's files:

        cmd.exe /C "icacls $env:SystemDrive\PostMaster /inheritance:r /grant BUILTIN\IIS_IUSRS:(OI)(CI)(RX) /grant BUILTIN\Administrators:(OI)(CI)F /grant SYSTEM:(OI)(CI)(F)"

16. A python virtual environment is now required. This allows you to separate the system installed python packages from PostMaster's required python packages.
This is done with the following command:

        & "$env:SystemDrive\Program Files\Python35\Scripts\pip.exe" install virtualenv

17. Create a Python virtualenv for PostMaster with the following commands:

        & "$env:SystemDrive\Program Files\Python35\Scripts\virtualenv.exe" "$env:SystemDrive\PostMaster\env"

18. To use the newly created virtual environment in your PowerShell window, run the following command:

        & "$env:SystemDrive\PostMaster\env\Scripts\activate.ps1"

19. Install the Python packages that PostMaster requires with the following commands:

        pip install -r "$env:SystemDrive\PostMaster\git\requirements.txt"
        pip install wfastcgi

20. Create the PostMaster configuration file from using the sample file that was included:

        Copy-Item "$env:SystemDrive\PostMaster\git\config.default.py" "$env:SystemDrive\PostMaster\git\config.py"

21. Copy wfastcgi.py, created by Microsoft Web Platform Installer earlier, to C:\PostMaster\git:

        Copy-Item "$env:SystemDrive\PostMaster\env\Lib\site-packages\wfastcgi.py" "$env:SystemDrive\PostMaster\git"

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
        Add-WebConfiguration -Filter "/system.webServer/fastCgi/application[@fullPath='$env:SystemDrive\PostMaster\env\Scripts\python.exe' and @arguments='$env:SystemDrive\PostMaster\git\wfastcgi.py']/environmentVariables" -Value @{name='WSGI_HANDLER'; value='postmaster.app'} -AtIndex 1

24. PostMaster needs to be configured to connect to the MySQL database using the MySQL user created in step 2 of MySQL Preparation.
Make sure to replace "password_changeme" with the actual value supplied in step 2 of MySQL Preparation, and
replace '127.0.0.1' with the IP address or DNS specified in step 2 of MySQL Preparation:

        Set-Location 'C:\Postmaster\git'
        python manage.py setdburi 'mysql+pymysql://postmasteruser:password_changeme@127.0.0.1:3306/servermail'

25. PostMaster needs to create a few tables under the servermail database. This is done via a database migration,
which means that only the necessary changes to the database are made, and these changes are reversible if something went wrong.
To start the migration, run the following command:

        python manage.py upgradedb

26. PostMaster uses a secret key for certain cryptographic functions. To generate a random key, run the following command:

        python manage.py generatekey

27. By deafult, PostMaster logs to a Linux based path, run the following command to change the log to the text file created in step 11
(note that forward slashes must be used instead of backslashes):

        python manage.py setlogfile "$env:SystemDrive/PostMaster/logs/postmaster.log"

28. You may now exit the Python virtual environment:

        deactivate

29. Restart IIS to make sure all the changes take effect:

        iisreset

30. At this point it is highly recommended that you implement SSL before using PostMaster in production.

31. PostMaster should now be running. Simply use the username "admin" and the password "PostMaster" to login.
You can change your username and password from Manage -> Administrators.
