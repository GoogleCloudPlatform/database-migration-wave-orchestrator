# Copyright 2022 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from googleapiclient import discovery
from oauth2client.client import GoogleCredentials

from bms_app.services.gcloud import get_gcloud_metadata


def list_instances(compute, project, zone):
    result = compute.instances().list(project=project, zone=zone).execute()
    return result['items'] if 'items' in result else None


def get_gce_instances():
    """ Parse GCE running instances.

    Output:
    [
        {'create_time': '2021-10-05T14:34:33.776-07:00',
         'luns': [{'lun_name': 'oracle-bms-vm1',
                   'size_gb': '20',
                   'storage_type': 'PERSISTENT',
                   'storage_volume': ''
                   },
                   .....
                ],
         'machine_type': 'e2-small',
         'name': 'oracle-bms-vm1',
         'networks': [{'ip_address': '172.25.9.8',
                       'network_name': 'nic0',
                       'type': 'ONE_TO_ONE_NAT'}],
         'state': 'RUNNING'
        }
    .....
    ]
    """

    credentials = GoogleCredentials.get_application_default()
    compute = discovery.build('compute', 'v1', credentials=credentials)

    gcloud_md = get_gcloud_metadata()

    instances = list_instances(
        compute,
        gcloud_md['project_id'],
        gcloud_md['zone']
    )

    servers = []

    for instance in instances:
        if instance['status'] == 'RUNNING':

            luns = []
            for lun in instance['disks']:
                luns.append({
                    'lun_name': lun['deviceName'],
                    'size_gb': lun['diskSizeGb'],
                    'storage_volume': '',
                    'storage_type': lun['type']
                })

            networks = []
            for network in instance['networkInterfaces']:
                networks.append({
                    'network_name': network['name'],
                    'ip_address': network['networkIP'],
                    'type': network['accessConfigs'][0]['type']
                })


            servers.append({
                'id': instance['id'],
                'name': instance['name'],
                'create_time': instance['creationTimestamp'],
                'state': instance['status'],
                'machine_type': instance['machineType'].split('/')[-1],
                'luns': luns,
                'networks': networks
            })
    return servers
