#!/usr/bin/python
#
# Copyright 2016 by Redhat, Inc
# Licensed under GPLv3 or later
#
# Author: Luc de Louw <ldelouw@redhat.com>, <luc@delouw.ch>
#
# This Script imports users from /etc/passwd and /etc/shadow to IPA
# Usually users start with an UID of 1000, so lets start importing
# with UIDs greater that 1000.
# 
# Ensure you run ipa config-mod --enable-migration=true to be able to add 
# password hashes to a user
#
# Check whether your crypted passwords are supported:
# ldapsearch -D "cn=directory manager" -W -x -s sub -b "cn=password storage schemes,cn=plugins,cn=config" |grep cn:
#
# Note: Despite userpassword={crypt}% is used when adding the user, its still the orginal hashing algo as long
# See also crypt(3) -> man 3 crypt

import pwd
import spwd
import os
import datetime
from ipalib import api, errors

# Do not import users which have not changed its password since number of days
# Set it to a very high value to import all users i.e. 999999
max_days_since_last_pw_change=90

# Makes sense right? /etc/shadow must only be readable by root
if os.getuid() != 0:
	print "This script must be run as root"
	sys.exit()

# Initialize the API connection
api.bootstrap(context='cli')
api.finalize()
api.Backend.rpcclient.connect()

# Did not figured out a better way who to calculate the
# difference between today since epoch and the last passwd change
epoch = datetime.datetime.utcfromtimestamp(0)
today = datetime.datetime.today()
today_since_epoch = today - epoch

entries = pwd.getpwall()
for e in entries:
	if e.pw_uid < 1000:
		continue
		# nfsnobody has UID 65534, we do not want to add this user to IPA
		# Add more filtes as needed
	if e.pw_name == 'nfsnobody':
		continue

        # Empty GECOS? No way!
	if e.pw_gecos == '':
		print 'Format of the GECOS field should be <Firstname> <Lastname>,  user "%s". Skipped' % e.pw_name
		continue
	if today_since_epoch.days-spwd.getspnam(e.pw_name).sp_lstchg > max_days_since_last_pw_change:
		print "User inactive since too long time, not importing"
		continue

	# If the Format of the GECOS field is something else that <Firstname> <Lastname>, you will get funny results,
	# You probably want to normalize the GECOS before or after the import
	# All content after the first space in the GECOS is considered as Lastname
	name = e.pw_gecos.split(None)
	passhash = spwd.getspnam(e.pw_name).sp_pwd

	uid=unicode(e.pw_name,"utf-8")
	givenname=unicode(name[0],"utf-8")
	sn=unicode(name[1],"utf-8")
	homedir=unicode(e.pw_dir,"utf-8")
	shell=unicode(e.pw_shell,"utf-8")

	result=api.Command['user_add'](uid,givenname=givenname,sn=sn,uidnumber=e.pw_uid,gidnumber=e.pw_gid,loginshell=shell,homedirectory=homedir,addattr=u'userPassword={crypt}%s' % passhash)
