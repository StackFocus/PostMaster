### Prerequisites
1. An Ubuntu 14.04 mail server configured with the guide from [DigitalOcean](https://www.digitalocean.com/community/tutorials/how-to-configure-a-mail-server-using-postfix-dovecot-mysql-and-spamassassin) or [Linode](https://www.linode.com/docs/email/postfix/email-with-postfix-dovecot-and-mysql).
Any other MySQL configuration requires edits to PostMaster's database models. Paid support for this is available.
2. A working Docker host

### MySQL Preparation

1. Start by logging into the MySQL server that your mail server uses:

        mysql -u root -p

2. Once you've logged into MySQL, create a PostMaster MySQL user that has privileges to edit the tables for the servermail database.
Make sure to replace 'docker.postmaster.local' with your Docker host's IP address or DNS:

        GRANT ALL PRIVILEGES ON servermail.* TO 'postmasteruser'@'docker.postmaster.local' IDENTIFIED BY 'password_changeme';

3. Exit from MySQL:

        exit

4. If you are installing PostMaster on a server other than where your mail server's MySQL server is installed, make sure that
bind-address is set 0.0.0.0 and not 127.0.0.1 in:

        /etc/mysql/my.cnf

### Installation

1. Download the PostMaster sourcecode from GitHub:

        git clone https://github.com/StackFocus/PostMaster.git ~/postmaster

2. Build the Docker image:

        cd ~/postmaster
        docker build -t postmaster .

3. Run a PostMaster Docker container from the created image.
The -p has the Docker host serve port 80 of the PostMaster container. Change this to what suits your environment.
The -e specifies the value of the DB_URI environment variable, which is the URI that PostMaster will use to connect to your mail server's MySQL server.
Make sure to replace 'password_changeme' and 'docker.postmaster.local' with what you configured in step 2 of MySQL Preparation:

        docker run -p 0.0.0.0:80:8082 \
             -e DB_URI=mysql://postmasteruser:password_changeme@docker.postmaster.local:3306/servermail -d postmaster

4. PostMaster should now be running. Simply use the username "admin" and the password "PostMaster" to login.
You can change your username and password from Manage -> Administrators.
