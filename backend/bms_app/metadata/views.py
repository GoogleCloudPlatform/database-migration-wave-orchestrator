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

import logging
import os

from bms_app import settings
from bms_app.metadata import bp
from bms_app.services.gce import get_network_subnetwork
from bms_app.wave_steps import DEPLOYMENT_STEPS, ROLLBACK_STEPS


logger = logging.getLogger(__name__)


@bp.route('', methods=['GET'])
def get_gcp_metadata():
    project = settings.GCP_PROJECT_NAME

    try:
        nets = get_network_subnetwork(project)
    except:
        logger.exception('error getting subnetworks')
        nets = []

    return {
        'networks': nets
    }


@bp.route('/settings')
def get_gcs_metadata():
    """Return url to GCS location with oracle binaries."""
    bucket_name = settings.GCS_BUCKET
    binary_prefix = settings.GCS_ORACLE_BINARY_PREFIX

    if binary_prefix:
        full_path = os.path.join(bucket_name, binary_prefix)
    else:
        full_path = bucket_name

    url = f'https://console.cloud.google.com/storage/browser/{full_path}'

    return {
        'project_id': settings.GCP_PROJECT_NAME,
        'project_number': settings.GCP_PROJECT_NUMBER,
        'sw_lib_url': url
    }


@bp.route('/wave-steps')
def get_wave_steps():
    return {
        'deployment': DEPLOYMENT_STEPS,
        'rollback': ROLLBACK_STEPS
    }
