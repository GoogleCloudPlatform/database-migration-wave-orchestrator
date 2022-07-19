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

import factory
from factory.alchemy import SQLAlchemyModelFactory

from bms_app.models import (
    BMSServer, Config, Label, Mapping, Operation, OperationDetails,
    OperationDetailsError, Project, RestoreConfig, ScheduledTask, SourceDB,
    SourceDBStatus, SourceDBType, Wave, db
)


class ProjectFactory(SQLAlchemyModelFactory):
    class Meta:
        model = Project
        sqlalchemy_session = db.session
        sqlalchemy_session_persistence = 'commit'

    name = factory.Sequence(lambda n: f'project_{n}')
    description = factory.Faker('text', max_nb_chars=100)
    vpc = factory.Faker('word')
    subnet = factory.Faker('word')


class WaveFactory(SQLAlchemyModelFactory):
    class Meta:
        model = Wave
        sqlalchemy_session = db.session
        sqlalchemy_session_persistence = 'commit'

    name = factory.Sequence(lambda n: f'wave_{n}')
    project = factory.SubFactory(ProjectFactory)


class SourceDBFactory(SQLAlchemyModelFactory):
    class Meta:
        model = SourceDB
        sqlalchemy_session = db.session
        sqlalchemy_session_persistence = 'commit'

    server = factory.Faker('word')
    oracle_version = factory.Faker('word')
    oracle_release = factory.Faker('word')
    oracle_edition = factory.Faker('word')
    db_type = SourceDBType.SI
    rac_nodes = 0
    fe_rac_nodes = 0
    arch = factory.Faker('word')
    db_name = factory.Faker('word')
    cores = factory.Faker('random_number', digits=3)
    ram = factory.Faker('random_number', digits=5)
    allocated_memory = factory.Faker('random_number', digits=7)
    db_size = factory.Faker('random_number', digits=7)
    status = SourceDBStatus.EMPTY
    project = factory.SubFactory(ProjectFactory)
    wave = None  # subfactory generates extra wave.project models


class ConfigFactory(SQLAlchemyModelFactory):
    class Meta:
        model = Config
        sqlalchemy_session = db.session
        sqlalchemy_session_persistence = 'commit'

    install_config_values = {"oracle_user": "oracle", "oracle_group": "oinstall", "home_name": "db_home19c",
                             "grid_user": "grid", "grid_group": "asmadmin"}

    db_params_values = {"db_name": "ORCL"}
    data_mounts_values = [{"purpose": "software", "blk_device": "/dev/sdb", "name": "u01", "fstype": "xfs",
                           "mount_point": "/u01", "mount_opts": "nofail"}]
    asm_config_values = [{"diskgroup": "disk", "disks": [{"blk_device": "/dev/sdc", "name": "disk_1", "size": "20"}],
                          "au_size": "20", "redundancy": "a"}]
    rac_config_values = {"vip_name": "a", "vip_ip": "1", "scan_name": "SCAN", "scan_port": "1521", "cluster_name": "a",
                         "cluster_domain": "a", "public_net": "eth0", "private_net": "eth1", "scan_ip1": "1",
                         "scan_ip2": "1", "scan_ip3": "1", "dg_name": "a",
                         "rac_nodes": [{"node_name": "a", "node_id": 1, "node_ip": "1", "vip_name": "a",
                                        "vip_ip": "1"}]}
    misc_config_values = {"swap_blk_device": "/dev/sda", "oracle_root": "/u01/app", "ntp_preferred": "/etc/ntp.conf",
                          "role_separation": True, "compatible_asm": "a", "compatible_rdbms": "a",
                          "asm_disk_management": "a"}
    created_at = datetime.now()

    source_db = factory.SubFactory(SourceDBFactory)


class BMSServerFactory(SQLAlchemyModelFactory):
    class Meta:
        model = BMSServer
        sqlalchemy_session = db.session
        sqlalchemy_session_persistence = 'commit'

    name = factory.Sequence(lambda n: f'bms_server_{n}')
    state = None
    machine_type = 'o2-standard-16-metal'
    luns = [{"lun_name": "lun-1", "size_gb": "20", "storage_type": "PERSISTENT", "storage_volume": "/dev/sda"},
            {"lun_name": "lun-2", "size_gb": "40", "storage_type": "PERSISTENT", "storage_volume": "/dev/sdb"}]
    networks = [{"ipAddress": "172.25.9.8", "name": "nic0", "type": "CLIENT"},
                {"ipAddress": "192.0.0.0", "name": "nic1", "type": "PRIVATE"}]
    deleted = False
    secret_name = factory.Faker('word')
    cpu = factory.Faker('random_number', digits=3)
    socket = factory.Faker('random_number', digits=3)
    ram = factory.Faker('random_number', digits=3)
    created_at = datetime.now()


class MappingFactory(SQLAlchemyModelFactory):
    class Meta:
        model = Mapping
        sqlalchemy_session = db.session
        sqlalchemy_session_persistence = 'commit'

    rac_node = 0

    source_db = factory.SubFactory(SourceDBFactory)
    bms = factory.SubFactory(BMSServerFactory)


class OperationFactory(SQLAlchemyModelFactory):
    class Meta:
        model = Operation
        sqlalchemy_session = db.session
        sqlalchemy_session_persistence = 'commit'

    operation_type = 'DEPLOYMENT'
    status = 'STARTING'
    started_at = factory.Faker('date_object')

    wave = factory.SubFactory(WaveFactory)


class OperationDetailsFactory(SQLAlchemyModelFactory):
    class Meta:
        model = OperationDetails
        sqlalchemy_session = db.session
        sqlalchemy_session_persistence = 'commit'

    operation_type = 'DEPLOYMENT'
    started_at = factory.Faker('date_object')
    step = 'PRE_DEPLOYMENT'
    status = 'STARTING'

    mapping = factory.SubFactory(MappingFactory)
    wave = factory.SubFactory(WaveFactory)
    operation = factory.SubFactory(OperationFactory)


class OperationDetailsErrorFactory(SQLAlchemyModelFactory):
    class Meta:
        model = OperationDetailsError
        sqlalchemy_session = db.session
        sqlalchemy_session_persistence = 'commit'

    operation_details = factory.SubFactory(OperationDetailsFactory)
    message = factory.Faker('word')


class RestoreConfigFactory(SQLAlchemyModelFactory):
    class Meta:
        model = RestoreConfig
        sqlalchemy_session = db.session
        sqlalchemy_session_persistence = 'commit'

    backup_location = factory.Faker('word')
    pfile_file = factory.Faker('word')
    pwd_file = factory.Faker('word')
    tnsnames_file = factory.Faker('word')
    listener_file = factory.Faker('word')
    rman_cmd = factory.Faker('word')
    is_configured = False
    backup_type = 'full'

    source_db = factory.SubFactory(SourceDBFactory)


class ScheduledTaskFactory(SQLAlchemyModelFactory):
    class Meta:
        model = ScheduledTask
        sqlalchemy_session = db.session
        sqlalchemy_session_persistence = 'commit'

    schedule_time = factory.Faker('date_object')

    source_db = factory.SubFactory(SourceDBFactory)


class LabelFactory(SQLAlchemyModelFactory):
    class Meta:
        model = Label

        sqlalchemy_session = db.session
        sqlalchemy_session_persistence = 'commit'

    name = factory.Sequence(lambda n: f'label_{n}')
    project = factory.SubFactory(ProjectFactory)
