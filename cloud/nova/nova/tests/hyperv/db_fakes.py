# vim: tabstop=4 shiftwidth=4 softtabstop=4

#  Copyright 2012 Cloudbase Solutions Srl
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

"""
Stubouts, mocks and fixtures for the test suite
"""

import time
import uuid

from nova.compute import task_states
from nova.compute import vm_states
from nova import db
from nova import utils


def get_fake_instance_data(name, project_id, user_id):
    return {'name': name,
              'id': 1,
              'uuid': uuid.uuid4(),
              'project_id': project_id,
              'user_id': user_id,
              'image_ref': "1",
              'kernel_id': "1",
              'ramdisk_id': "1",
              'mac_address': "de:ad:be:ef:be:ef",
              'instance_type': 'm1.tiny',
              }


def get_fake_image_data(project_id, user_id):
    return {'name': 'image1',
              'id': 1,
              'project_id': project_id,
              'user_id': user_id,
              'image_ref': "1",
              'kernel_id': "1",
              'ramdisk_id': "1",
              'mac_address': "de:ad:be:ef:be:ef",
              'instance_type': 'm1.tiny',
              }


def get_fake_volume_info_data(target_portal, volume_id):
    return {
        'driver_volume_type': 'iscsi',
        'data': {
            'volume_id': 1,
            'target_iqn': 'iqn.2010-10.org.openstack:volume-' + volume_id,
            'target_portal': target_portal,
            'target_lun': 1,
            'auth_method': 'CHAP',
            'auth_method': 'fake',
            'auth_method': 'fake',
        }
}


def get_fake_block_device_info(target_portal, volume_id):
    return {
            'block_device_mapping': [{'connection_info': {
                'driver_volume_type': 'iscsi',
                'data': {'target_lun': 1,
                         'volume_id': volume_id,
                         'target_iqn': 'iqn.2010-10.org.openstack:volume-' +
                            volume_id,
                         'target_portal': target_portal,
                         'target_discovered': False}},
                'mount_device': 'vda',
                'delete_on_termination': False}],
            'root_device_name': None,
            'ephemerals': [],
            'swap': None
    }


def stub_out_db_instance_api(stubs):
    """Stubs out the db API for creating Instances."""

    INSTANCE_TYPES = {
        'm1.tiny': dict(memory_mb=512, vcpus=1, root_gb=0, flavorid=1),
        'm1.small': dict(memory_mb=2048, vcpus=1, root_gb=20, flavorid=2),
        'm1.medium':
            dict(memory_mb=4096, vcpus=2, root_gb=40, flavorid=3),
        'm1.large': dict(memory_mb=8192, vcpus=4, root_gb=80, flavorid=4),
        'm1.xlarge':
            dict(memory_mb=16384, vcpus=8, root_gb=160, flavorid=5)}

    class FakeModel(object):
        """Stubs out for model."""

        def __init__(self, values):
            self.values = values

        def __getattr__(self, name):
            return self.values[name]

        def __getitem__(self, key):
            if key in self.values:
                return self.values[key]
            else:
                raise NotImplementedError()

    def fake_instance_create(context, values):
        """Stubs out the db.instance_create method."""

        if 'instance_type' not in values:
            return

        type_data = INSTANCE_TYPES[values['instance_type']]

        base_options = {
            'name': values['name'],
            'id': values['id'],
            'uuid': uuid.uuid4(),
            'reservation_id': utils.generate_uid('r'),
            'image_ref': values['image_ref'],
            'kernel_id': values['kernel_id'],
            'ramdisk_id': values['ramdisk_id'],
            'vm_state': vm_states.BUILDING,
            'task_state': task_states.SCHEDULING,
            'user_id': values['user_id'],
            'project_id': values['project_id'],
            'launch_time': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
            'instance_type': values['instance_type'],
            'memory_mb': type_data['memory_mb'],
            'vcpus': type_data['vcpus'],
            'mac_addresses': [{'address': values['mac_address']}],
            'root_gb': type_data['root_gb'],
            }
        return FakeModel(base_options)

    def fake_network_get_by_instance(context, instance_id):
        """Stubs out the db.network_get_by_instance method."""

        fields = {
            'bridge': 'vmnet0',
            'netmask': '255.255.255.0',
            'gateway': '10.10.10.1',
            'broadcast': '10.10.10.255',
            'dns1': 'fake',
            'vlan': 100}
        return FakeModel(fields)

    def fake_instance_type_get_all(context, inactive=0, filters=None):
        return INSTANCE_TYPES.values()

    def fake_instance_type_get_by_name(context, name):
        return INSTANCE_TYPES[name]

    stubs.Set(db, 'instance_create', fake_instance_create)
    stubs.Set(db, 'network_get_by_instance', fake_network_get_by_instance)
    stubs.Set(db, 'instance_type_get_all', fake_instance_type_get_all)
    stubs.Set(db, 'instance_type_get_by_name', fake_instance_type_get_by_name)
