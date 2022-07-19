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
from unittest.mock import patch

import pytest

from bms_app import settings
from bms_app.models import RestoreConfig, db

from tests.factories import (
    ConfigFactory, ProjectFactory, RestoreConfigFactory, SourceDBFactory
)


@pytest.fixture
def pfile_path(files_dir):
    return os.path.join(files_dir, 'restore_configs_1101_pfile.ora')


@patch('bms_app.restore.services.StreamWrapper', return_value=1)
@patch('bms_app.restore.services.upload_blob')
def test_uploading_pfile(upload_mock, stream_mock, client, pfile_path):
    """Test adding config file"""
    pr = ProjectFactory()
    db_1 = SourceDBFactory(project=pr, db_name='orabase')
    ConfigFactory(source_db=db_1)

    with open(pfile_path, 'rb') as fp:
        data = {
            'file': (fp, 'restore_configs_1101_pfile.ora')
        }

        req = client.post(
            f'/api/restore/source-dbs/{db_1.id}/config/pfile',
            data=data,
            content_type='multipart/form-data'
        )

    assert req.status_code == 201
    assert req.json['content']
    assert req.json['url']

    gcs_key = os.path.join(
        settings.GCP_RESTORE_CONFIGS_PREFIX,
        str(db_1.id),
        'pfile.ora'
    )

    assert db_1.restore_config.pfile_file == gcs_key

    upload_mock.assert_called_with(
        settings.GCS_BUCKET,
        gcs_key,
        stream_mock.return_value
    )


@patch('bms_app.restore.services.StreamWrapper', return_value=1)
@patch('bms_app.restore.services.upload_blob')
def test_editing_pfile(upload_mock, stream_mock, client, pfile_path):
    """Test editing config file"""
    pr = ProjectFactory()
    db_1 = SourceDBFactory(project=pr, db_name='orabase')
    ConfigFactory(source_db=db_1)
    restore_conf = RestoreConfigFactory(source_db=db_1)

    with open(pfile_path, 'rb') as fp:
        data = {
            'file': (fp, 'restore_configs_1101_pfile.ora')
        }

        req = client.post(
            f'/api/restore/source-dbs/{db_1.id}/config/pfile',
            data=data,
            content_type='multipart/form-data'
        )

    assert req.status_code == 201
    assert req.json['content']
    assert req.json['url']

    gcs_key = os.path.join(
        settings.GCP_RESTORE_CONFIGS_PREFIX,
        str(db_1.id),
        'pfile.ora'
    )

    assert restore_conf.pfile_file == gcs_key

    upload_mock.assert_called_with(
        settings.GCS_BUCKET,
        gcs_key,
        stream_mock.return_value
    )


@patch('bms_app.restore.services.upload_blob')
def test_uploading_empty_pfile(upload_mock, client, files_dir):
    """Test uploading correct pfile file"""
    pr = ProjectFactory()
    db_1 = SourceDBFactory(project=pr)

    with open(os.path.join(files_dir, 'empty_file.txt'), 'rb') as fp:
        data = {
            'file': (fp, 'empty_file.txt')
        }

        req = client.post(
            f'/api/restore/source-dbs/{db_1.id}/config/pfile',
            data=data,
            content_type='multipart/form-data'
        )

    assert req.status_code == 400

    assert req.json['errors'].get('file')


@patch('bms_app.restore.services.upload_blob')
def test_error_if_incorrect_pfile(upload_mock, client, pfile_path):
    """Test uploading correct pfile file"""
    pr = ProjectFactory()
    db_1 = SourceDBFactory(project=pr, db_name='another_db')

    with open(pfile_path, 'rb') as fp:
        data = {
            'file': (fp, 'restore_configs_1101_pfile.ora')
        }

        req = client.post(
            f'/api/restore/source-dbs/{db_1.id}/config/pfile',
            data=data,
            content_type='multipart/form-data'
        )

    assert req.status_code == 400


@patch('bms_app.restore.services.upload_blob_from_string')
def test_not_saving_empty_pfile_content(mock, client):
    """Test adding restore settings"""
    pr = ProjectFactory()
    db_1 = SourceDBFactory(project=pr)
    ConfigFactory(source_db=db_1)

    post_data = {
        'is_configured': False,
        'backup_location': '',
        'rman_cmd': '',
        'pfile_content': '',
        'backup_type': '',
        'run_pre_restore': False,
        'validations': [],
        'control_file': ''
    }

    req = client.post(
        f'/api/restore/source-dbs/{db_1.id}/config',
        json=post_data
    )
    assert req.status_code == 201

    assert db_1.restore_config
    assert not db_1.restore_config.pfile_file

    assert not mock.called


@pytest.mark.parametrize(
    'file_obj,field_name',
    [
        (io.BytesIO(b'text'), 'listener_file'),
        (io.BytesIO(b'text'), 'tnsnames_file'),
    ]
)
@patch('bms_app.restore.services.upload_blob')
def test_uploading_listener_and_tnsnames_files(upload_mock, file_obj,
                                               field_name, client):
    pr = ProjectFactory()
    db_1 = SourceDBFactory(project=pr, db_name='orabase')

    assert not db_1.restore_config

    data = {
        'file': (io.BytesIO(b'text here'), 'config_file.ora')
    }

    req = client.post(
        f'/api/restore/source-dbs/{db_1.id}/config/{field_name}',
        data=data,
        content_type='multipart/form-data'
    )

    assert req.status_code == 201
    assert req.json['url']

    assert db_1.restore_config
    assert getattr(db_1.restore_config, field_name)

    assert upload_mock.called


@patch('bms_app.restore.services.upload_blob')
def test_uploading_pwd_file(upload_mock, client):
    """Test uploading binary RestoreConfig.pwd_file"""
    pr = ProjectFactory()
    db_1 = SourceDBFactory(project=pr, db_name='orabase')

    assert not db.session.query(RestoreConfig) \
        .filter(RestoreConfig.db_id == db_1.id) \
        .first()

    data = {
        'file': (io.BytesIO(b'\xd4\xa2\x16\x18\xe1\xeb+\xe8'),
                 'config_file.ora')
    }

    req = client.post(
        f'/api/restore/source-dbs/{db_1.id}/config/pwd_file',
        data=data,
        content_type='multipart/form-data'
    )

    assert req.status_code == 201

    assert db_1.restore_config
    assert db_1.restore_config.pwd_file

    assert upload_mock.called
