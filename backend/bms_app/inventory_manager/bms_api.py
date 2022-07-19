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

from googleapiclient.discovery import build


def fetch_bms_instances(gcp_project_name):
    """Return list of bms instances from BMS API."""
    service = build('baremetalsolution', 'v2', static_discovery=False)
    locations = service.projects().locations()

    parent = f'projects/{gcp_project_name}/locations/global'
    req = locations.instances().list(parent=parent)

    instances = []
    for item in req.execute()['instances']:
        data = locations.instances().get(name=item['name']).execute()
        instances.append(data)

    return instances
