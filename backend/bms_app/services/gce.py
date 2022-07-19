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


# from bms_app.services.gcloud import get_gcloud_metadata


def create_instance(project, zone, name, vpc, subnet,
                    service_account, machine_type, startup_script=None):
    # Get the latest bms-control-node image.
    compute = discovery.build('compute', 'v1')
    image_response = compute.images().getFromFamily(
        project='centos-cloud', family='centos-7').execute()
    source_disk_image = image_response['selfLink']

    # Configure the machine
    full_machine_type = f'zones/{zone}/machineTypes/{machine_type}'

    config = {
        'name': name,
        'machineType': full_machine_type,

        # Specify the boot disk and the image to use as a source.
        'disks': [
            {
                'boot': True,
                'autoDelete': True,
                'initializeParams': {
                    'sourceImage': source_disk_image,
                }
            }
        ],

        'networkInterfaces': [{
            'network': vpc,
            'subnetwork': subnet,
            'accessConfigs': [
                {'type': 'ONE_TO_ONE_NAT', 'name': 'External NAT'}
            ]
        }],

        # Allow the instance to access cloud storage and logging.
        'serviceAccounts': [{
            'email': service_account,
            'scopes': [
                "https://www.googleapis.com/auth/devstorage.read_only",
                "https://www.googleapis.com/auth/logging.write",
                "https://www.googleapis.com/auth/monitoring.write",
                "https://www.googleapis.com/auth/servicecontrol",
                "https://www.googleapis.com/auth/service.management.readonly",
                "https://www.googleapis.com/auth/trace.append",
                "https://www.googleapis.com/auth/cloud-platform",
            ]
        }],

        # Metadata is readable from the instance and allows you to
        # pass configuration from deployment scripts to instances.
        'metadata': {
            'items': []
        }
    }

    if startup_script:
        config['metadata']['items'].append(
            {
                'key': 'startup-script',
                'value': startup_script
            }
        )

    return compute.instances().insert(
        project=project,
        zone=zone,
        body=config
    ).execute()


def delete_instance(project, zone, name):
    compute = discovery.build('compute', 'v1')
    return compute.instances().delete(
        project=project,
        zone=zone,
        instance=name).execute()


# vpc = 'global/networks/network-go3-inv'
# subnetwork = 'regions/europe-west1/subnetworks/europe-west1-b-network-go3-inv-subnet'
# # metadata = get_gcloud_metadata()
# metadata = {
#     'project_id': 'or2-msq-go3-inv-t1iylu',
#     'zone': 'europe-west1-b'
# }
# create_instance(
#     metadata['project_id'],
#     zone=get_zone(metadata['project_id'], subnetwork),
#     vpc=vpc,
#     subnet=subnetwork,
#     name='vk-test-auto-ch',
#     service_account='<service_account_name>'
# )

def get_network_subnetwork(project):
    service = discovery.build('compute', 'v1')
    request = service.networks().list(project=project)

    networks = []
    while request is not None:
        response = request.execute()

        for network in response.get('items', []):
            subnetworks = []
            for subnetwork in network.get('subnetworks', []):
                subnetworks.append('/'.join(subnetwork.split('/')[-4:]))
            networks.append({
                "network": '/'.join(network['selfLink'].split('/')[-3:]),
                "subnetwork": subnetworks
            })
        request = service.networks().list_next(previous_request=request, previous_response=response)

    return networks


def get_service_accounts(project):

    service = discovery.build('iam', 'v1')

    name = 'projects/' + project

    request = service.projects().serviceAccounts().list(name=name)

    sa = []
    while True:
        response = request.execute()

        for service_account in response.get('accounts', []):
            sa.append(service_account['name'].split('/')[-1])

        request = service.projects().serviceAccounts().list_next(previous_request=request, previous_response=response)
        if request is None:
            break

    return sa


def get_zone(project, subnet):
    """Return 1-st zone for project/subnet."""
    service = discovery.build('compute', 'v1')

    request = service.zones().list(project=project)
    while request is not None:
        response = request.execute()

        for zone in response['items']:
            if zone['region'].split('/')[-1] == subnet.split('/')[1]:
                return zone['name']

        request = service.zones().list_next(previous_request=request, previous_response=response)
