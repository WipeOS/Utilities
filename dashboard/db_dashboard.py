import mysql.connector
from mysql.connector import pooling
from bottle import route, run, request, response
import logging
import time
import math
import shlex
import json
from db_login import DB_CREDENTIALS
from db_portal_login import PORTAL_CREDENTIALS
import psycopg2

logging.basicConfig(filename='db.log', encoding='utf-8', level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
logger = logging.getLogger('database')

class DB:
    def __init__(self):
        self.settings = {}
        self.wipeboxes = []
        self.versions = []
        self.version_hashes = {}
        self.repo_index = {}
        self.mount_points = []
        self.db_portal_info = {}
        self.pool = mysql.connector.pooling.MySQLConnectionPool(pool_name="mypool", pool_size=5, **DB_CREDENTIALS)

@route('/up')
def is_up():
    return {"status":"up"}
@route('/get_update_info')
def get_update_info():


@route('/get_portal_info')
def get_portal_info():
    try:
        connection = psycopg2.connect(
            host="login.wipeos.com",
            database="wipeos_portal",
            user="wipeos",
            password="WiPe332"
        )
        cursor = connection.cursor()
        cursor.execute("SELECT row_to_json(t) FROM (SELECT name,system_id,(select value from wipers_settings where setting='siteid' and system_id=ww.system_id),to_char(last_sync, 'YYYY/MM/DD HH24:MI:SS') as last_sync,version from wipers_wipebox ww join account_account aa on aa.id=ww.account_id where last_sync>=current_date-90) t")
        result = cursor.fetchall()
        all_boxes_last_90_days = []
        for r in result:
            all_boxes_last_90_days.append(r[0])
        return {"status": "success", "data": all_boxes_last_90_days}
    except psycopg2.Error as error:
        logger.error("Error while connecting to PostgreSQL", error) #error checking for actual connection?
        return {"status": "failure", "message": str(error)}
    finally: #end closing connection
        if connection:
            cursor.close()
            connection.close()

@route('/insert_wipebox', method='POST')
def insert_wipebox():
    try:
        data = request.json
        certificate = data.get('cert')
        version_id = data.get('hash')
        last_update = data.get('last_update')
        logger.info("Inserting wipebox with cert: %s, version hash: %s, version index: %s, last_update: %s", certificate, version_id,db.version_hashes[version_id], last_update)
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO wipebox (cert, version_id, last_update) VALUES (%s, %s, %s)", (certificate, db.version_hashes[version_id], last_update))
        last_row_id = cursor.lastrowid
        conn.commit()
        cursor.close()
        conn.close()
    except Exception as e:
        logger.error("Error inserting wipebox: %s", str(e))
        response.status = 500
        return {"status": "error", "message": str(e)}
    logger.info("Wipebox inserted successfully with cert: %s", certificate)
    return {"status": "success", "cert": certificate, "id": last_row_id}

def get_unique_wipeboxes():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT distinct(cert) FROM wipebox")
    results = cursor.fetchall()
    wipeboxes = []
    for r in results:
        wipeboxes.append(r)
    cursor.close()
    conn.close()
    return wipeboxes

@route('/insert_version/<version_string>')
def insert_version(version_string):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO version (version_string) VALUES (%s)", (version_string,))
    conn.commit()
    last_row_id = cursor.lastrowid
    cursor.close()
    conn.close()
    return {"status": "success", "version": version_string, "id": last_row_id}

@route('/insert_repo_version/<repo_id>/<version_id>/<hash>')
def insert_version(repo_id, version_id, hash):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO repo_version (repository_id,version_id,hash) VALUES (%s,%s,%s)", (repo_id,version_id,hash))
    conn.commit()
    cursor.close()
    conn.close()
    return {"status": "success"}

@route('/does_version_exist/<version_string>')
def does_version_exist(version_string):
    exists = version_string in db.versions
    response.status = 200
    response.set_header('Content-Type', 'text/plain')
    return str(exists)

def get_unique_versions():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT distinct(version_string) FROM version")
    results = cursor.fetchall()
    versions = []
    for r in results:
        versions.append(r[0])
    cursor.close()
    conn.close()
    return versions

@route('/insert_disk_usage', method='POST')
def insert_disk_usage():
    data = request.json
    wipebox_id = data.get('wipebox_id')
    mount_point = data.get('mount_point')
    if mount_point not in db.mount_points:
        response.status = 400
        return {"status": "error", "message": "Mount point not found"}
    total = data.get('total')
    used = data.get('used')
    available = data.get('available')
    percent_used = data.get('percent_used')
    try:
        conn = get_db()
        cursor = conn.cursor()
        logger.info("Inserting disk usage for wipebox_id: %s, mount_point: %s, total: %s, used: %s, available: %s, percent_used: %s", wipebox_id, mount_point, total, used, available, percent_used)
        cursor.execute("INSERT INTO disk_usage (wipebox_id,mount_point_id, total, used, available, percent_used) VALUES (%s, %s, %s, %s, %s, %s)", (wipebox_id, db.mount_points[mount_point], total, used, available, percent_used))
        conn.commit()
        cursor.close()
        conn.close()
        return {"status": "success"}
    except Exception as e:
        logger.error("Error inserting disk usage: %s", str(e))
        response.status = 500
        return {"status": "error", "message": str(e)}

@route('/insert_generic_config', method='POST')
def insert_generic_config():
    data = request.json
    wipebox_id = data.get('wipebox_id')
    name = data.get('name')
    value = data.get('value')
    try:
        conn = get_db()
        cursor = conn.cursor()
        logger.info("Inserting generic config for wipebox_id: %s, name: %s, value: %s", wipebox_id, name, json.dumps(value))
        cursor.execute("INSERT INTO generic_config (wipebox_id, name, value) VALUES (%s, %s, %s)", (wipebox_id, name, json.dumps(value)))
        conn.commit()
        return {"status": "success"}
    except Exception as e:
        logger.error("Error inserting generic config: %s", str(e))
        response.status = 500
        return {"status": "error", "message": str(e)}
    finally:
        cursor.close()
        conn.close()

def get_mount_points():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT mount_point_id,mount_point FROM mount_point")
    results = cursor.fetchall()
    mountpoints = {}
    for r in results:
        mountpoints[r[1]] = r[0]
    cursor.close()
    conn.close()
    return mountpoints

@route('/get_repo_index/<repo>')
def get_repo_index(repo):
    response.status = 200
    response.set_header('Content-Type', 'text/plain')
    return str(db.repo_index[repo])

@route('/does_version_hash_exist/<hash>')
def does_version_hash_exist(hash):
    exists = hash in db.version_hashes
    response.status = 200
    response.set_header('Content-Type', 'text/plain')
    return str(exists)

@route('/update_versions')
def update_versions():
    db.versions = get_unique_versions()
    db.version_hashes = get_version_hashes()
    logger.info("Versions: %s", db.versions)
    logger.info("Version Hashes: %s", db.version_hashes)

def get_repo_indices():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("select repository_id,repo_name from repository")
    results = cursor.fetchall()
    repository_index = {}
    for r in results:
        repository_index[r[1]] = r[0]
    cursor.close()
    conn.close()
    return repository_index

def get_version_hashes():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("select version_id,group_concat(hash order by repository_id separator '') from repo_version group by version_id")
    results = cursor.fetchall()
    version_hashes = {'-1': 1}
    for r in results:
        version_hashes[r[1]] = r[0]
    cursor.close()
    conn.close()
    return version_hashes

def get_db():
    conn = db.pool.get_connection()
    return conn

if __name__ == '__main__':
    db = DB()
    db.wipeboxes = get_unique_wipeboxes()
    logger.info("Wipeboxes: %s", db.wipeboxes)
    db.versions = get_unique_versions()
    logger.info("Versions: %s", db.versions)
    db.version_hashes = get_version_hashes()
    logger.info("Version Hashes: %s", db.version_hashes)
    db.repo_index = get_repo_indices()
    logger.info("Repository Index: %s", db.repo_index)
    db.mount_points = get_mount_points()
    logger.info("Mount Points: %s", db.mount_points)
    db.db_portal_info = get_portal_info()
    run(host='0.0.0.0', port=8090, debug=True, quiet=True,reloader=True)