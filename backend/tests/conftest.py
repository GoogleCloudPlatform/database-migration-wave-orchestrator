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

import pytest


os.environ['DATABASE_URL'] = 'sqlite:///'
os.environ['SECRET_KEY'] = 'secret key'
os.environ['GCS_BUCKET'] = 'test-bucket'
os.environ['GCP_PROJECT_NAME'] = 'test-gcp-project'
os.environ['GCP_PROJECT_NUMBER'] = '123456'
os.environ['GCP_PUBSUB_TOPIC'] = 'test-gcp-topic'
os.environ['GCS_DEPLOYMENT_CONFIG_PREFIX'] = ''
os.environ['GCP_SERVICE_ACCOUNT'] = 'sa@email'
os.environ['GCP_CLOUD_TASKS_QUEUE'] = ''
os.environ['GCP_RESTORE_CONFIGS_PREFIX'] = 'restore_configs'
os.environ['GCP_CLOUD_RUN_SERVICE_NAME'] = ''
os.environ['GCP_OAUTH_CLIENT_ID'] = '12345'
os.environ['GCP_LB_URL'] = 'https://abc.com'


from bms_app import create_app
from bms_app.models import db


@pytest.fixture
def client():
    app = create_app('test')
    app.before_first_request_funcs = []

    with app.test_client() as client:
        with client.application.app_context():
            db.create_all()
            yield client


@pytest.fixture
def files_dir():
    return os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        'files'
    )
