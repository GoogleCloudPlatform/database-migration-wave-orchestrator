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

import json
import os

import yaml

from bms_app import settings
from bms_app.services.gcs import upload_blob_from_string


class FileUploadMixin:
    gcs_config_dir = None

    def _upload_yaml(self, data, file_name):
        """Upload file in yaml format to GCS."""
        file_content = yaml.safe_dump(data)
        gcs_key = os.path.join(self.gcs_config_dir, file_name)
        upload_blob_from_string(settings.GCS_BUCKET, gcs_key, file_content)

    def _upload_json(self, data, dir_name, file_name):
        """Upload file in json format to GCS."""
        file_content = json.dumps(data, indent=4)
        gcs_key = os.path.join(self.gcs_config_dir, dir_name, file_name)
        upload_blob_from_string(settings.GCS_BUCKET, gcs_key, file_content)
