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

import urllib.request
from contextlib import closing


METADATA_URL = 'http://metadata.google.internal/computeMetadata/v1/instance/zone'
PROJECT_ID_URL = 'http://metadata.google.internal/computeMetadata/v1/project/project-id'
METADATA_HEADERS = {'Metadata-Flavor': 'Google'}


def get_gcloud_metadata():
    """Return current project_id."""
    req = urllib.request.Request(METADATA_URL, headers=METADATA_HEADERS)
    with closing(urllib.request.urlopen(req)) as conn:
        resp = conn.read().decode()

    data = resp.split('/')

    return {
        'project_id': data[1]
    }


def get_gcp_project_name():
    """Return current GCP project name."""
    req = urllib.request.Request(PROJECT_ID_URL, headers=METADATA_HEADERS)
    with closing(urllib.request.urlopen(req)) as conn:
        resp = conn.read().decode()

    return resp
