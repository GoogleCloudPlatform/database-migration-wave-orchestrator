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

from unittest.mock import patch

from bms_app import settings
from bms_app.models import RestoreConfig, db
from bms_app.pre_restore_validations import PRE_RESTORE_VALIDATIONS

from tests.factories import (
    ConfigFactory, ProjectFactory, RestoreConfigFactory, SourceDBFactory
)


GCS_BASE_URL = 'https://console.cloud.google.com/storage/browser/_details/test-bucket/'


def test_get_empty_restore_config(client):
    """Test for returning restore settings."""
    db_1 = SourceDBFactory(db_name='ORCL')
    conf = ConfigFactory(
        db_params_values={'db_name': 'ORCL'},
        source_db=db_1,
    )

    req = client.get(f'/api/restore/source-dbs/{db_1.id}/config')

    assert req.status_code == 200

    data = req.json

    assert data['db_name'] == conf.db_params_values['db_name']
    assert len(data['validations']) == len(PRE_RESTORE_VALIDATIONS)


@patch('bms_app.restore.restore_config_views.get_pfile_content', return_value='a')
def test_get_restore_config(mock, client):
    """Test for returning restore settings."""
    db_1 = SourceDBFactory()
    conf = ConfigFactory(source_db=db_1)
    restore_conf = RestoreConfigFactory(source_db=db_1)

    req = client.get(f'/api/restore/source-dbs/{db_1.id}/config')

    assert req.status_code == 200

    data = req.json

    assert data['db_name'] == conf.db_params_values['db_name']
    assert data['backup_location'] == restore_conf.backup_location
    assert data['pfile_file'] == GCS_BASE_URL + restore_conf.pfile_file
    assert data['pwd_file'] == GCS_BASE_URL + restore_conf.pwd_file
    assert data['tnsnames_file'] == GCS_BASE_URL + restore_conf.tnsnames_file
    assert data['listener_file'] == GCS_BASE_URL + restore_conf.listener_file
    assert data['rman_cmd'] == restore_conf.rman_cmd
    assert data['is_configured'] == restore_conf.is_configured
    assert data['pfile_content'] == mock.return_value
    assert data['backup_type'] == restore_conf.backup_type.value
    assert data['control_file'] == ''
    assert data['validations']


@patch('bms_app.restore.restore_config_views.get_pfile_content', return_value='a')
def test_get_restore_config_validations_output(mock, client):
    """Test return validations output."""
    db_1 = SourceDBFactory()
    ConfigFactory(source_db=db_1)
    RestoreConfigFactory(
        source_db=db_1,
        validations=['RMAN> list backup', 'disk space validation']
    )

    req = client.get(f'/api/restore/source-dbs/{db_1.id}/config')

    assert req.status_code == 200

    data = req.json
    assert len(data['validations']) == len(PRE_RESTORE_VALIDATIONS)

    # test two options are enabled
    assert next(x for x in data['validations']
                if x['name'] == 'RMAN> list backup' and x['enabled'])

    assert next(x for x in data['validations']
                if x['name'] == 'disk space validation' and x['enabled'])

    # all other options are disabled
    disabled = [x for x in data['validations'] if not x['enabled']]
    assert len(disabled) == len(PRE_RESTORE_VALIDATIONS) - 2


@patch('bms_app.restore.services.upload_blob_from_string')
def test_add_restore_config(mock, client):
    """Test adding restore settings"""
    pr = ProjectFactory()
    db_1 = SourceDBFactory(project=pr)
    ConfigFactory(source_db=db_1)

    post_data = {
        'backup_location': 'location',
        'rman_cmd': 'rmn',
        'is_configured': True,
        'pfile_content': 'text',
        'backup_type': 'full',
        'run_pre_restore': False,
        'control_file': 'text',
        'validations': [],
    }

    req = client.post(
        f'/api/restore/source-dbs/{db_1.id}/config',
        json=post_data
    )
    assert req.status_code == 201

    restore_conf = db.session.query(RestoreConfig) \
        .filter(RestoreConfig.db_id == db_1.id) \
        .first()

    assert restore_conf.backup_location == post_data['backup_location']
    assert restore_conf.rman_cmd == post_data['rman_cmd']
    assert restore_conf.is_configured == post_data['is_configured']
    assert restore_conf.backup_type.value == post_data['backup_type']
    assert restore_conf.control_file == post_data['control_file']
    assert not restore_conf.run_pre_restore
    assert not restore_conf.validations

    mock.assert_called_with(
        settings.GCS_BUCKET,
        f'restore_configs/{db_1.id}/pfile.ora',
        post_data['pfile_content']
    )


