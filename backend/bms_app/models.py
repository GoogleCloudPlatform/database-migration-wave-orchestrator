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

from datetime import datetime
from enum import Enum

from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import relationship
from sqlalchemy_utils import ChoiceType

from bms_app import db


now = datetime.now


source_db_to_label = db.Table('source_db_labels', db.Model.metadata,
    db.Column('db_id', db.Integer, db.ForeignKey('source_dbs.id')),
    db.Column('label_id', db.Integer, db.ForeignKey('labels.id'))
)


class Project(db.Model):
    __tablename__ = 'projects'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False, unique=True)
    vpc = db.Column(db.String, nullable=False)
    subnet = db.Column(db.String, nullable=False)
    description = db.Column(db.String, nullable=False)

    waves = relationship('Wave', back_populates='project')
    source_dbs = relationship('SourceDB', back_populates='project')
    labels = relationship('Label', back_populates='project')

class DBTool(db.Model):
    __tablename__ = 'dbtools'

    id = db.Column(db.Integer, primary_key=True)
    db_engine = db.Column(db.String, nullable=False)
    type = db.Column(db.String, nullable=True, index=True)

    #source_dbs = relationship('SourceDB', back_populates='db_engine')
    source_db = relationship('SourceDB', back_populates='dbtools')
    bms = relationship('BMSServer', back_populates='dbtools')


class BMSServer(db.Model):
    __tablename__ = 'bms_servers'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, unique=True)
    state = db.Column(db.String)
    machine_type = db.Column(db.String)
    luns = db.Column(db.JSON)
    networks = db.Column(db.JSON)
    deleted = db.Column(db.Boolean, default=False)
    secret_name = db.Column(db.String)
    cpu = db.Column(db.String)
    socket = db.Column(db.String)
    ram = db.Column(db.String)
    created_at = db.Column(db.DateTime, default=datetime.now)
    location = db.Column(db.String)

    db_tool_id = db.Column(db.Integer,db.ForeignKey('dbtools.id'),nullable=True)
    db_version = db.Column(db.String)
    db_port    = db.Column(db.Numeric)


    mapping = relationship('Mapping', back_populates='bms')
    dbtools = relationship('DBTool', back_populates='bms')


class SourceDBType(Enum):
    SI = 'SI'
    RAC = 'RAC'
    DG = 'DG'


class SourceDBStatus(Enum):
    EMPTY = 'EMPTY'
    ROLLBACKED = 'ROLLBACKED'
    FAILED = 'FAILED'
    DEPLOYED = 'DEPLOYED'
    PRE_RESTORE = 'PRE_RESTORE'
    PRE_RESTORE_COMPLETE = 'PRE_RESTORE_COMPLETE'
    PRE_RESTORE_FAILED = 'PRE_RESTORE_FAILED'
    DT = 'DT'
    DT_COMPLETE = 'DT_COMPLETE'
    DT_FAILED = 'DT_FAILED'
    DT_PARTIALLY = 'DT_PARTIALLY'
    DT_ROLLBACK = 'DT_ROLLBACK'
    FAILOVER = 'FAILOVER'
    FAILOVER_COMPLETE = 'FAILOVER_COMPLETE'
    FAILOVER_FAILED = 'FAILOVER_FAILED'


