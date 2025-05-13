# wipeos_email_daemon
## Server
portal/login.wipeos.com
## Location
/home/rmartin/sendmail
## Run
service via /etc/systemd/system/wipeos-email.service
## Description
This is a lightweight bottle service that listens on port 17771 for incoming JSON messages. The JSON has 4 fields:
1. to
2. subject
3. body(html format allowed)
4. mimetext(default plain)

and this email is send using the alerts@wipeos.com account via the Google SMTP server.
