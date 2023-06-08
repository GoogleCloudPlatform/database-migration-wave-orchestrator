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
from sqlalchemy import func

from bms_app.models import (
    DEPLOYED_STATUSES, OPERATION_STATUSES_ORDER, BMSServer, Config, Mapping,
    Operation, OperationDetails, OperationType, SourceDB, SourceDBStatus, Wave,
    SourceDBEngine, db
)
from bms_app.schema import WaveSchema
from bms_app.services.utils import generate_target_gcp_logs_link
from bms_app.wave_steps import DEPLOYMENT_STEPS, ROLLBACK_STEPS


def validate_wave_name_is_unique(name, project_id, exclude_wave_id=None):
    """Raise err if wave name already exist in the project."""
    qs = Wave.query.filter(
        Wave.name == name,
        Wave.project_id == project_id
    )

    if exclude_wave_id:
        qs = qs.filter(Wave.id != exclude_wave_id)

    if qs.count():
        raise ValidationError({'name': ['This name already exists']})


def get_wave_steps(operation):
    if operation.is_deployment:
        return DEPLOYMENT_STEPS

    if operation.is_rollback:
        return ROLLBACK_STEPS

    return []


def wave_rate_info(wave_id):
    """Calculate of undeployed, deployed and failed db for each wave."""
    undeployed_db = 0
    deployed_db = 0
    failed_db = 0

    rate_info = db.session.query(SourceDB.status, func.count()) \
        .filter(SourceDB.wave_id == wave_id) \
        .group_by(SourceDB.status) \
        .all()

    if rate_info:
        undeployed_db = sum((x[1] for x in rate_info if x[0] in SourceDB.DEPLOYABLE_STATUSES), 0)
        deployed_db = sum((x[1] for x in rate_info if x[0] in DEPLOYED_STATUSES), 0)
        failed_db = next((x[1] for x in rate_info if x[0] == SourceDBStatus.FAILED), 0)

    return {
        'undeployed': undeployed_db,
        'deployed': deployed_db,
        'failed': failed_db
    }


def list_waves_service(project_id):
    """Return list of waves."""
    qs = db.session.query(Wave)

    if project_id:
        qs = qs.filter(Wave.project_id == project_id)

    waves_data = WaveSchema(many=True).dump(qs)

    for wave in waves_data:
        wave['status_rate'] = wave_rate_info(wave['id'])

        # add step data if wave is running
        if wave['is_running']:
            wave['step'] = RunningWaveDetails(wave['id']).get_step_data()

    return waves_data


def add_secret_name_status(mappings_data, secret_names):
    for db_id in mappings_data:
        mappings_data[db_id]['has_secret_name'] = all(secret_names[db_id])


def add_aggregated_db_status(wave_mappings_data):
    """Add calculated db status based on statuses of targtes.

    Compare statuses from the db and to predifined ordered list.
    That list is organized in the order in which stasuses can change.
    So the 1-st found status can be treated as status of the operation.
    """
    for db_id in wave_mappings_data:
        all_statuses = [
            x['operation_status'] for x in wave_mappings_data[db_id]['bms']
        ]

        status = ''

        for st_option in OPERATION_STATUSES_ORDER:
            if st_option.value in all_statuses:
                status = st_option.value
                break

        wave_mappings_data[db_id]['operation_status'] = status


