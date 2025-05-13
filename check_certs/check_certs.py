#!/usr/bin/python3
from utility import *
import dateutil.parser #  sudo apt install python3-dateutil

today = datetime.now().date()
one_month_from_now = today + timedelta(days=30)

def open_cert(filepath):
  return Command('openssl x509 -noout -text -in {}'.format(filepath)).run(1)

def expiration(cert):
  line = [x for x in cert.split('\n') if 'Not After :' in x][0]
  line = line.split(':', 1)
  return dateutil.parser.parse(line[1].strip()).date()


#c = open_cert('/opt/certificate_authority/intermediate/clients/cert/2024.cert.p
em')
#e = expiration(c)

immediately_failing = []
soon_to_fail = []


'''
Yeah, this sucks! but we need to have this for sanity's sake
it works, its written this way because i needed to get something done quick
'''

def check_all_certs(filepath='/opt/certificate_authority/intermediate/clients/cert/'):
  certs = Command('find  {} -type f'.format(filepath)).run(1).split('\n')
  for cert in certs:
    c = open_cert(cert)
    exp = expiration(c)
    cert_id = re.findall('CN = [0-9]{4}', c)
    if cert_id:
      cert_id = cert_id[0].split(' = ')[-1]
    else:
      cert_id = 'unknown'
    if exp < today:
      p('{}, {}'.format(cert_id, exp))
      immediately_failing.append('{}, {}'.format(cert_id, exp))
    elif exp < one_month_from_now:
      p('{}, {}'.format(cert_id, exp))
      soon_to_fail.append('{}, {}'.format(cert_id, exp))

check_all_certs()

output = 'These certs are going to fail in less than 30 days:\n'
output += '\n'.join(soon_to_fail)
# copied the /etc/ssmtp/ssmtp.conf from the appliances, it uses our existing infrastructure:
if any(soon_to_fail):
  Command('echo "{}" | mail -s "Certs going to expire" developers@wipeos.com'.format(output)).run(1)
