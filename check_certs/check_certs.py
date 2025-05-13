#!/usr/bin/python3
import subprocess
import os
import re
import datetime
import dateutil.parser
import psycopg2
import requests
import json
import logging

SERVER = 'login.wipeos.com'
PORT = 17771
ENDPOINT = 'send_email'
EXPIRY = 30
today = datetime.datetime.now().date()
one_month_from_now = today + datetime.timedelta(days=EXPIRY)

logging.basicConfig(filename='check_certs.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
check_certs_logger = logging.getLogger('check_certs')

def list_files_by_type(directory, extension):
    files_of_type = [
        os.path.join(directory, f)
        for f in os.listdir(directory)
        if os.path.isfile(os.path.join(directory, f)) and f.lower().endswith(extension.lower())
    ]
    return files_of_type

def open_cert(filepath):
  return subprocess.check_output(['openssl', 'x509', '-noout', '-text', '-in', filepath]).decode('utf-8')

def expiration(cert):
  line = [x for x in cert.split('\n') if 'Not After :' in x][0]
  line = line.split(':', 1)
  return dateutil.parser.parse(line[1].strip()).date()

immediately_failing = []
soon_to_fail = []

def check_all_certs(filepath='/home/rfkmartin/certs'):
  certs = list_files_by_type(filepath, ".pem")
  for cert in certs:
    c = open_cert(cert)
    exp = expiration(c)
    cert_id = re.search('Subject.*CN = ([A-Z0-9a-z]*)', c)
    if exp < today:
      immediately_failing.append((exp, cert_id[1]))
    elif exp < one_month_from_now:
      soon_to_fail.append((exp, cert_id[1]))

check_all_certs()

body = '<html><h2>These certs are going to fail in less than {} days:</h2>'.format(EXPIRY)
try:
  connection = psycopg2.connect(
      host="login.wipeos.com",
      database="wipeos_portal",
      user="wipeos",
      password="WiPe332"
  )
  cursor = connection.cursor()

  body += '<br><table border="1"><tr><th align ="left">Company</th><th align ="left">Wipebox</th><th align ="left">Cert</th><th align ="left">Expiration Date</th><th align ="left">Last Sync</th></tr>'
  cert_list = sorted(soon_to_fail)
  for s in sorted(cert_list):
    cursor.execute("SELECT name,system_id,(select value from wipers_settings where setting='siteid' and system_id=ww.system_id),last_sync from wipers_wipebox ww join account_account aa on aa.id=ww.account_id where system_id={}".format(s[1]))
    last_sync = cursor.fetchall()
    for l in last_sync:
      body += '<tr><td align ="left">{}</td><td align ="left">{}</td><td align ="left">{}</td><td align ="left">{}</td><td align ="left">{}</td></tr>'.format(l[0],l[2],s[1],s[0].strftime('%Y-%m-%d'),l[3].strftime('%Y-%m-%d'))
  body += '</table></html>'
  data = {"to": "rfkmartin@gmail.com","subject": "Appliance Certificate Expiration Check", "body": body, "mimetype": "html"}
  headers = {"Content-Type": "application/json"}
  json_data = json.dumps(data)
  dest = 'http://{}:{}/{}'.format(SERVER, PORT, ENDPOINT)
  try:
        response = requests.post(dest, data=json_data, headers=headers)
        check_certs_logger.info("Response: {}, {}".format(response.status_code, response.text))
  except Exception as e:
      check_certs_logger.error("An unexpected error occurred: {}".format(e))
      check_certs_logger.info("FAILURE: {}".format(json_data))
except psycopg2.Error as error:
    check_certs_logger.error("Error while connecting to PostgreSQL", error) #error checking for actual connection?
    check_certs_logger.info("FAILURE: {}".format(json_data))
finally: #end closing connection
    if connection:
        cursor.close()
        connection.close()
