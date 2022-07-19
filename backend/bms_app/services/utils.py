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

import urllib.parse
from datetime import datetime, timedelta

from bms_app import settings


def generate_target_gcp_logs_link(operaion_details, bms_server):
    """
    Return a link to gcloud logging for a specific host
    including all neccessary query filters.
    """
    date_format = '%Y-%m-%dT%H:%M:%S.%fZ'

    started_at = operaion_details.started_at

    if operaion_details.completed_at:
        completed_at = operaion_details.completed_at
    else:
        completed_at = datetime.now() + timedelta(days=1)

    # build query
    query_filters = [
        f'logName="projects/{settings.GCP_PROJECT_NAME}/logs/BMS_LOG_RECEIVER"',
        f'jsonPayload.deploymentid="{operaion_details.operation_id}"',
    ]
    if bms_server:
        query_filters.append(f'jsonPayload.targethost="{bms_server.name}"')

    encoded_query = urllib.parse.quote_plus('\n'.join(query_filters))

    # build time range
    time_range_filter = (
        f'{started_at.strftime(date_format)}'
        f'{urllib.parse.quote_plus("/")}'
        f'{completed_at.strftime(date_format)}'
    )

    return (
        'https://console.cloud.google.com/logs/query'
        f';query={encoded_query}'
        f';timeRange={time_range_filter}'
        f'?project={settings.GCP_PROJECT_NAME}'
    )
