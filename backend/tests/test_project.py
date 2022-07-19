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

from faker import Faker

from bms_app.models import (
    Config, Label, Mapping, Operation, OperationDetails, OperationDetailsError,
    Project, RestoreConfig, ScheduledTask, SourceDB, Wave, db
)

from .factories import (
    BMSServerFactory, ConfigFactory, LabelFactory, MappingFactory,
    OperationDetailsErrorFactory, OperationDetailsFactory, OperationFactory,
    ProjectFactory, RestoreConfigFactory, ScheduledTaskFactory,
    SourceDBFactory, WaveFactory
)


fk = Faker()


add_project_data = {
    'name': 'pr-1',
    'description': 'desc-1',
    'vpc': 'vpc',
    'subnet': 'subnet',
}

edit_project_data = {
    'name': fk.word(),
    'description': fk.text(50),
    'vpc': fk.word(),
    'subnet': fk.word(),
}


def test_add_project(client):
    """Test adding project"""
    req = client.post('/api/projects', json=add_project_data)
    assert req.status_code == 201
    assert 'id' in req.json

    pr = Project.query.get(req.json['id'])
    assert pr

    assert pr.name == add_project_data['name']
    assert pr.description == add_project_data['description']
    assert pr.vpc == add_project_data['vpc']
    assert pr.subnet == add_project_data['subnet']


def test_add_project_unique_name_err(client):
    pr = ProjectFactory()

    add_project_data = {
        'name': pr.name,
        'description': 'desc-1',
        'vpc': 'vpc',
        'subnet': 'subnet',
    }

    req = client.post('/api/projects', json=add_project_data)

    assert req.status_code == 400


def test_get_all_projects(client):
    """Start with a blank database."""
    pr_1 = ProjectFactory.create()
    pr_2 = ProjectFactory.create()

    req = client.get('/api/projects')

    assert req.status_code == 200
    data = req.json.get('data')

    assert data
    assert isinstance(data, list)
    assert len(data) == 2

    assert {
        'id': pr_1.id,
        'name': pr_1.name,
        'description': pr_1.description,
        'vpc': pr_1.vpc,
        'subnet': pr_1.subnet,
    } in data

    assert {
        'id': pr_2.id,
        'name': pr_2.name,
        'description': pr_2.description,
        'vpc': pr_2.vpc,
        'subnet': pr_2.subnet,
    } in data


def test_get_a_project(client):
    """Start with a blank database."""
    pr_1 = ProjectFactory.create()
    ProjectFactory.create()

    req = client.get(f'/api/projects/{pr_1.id}')

    assert req.status_code == 200
    data = req.json

    assert data
    assert isinstance(data, dict)
    assert data == {
        'id': pr_1.id,
        'name': pr_1.name,
        'description': pr_1.description,
        'vpc': pr_1.vpc,
        'subnet': pr_1.subnet,
    }


def test_delete_a_project(client):
    """Start with a blank database."""
    pr_1 = ProjectFactory.create()
    ProjectFactory.create()

    req = client.delete(f'/api/projects/{pr_1.id}')

    assert req.status_code == 204
    assert db.session.query(Project).count() == 1
    assert not db.session.query(Project).get(pr_1.id)


def test_edit_a_project(client):
    """Start with a blank database."""
    pr_1 = ProjectFactory.create()

    req = client.put(f'/api/projects/{pr_1.id}', json=edit_project_data)

    assert req.status_code == 200
    assert req.json
    assert isinstance(req.json, dict)

    db_pr = db.session.query(Project).get(pr_1.id)
    assert db_pr.name == edit_project_data['name']
    assert db_pr.description == edit_project_data['description']
    assert db_pr.vpc == edit_project_data['vpc']
    assert db_pr.subnet == edit_project_data['subnet']


