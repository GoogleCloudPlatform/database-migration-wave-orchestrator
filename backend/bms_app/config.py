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

from bms_app import settings


class Default:
    """Base configuration for the flask application."""

    DEBUG = False
    SQLALCHEMY_DATABASE_URI = settings.DATABASE_URL
    SQLALCHEMY_TRACK_MODIFICATIONS = False


class Development(Default):
    DEBUG = True
    ENV = 'development'


class Production(Default):
    DEBUG = False


class Testing(Default):
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = 'sqlite://'


CONFIGS = {
    'dev': Development,
    'test': Testing,
    'prod': Production,
}


LOGGING_CONFIG = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'default': {
            'format': '%(levelname)s [%(asctime)s] %(name)s: %(message)s',
        }
    },
    'handlers': {
        'wsgi': {
            'class': 'logging.StreamHandler',
            'stream': 'ext://flask.logging.wsgi_errors_stream',
        },
        'console': {
            'class': 'logging.StreamHandler',
            'stream': 'ext://sys.stdout',
            'formatter': 'default'
        }
    },
    'loggers': {
        'bms_app': {
            'level': 'DEBUG',
            'handlers': ['console'],
        },
        'alembic': {
            'level': 'DEBUG',
            'handlers': ['console'],
        },
        'sqlalchemy.engine': {
            'level': 'WARN',
            'handlers': ['console'],
        },
        'root': {
            'level': 'INFO',
            'handlers': ['wsgi'],
        },
    }
}
