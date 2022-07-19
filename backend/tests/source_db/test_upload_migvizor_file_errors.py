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

import io
import os

from pandas import DataFrame

from tests.factories import ProjectFactory


def test_bad_file_format(client):
    """Test error if not excel format."""
    pr = ProjectFactory()

    data = {
        'project_id': pr.id,
        'file': (io.BytesIO(b'text data'), 'MigVisor_example.xlsx'),
    }

    req = client.post(
        '/api/source-dbs/migvisor',
        data=data,
        content_type='multipart/form-data',
    )

    assert req.status_code == 400
    assert 'file' in req.json['errors']


def test_error_if_missing_data(client, files_dir):
    """Test error if missed some key data."""
    pr = ProjectFactory()

    file_path = os.path.join(files_dir, 'MigVisor_bad_example.xlsx')
    with open(file_path, 'rb') as fp:
        data = {
            'project_id': pr.id,
            'file': (fp, 'MigVisor_bad_example.xlsx'),
        }

        req = client.post(
            '/api/source-dbs/migvisor',
            data=data,
            content_type='multipart/form-data',
        )

    assert req.status_code == 400

    err = req.json['errors'].get('file')

    assert err
    assert 'Database name' in err
    assert 'Version' in err
    assert 'Server' in err


def test_empty_file_error(client):
    pr = ProjectFactory()

    with io.BytesIO() as fp:
        df = DataFrame()  # empty
        df.to_excel(fp)

        data = {
            'project_id': pr.id,
            'file': (fp, 'MigVisor_empty_example.xlsx'),
        }

        req = client.post(
            '/api/source-dbs/migvisor',
            data=data,
            content_type='multipart/form-data',
        )

        assert req.status_code == 400
        assert req.json['errors'].get('file')
