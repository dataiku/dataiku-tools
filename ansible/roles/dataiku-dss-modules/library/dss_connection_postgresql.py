#!/usr/bin/env python2

ANSIBLE_METADATA = {
    'metadata_version': '1.1',
    'status': ['preview'],
    'supported_by': 'dataiku-tools'
}

DOCUMENTATION = '''
---
module: dss_connection_postgresql

short_description: Creates, edit or delete a Data Science Studio postgresql connection

description:
    - "This module edits a complete connection"

options:
    connect_to:
        description:
            - A dictionary containing "port" and "api_key". This parameter is a short hand to be used with dss_get_credentials
        required: true
    host:
        description:
            - The host on which to make the requests.
        required: false
        default: localhost
    port:
        description:
            - The port on which to make the requests.
        required: false
        default: 80
    api_key:
        description:
            - The API Key to authenticate on the API. Mandatory if connect_to is not used
        required: false
    name:
        description:
            - Name of the connection
        required: true
    postgresql_host:
        description:
            - Hostname of the postgresql server. Not needed if modifying an existing connection.
        required: false
    postgresql_port:
        description:
            - Hostname of the postgresql server.
        required: false
    user:
        description:
            - Username to connect. Not needed if modifying an existing connection.
        required: false
    password:
        description:
            - Password to connect. Not needed if modifying an existing connection.
        required: true
    database:
        description:
            - Database to use. Not needed if modifying an existing connection.
        required: true
    additional_args:
        description:
            - A dictionary of additional arguments passed into the json of the connection.
        required: true
    state:
        description:
            - Wether the connection is supposed to exist or not. Possible values are "present" and "absent"
        default: present
        required: false
    set_password_at_creation_only:
        description:
            - Allow not to change the password to the requested one if the connection already exists. This is
              the only way to actually achieve idempotency, so it is true by default. If set to false, the task
              will always have the "changed" status because we cannot check if the password was actually different before
              or not
        default: true
        required: false
author:
    - Jean-Bernard Jansen (jean-bernard.jansen@dataiku.com)
'''

EXAMPLES = '''
# Creates a group using dss_get_credentials if you have SSH Access
- name: Get the API Key
  become: true
  become_user: dataiku
  dss_get_credentials:
    datadir: /home/dataiku/dss
    api_key_name: myadminkey
  register: dss_connection_info
'''

RETURN = '''
previous_connection_def:
    description: The previous values
    type: dict
connection_def:
    description: The current values if the connection have not been deleted
    type: dict
message:
    description: CREATED, MODIFIED, UNCHANGED or DELETED 
    type: str
'''

from ansible.module_utils.basic import AnsibleModule
from dataikuapi import DSSClient
from dataikuapi.dss.admin import DSSConnection
from dataikuapi.utils import DataikuException
import copy
import traceback
import re
import time

# Trick to expose dictionary as python args
class MakeNamespace(object):
    def __init__(self,values):
        self.__dict__.update(values)

# Similar to dict.update but deep
def update(d, u):
    for k, v in u.iteritems():
        if isinstance(v, collections.Mapping):
            d[k] = update(d.get(k, {}), v)
        else:
            d[k] = v
    return d


connection_template = {
    "allowManagedDatasets": True,
    "allowManagedFolders": False,
    "allowWrite": True,
    "allowedGroups": [],
    #"creationTag": {},
    "credentialsMode": "GLOBAL", 
    "detailsReadability": {
	"allowedGroups": [], 
	"readableBy": "NONE"
    },
    "indexingSettings": {
	"indexForeignKeys": False,
	"indexIndices": False,
	"indexSystemTables": False
    },
    "maxActivities": 0,
    #"name": "",
    "params": {
	"autocommitMode": False,
	#"db": "",
	#"host": "",
	"namingRule": {
	    "canOverrideSchemaInManagedDatasetCreation": False,
	    "tableNameDatasetNamePrefix": "${projectKey}_"
	}, 
	#"password": "",
	"port": 5432,
	"properties": [],
	"useTruncate": False,
	"useURL": False,
	#"user": ""
    }, 
    "type": "PostgreSQL",
    "usableBy": "ALL", 
    "useGlobalProxy": False
}

