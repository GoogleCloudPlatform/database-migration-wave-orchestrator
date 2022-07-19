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
from decimal import Decimal

from bms_app.models import SourceDB, SourceDBType, db

from tests.factories import (
    MappingFactory, OperationDetailsFactory, OperationFactory, ProjectFactory,
    SourceDBFactory, WaveFactory
)


def test_add_the_same_source_db_to_another_project(client, files_dir):
    """Test adding the same db to different projects."""
    pr_1 = ProjectFactory()
    pr_2 = ProjectFactory()
    SourceDBFactory(project=pr_1, server='lxoradbprod1', db_name='FIN_DB')

    with open(os.path.join(files_dir, 'MigVisor_example.xlsx'), 'rb') as fp:
        data = {
            'project_id': pr_2.id,
            'file': (fp, 'MigVisor_example.xlsx'),
        }

        req = client.post(
            '/api/source-dbs/migvisor',
            data=data,
            content_type='multipart/form-data',
        )

    assert req.status_code == 201

    fin_dbs = db.session.query(SourceDB) \
        .filter(SourceDB.server == 'lxoradbprod1',
                SourceDB.db_name == 'FIN_DB') \
        .all()

    assert data
    assert len(fin_dbs) == 2

    assert fin_dbs[0].server == fin_dbs[1].server
    assert fin_dbs[0].db_name == fin_dbs[1].db_name
    assert fin_dbs[0].project_id != fin_dbs[1].project_id


def test_overwrite_db_for_specific_project(client, files_dir):
    """Test for checking possibility to overwrite db for specific project."""
    pr_1 = ProjectFactory()
    pr_2 = ProjectFactory()
    db_1 = SourceDBFactory(project=pr_1, server='lxoradbprod1', db_name='FIN_DB')
    db_2 = SourceDBFactory(
        project=pr_2,
        server='lxoradbprod1',
        db_name='FIN_DB',
        oracle_release='abc',
        cores=8
    )

    with open(os.path.join(files_dir, 'MigVisor_example.xlsx'), 'rb') as fp:
        data = {
            'project_id': pr_1.id,
            'file': (fp, 'MigVisor_example.xlsx'),
            'overwrite': True
        }

        req = client.post(
            '/api/source-dbs/migvisor',
            data=data,
            content_type='multipart/form-data',
        )

    assert req.status_code == 201

    fin_dbs = db.session.query(SourceDB) \
        .filter(SourceDB.server == 'lxoradbprod1',
                SourceDB.db_name == 'FIN_DB',
                SourceDB.project_id == 1) \
        .all()

    assert len(fin_dbs) == 1

    assert db_1.server == 'lxoradbprod1'
    assert db_1.db_name == 'FIN_DB'
    assert db_1.project_id == 1
    assert db_1.oracle_release == 'base'
    assert db_1.cores == 2

    assert db_2.server == 'lxoradbprod1'
    assert db_2.db_name == 'FIN_DB'
    assert db_2.project_id == 2
    assert db_2.oracle_release == 'abc'
    assert db_2.cores == 8


def test_migvisor_file(client, files_dir):
    pr = ProjectFactory()

    data = {'project_id': pr.id}

    with open(os.path.join(files_dir, 'MigVisor_example.xlsx'), 'rb') as fp:
        data = {
            'project_id': pr.id,
            'file': (fp, 'MigVisor_example.xlsx'),
        }

        req = client.post(
            '/api/source-dbs/migvisor',
            data=data,
            content_type='multipart/form-data',
        )

    assert req.status_code == 201

    fin_db = db.session.query(SourceDB) \
        .filter(SourceDB.server == 'lxoradbprod1',
                SourceDB.db_name == 'FIN_DB',
                SourceDB.project_id == pr.id) \
        .first()
    report_db = db.session.query(SourceDB) \
        .filter(SourceDB.server == 'lxoradbprod2',
                SourceDB.db_name == 'REPOR_DB',
                SourceDB.project_id == pr.id) \
        .first()
    rac_db = db.session.query(SourceDB) \
        .filter(SourceDB.server == 'lxoradbprod3',
                SourceDB.db_name == 'RAC_DB',
                SourceDB.project_id == pr.id) \
        .first()
    test_1 = db.session.query(SourceDB) \
        .filter(SourceDB.server == 'lxoradbprod5',
                SourceDB.db_name == 'test_1',
                SourceDB.project_id == pr.id) \
        .first()

    assert fin_db
    assert rac_db
    assert report_db
    assert test_1

    assert fin_db.project_id == pr.id

    assert fin_db.arch == 'x86_64/Linux 2.4.xx'
    assert fin_db.cores == 2
    assert fin_db.ram == 4
    assert fin_db.allocated_memory == 3
    assert fin_db.db_size == Decimal('13.224')

    # RAC
    assert fin_db.db_type is SourceDBType.SI
    assert rac_db.db_type is SourceDBType.RAC
    assert rac_db.rac_nodes == 2

    # Oracle version
    assert fin_db.oracle_version == '19.3.0.0.0'
    assert test_1.oracle_version == '19.3.0.0.0'

    # PSU checking
    assert fin_db.oracle_release == 'base'
    assert report_db.oracle_release == '19.11.0.0.210412'

    assert test_1.config
    assert test_1.config.asm_config_values == [
        {'redundancy': 'EXTERNAL', 'diskgroup': 'DATA', 'au_size': '1M'},
        {'redundancy': 'EXTERNAL', 'diskgroup': 'RECO', 'au_size': '1M'}
    ]
    assert test_1.config.misc_config_values == {
        'compatible_asm': '12.2.0.1.0',
        'compatible_rdbms': '12.2.0.1.1',
    }

    assert req.json == {'added': 5, 'skipped': 0, 'updated': 0}


