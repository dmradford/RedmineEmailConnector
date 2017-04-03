# RedmineEmailConnector

This simple email connector for Redmine will transfer emails from an external email server, such as Gmail, to your internal Redmine server.

This application is designed to run on a schedule such as a cron job.

As this was originally designed as an in-house tool, some configuration will be required for your email settings. At this time, this configuration is within the code file itself "connector.py".

Custom settings must be configured in the following files and lines of code:

UserEmails.txt. This file is not required, however if not used, ever email will be sent to redmine from the Default email, set in connector.py
UserEmails should be configured as 1 user per line with a uniquely identifying part of the "From" name whe you send an email followed by a comma, then your internal email address as configured in your Redmine instance. For example, if your From is configured as "MyCompany | John Doe" and your internal email is "jdoe@myIntranet.intranet", the first line of this file would read:

| John Doe, jdoe@myIntranet.intranet

connector.py. You will need to input your email settings into the following lines:

Line 79: Default internal "From" address for Redmine, typically this should be set to a non-user administrator, likely dedicated to this connector
Lines 123-137: These settings determine your external mail server and which folders to search within for emails. Default settings should work with Gmail, though you will still have to configure lines 123-125 with your specific settings
Line 140: This is simply the "To" address that you have configured to receive Redmine emails