class SourceDB(db.Model):
    __tablename__ = 'source_dbs'
    __table_args__ = (db.UniqueConstraint('server', 'db_name', 'project_id'), )

    DEPLOYABLE_STATUSES = (SourceDBStatus.EMPTY, SourceDBStatus.ROLLBACKED)

    id = db.Column(db.Integer, primary_key=True)
    server = db.Column(db.String, nullable=False)
    oracle_version = db.Column(db.String, nullable=True)
    oracle_release = db.Column(db.String)
    oracle_edition = db.Column(db.String, default='EE')
    db_type = db.Column(ChoiceType(SourceDBType, impl=db.String(10)), default=SourceDBType.SI)
    rac_nodes = db.Column(db.Integer, default=0)  # value parsed from assessment file
    fe_rac_nodes = db.Column(db.Integer)
    arch = db.Column(db.String, nullable=True)
    cores = db.Column(db.Integer, nullable=False)
    ram = db.Column(db.Integer, nullable=False)
    allocated_memory = db.Column(db.Integer, nullable=False)
    db_name = db.Column(db.String, nullable=False)
    db_size = db.Column(db.Numeric, nullable=False)
    status = db.Column(ChoiceType(SourceDBStatus, impl=db.String(20)), default=SourceDBStatus.EMPTY)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=False)
    wave_id = db.Column(db.Integer, db.ForeignKey('waves.id'))

    db_tool_id = db.Column(db.Integer,db.ForeignKey('dbtools.id'),nullable=True)
    db_version = db.Column(db.String)
    db_port    = db.Column(db.Numeric)

    wave = relationship('Wave', back_populates='source_db', uselist=False)
    config = relationship('Config', back_populates='source_db', uselist=False)
    mappings = relationship('Mapping', back_populates='source_db')
    project = relationship(Project, back_populates='source_dbs', uselist=False)
    restore_config = relationship('RestoreConfig', back_populates='source_db', uselist=False)
    scheduled_tasks = relationship('ScheduledTask', back_populates='source_db')

    dbtools = relationship('DBTool', back_populates='source_db')

   ## mappings = relationship('Mapping', back_populates='source_db')

    labels = db.relationship('Label', secondary=source_db_to_label, back_populates='source_dbs', cascade='save-update, merge')


    @hybrid_property
    def is_rac(self):
        return self.db_type == SourceDBType.RAC

    @hybrid_property
    def is_deployable(self):
        return self.status in self.DEPLOYABLE_STATUSES

    @is_deployable.expression
    def is_deployable(cls):
        return cls.status.in_(cls.DEPLOYABLE_STATUSES)


class Config(db.Model):
    __tablename__ = 'configs'

    id = db.Column(db.Integer, primary_key=True)
    db_id = db.Column(db.Integer, db.ForeignKey('source_dbs.id'), unique=True, nullable=False)
    install_config_values = db.Column(db.JSON)
    db_params_values = db.Column(db.JSON)
    data_mounts_values = db.Column(db.JSON)
    asm_config_values = db.Column(db.JSON)
    rac_config_values = db.Column(db.JSON)
    misc_config_values = db.Column(db.JSON)
    created_at = db.Column(db.DateTime)
    is_configured = db.Column(db.Boolean, default=False)
    network_config_values = db.Column(db.JSON)

    source_db = relationship('SourceDB', back_populates='config')


class Wave(db.Model):
    __tablename__ = 'waves'
    __table_args__ = (db.UniqueConstraint('name', 'project_id'), )

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=False)
    is_running = db.Column(db.Boolean, default=False)

    project = relationship(Project, back_populates='waves', uselist=False)
    operations = relationship('Operation', back_populates='wave')
    source_db = relationship('SourceDB', back_populates='wave')
    operation_details = relationship('OperationDetails', back_populates='wave')


class Mapping(db.Model):
    __tablename__ = 'mappings'
    __table_args__ = (db.UniqueConstraint('db_id', 'bms_id'), )

    id = db.Column(db.Integer, primary_key=True)
    db_id = db.Column(db.Integer, db.ForeignKey('source_dbs.id'), nullable=False)
    bms_id = db.Column(db.Integer, db.ForeignKey('bms_servers.id'), nullable=False)
    rac_node = db.Column(db.Integer)  # node order in RAC

    bms = relationship('BMSServer', back_populates='mapping')
    source_db = relationship('SourceDB', back_populates='mappings')
    operation_details = relationship('OperationDetails', back_populates='mapping')


class OperationStatus(Enum):
    STARTING = 'STARTING'
    IN_PROGRESS = 'IN_PROGRESS'
    COMPLETE = 'COMPLETE'
    FAILED = 'FAILED'
    COMPLETE_PARTIALLY = 'COMPLETE_PARTIALLY'


class OperationType(Enum):
    DEPLOYMENT = 'DEPLOYMENT'
    ROLLBACK = 'ROLLBACK'
    PRE_RESTORE = 'PRE_RESTORE'
    BACKUP_RESTORE = 'BACKUP_RESTORE'
    IMPORT_EXPORT = 'IMPORT_EXPORT'
    DATA_GUARD = 'DATA_GUARD'
    ROLLBACK_RESTORE = 'ROLLBACK_RESTORE'
    DB_FAILOVER = 'DB_FAILOVER'