class LastOpWaveDetails:
    """Provide info about wave last operation."""

    def __init__(self, wave_id):
        self.wave_id = wave_id

    def get_extra_data(self):
        """Return details re last deployment and all db mappings."""
        return {
            'last_deployment': self._get_last_deployment_data(),
            'mappings': self._get_mappings_data(),
        }

    def _get_last_deployment_data(self):
        """Retun last deploymnet data."""
        last_deploy = db.session.query(Operation) \
            .filter(Operation.wave_id == self.wave_id,
                    Operation.operation_type == OperationType.DEPLOYMENT) \
            .order_by(Operation.id.desc()) \
            .first()

        if last_deploy:
            return {
                'id': last_deploy.id,
                'started_at': last_deploy.started_at,
                'completed_at': last_deploy.completed_at,
                'operation_type': last_deploy.operation_type.value,
            }
    
    def _get_dms_auto_mappings(self):
        query = db.session.query(SourceDB)\
            .outerjoin(Config) \
            .with_entities(SourceDB, Config.is_configured) \
            .filter(SourceDB.wave_id == self.wave_id) \
            .filter(SourceDB.db_engine == SourceDBEngine.POSTGRES)

        mappings = [] 
        for source_db, is_configured in query:
            mapping = {
                'server': source_db.server,
                'db_id': source_db.id,
                'db_name': source_db.db_name,
                'is_deployable': source_db.is_deployable,
                'is_dms_auto_mapping': True,
                'db_engine': source_db.db_engine.value,
                'operation_type': None, # TODO: get last operation type
                'operation_status': '',
                'operation_id': None, # TODO: get last operation id
                'is_configured': is_configured if is_configured is not None else False,
            }
            mappings.append(mapping)
        
        return mappings

    def _get_mappings_data(self):
        """Return info and last operation for each db mapping."""
        mappings_data = {}
        secret_names = {}

        # get latest operation id per mapping/bms_target
        subq = db.session.query(OperationDetails) \
            .with_entities(func.max(OperationDetails.id)) \
            .filter(OperationDetails.wave_id == self.wave_id) \
            .group_by(OperationDetails.mapping_id)
        # get latest operation details/history for these mappings
        joinq = db.session.query(OperationDetails) \
            .filter(OperationDetails.id.in_(subq)) \
            .subquery()

        query = db.session.query(Mapping, SourceDB, BMSServer, joinq) \
            .outerjoin(SourceDB) \
            .outerjoin(BMSServer) \
            .outerjoin(Config) \
            .with_entities(SourceDB, BMSServer, Config.is_configured,
                           joinq.c.operation_type, joinq.c.status,
                           joinq.c.operation_id, joinq.c.step) \
            .outerjoin(joinq, Mapping.id == joinq.c.mapping_id) \
            .filter(SourceDB.wave_id == self.wave_id)

        for row in query:
            source_db, bms_server, is_configured, last_op_type, \
                last_op_status, last_op_id, last_op_step = row
            db_id = source_db.id

            if db_id not in mappings_data:
                mappings_data[db_id] = {
                    'server': source_db.server,
                    'db_id': source_db.id,
                    'db_name': source_db.db_name,
                    'db_type': source_db.db_type.value,
                    'is_deployable': source_db.is_deployable,
                    'operation_type': last_op_type.value if last_op_type else None,
                    'operation_status': '',
                    'operation_id': last_op_id,
                    'bms': [],
                    'is_configured': is_configured if is_configured is not None else False,
                }

                secret_names[db_id] = [bool(bms_server.secret_name)]

            mappings_data[db_id]['bms'].append({
                'bms_id': bms_server.id,
                'bms_name': bms_server.name,
                'operation_status': last_op_status.value if last_op_status else None,
                'operation_step': last_op_step,

            })
        add_secret_name_status(mappings_data, secret_names)

        add_aggregated_db_status(mappings_data)

        dms_auto_mappings = self._get_dms_auto_mappings()

        return list(mappings_data.values()) + dms_auto_mappings


