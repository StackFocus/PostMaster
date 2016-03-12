<style>
div.wy-nav-content {
    max-width: 1100px;
}
</style>
**Minimum Password Length** specifies the minimum password length that all mail users and administrators must adhere to.

**Login Auditing** determines whether login and logout events are recorded in the log file. In order to enable this, the "Log File" setting must be configured.

**Mail Database Auditing** determines whether changes to domains, users, aliases, administrators, and configuration settings should be recorded in the log file.
In order to enable this, the "Log File" setting must be configured.

**Log File** specifies a file path to where the log file should be. The path can be relative or absolute, but the file location must be writable by the web server.
When configuring this setting, "Mail Database Auditing" will be turned on automatically.

**Enable LDAP Authentication** determines whether Active Directory LDAP authentication is turned on or off. In order to enable LDAP authentication,
the "AD Server LDAP String", "AD Domain", and "AD PostMaster Group" must be configured.

**AD Server LDAP String** specifies the LDAP string used to connect to Active Directory. For instance, if you are using LDAPS and you have a Domain called postmaster.local,
you can specify "LDAPS://postmaster.local:636", since postmaster.local should be a round robin to all of your Domain Controllers. You can also chose to target a specific Domain Controller
such as "LDAPS://dc1.postmaster.local:636". Although not recommended, you can also use LDAP without SSL by specifying something like "LDAP://postmaster.local".

**AD Domain** specifies the fully qualified domain name of your Active Directory Domain (i.e. postmaster.local).

**AD PostMaster Group** specifies the Active Directory group name that Active Directory users must be a member of in order to be an administrator of PostMaster.
This setting's value must be the same as the "Group name (pre-Windows 2000)" value of the desired group as shown in the screenshot below.

[![PostMaster Active Directory Group](../imgs/AD_Group.png)](../imgs/AD_Group.png)