@patch('bms_app.restore.services.upload_blob_from_string')
def test_add_restore_config_with_run_pre_restore_option(mock, client):
    pr = ProjectFactory()
    db_1 = SourceDBFactory(project=pr)
    ConfigFactory(source_db=db_1)

    post_data = {
        'backup_location': 'location',
        'rman_cmd': 'rmn',
        'is_configured': True,
        'pfile_content': 'text',
        'backup_type': 'full',
        'run_pre_restore': True,
        'control_file': 'file',
        'validations': ['RMAN> list backup', 'disk space validation'],
    }

    req = client.post(
        f'/api/restore/source-dbs/{db_1.id}/config',
        json=post_data
    )
    assert req.status_code == 201

    restore_conf = db.session.query(RestoreConfig) \
        .filter(RestoreConfig.db_id == db_1.id) \
        .first()

    assert restore_conf.backup_location == post_data['backup_location']
    assert restore_conf.rman_cmd == post_data['rman_cmd']
    assert restore_conf.is_configured == post_data['is_configured']
    assert restore_conf.backup_type.value == post_data['backup_type']
    assert restore_conf.run_pre_restore == post_data['run_pre_restore']
    assert restore_conf.validations == post_data['validations']
    assert restore_conf.control_file == post_data['control_file']

    mock.assert_called_with(
        settings.GCS_BUCKET,
        f'restore_configs/{db_1.id}/pfile.ora',
        post_data['pfile_content']
    )



@patch('bms_app.restore.services.upload_blob_from_string')
def test_edit_restore_configs(mock, client):
    """Test edit restore settings"""
    pr = ProjectFactory()
    db_1 = SourceDBFactory(project=pr)
    ConfigFactory(source_db=db_1)
    restore_conf = RestoreConfigFactory(source_db=db_1)

    post_data = {
        'backup_location': 'location',
        'rman_cmd': 'rmn',
        'is_configured': True,
        'pfile_content': 'text',
        'backup_type': 'full',
        'run_pre_restore': False,
        'validations': [],
        'control_file': 'text',
    }

    req = client.post(
        f'/api/restore/source-dbs/{db_1.id}/config',
        json=post_data
    )

    assert req.status_code == 201

    assert restore_conf.backup_location == post_data['backup_location']
    assert restore_conf.rman_cmd == post_data['rman_cmd']
    assert restore_conf.is_configured == post_data['is_configured']
    assert restore_conf.backup_type.value == post_data['backup_type']
    assert restore_conf.control_file == post_data['control_file']

    mock.assert_called_with(
        settings.GCS_BUCKET,
        f'restore_configs/{db_1.id}/pfile.ora',
        post_data['pfile_content']
    )


@patch('bms_app.restore.services.upload_blob_from_string')
def test_draft_restore_configs(mock, client):
    """Test adding restore settings"""
    pr = ProjectFactory()
    db_1 = SourceDBFactory(project=pr)
    ConfigFactory(source_db=db_1)

    post_data = {
        'is_configured': False,
        'backup_location': '',
        'rman_cmd': '',
        'pfile_content': 'text',
        'backup_type': '',
        'run_pre_restore': True,
        'validations': [],
    }

    req = client.post(
        f'/api/restore/source-dbs/{db_1.id}/config',
        json=post_data
    )
    assert req.status_code == 201

    restore_conf = db.session.query(RestoreConfig) \
        .filter(RestoreConfig.db_id == db_1.id) \
        .first()

    assert not restore_conf.is_configured
    assert not restore_conf.backup_location
    assert not restore_conf.rman_cmd
    assert not restore_conf.backup_type.value

    mock.assert_called_with(
        settings.GCS_BUCKET,
        f'restore_configs/{db_1.id}/pfile.ora',
        'text'
    )


@patch('bms_app.restore.services.upload_blob_from_string')
def test_required_fields(mock, client):
    pr = ProjectFactory()
    db_1 = SourceDBFactory(project=pr)
    ConfigFactory(source_db=db_1)

    post_data = {
        'is_configured': True,
        'backup_location': '',
        'rman_cmd': '',
        'pfile_content': '',
        'backup_type': '',
        'run_pre_restore': False,
    }

    req = client.post(
        f'/api/restore/source-dbs/{db_1.id}/config',
        json=post_data
    )
    assert req.status_code == 400

    assert 'backup_location' in req.json['errors']
    assert 'rman_cmd' in req.json['errors']
    assert 'pfile_content' in req.json['errors']
    assert 'backup_type' in req.json['errors']


@patch('bms_app.restore.services.upload_blob_from_string')
def test_run_pre_restore_required_fields(mock, client):
    pr = ProjectFactory()
    db_1 = SourceDBFactory(project=pr)
    ConfigFactory(source_db=db_1)

    post_data = {
        'backup_location': 'location',
        'rman_cmd': 'rmn',
        'is_configured': True,
        'pfile_content': 'text',
        'backup_type': 'full',
        'run_pre_restore': True,
        'control_file': '',
        'validations': [],
    }

    req = client.post(
        f'/api/restore/source-dbs/{db_1.id}/config',
        json=post_data
    )
    assert req.status_code == 400

    assert 'control_file' in req.json['errors']
    assert 'validations' in req.json['errors']