def run_module():
    # define the available arguments/parameters that a user can pass to
    # the module
    module_args = dict(
        connect_to=dict(type='dict', required=False, default={}, no_log=True),
        host=dict(type='str', required=False, default="127.0.0.1"),
        port=dict(type='str', required=False, default=None),
        api_key=dict(type='str', required=False, default=None),
        name=dict(type='str', required=True),
        state=dict(type='str', required=False, default="present"),
        set_password_at_creation_only=dict(type='bool', required=False, default=True),
        postgresql_host=dict(type='str', default=None, required=False),
        postgresql_port=dict(type='str', default=None, required=False),
        user=dict(type='str', default=None, required=False),
        password=dict(type='str', required=False, no_log=True),
        database=dict(type='str', default=None, required=False),
        additional_args=dict(type='dict', default={}, required=False),
    )

    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True
    )

    args = MakeNamespace(module.params)
    if args.state not in ["present","absent"]:
        module.fail_json(msg="Invalid value '{}' for argument state : must be either 'present' or 'absent'".format(args.source_type))
    api_key = args.api_key if args.api_key is not None else args.connect_to.get("api_key",None)
    if api_key is None:
        module.fail_json(msg="Missing an API Key, either from 'api_key' or 'connect_to' parameters".format(args.state))
    port = args.port if args.port is not None else args.connect_to.get("port","80")
    host = args.host

    result = dict(
        changed=False,
        message='UNCHANGED',
    )

    try:
        client = DSSClient("http://{}:{}".format(args.host, port),api_key=api_key)
        exists = True
        create = False
        connection = client.get_connection(args.name)
        current_def = None
        try:
            current_def  = connection.get_definition()
        except DataikuException as e:
            #if e.message.startswith("com.dataiku.dip.server.controllers.NotFoundException"):
            if str(e) == "java.lang.IllegalArgumentException: Connection '{}' does not exist".format(args.name):
                exists = False
                if args.state == "present":
                    create = True
            else:
                raise
        except Exception as e:
            raise

        current_def = None
        encrypted_password_before_change = None
        if exists:
            result["previous_group_def"] = current_def = connection.get_definition()
            # Check this is the same type
            if current_def["type"] != connection_template["type"]:
                module.fail_json(msg="Connection '{}' already exists but is of type '{}'".format(args.name,current_def["type"]))
                return
            # Remove some values from the current def
            encrypted_password_before_change = current_def["params"].get("password",None)
            if encrypted_password_before_change is not None:
                del current_def["params"]["password"]
        else:
            if args.state == "present":
                for mandatory_create_param in ["user", "password", "database", "postgresql_host"]:
                    if module.params[mandatory_create_param] is None:
                        module.fail_json(msg="Connection '{}' does not exist and cannot be created without the '{}' parameter".format(args.name,mandatory_create_param))

        # Build the new definition
        new_def = copy.deepcopy(current_def) if exists else connection_template # Used for modification

        # Apply every attribute except the password for now
        new_def["name"] = args.name
        if args.database is not None:
            new_def["params"]["db"] = args.database
        if args.user is not None:
            new_def["params"]["user"] = args.user
        if args.postgresql_host is not None:
            new_def["params"]["host"] = args.postgresql_host
        if args.postgresql_port is not None:
            new_def["params"]["port"] = args.postgresql_port

        # Bonus args
        update(new_def, args.additional_args)

        # Prepare the result for dry-run mode
        result["changed"] = create or (exists and args.state == "absent") or (exists and current_def != new_def)
        if result["changed"]:
            if create:
                result["message"] = "CREATED"
            elif exists:
                if  args.state == "absent":
                    result["message"] = "DELETED"
                elif current_def != new_def:
                    result["message"] = "MODIFIED"

        if args.state == "present":
            result["connection_def"] = new_def

        if module.check_mode:
            module.exit_json(**result)

        ## Apply the changes
        if result["changed"] or (args.password is not None and exists):
            if create:
                new_def["params"]["password"] = args.password
                params = {
                    "db": args.database,
                    "user": args.user,
                    "password": args.password,
                    "host": args.postgresql_host,
                }
                if args.postgresql_port is not None:
                    params["port"] = args.postgresql_port
                connection = client.create_connection(args.name, connection_template["type"], params)
                connection.set_definition(new_def) # 2nd call to apply additional parameters
            elif exists:
                if args.state == "absent":
                    connection.delete()
                elif current_def != new_def or args.password is not None:
                    if args.password is not None:
                        new_def["params"]["password"] = args.password
                    else:
                        new_def["params"]["password"] = encrypted_password_before_change
                    result["message"] = str(connection.set_definition(new_def))
                    if args.password is not None:
                        # Get again the definition to test again the encrypted pass
                        new_def_after_submit = connection.get_definition()
                        if encrypted_password_before_change != new_def_after_submit["params"]["password"]:
                            result["changed"] = True
                            result["message"] = "MODIFIED"

        module.exit_json(**result)
    except Exception as e:
        module.fail_json(msg="{}: {}".format(type(e).__name__,str(e)))

def main():
    run_module()

if __name__ == '__main__':
    main()
