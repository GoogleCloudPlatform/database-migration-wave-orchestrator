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


try:
    from . import local_config as cfg
except ImportError:
    cfg = None


def get_config_value(attr, default=None):
    """Retrive config value from env or config file."""
    value = None

    def read_env():
        return os.environ.get(attr)

    def read_cfg():
        return getattr(cfg, attr, None) if cfg else None

    def read_default():
        return default

    for func in (read_env, read_cfg, read_default):
        value = func()

        if value is not None:
            break

    if value is None:
        raise ValueError(f'missing {attr} setting')

    return value


DATABASE_URL = get_config_value('DATABASE_URL')
GCS_BUCKET = get_config_value('GCS_BUCKET')
GCP_PROJECT_NAME = get_config_value('GCP_PROJECT_NAME')
GCP_PROJECT_NUMBER = get_config_value('GCP_PROJECT_NUMBER')
GCP_PUBSUB_TOPIC = get_config_value('GCP_PUBSUB_TOPIC')
GCP_SERVICE_ACCOUNT = get_config_value('GCP_SERVICE_ACCOUNT')
GCP_CLOUD_TASKS_QUEUE = get_config_value('GCP_CLOUD_TASKS_QUEUE')
GCP_CLOUD_RUN_SERVICE_NAME = get_config_value('GCP_CLOUD_RUN_SERVICE_NAME')
# folder to store db restore configurations
GCP_RESTORE_CONFIGS_PREFIX = get_config_value('GCP_RESTORE_CONFIGS_PREFIX', default='restore_configs')
# folder to store all (deployemant, rollback, restore, ..) ansible configs
GCS_DEPLOYMENT_CONFIG_PREFIX = get_config_value('GCS_DEPLOYMENT_CONFIG_PREFIX', default='ansible_configs')
GCS_ORACLE_BINARY_PREFIX = get_config_value('GCS_ORACLE_BINARY_PREFIX', default='')
GCP_OAUTH_CLIENT_ID = get_config_value('GCP_OAUTH_CLIENT_ID')
GCP_LB_URL = get_config_value('GCP_LB_URL')

# log to gcloud logging
USE_GCLOUD_LOGGING = get_config_value('USE_GCLOUD_LOGGING', default=False)