def test_edit_project_unique_name_err(client):
    pr_1 = ProjectFactory()
    pr_2 = ProjectFactory()

    edit_project_data = {
        'name': pr_2.name,
        'description': pr_1.description,
        'vpc': pr_1.vpc,
        'subnet': pr_1.subnet,
    }

    req = client.put(f'/api/projects/{pr_1.id}', json=edit_project_data)

    assert req.status_code == 400


def test_edit_project_update_the_same_name(client):
    pr_1 = ProjectFactory()

    edit_project_data = {
        'name': pr_1.name,
        'description': pr_1.description,
        'vpc': pr_1.vpc,
        'subnet': pr_1.subnet,
    }

    req = client.put(f'/api/projects/{pr_1.id}', json=edit_project_data)

    assert req.status_code == 200


def test_not_delete_project_with_wave(client):
    """Porject containg wave can not be deleted."""
    pr = ProjectFactory.create()
    WaveFactory(project=pr)

    req = client.delete(f'/api/projects/{pr.id}')

    assert req.status_code == 400
    assert db.session.query(Project == pr.id).count() == 1


def test_not_delete_project_with_source_db(client):
    """Porject containg source db can not be deleted."""
    pr = ProjectFactory.create()
    SourceDBFactory(project=pr)

    req = client.delete(f'/api/projects/{pr.id}')

    assert req.status_code == 400
    assert Project.query.filter(Project.id == pr.id).count() == 1


def test_delete_testing_project(client):
    """Deleting test project and all related data."""
    pr = ProjectFactory.create()
    wave_1 = WaveFactory(project=pr)
    wave_2 = WaveFactory(project=pr)
    sdb_1 = SourceDBFactory(project=pr, wave=wave_1)
    sdb_2 = SourceDBFactory(project=pr, wave=None)
    ConfigFactory(source_db=sdb_1)
    ConfigFactory(source_db=sdb_2)
    bms_1 = BMSServerFactory()
    bms_2 = BMSServerFactory()
    map_1 = MappingFactory(source_db=sdb_1, bms=bms_1)
    map_2 = MappingFactory(source_db=sdb_2, bms=bms_2)
    RestoreConfigFactory(source_db=sdb_1)
    RestoreConfigFactory(source_db=sdb_2)
    ScheduledTaskFactory(source_db=sdb_1)
    ScheduledTaskFactory(source_db=sdb_2)
    op_1 = OperationFactory(wave=wave_1)
    op_2 = OperationFactory(wave=wave_2)
    op_det_1 = OperationDetailsFactory(mapping=map_1, wave=wave_1, operation=op_1)
    op_det_2 = OperationDetailsFactory(mapping=map_2, wave=wave_2, operation=op_2)
    OperationDetailsErrorFactory(operation_details=op_det_1)
    OperationDetailsErrorFactory(operation_details=op_det_2)
    LabelFactory(project=pr, source_dbs=[sdb_1, sdb_2])
    LabelFactory(project=pr, source_dbs=[sdb_1])


    # records that should not be deleted
    other_wave = WaveFactory()
    other_db = SourceDBFactory(wave=other_wave)
    other_mapping = MappingFactory(source_db=other_db)
    other_operation = OperationFactory(wave=other_wave)
    OperationDetailsFactory(
        wave=other_wave,
        operation=other_operation,
        mapping=other_mapping
    )

    req = client.delete(f'/api/projects/{pr.id}?force=True')

    assert req.status_code == 204
    assert Wave.query.count() == 1
    assert SourceDB.query.count() == 1
    assert Operation.query.count() == 1
    assert OperationDetails.query.count() == 1
    assert Project.query.filter(Project.id == pr.id).count() == 0
    assert Mapping.query.count() == 1
    assert Config.query.count() == 0
    assert RestoreConfig.query.count() == 0
    assert ScheduledTask.query.count() == 0
    assert OperationDetailsError.query.count() == 0
    assert Label.query.count() == 0

    # assert not db.session.query(Mapping).join(SourceDB).filter(SourceDB.project_id == pr.id).all()
