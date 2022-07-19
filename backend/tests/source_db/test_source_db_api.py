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

from bms_app.models import SourceDB, SourceDBStatus, db

from tests.factories import LabelFactory, ProjectFactory, SourceDBFactory


def test_get_source_db(client):
    """Test GET source_db api."""
    proj_1 = ProjectFactory()
    db_1 = SourceDBFactory(project=proj_1)
    label_1 = LabelFactory(project=proj_1)
    label_2 = LabelFactory(project=proj_1)
    db_1.labels.append(label_1)
    db_1.labels.append(label_2)

    req = client.get(f'/api/source-dbs/{db_1.id}')

    assert req.status_code == 200
    data = req.json

    assert data
    assert isinstance(data, dict)

    assert data == {
        'allocated_memory': db_1.allocated_memory,
        'arch': db_1.arch,
        'cores': db_1.cores,
        'db_name': db_1.db_name,
        'db_size': db_1.db_size,
        'db_type': db_1.db_type.value,
        'fe_rac_nodes': db_1.fe_rac_nodes,
        'id': db_1.id,
        'is_rac': db_1.is_rac,
        'oracle_edition': db_1.oracle_edition,
        'oracle_release': db_1.oracle_release,
        'oracle_version': db_1.oracle_version,
        'project_id': db_1.project_id,
        'rac_nodes': db_1.rac_nodes,
        'ram': db_1.ram,
        'server': db_1.server,
        'status': SourceDBStatus.EMPTY.value,
        'labels': [
            {
                'id': db_1.labels[0].id,
                'name': db_1.labels[0].name
            },
            {
                'id': db_1.labels[1].id,
                'name': db_1.labels[1].name
            }
        ]
    }


def test_get_all_dbs(client):
    """Test to verify the creation of multiple databases."""
    pr = ProjectFactory()
    db_1 = SourceDBFactory(project=pr, db_type='SI')
    db_2 = SourceDBFactory(project=pr, db_type='RAC')
    label_1 = LabelFactory(project=pr)
    db_1.labels.append(label_1)

    req = client.get('/api/source-dbs')

    assert req.status_code == 200
    data = req.json.get('data')

    assert data
    assert isinstance(data, list)
    assert len(data) == 2

    assert {
        'allocated_memory': db_1.allocated_memory,
        'arch': db_1.arch,
        'cores': db_1.cores,
        'db_name': db_1.db_name,
        'db_size': db_1.db_size,
        'db_type': 'SI',
        'fe_rac_nodes': db_1.fe_rac_nodes,
        'id': db_1.id,
        'is_rac': False,
        'oracle_edition': db_1.oracle_edition,
        'oracle_release': db_1.oracle_release,
        'oracle_version': db_1.oracle_version,
        'project_id': db_1.project_id,
        'rac_nodes': db_1.rac_nodes,
        'ram': db_1.ram,
        'server': db_1.server,
        'status': SourceDBStatus.EMPTY.value,
        'labels': [{
            'id': db_1.labels[0].id,
            'name': db_1.labels[0].name
        }]
    } in data

    assert {
        'allocated_memory': db_2.allocated_memory,
        'arch': db_2.arch,
        'cores': db_2.cores,
        'db_name': db_2.db_name,
        'db_size': db_2.db_size,
        'db_type': 'RAC',
        'fe_rac_nodes': db_2.fe_rac_nodes,
        'id': db_2.id,
        'is_rac': True,
        'oracle_edition': db_2.oracle_edition,
        'oracle_release': db_2.oracle_release,
        'oracle_version': db_2.oracle_version,
        'project_id': db_2.project_id,
        'rac_nodes': db_2.rac_nodes,
        'ram': db_2.ram,
        'server': db_2.server,
        'status': SourceDBStatus.EMPTY.value,
        'labels': []
    } in data


def test_filter_source_dbs_by_project_id(client):
    """Test for checking the correct working of the filter for project_id."""
    pr_1 = ProjectFactory()
    pr_2 = ProjectFactory()
    SourceDBFactory(project=pr_1)
    SourceDBFactory(project=pr_1)
    SourceDBFactory(project=pr_2)

    req_1 = client.get(f'/api/source-dbs?project_id={pr_1.id}')
    req_2 = client.get(f'/api/source-dbs?project_id={pr_2.id}')

    assert req_1.status_code == 200
    assert req_2.status_code == 200
    data_1 = req_1.json.get('data')
    data_2 = req_2.json.get('data')

    assert len(data_1) == 2
    assert len(data_2) == 1


def test_delete_a_source_db(client):
    """Test for checking database deletion."""
    pr = ProjectFactory()
    db_1 = SourceDBFactory(project=pr)
    SourceDBFactory(project=pr)

    req = client.delete(f'/api/source-dbs/{db_1.id}')

    assert req.status_code == 204
    assert db.session.query(SourceDB).count() == 1
    assert not db.session.query(SourceDB).get(pr.id)