class RunningWaveDetails:
    """Running wave data."""

    def __init__(self, wave_id):
        self.wave_id = wave_id
        self._curr_op = None

    @property
    def curr_op(self):
        if not self._curr_op:
            self._curr_op = db.session.query(Operation) \
                .filter(Operation.wave_id == self.wave_id) \
                .order_by(Operation.id.desc()) \
                .first()
        return self._curr_op

    def get_extra_data(self):
        """Return details re current running operation and its db mappings."""
        return {
            'curr_operation': self._get_running_op_data(),
            'mappings': self._get_running_mappings_data(),
        }

    def get_step_data(self):
        """Return current/total step number."""
        all_steps = db.session.query(OperationDetails.step). \
            filter(OperationDetails.operation_id == self.curr_op.id). \
            all()
        all_steps = [x[0] for x in all_steps]
        wave_steps = get_wave_steps(self.curr_op)

        last_step_index = 0
        # find the latest step within all_steps
        for ind, item in enumerate(wave_steps, 1):
            if item['id'] in all_steps:
                last_step_index = ind

        return {
            'curr_step': last_step_index,
            'total_steps': len(wave_steps)
        }

    def _get_running_op_data(self):
        return {
            'operation_type': self.curr_op.operation_type.value,
            'started_at': self.curr_op.started_at,
            'completed_at': self.curr_op.completed_at,
            'id': self.curr_op.id,
        }

    def _get_running_mappings_data(self):
        """Return running mappings data."""
        query = db.session.query(OperationDetails, SourceDB, BMSServer, Config) \
            .filter(OperationDetails.operation_id == self.curr_op.id) \
            .outerjoin(Mapping, OperationDetails.mapping_id == Mapping.id) \
            .outerjoin(SourceDB, Mapping.db_id == SourceDB.id) \
            .outerjoin(BMSServer, Mapping.bms_id == BMSServer.id) \
            .outerjoin(Config)
        mappings = {}
        secret_names = {}
        for op_details, source_db, bms_server, config in query:
            db_id = source_db.id
            if db_id not in mappings:
                mappings[db_id] = {
                    'server': source_db.server,
                    'db_id': source_db.id,
                    'db_name': source_db.db_name,
                    'db_type': source_db.db_type.value,
                    'is_deployable': source_db.is_deployable,
                    'operation_type': op_details.operation_type.value,
                    'operation_id': op_details.operation_id,
                    'bms': [],
                    'is_configured': config.is_configured if config else False,
                }

            logs_url = generate_target_gcp_logs_link(op_details, bms_server)
            mappings[db_id]['bms'].append({
                'id': bms_server.id,
                'name': bms_server.name,
                'operation_status': op_details.status.value,
                'operation_step': op_details.step,
                'logs_url': logs_url
            })

            secret_names[db_id] = [bool(bms_server.secret_name)]

        add_secret_name_status(mappings, secret_names)

        add_aggregated_db_status(mappings)

        return list(mappings.values())


class GetWaveService:
    @classmethod
    def run(cls, wave_id, return_details=False):
        """Return wave data."""
        wave = Wave.query.get_or_404(wave_id)
        data = WaveSchema().dump(wave)

        data['status_rate'] = wave_rate_info(wave_id)

        if wave.is_running:
            wave_details_cls = RunningWaveDetails(wave_id=wave_id)
            data['step'] = wave_details_cls.get_step_data()
        else:
            wave_details_cls = LastOpWaveDetails(wave_id=wave_id)

        if return_details:
            data['mappings_count'] = cls._get_mappings_count(wave_id)
            extra_data = wave_details_cls.get_extra_data()
            data.update(extra_data)

        return data

    @staticmethod
    def _get_mappings_count(wave_id):
        """Count total number of mappings of the specific wave."""
        return db.session.query(Mapping) \
            .join(SourceDB) \
            .filter(SourceDB.wave_id == wave_id) \
            .count()


def assign_source_db_wave(wave, db_ids):
    """Assign wave to databases, and count assigned, skipped and unmapped"""
    assigned = skipped = unmapped = 0

    # join Mapping in order to know if db is mapped to any target
    query = db.session.query(SourceDB, func.count(Mapping.id))\
        .outerjoin(Mapping, SourceDB.id == Mapping.db_id)\
        .filter(
            SourceDB.id.in_(db_ids),
            SourceDB.project_id == wave.project_id) \
        .group_by(SourceDB)\
        .all()

    for source_db, mapp_count in query:
        if not mapp_count and source_db.db_engine == SourceDBEngine.ORACLE:
            unmapped += 1
        # assign only db without any operation
        elif source_db.status == SourceDBStatus.EMPTY and \
                (not source_db.wave or not source_db.wave.is_running):
            source_db.wave_id = wave.id
            assigned += 1
        else:
            skipped += 1

    db.session.commit()

    return {
        'assigned': assigned,
        'skipped': skipped,
        'unmapped': unmapped,
    }
