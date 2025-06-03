import mysql.connector
from mysql.connector import pooling
from bottle import route, run, request, response
import logging
import time
import math
import shlex
import json
from db_login import DB_CREDENTIALS

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
        self.pool = mysql.connector.pooling.MySQLConnectionPool(pool_name="mypool", pool_size=5, **DB_CREDENTIALS)

@route('/up')
def is_up():
    return {"status":"up"}

@route('/insert_wipebox', method='POST')
def insert_wipebox():
    try:
        data = request.json
        logger.info("Data received for insert_wipebox: {}".format(data))
        logger.info(db.version_hashes)
        certificate = data.get('cert')
        version_id = data.get('hash')
        last_update = data.get('last_update')
        logger.info("Inserting wipebox with cert: %s, version hash: %s, version index: %s, last_update: %s", certificate, version_id,db.version_hashes[version_id], last_update)
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO wipebox (cert, version_id, last_update) VALUES (%s, %s, %s)", (certificate, db.version_hashes[version_id], last_update))
        conn.commit()
        cursor.close()
        conn.close()
    except Exception as e:
        logger.error("Error inserting wipebox: %s", str(e))
        response.status = 500
        return {"status": "error", "message": str(e)}
    logger.info("Wipebox inserted successfully with cert: %s", certificate)
    return {"status": "success", "cert": certificate}

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

@route('/insert_disk_usage/', method='POST')
def insert_disk_usage():
    data = request.json
    mount_point = data.get('mount_point')
    size = data.get('size')
    used = data.get('used')
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO disk_usage (mountpoint, size, used) VALUES (%s, %s, %s)", (mount_point, size, used))
    conn.commit()
    cursor.close()
    conn.close()
    return {"status": "success", "mountpoint": mountpoint}

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
    version_hashes = {}
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
    run(host='0.0.0.0', port=8090, debug=True, quiet=True,reload=True)