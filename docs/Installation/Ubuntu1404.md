### Prerequisites
1. An Ubuntu 14.04 mail server configured with the guide from [DigitalOcean](https://www.digitalocean.com/community/tutorials/how-to-configure-a-mail-server-using-postfix-dovecot-mysql-and-spamassassin) or [Linode](https://www.linode.com/docs/email/postfix/email-with-postfix-dovecot-and-mysql).
Any other MySQL configuration requires edits to PostMaster's database models. Paid support for this is available.
2. If you are installing PostMaster on a separate server, you'll need a clean Ubuntu 14.04 installation.

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

### Package Installation
The PostMaster package can be found on Bintray at [https://bintray.com/stackfocus/deb/PostMaster](https://bintray.com/stackfocus/deb/PostMaster)

This installation method works best on a fresh installation of the operating system.

1. Run this command to add to the `/etc/apt/sources.list`:

        echo "deb https://dl.bintray.com/stackfocus/deb {distribution} {components}" | sudo tee -a /etc/apt/sources.list

2. Install the PostMaster package:

        apt-get update && apt-get install postmaster

3. Start using the new python virtual environment that PostMaster created

        source /opt/postmaster/env/bin/activate

4. PostMaster needs to be configured to connect to the MySQL database using the MySQL user created in step 2 of MySQL Preparation.
Make sure to replace "password_changeme" with the actual password supplied in step 2 of MySQL Preparation, and if needed,
replace '127.0.0.1' with the IP address or DNS specified in step 2 of MySQL Preparation:

        cd /opt/postmaster/git
        python manage.py setdburi 'mysql://postmasteruser:password_changeme@127.0.0.1:3306/servermail'

5. PostMaster needs to create a few tables under the servermail database. This is done via a database migration,
which means that only the necessary changes to the database are made, and these changes are reversible if something went wrong.
To start the migration, run the following command:

        python manage.py createdb

 - If you are coming from an existing database with `virtual_users`, `virtual_domains`, and `virtual_aliases` tables (you followed the mailserver setup guides at the top), then run this command instead of the above:  
   `python manage.py existingdb`  

6. PostMaster uses a secret key for certain cryptographic functions. To generate a random key, run the following command:

        python manage.py generatekey

7. You may now exit from the python virtual environment:

        deactivate

8. PostMaster should now be running on port 8082. Simply use the username "admin" and the password "PostMaster" to login.
You can change your username and password from Manage -> Administrators.

### Manual Installation
1. Switch to the server that will host PostMaster if applicable, and login as root:

        sudo su -

2. Update the aptitude package list:

        apt-get update

3. Install the required packages for PostMaster:

        apt-get install git python python-pip python-dev libldap2-dev libssl-dev libsasl2-dev libffi-dev apache2 libapache2-mod-wsgi mysql-server libmysqlclient-dev

4. Make sure you are running Python 2.7 as your default Python installation, as PostMaster relies on Python 2.7:

        python -V

5. Create the required directories for PostMaster:

        mkdir /opt/postmaster
        mkdir /opt/postmaster/logs
        mkdir /opt/postmaster/git

6. Download the PostMaster sourcecode from GitHub:

        git clone https://github.com/StackFocus/PostMaster.git /opt/postmaster/git

7. A python virtual environment is now required.
This allows you to separate the system installed python packages from PostMaster's required python packages:

        pip install virtualenv
        virtualenv /opt/postmaster/env

8. Start using the new python virtual environment

        source /opt/postmaster/env/bin/activate

9. Install the Python packages required by PostMaster into the python virtual environment:

        cd /opt/postmaster/git
        pip install -r requirements.txt

10. PostMaster needs to be configured to connect to the MySQL database using the MySQL user created in step 2 of MySQL Preparation.
Make sure to replace "password_changeme" with the actual password supplied in step 2 of MySQL Preparation, and if needed,
replace '127.0.0.1' with the IP address or DNS specified in step 2 of MySQL Preparation:

        cd /opt/postmaster/git
        python manage.py setdburi 'mysql://postmasteruser:password_changeme@127.0.0.1:3306/servermail'

11. PostMaster needs to create a few tables under the servermail database. This is done via a database migration,
which means that only the necessary changes to the database are made, and these changes are reversible if something went wrong.
To start the migration, run the following command:

        python manage.py createdb

 - If you are coming from an existing database with `virtual_users`, `virtual_domains`, and `virtual_aliases` tables (you followed the mailserver setup guides at the top), then run this command instead of the above:  
   `python manage.py existingdb`  

12. PostMaster uses a secret key for certain cryptographic functions. To generate a random key, run the following command:

        python manage.py generatekey

13. You may now exit from the python virtual environment:

        deactivate

14. Provide the proper permissions on the PostMaster files:

        chown -R www-data:www-data /opt/postmaster
        chmod -R 550 /opt/postmaster
        chmod 770 /opt/postmaster/logs

15. Disable the default Apache site:

        a2dissite 000-default.conf

16. Copy the default PostMaster Apache site configuration and give it the appropriate permissions.
It is highly recommended that you implement SSL before using PostMaster in production:

        cp /opt/postmaster/git/ops/apache.conf /etc/apache2/sites-available/postmaster.conf
        chmod 644 /etc/apache2/sites-available/postmaster.conf
        chown root:root /etc/apache2/sites-available/postmaster.conf

17. Enable the PostMaster Apache site:

        a2ensite postmaster.conf

18. Restart Apache for the changes to take effect:

        service apache2 restart

19. PostMaster should now be running. Simply use the username "admin" and the password "PostMaster" to login.
You can change your username and password from Manage -> Administrators.

20. Please keep in mind that the /opt/postmaster/git/db/migrations folder should be backed up after installation/updates.
This is because PostMaster uses database migrations to safely upgrade the database schema,
and this folder contains auto-generated database migration scripts that allow you to revert back if a database migration ever failed.
If this folder is missing, PostMaster can't tell what state your database is in, and therefore, cannot revert back.
