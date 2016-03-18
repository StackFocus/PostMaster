# PostMaster Documentation

### Overview

PostMaster is a beautiful web application to manage domains, users, and aliases on a Linux mail server.
After setting up a Linux mail server using the guide from [DigitalOcean](https://www.digitalocean.com/community/tutorials/how-to-configure-a-mail-server-using-postfix-dovecot-mysql-and-spamassassin) or [Linode](https://www.linode.com/docs/email/postfix/email-with-postfix-dovecot-and-mysql),
you start to see how tedious it can be to write raw SQL queries to add a new user to your Linux mail server.
PostMaster abstracts the domain, user, and alias management of your mail server into a responsive web interface, that is both simple to use and secure.

Although PostMaster was built to work with the database schema instructed in the [DigitalOcean](https://www.digitalocean.com/community/tutorials/how-to-configure-a-mail-server-using-postfix-dovecot-mysql-and-spamassassin) or [Linode](https://www.linode.com/docs/email/postfix/email-with-postfix-dovecot-and-mysql) guides,
paid support is available for the developers of PostMaster to customize it to work in your environment.

PostMaster is written by Kevin Law and Matthew Prahl.

### Features

* Add, remove, edit, or search domains, users, and aliases on a Linux mail server database
* Responsive web interface that works great on phones, tablets, and PCs
* Configurable auditing to keep track of changes
* Active Directory LDAP login support
* Friendly REST APIs to automate tasks
* Runs on Linux, Docker, and Windows

### Screenshots

#### Dashboard:
[![Dashboard](imgs/Dashboard.png)](imgs/Dashboard.png)

#### Domains:
[![Domains](imgs/Domains.png)](imgs/Domains.png)

#### Users:
[![Users](imgs/Users.png)](imgs/Users.png)

#### Aliases:
[![Aliases](imgs/Aliases.png)](imgs/Aliases.png)

#### Configurations:
[![Configurations](imgs/Configurations.png)](imgs/Configurations.png)

#### Search:
[![Search](imgs/Search.png)](imgs/Search.png)

#### Mobile:
[![Mobile](imgs/Mobile.png)](imgs/Mobile.png)
