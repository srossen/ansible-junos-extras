#!/usr/bin/env python2.7

DOCUMENTATION = '''
---
module: junos_lldp
author: Tyler Christiansen
version_added: "1.1.0"
short_description: Show LLDP Neighbors
description:
  - Get list of LLDP neighbors
requirements:
  - py-junos-eznc
options:
  host:
    description:
      - should be {{ inventory_hostname }}
    required: true
  user:
    description:
      - login user-name
    required: false
    default: $USER
  passwd:
    description:
      - login password
    required: false
    default: assumes ssh-key
'''

import sys
import os
from jnpr.junos import Device
from jnpr.junos.factory.table import Table
from jnpr.junos.factory.view import View
from jnpr.junos.op.lldp import LLDPNeighborTable
import json

class TableJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, View):
            obj = dict(obj.items())
        elif isinstance(obj, Table):
            obj = {item.name: item for item in obj}
        elif isinstance(obj, lxml.etree._Element):
            def recursive_dict(element):
                return element.tag, dict(map(recursive_dict, element)) \
                       or element.text
            _, obj = recursive_dict(obj)
        else:
            obj = super(TableJSONEncoder, self).default(obj)
        return obj

def main():
    module = AnsibleModule(
        argument_spec=dict(
            host=dict(required=True),
            user=dict(required=False, default=os.getenv('USER')),
            passwd=dict(required=False, default=None)),
        supports_check_mode=False)

    m_args = module.params
    m_results = dict(changed=False)
    dev = Device(m_args['host'], user=m_args['user'], passwd=m_args['passwd'])
    try:
        dev.open()
    except Exception as err:
        msg = 'unable to connect to {}: {}'.format(m_args['host'], str(err))
        module.fail_json(msg=msg)
        return
    results = {}
    lldp_results = []
    try:
        lldp = LLDPNeighborTable(dev)
        lldp.get()
        lldp = json.loads(json.dumps(lldp, cls=TableJSONEncoder))
    except Exception as err:
        dev.close()
        module.fail_json(msg=err)
        return
    dev.close()
    module.exit_json(results=lldp)
from ansible.module_utils.basic import *
main()