class Operation(db.Model):
    __tablename__ = 'operations'

    id = db.Column(db.Integer, primary_key=True)
    wave_id = db.Column(db.Integer, db.ForeignKey('waves.id'), nullable=True)
    operation_type = db.Column(ChoiceType(OperationType, impl=db.String(20)))
    status = db.Column(ChoiceType(OperationStatus, impl=db.String(20)))
    started_at = db.Column(db.DateTime, default=now)
    completed_at = db.Column(db.DateTime)

    wave = relationship('Wave', back_populates='operations', uselist=False)
    operation_details = relationship('OperationDetails', back_populates='operation')

    @hybrid_property
    def is_deployment(self):
        return self.operation_type == OperationType.DEPLOYMENT

    @hybrid_property
    def is_rollback(self):
        return self.operation_type == OperationType.ROLLBACK


class OperationDetails(db.Model):
    __tablename__ = 'operation_details'

    id = db.Column(db.Integer, primary_key=True)
    mapping_id = db.Column(db.Integer, db.ForeignKey('mappings.id'), nullable=False)
    wave_id = db.Column(db.Integer, db.ForeignKey('waves.id'), nullable=True)
    operation_id = db.Column(db.Integer, db.ForeignKey('operations.id'), nullable=False)
    operation_type = db.Column(ChoiceType(OperationType, impl=db.String(20)))
    step = db.Column(db.String(20))
    step_upd_at = db.Column(db.DateTime)
    status = db.Column(ChoiceType(OperationStatus, impl=db.String(20)))
    started_at = db.Column(db.DateTime, default=now)
    completed_at = db.Column(db.DateTime)

    mapping = relationship('Mapping', back_populates='operation_details')
    wave = relationship('Wave', back_populates='operation_details')
    operation = relationship('Operation', back_populates='operation_details')
    errors = relationship('OperationDetailsError', back_populates='operation_details')

    @hybrid_property
    def is_deployment(self):
        return self.operation_type == OperationType.DEPLOYMENT

    @hybrid_property
    def is_rollback(self):
        return self.operation_type == OperationType.ROLLBACK


class OperationDetailsError(db.Model):
    __tablename__ = 'operation_details_errors'

    id = db.Column(db.Integer, primary_key=True)
    operation_details_id = db.Column(db.Integer, db.ForeignKey('operation_details.id'), nullable=False)
    message = db.Column(db.String(255), nullable=False)

    operation_details = relationship('OperationDetails', back_populates='errors', uselist=False)


class BackupType(Enum):
    NONE = ''
    FULL = 'full'
    INCREMENTAL = 'incremental'
    ARCHIVE_LOG = 'archivelogs'

    @classmethod
    def values(cls):
        return [x.value for x in cls]


class RestoreConfig(db.Model):
    __tablename__ = 'restore_configs'

    id = db.Column(db.Integer, primary_key=True)
    db_id = db.Column(db.Integer, db.ForeignKey('source_dbs.id'), unique=True, nullable=False)
    backup_location = db.Column(db.String, nullable=False, server_default='', default='')
    rman_cmd = db.Column(db.Text, nullable=False, server_default='', default='')
    is_configured = db.Column(db.Boolean, nullable=False, server_default='f', default=False)
    pfile_file = db.Column(db.String, nullable=False, server_default='', default='')
    pwd_file = db.Column(db.String, nullable=False, server_default='', default='')
    tnsnames_file = db.Column(db.String, nullable=False, server_default='', default='')
    listener_file = db.Column(db.String, nullable=False, server_default='', default='')
    backup_type = db.Column(ChoiceType(BackupType, impl=db.String()), default='')
    run_pre_restore = db.Column(db.Boolean, nullable=False, default=False, server_default='0')
    control_file = db.Column(db.String, nullable=False, server_default='', default='')
    validations = db.Column(db.JSON, default=list)

    source_db = relationship('SourceDB', back_populates='restore_config')

    @hybrid_property
    def is_full_backup_type(self):
        return self.backup_type is BackupType.FULL


