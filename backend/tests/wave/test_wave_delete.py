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

from bms_app.models import Wave, db

from tests.factories import (
    OperationFactory, ProjectFactory, SourceDBFactory, WaveFactory
)


def test_delete_a_wave(client):
    pr = ProjectFactory()
    wave_1 = WaveFactory(project=pr)
    WaveFactory(project=pr)

    req = client.delete(f'/api/waves/{wave_1.id}')

    assert req.status_code == 204
    assert db.session.query(Wave).count() == 1
    assert not db.session.query(Wave).get(wave_1.id)


def test_update_db_on_delete_wave(client):
    pr_1 = ProjectFactory()
    wave_1 = WaveFactory(project=pr_1)
    db_1 = SourceDBFactory(project=pr_1, wave=wave_1)

    req = client.delete(f'/api/waves/{wave_1.id}')
    assert req.status_code == 204

    assert not db_1.wave_id
    assert not db.session.query(Wave).count()


def test_error_deletion_if_operation_exists(client):
    wave_1 = WaveFactory()
    OperationFactory(wave=wave_1)

    req = client.delete(f'/api/waves/{wave_1.id}')
    assert req.status_code == 400
