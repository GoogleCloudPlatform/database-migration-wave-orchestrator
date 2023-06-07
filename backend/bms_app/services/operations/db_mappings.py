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

from bms_app.models import Mapping, SourceDB, db

from .objects import DbMapping


def get_db_mappings_qs(wave_id=None, db_ids=None, filter_deployable=False):
    """Return queryset to retrieve source dbs according to the filters."""
    qs = db.session.query(SourceDB, Mapping).outerjoin(Mapping)

    if wave_id:
        qs = qs.filter(SourceDB.wave_id == wave_id)

    if db_ids:
        qs = qs.filter(SourceDB.id.in_(db_ids))

    if filter_deployable:
        qs = qs.filter(SourceDB.is_deployable.is_(True))

    return qs


def generate_db_mappings_objects(qs):
    """Get list of SourceDB/Mapping objects.

    Output: [
        DbMapping(db=<SourceDB 1>, mappings=[<Mapping 1>, <Mapping 2>]),
        DbMapping(db=<SourceDB 2>, mappings=[<Mapping 3>]),
        ....
    ]
    """
    data = {}

    for source_db, mapping in qs.all():
        db_id = source_db.id

        if db_id not in data:
            data[db_id] = {
                'db': source_db,
                'mappings': [],
            }
        
        if not mapping:
            data[db_id]['is_dms'] = True

        data[db_id]['mappings'].append(mapping)

    objects = []

    for obj in data.values():
        objects.append(
            DbMapping(
                db=obj['db'],
                mappings=obj['mappings'],
                is_dms=obj['is_dms'],
            )
        )

    return objects


def get_wave_db_mappings_objects(wave_id,
                                 db_ids=None,
                                 filter_deployable=False):
    """Return list of DbMapping objects for wave operations."""
    qs = get_db_mappings_qs(wave_id, db_ids, filter_deployable)
    return generate_db_mappings_objects(qs)


def get_restore_db_mappings_objects(db_id):
    """Return list of DbMapping objects for restore operations."""
    qs = get_db_mappings_qs(db_ids=[db_id], filter_deployable=False)
    return generate_db_mappings_objects(qs)
