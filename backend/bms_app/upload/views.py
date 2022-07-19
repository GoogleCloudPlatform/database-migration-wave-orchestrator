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

import os

from flask import request

from bms_app import settings
from bms_app.services.gcs import list_blobs, upload_stream_to_gcs
from bms_app.upload import bp
from bms_app.upload.services import get_software_library


class StreamWrapper:
    """Wrap gunicorn.http.body.Body to provide .tell() method.

    gunicorn.http.body.Body does not provide .tell()
    that is required by from google.resumable_media.requests.ResumableUpload
    add custom .tell() method to make ResumableUpload work.
    """

    def __init__(self, stream):
        self.stream = stream
        self._pos = 0  # keep current position

    def read(self, *args, **kwargs):
        data = self.stream.read(*args, **kwargs)
        self._pos += len(data)
        return data

    def tell(self):
        return self._pos


@bp.route('/binaries/<path:file_name>', methods=['POST'])
def upload_oracle_binary(file_name):
    gcs_key = os.path.join(
        settings.GCS_ORACLE_BINARY_PREFIX,
        file_name
    )
    stream = StreamWrapper(request.stream)
    upload_stream_to_gcs(
        stream,
        settings.GCS_BUCKET,
        gcs_key
    )

    return {}, 201


@bp.route('/binaries', methods=['GET'])
def list_oracle_binaries():
    binaries = list_blobs(
        settings.GCS_BUCKET,
        settings.GCS_ORACLE_BINARY_PREFIX
    )
    file_names = [os.path.basename(f['name']) for f in binaries]
    items = get_software_library(file_names)

    return {'data': items}, 201