def test_overwrite(client, files_dir):
    """Test for checking correct overwrite functionality."""
    pr = ProjectFactory()
    SourceDBFactory.create(
        project=pr,
        server='lxoradbprod1',
        db_name='FIN_DB',
        oracle_release='a.b.c',
        db_size=Decimal('4'),
        cores=5,
        ram=10
    )

    with open(os.path.join(files_dir, 'MigVisor_example.xlsx'), 'rb') as fp:
        data = {
            'project_id': pr.id,
            'file': (fp, 'MigVisor_example.xlsx'),
            'overwrite': True,
        }

        req = client.post(
            '/api/source-dbs/migvisor',
            data=data,
            content_type='multipart/form-data',
        )

    assert req.status_code == 201

    fin_db = db.session.query(SourceDB) \
        .filter(SourceDB.server == 'lxoradbprod1',
                SourceDB.db_name == 'FIN_DB') \
        .first()

    assert fin_db

    assert fin_db.project_id == pr.id

    assert fin_db.arch == 'x86_64/Linux 2.4.xx'
    assert fin_db.cores == 2
    assert fin_db.ram == 4
    assert fin_db.db_size == Decimal('13.224')
    assert fin_db.oracle_release == 'base'
    assert req.json == {'added': 4, 'skipped': 0, 'updated': 1}


def test_not_update_db_for_existing_mapping(client, files_dir):
    pr = ProjectFactory()
    wave = WaveFactory(project=pr)
    fin_db = SourceDBFactory.create(
        project=pr,
        server='lxoradbprod1',
        db_name='FIN_DB',
        oracle_release='a.b.c',
        cores=5,
        ram=10,
        arch='x86_64'
    )
    report_db = SourceDBFactory.create(
        project=pr,
        server='lxoradbprod2',
        db_name='REPOR_DB',
        oracle_release='a.b.c',
        cores=5,
        ram=10,
        arch='x86_64',
    )
    map_1 = MappingFactory(source_db=fin_db)
    op_1 = OperationFactory(wave=wave)
    OperationDetailsFactory(mapping=map_1, wave=wave, operation=op_1)

    with open(os.path.join(files_dir, 'MigVisor_example.xlsx'), 'rb') as fp:
        data = {
            'project_id': pr.id,
            'file': (fp, 'MigVisor_example.xlsx'),
            'overwrite': True,
        }

        req = client.post(
            '/api/source-dbs/migvisor',
            data=data,
            content_type='multipart/form-data',
        )

    assert req.status_code == 201

    # not overwritten
    assert fin_db.arch == 'x86_64'
    assert fin_db.cores == 5
    assert fin_db.ram == 10
    assert fin_db.oracle_release == 'a.b.c'

    # overwritten
    assert report_db.oracle_release == '19.11.0.0.210412'
    assert report_db.cores == 2
    assert report_db.arch == 'Linux x86 64-bit'
    assert req.json == {'added': 3, 'skipped': 1, 'updated': 1}


def test_update_rac_to_si(client, files_dir):
    pr = ProjectFactory()
    fin_db = SourceDBFactory.create(
        project=pr,
        server='lxoradbprod1',
        db_name='FIN_DB',
        db_type=SourceDBType.RAC,
        rac_nodes=0,
    )

    with open(os.path.join(files_dir, 'MigVisor_example.xlsx'), 'rb') as fp:
        data = {
            'project_id': pr.id,
            'file': (fp, 'MigVisor_example.xlsx'),
            'overwrite': True,
        }

        req = client.post(
            '/api/source-dbs/migvisor',
            data=data,
            content_type='multipart/form-data',
        )

    assert req.status_code == 201

    assert fin_db.rac_nodes == 0
    assert fin_db.db_type == SourceDBType.SI


def test_update_si_to_rac(client, files_dir):
    pr = ProjectFactory()
    rac_db = SourceDBFactory.create(
        project=pr,
        server='lxoradbprod3',
        db_name='RAC_DB',
        db_type=SourceDBType.SI,
        rac_nodes=0,
    )

    with open(os.path.join(files_dir, 'MigVisor_example.xlsx'), 'rb') as fp:
        data = {
            'project_id': pr.id,
            'file': (fp, 'MigVisor_example.xlsx'),
            'overwrite': True,
        }

        req = client.post(
            '/api/source-dbs/migvisor',
            data=data,
            content_type='multipart/form-data',
        )

    assert req.status_code == 201

    assert rac_db.rac_nodes == 2
    assert rac_db.db_type == SourceDBType.RAC
