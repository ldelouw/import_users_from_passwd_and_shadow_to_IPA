# import_users_from_passwd_and_shadow_to_IPA
A script that imports users and password from /etc/passwd and /etc/shadow to (Free) IPA 

Copyright 2016 by Redhat, Inc
Licensed under GPLv3 or later

Author: Luc de Louw <ldelouw@redhat.com>, <luc@delouw.ch>

## About (Free)IPA
FreeIPA (or Redhat Identity Management with IPA) is an open source project to manage identities and the like
such as Users, Hosts, sudoers rules, Host based Access control and so on


See more about IPA on http://www.freeipa.org/page/Main_Page

## Import existing Users from /etc/passwd and /etc/shadow to (Free)IPA

When implementing an IPA environment, you mostly need to migrate existing users. The only automated migration path
is when migrating from an LDAP Server. Migrating from other sources is done by custom scripts done 
your own. This script is about to import old school local system users.
import local users 

Usually local users starts with UIDs 1000. If you need to preserve the UID (not recommended)
you can do so by remove the uidnumber=e.pw_uid from the script. It will be enhanced with 
some input parameter later.

Ensure migration mode is enabled, run the following:

$ ipa config-mod --enable-migration=true 

This is needed to be able to import hashed passwords

## Performance
When using the API, you can expect roughtly 100 users per minute, depending on the hardware (or VM) iof the 
IPA Servers

## Testing
You may want to test this script in a test environment before using it in the production envirtonment. 
This repo also provided the mkusers.sh script which creates a bulk amount of users

## Limitations
At this stage the script is not very smart, i.e. First and Last name must be available in the GECOS field in 
the form of "Fistname Lastname". When you have users with middlenames you will experience funny results.

At the moment the script expects a password hash algorithm supported by crypt(3) see also $man 3 crypt
this are:

* MD5 
* SHA256
* SHA512

As soon as I have more time, I'll enhance the script. You are welcome to contribute as well, its Opensource :-)

