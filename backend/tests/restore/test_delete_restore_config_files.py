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
from unittest.mock import patch

import pytest

from bms_app import settings
from bms_app.restore.services import DeleteConfigFileService

from tests.factories import (
    ConfigFactory, ProjectFactory, RestoreConfigFactory, SourceDBFactory
)


@pytest.mark.parametrize(
    'file_name,field_name',
    [
        ('pfile.ora', 'pfile_file'),
        ('pwd_file.ora', 'pwd_file'),
        ('tnsnames_file.ora', 'tnsnames_file'),
        ('listener_file.ora', 'listener_file'),
    ]
)
@patch('bms_app.restore.services.delete_blob')
def test_delete_config_file(delete_mock, file_name, field_name, client):
    """Test DeleteConfigFileService."""
    pr = ProjectFactory()
    db_1 = SourceDBFactory(project=pr)
    ConfigFactory(source_db=db_1)
    restore_conf = RestoreConfigFactory(source_db=db_1)

    DeleteConfigFileService.run(
        restore_conf,
        file_name,
        field_name
    )

    gcs_key = os.path.join(
        settings.GCP_RESTORE_CONFIGS_PREFIX,
        str(db_1.id),
        file_name
    )

    delete_mock.assert_called_with(
        settings.GCS_BUCKET,
        gcs_key
    )

    assert not getattr(restore_conf, field_name)


@pytest.mark.parametrize(
    'fname, file_name,field_name',
    [
        ('pfile', 'pfile.ora', 'pfile_file'),
        ('pwd_file', 'pwd_file.ora', 'pwd_file'),
        ('tnsnames_file', 'tnsnames_file.ora', 'tnsnames_file'),
        ('listener_file', 'listener_file.ora', 'listener_file'),
    ]
)
@patch('bms_app.restore.restore_config_views.DeleteConfigFileService.run')
def test_delete_config_file_api(delete_srv_mock, fname, file_name, field_name, client):
    """Test delete config file api"""
    pr = ProjectFactory()
    db_1 = SourceDBFactory(project=pr)
    ConfigFactory(source_db=db_1)
    restore_conf = RestoreConfigFactory(source_db=db_1)

    client.delete(f'/api/restore/source-dbs/{db_1.id}/config/{fname}')

    delete_srv_mock.assert_called_with(
        restore_conf,
        file_name=file_name,
        config_field_name=field_name
    )
