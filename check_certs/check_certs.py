#!/usr/bin/python3
from utility import *
from datetime import datetime
import dateutil.parser #  sudo apt install python3-dateutil

EXPIRY = 30
today = datetime.now().date()
one_month_from_now = today + timedelta(days=EXPIRY)

def open_cert(filepath):
  return Command('openssl x509 -noout -text -in {}'.format(filepath)).run(1)

def expiration(cert):
  line = [x for x in cert.split('\n') if 'Not After :' in x][0]
  line = line.split(':', 1)
  return dateutil.parser.parse(line[1].strip()).date()

#c = open_cert('/opt/certificate_authority/intermediate/clients/cert/2024.cert.pem')
#e = expiration(c)

immediately_failing = []
soon_to_fail = []

def check_all_certs(filepath='/opt/certificate_authority/intermediate/clients/cert/'):
  certs = Command('find  {} -type f'.format(filepath)).run(1).split('\n')
  for cert in certs:
    c = open_cert(cert)
    exp = expiration(c)
    cert_id = re.search('Subject.*CN = ([A-Z0-9a-z]*)', c)
    if exp < today:
      immediately_failing.append((exp, cert_id[1]))
    elif exp < one_month_from_now:
      soon_to_fail.append((exp, cert_id[1]))

check_all_certs()

output = ''
#output = 'These certs have already failed. FIX NOW!!!!\n'
#cert_list = sorted(immediately_failing)
#for i in sorted(cert_list):
#  output += 'cert: ' + str(i[1]) + ' -- ' + i[0].strftime('%Y-%m-%d') + '\n'
output += '\n\nThese certs are going to fail in less than ' + str(EXPIRY) + ' days:\n'
cert_list = sorted(soon_to_fail)
for s in sorted(cert_list):
  output += 'cert: ' + str(s[1]) + ' -- ' + s[0].strftime('%Y-%m-%d') + '\n'

# copied the /etc/ssmtp/ssmtp.conf from the appliances, it uses our existing infrastructure:
if any(soon_to_fail):
  Command('echo "{}" | mail -s "Certs going to expire" developers@wipeos.com'.format(output)).run(1)
