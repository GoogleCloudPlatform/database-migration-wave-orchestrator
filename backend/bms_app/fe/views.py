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

# Workaround to server FE files
import os

from flask import send_from_directory

from bms_app.fe import bp


FE_DIR = os.path.normpath(
    os.path.join(
        os.path.realpath(__file__),
        '../../..',
        'bms-frontend-dev',
    )
)


@bp.route('/')
@bp.route('/<path:name>')
def download_file(name='index.html'):
    file_path = os.path.join(FE_DIR, name)
    if not os.path.exists(file_path):
        name = 'index.html'

    return send_from_directory(
        FE_DIR, name,
    )
