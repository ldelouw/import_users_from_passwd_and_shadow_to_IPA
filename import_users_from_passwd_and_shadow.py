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
# Note: Despite userpassword={crypt}% is used when adding the user, its still SHA512

import pwd
import spwd
from ipapython.ipautil import run
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

	# If the Format of the GECOS field is something else that <Firstname> <Lastname>, you will get funny results,
	# You probably want to normalize the GECOS before or after the import
	# All content after the first space in the GECOS is considered as Lastname
	name = e.pw_gecos.split(None)
	passhash = spwd.getspnam(e.pw_name).sp_pwd
	#passhash = spwd.getspnam("root").sp_pwd

	args = ['/usr/bin/ipa', 'user-add',
            '--first', name[0],
            '--last', ' '.join(name[1:]),
            '--homedir', e.pw_dir,
            '--shell', e.pw_shell,
            '--setattr', 'uidnumber=%d' % e.pw_uid,
            '--setattr', 'gidnumber=%d' % e.pw_gid,
            '--setattr', 'userpassword={crypt}%s' % passhash,
            e.pw_name]

	print args
	(stdout, stderr, rc) = run(args, raiseonerr=False)

	if rc != 0:
		print 'User "%s" failed to add: %s' % (e.pw_name, stderr)
	else:
		print 'Successfully added User"%s"' % e.pw_name
