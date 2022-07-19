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

DATABASE_URL = 'postgresql+psycopg2://user:password@host/db'  # sqlalchemy dsn connection string

GCP_PROJECT_NAME = 'gcp-project-name'  # GCP project name. Required
GCP_PROJECT_NUMBER = '1234567890'  # GCP project number. Required
GCP_PUBSUB_TOPIC = 'projects/<porject_name>/topics/<topic_name>'  # Required
GCP_CLOUD_TASKS_QUEUE = 'projects/<porject_name>/locations/<location_name>/queues/<queue_name>'  # GCP Cloud Tasks Queue. Required
GCP_CLOUD_RUN_SERVICE_NAME = 'projects/<porject_name/locations/<region>/services/<name>'  # GCP CloudRun service name. Required
GCS_BUCKET = 'gcp-bucket-name'  # Required
GCS_ORACLE_BINARY_PREFIX = ''  # subdir in the bucket for oracle binaries. Currently only '' is supported.
GCS_DEPLOYMENT_CONFIG_PREFIX = 'wave_ansible_configs'  # subdir in the bucket for ansible config files. Optional, default is 'wave_ansible_configs'
GCP_SERVICE_ACCOUNT = 'sa-user@abc.iam.gserviceaccount.com'  # Required
GCP_RESTORE_CONFIGS_PREFIX = 'restore_ansible_configs'  # subdir in the bucket for restore_configs files. Optional, default is 'restore_ansible_configs'
