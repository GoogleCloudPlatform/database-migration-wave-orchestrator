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

from marshmallow import ValidationError

from bms_app.models import (
    DEPLOYED_STATUSES, BMSServer, Config, Mapping, SourceDB, SourceDBType,
    Wave, db , DBTool
)
from bms_app.services.source_db import (
    clear_bms_target_params, does_db_have_operation
)

import sys

def validate_db(db_id):
    """Check if db can be mapped.

    Only RAC db can be mapped to multiple bms targets.
    """
    source_db = SourceDB.query.get(db_id)
    if not source_db:
        raise ValidationError({'db_id': ['no such database']})

    is_rac = source_db.db_type == SourceDBType.RAC
    if Mapping.query.filter(Mapping.db_id == db_id).count() \
            and not is_rac:
        raise ValidationError({'db_id': ['database already has mapping']})


def validate_bms(bms_id, db_id=None):
    if not BMSServer.query.get(bms_id):
        raise ValidationError({'bms_id': ['no such bms server']})

    qs = Mapping.query.filter(Mapping.bms_id == bms_id)
    if db_id:  # exclude current mapping
        qs = qs.filter(Mapping.db_id != db_id)

    if qs.count():
        raise ValidationError({'bms_id': ['server already has mapping']})


def validate_wave(wave_id):
    if not Wave.query.get(wave_id):
        raise ValidationError({'wave_id': ['no such wave']})


class GetMappingsService:
    @classmethod
    def run(cls, project_id=None, db_id=None):
        """Return list of mappings. Filter by project/db_id optionally."""
        query = cls._generate_query(project_id, db_id)

        data = {}
        for mapping, source_db, bms_server, config in query:
            if mapping.db_id not in data:
                data[mapping.db_id] = cls._add_main_data(
                    mapping, source_db, bms_server, config
                )

                for label in source_db.labels:
                    data[mapping.db_id]['labels'].append(
                        cls._add_label_data(label)
                    )

            data[mapping.db_id]['bms'].append(
                cls._add_bms_data(bms_server)
            )

        return list(data.values())

    @staticmethod
    def _generate_query(project_id, db_id):
        query = (
            db.session.query(Mapping, SourceDB, BMSServer, Config)
            .join(BMSServer)
            .join(SourceDB)
            .outerjoin(Config)  # might not exists at some point
            .order_by(Mapping.rac_node)
        )

        if project_id:
            query = query.filter(SourceDB.project_id == project_id)

        if db_id:
            query = query.filter(Mapping.db_id == db_id)

        return query.all()

    @classmethod
    def _add_main_data(cls, mapping, source_db,bms_server,  config):
        return {
            'id': mapping.id,
            'db_id': mapping.db_id,
            'bms': [],
            'wave_id': source_db.wave_id,
            'source_hostname': source_db.server,
            'db_name': source_db.db_name,
            'oracle_version': source_db.oracle_version,
            'oracle_release': source_db.oracle_release,
            'db_type': source_db.db_type.value,
            'is_rac': source_db.db_type == SourceDBType.RAC,
            'fe_rac_nodes': source_db.fe_rac_nodes,
            'is_configured': config.is_configured if config else False,
            'is_deployed': cls._check_if_deployed(source_db),
            'labels': [],
            'editable': not does_db_have_operation(source_db.id),
            'target_db_tool_id': bms_server.db_tool_id,
        }

    @staticmethod
    def _check_if_deployed(source_db):
        return source_db.status in DEPLOYED_STATUSES

    @staticmethod
    def _add_bms_data(bms_server):
        return {
            'id': bms_server.id,
            'name': bms_server.name,
            # 'rac_node': mapping.rac_node,
        }

    @staticmethod
    def _add_label_data(label):
        return {
                'id': label.id,
                'name': label.name
        }


class AddMappingService:
    @classmethod
    def run(cls, db_id, bms_ids, wave_id=None, fe_rac_nodes=None):
        cls._validate(db_id, bms_ids)

        source_db = SourceDB.query.get_or_404(db_id)

        source_db.wave_id = wave_id
        db.session.add(source_db)

        if fe_rac_nodes is not None:
            source_db.fe_rac_nodes = fe_rac_nodes
            db.session.add(source_db)

        mappings = []
        for index, bms_id in enumerate(bms_ids, 1):
            mappings.append(Mapping(
                db_id=db_id,
                bms_id=bms_id,
                rac_node=index if source_db.is_rac else None,
            ))

        db.session.add_all(mappings)
        db.session.commit()

        return mappings

    @classmethod
    def _validate(cls, db_id, bms_ids):
        validate_db(db_id)

        for bms_id in bms_ids:
            validate_bms(bms_id)


class EditMappingService:
    @classmethod
    def run(cls, db_id, new_bms_ids, wave_id, fe_rac_nodes):
        cls._validate(wave_id, new_bms_ids, db_id)

        source_db = SourceDB.query.get_or_404(db_id)

        if fe_rac_nodes is not None:
            source_db.fe_rac_nodes = fe_rac_nodes
            db.session.add(source_db)

        if source_db.wave_id != wave_id:
            source_db.wave_id = wave_id
            db.session.add(source_db)

        cls._re_create_mappings(source_db, new_bms_ids)

        db.session.commit()

    @classmethod
    def _re_create_mappings(cls, source_db, new_bms_ids):
        db_id = source_db.id

        qs = db.session.query(Mapping) \
            .with_entities(Mapping.bms_id) \
            .filter(Mapping.db_id == db_id) \
            .all()
        existing_bms_ids = [x[0] for x in qs]

        # re-create mappings and clear config in case there are some changes
        if set(existing_bms_ids) != set(new_bms_ids):
            # delete all mappings for specific db
            db.session.query(Mapping).filter(Mapping.db_id == db_id)\
                .delete(synchronize_session=False)

            # create new mappings for db
            for index, bms_id in enumerate(new_bms_ids, 1):
                mapping = Mapping(
                    db_id=db_id,
                    bms_id=bms_id,
                    rac_node=index if source_db.is_rac else None,
                )
                db.session.add(mapping)

            if not new_bms_ids:
                source_db.wave_id = None
                db.session.add(source_db)

            cls._clear_db_config(source_db)

    @staticmethod
    def _clear_db_config(source_db):
        config = source_db.config
        if config:
            clear_bms_target_params(config)

    @classmethod
    def _validate(cls, wave_id, bms_ids, db_id):
        for bms_id in bms_ids:
            validate_bms(bms_id, db_id=db_id)

        if wave_id:
            validate_wave(wave_id)