class ScheduledTask(db.Model):
    __tablename__ = 'scheduled_tasks'

    id = db.Column(db.Integer, primary_key=True)
    g_task_name = db.Column(db.String, nullable=False, default='')  # task name in GoogleTask
    schedule_time = db.Column(db.DateTime, nullable=False)  # utc tz
    completed = db.Column(db.Boolean, nullable=False, default=False)
    db_id = db.Column(db.Integer, db.ForeignKey('source_dbs.id'), nullable=False)

    source_db = relationship('SourceDB', back_populates='scheduled_tasks')


class Label(db.Model):
    __tablename__ = 'labels'
    __table_args__ = (db.UniqueConstraint('name', 'project_id'), )

    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=False)
    name = db.Column(db.String(15), nullable=False, index=True)

    project = relationship(Project, back_populates='labels')
    source_dbs = relationship('SourceDB', secondary=source_db_to_label, back_populates='labels', cascade='save-update, merge')


# statuses that mean that operation is alredy finished
FINISHED_OPERATION_STATUSES = (
    OperationStatus.COMPLETE,
    OperationStatus.FAILED
)

# order in which operation status can change
OPERATION_STATUSES_ORDER = [
    OperationStatus.STARTING,
    OperationStatus.IN_PROGRESS,
    OperationStatus.FAILED,  # final
    OperationStatus.COMPLETE,  # final
]

# DB statuses that displayed on Data Transfer Manager page
DATA_TRANSFER_DB_STATUSES = [
    SourceDBStatus.DEPLOYED,
    SourceDBStatus.PRE_RESTORE,
    SourceDBStatus.PRE_RESTORE_COMPLETE,
    SourceDBStatus.PRE_RESTORE_FAILED,
    SourceDBStatus.DT,
    SourceDBStatus.DT_COMPLETE,
    SourceDBStatus.DT_FAILED,
    SourceDBStatus.DT_PARTIALLY,
    SourceDBStatus.DT_ROLLBACK,
    SourceDBStatus.FAILOVER,
    SourceDBStatus.FAILOVER_COMPLETE,
    SourceDBStatus.FAILOVER_FAILED,
]

WAVE_OPERATIONS = [
    OperationType.DEPLOYMENT,
    OperationType.ROLLBACK
]

PRE_RESTORE_ALLOWED_STATUSES = [
    SourceDBStatus.DEPLOYED,
    SourceDBStatus.PRE_RESTORE_FAILED,
    SourceDBStatus.PRE_RESTORE_COMPLETE,
]

RESTORE_ALLOWED_STATUSES = [
    # Also depends on RestoreConfig.run_pre_restore
    # See bms_app.services.operations.utils.is_restore_allowed function
    SourceDBStatus.DT_COMPLETE,
    SourceDBStatus.DT_PARTIALLY,
    SourceDBStatus.FAILOVER_FAILED,
]

ROLLBACK_RESTORE_ALLOWED_STATUSES = [
    SourceDBStatus.DT_COMPLETE,
    SourceDBStatus.DT_PARTIALLY,
    SourceDBStatus.DT_FAILED,
    SourceDBStatus.FAILOVER_FAILED,
    SourceDBStatus.FAILOVER_COMPLETE,
]

FAILOVER_ALLOWED_STATUSES = [
    SourceDBStatus.DT_COMPLETE
]

# statuses which mean that db is deployed
DEPLOYED_STATUSES = [
    SourceDBStatus.DEPLOYED,
    SourceDBStatus.PRE_RESTORE,
    SourceDBStatus.PRE_RESTORE_COMPLETE,
    SourceDBStatus.PRE_RESTORE_FAILED,
    SourceDBStatus.DT,
    SourceDBStatus.DT_COMPLETE,
    SourceDBStatus.DT_FAILED,
    SourceDBStatus.DT_PARTIALLY,
    SourceDBStatus.DT_ROLLBACK,
    SourceDBStatus.FAILOVER,
    SourceDBStatus.FAILOVER_COMPLETE,
    SourceDBStatus.FAILOVER_FAILED,
]