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

from bms_app.services.operations.db_mappings import (
    get_restore_db_mappings_objects, get_wave_db_mappings_objects
)
from bms_app.services.operations.objects import DbMapping

from tests.factories import (
    MappingFactory, ProjectFactory, SourceDBFactory, SourceDBStatus,
    WaveFactory
)


def test_filter_by_wave_only(client):
    pr = ProjectFactory()
    wave = WaveFactory(project=pr)
    wave2 = WaveFactory(project=pr)
    db1 = SourceDBFactory(wave=wave)
    db2 = SourceDBFactory(wave=wave)
    SourceDBFactory(wave=wave)  # have no mapping, so should be skipped
    db3 = SourceDBFactory(wave=wave2)  # another wave, so should be ksipped

    m1 = MappingFactory(source_db=db1)  # rac
    m11 = MappingFactory(source_db=db1)  # rac
    m2 = MappingFactory(source_db=db2)
    MappingFactory(source_db=db3)

    db_mappings_objects = get_wave_db_mappings_objects(wave_id=wave.id)

    assert isinstance(db_mappings_objects, list)
    assert len(db_mappings_objects) == 2

    db_map1 = DbMapping(
        db=db1,
        mappings=[m1, m11]
    )
    assert db_map1 in db_mappings_objects

    db_map2 = DbMapping(
        db=db2,
        mappings=[m2]
    )
    assert db_map2 in db_mappings_objects


def test_filter_by_wave_and_db_ids(client):
    pr = ProjectFactory()
    wave = WaveFactory(project=pr)
    db1 = SourceDBFactory(wave=wave)
    db2 = SourceDBFactory(wave=wave)

    MappingFactory(source_db=db1)
    m2 = MappingFactory(source_db=db2)

    db_mappings_objects = get_wave_db_mappings_objects(
        wave_id=wave.id,
        db_ids=[db2.id]
    )

    assert isinstance(db_mappings_objects, list)
    assert len(db_mappings_objects) == 1

    assert db_mappings_objects == [DbMapping(db=db2, mappings=[m2])]


def test_filter_deployable(client):
    pr = ProjectFactory()
    wave = WaveFactory(project=pr)
    db1 = SourceDBFactory(wave=wave, status=SourceDBStatus.EMPTY)
    db2 = SourceDBFactory(wave=wave, status=SourceDBStatus.FAILED)
    db3 = SourceDBFactory(wave=wave, status=SourceDBStatus.DEPLOYED)
    db4 = SourceDBFactory(wave=wave, status=SourceDBStatus.ROLLBACKED)

    m1 = MappingFactory(source_db=db1)
    MappingFactory(source_db=db2)
    MappingFactory(source_db=db3)
    m4 = MappingFactory(source_db=db4)

    db_mappings_objects = get_wave_db_mappings_objects(
        wave_id=wave.id,
        filter_deployable=True
    )

    assert isinstance(db_mappings_objects, list)
    assert len(db_mappings_objects) == 2

    assert DbMapping(db=db1, mappings=[m1]) in db_mappings_objects
    assert DbMapping(db=db4, mappings=[m4]) in db_mappings_objects


def test_get_restore_db_mappings(client):
    pr = ProjectFactory()
    db1 = SourceDBFactory(project=pr)
    db2 = SourceDBFactory(project=pr)

    MappingFactory(source_db=db1)
    m2 = MappingFactory(source_db=db2)

    db_mappings_objects = get_restore_db_mappings_objects(db_id=db2.id)

    assert isinstance(db_mappings_objects, list)
    assert len(db_mappings_objects) == 1

    assert db_mappings_objects == [DbMapping(db=db2, mappings=[m2])]
