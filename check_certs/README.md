# check_certs
## Server
folklore/10.3.3.39
## Location
/home/user/bin
## Run
cron job via user crontab ( 0 4 * * * /home/user/bin/check_certs )
## Description
This finds the expiration of all certificates ever created and creates a list of those expiring within EXPIRY days. This list of wipeboxes is then used to gather more information like company name, wipebox name, and last sync and then this list is sent to developers@wipeos.com
