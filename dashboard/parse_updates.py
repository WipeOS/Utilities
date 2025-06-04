import glob
import requests
import json
import os
import time
import datetime

headers = {"Content-Type": "application/json"}

def get_appliances():
    appliances = []
    pattern = "*_update.txt" # Example pattern: all text files
    for name in sorted(glob.glob(pattern)):
        timestamp = os.path.getmtime(name)
        last_mod_time = datetime.datetime.fromtimestamp(timestamp)
        appliances.append((name[:4], last_mod_time.strftime("%Y-%m-%d %H:%M:%S")))
    return appliances

def get_versions():
    versions = []
    pattern = "version_*.txt"
    for name in sorted(glob.glob(pattern)):
        filename = name.split(".")
        filename_no_extension = ".".join(filename[:-1])
        version = filename_no_extension[8:]
        versions.append(version)
        # for ech version check if it is in db, if not continue
        # reading file and put into repo_version table
        dest = 'http://{}:{}/{}/{}'.format('localhost', '8090', "does_version_exist", version)
        try:
            response = requests.get(dest, headers=headers)
            if response.text != "True":
                dest = 'http://{}:{}/{}/{}'.format('localhost', '8090', "insert_version", version)
                response = requests.get(dest, headers=headers)
                resp = json.loads(response.text)
                version_id = resp['id']
                with open(name, 'r') as file:
                    lines = file.readlines()
                for l in lines:
                    line = l.strip().split(": ")
                    dest = 'http://{}:{}/{}/{}'.format('localhost', '8090', "get_repo_index", line[0])
                    response = requests.get(dest, headers=headers)
                    repo_id = response.text
                    dest = 'http://{}:{}/{}/{}/{}/{}'.format('localhost', '8090', "insert_repo_version", repo_id, version_id, line[1])
                    response = requests.get(dest, headers=headers)
                versions.append(version)
        except Exception as e:
            print("An unexpected error occurred: {}".format(e))
            print("FAILURE: {}".format(json_data))
    dest = 'http://{}:{}/{}'.format('localhost', '8090', "update_versions")
    response = requests.get(dest, headers=headers)
    return versions

def get_version_hash(appliance):
    filename = "{}_update.txt".format(appliance)
    # if first line is not PRD, then return []
    # if first line is PRD, the go through next lines, get repo_id from db obj and return hash for that repo
    try:
        with open(filename, 'r') as file:
            lines = file.readlines()
        if lines[0].strip() != "PRD":
            return ""
        repo_list = {}
        for line in range(1, len(lines)):
            repo = lines[line].strip().split(": ")
            dest = 'http://{}:{}/{}/{}'.format('localhost', '8090', "get_repo_index", repo[0])
            try:
                response = requests.get(dest, headers=headers)
            except Exception as e:
                print("An unexpected error occurred: {}".format(e))
                print("FAILURE: {}".format(json_data))
            repo_list[int(response.text)] = repo[1]
        sorted_repo_list = sorted(repo_list.items(), key=lambda x: x[0])
        hash = ""
        for r in sorted_repo_list:
            hash += r[1]
        return hash
    except FileNotFoundError:
        return "File not found."

def update_disk_usage(appliance, wipebox_id):
    filename = "{}_diskusage.txt".format(appliance)
    try:
        with open(filename, 'r') as file:
            lines = file.readlines()
        for line in lines[1:]:
            mountpt = line.strip().split()
            total = mountpt[1][:-1]
            used = mountpt[2][:-1]
            available = mountpt[3][:-1]
            percent_used = mountpt[4][:-1] 
            mount_point = mountpt[5]
            dest = 'http://{}:{}/{}'.format('localhost', '8090', "insert_disk_usage")
            data = {"wipebox_id": wipebox_id, "mount_point": mount_point, "used": used, "total": total, "available": available, "percent_used": percent_used}
            response = requests.post(dest, data = json.dumps(data), headers=headers)
    except FileNotFoundError:
        print("File not found.")

def update_generic_config(appliance, wipebox_id):
    filename = "{}_generic_config.txt".format(appliance)
    try:
        with open(filename, 'r') as file:
            lines = file.readlines()
        for line in lines[2:-1]:
            field = json.loads(line.strip())
            print("{}: {}".format(field.get("name"), field.get("value")))
            dest = 'http://{}:{}/{}'.format('localhost', '8090', "insert_generic_config")
            data = {"wipebox_id": wipebox_id, "name": field.get("name"), "value": field.get("value")}
            response = requests.post(dest, data = json.dumps(data), headers=headers)
            print("Response: {}".format(response.text))
    except FileNotFoundError:
        print("File not found.")

if __name__ == '__main__':
    appliances = get_appliances()
    # print(appliances)
    version = get_versions()

    for appliance,last in appliances:
        hash = get_version_hash(appliance)
        # does hash exist
        dest = 'http://{}:{}/{}/{}'.format('localhost', '8090', "does_version_hash_exist", hash)
        try:
            response = requests.get(dest, headers=headers)
            if response.text != "True":
                data = {"cert": appliance,"hash": "-1", "last_update": last}
            else:
                data = {"cert": appliance,"hash": hash, "last_update": last}
            dest = 'http://{}:{}/{}'.format('localhost', '8090', "insert_wipebox")
            response = requests.post(dest, data = json.dumps(data), headers=headers)
            update_disk_usage(appliance, response.json().get("id"))
            update_generic_config(appliance, response.json().get("id"))
        except Exception as e:
            print("An unexpected error occurred: {}".format(e))

