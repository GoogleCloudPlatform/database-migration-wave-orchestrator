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

import re
from logging.config import dictConfig

from flask import Blueprint, Flask
from flask_cors import CORS
from flask_marshmallow import Marshmallow
from flask_migrate import Migrate, upgrade
from flask_sqlalchemy import SQLAlchemy
from marshmallow import ValidationError

from bms_app.config import CONFIGS, LOGGING_CONFIG
from bms_app.handlers import (
    catch_validation_errors, error_400, resource_not_found
)


dictConfig(LOGGING_CONFIG)

# list of allowed domains to make cross-domains requests, for local development
CORS_LOCALHOST_ORIGINS = [
    re.compile('http://127.0.0.1:.*'),
    re.compile('http://localhost:.*')
]

db = SQLAlchemy()
ma = Marshmallow()
migrate = Migrate()


def create_app(mode='prod'):
    app = Flask(__name__)
    app.config.from_object(CONFIGS[mode.lower()])
    db.init_app(app)
    ma.init_app(app)
    migrate.init_app(app, db)

    register_handlers(app)
    register_blueprints(app)

    @app.before_first_request
    def create_db_objects():
        upgrade()

    CORS(app, origins=CORS_LOCALHOST_ORIGINS)

    return app


def register_handlers(flask_app):
    flask_app.register_error_handler(404, resource_not_found)
    flask_app.register_error_handler(400, error_400)
    flask_app.register_error_handler(ValidationError, catch_validation_errors)


def register_blueprints(flask_app):
    api_bp = Blueprint('api blueprint', __name__, url_prefix='/api')

    from bms_app.project import bp as project_bp
    api_bp.register_blueprint(project_bp, url_prefix='/projects')

    from bms_app.source_db import bp as source_db_bp
    api_bp.register_blueprint(source_db_bp, url_prefix='/source-dbs')

    from bms_app.inventory_manager import bp as server_bp
    api_bp.register_blueprint(server_bp, url_prefix='/targets')

    from bms_app.upload import bp as upload_bp
    api_bp.register_blueprint(upload_bp, url_prefix='/uploads')

    from bms_app.wave import bp as wave_bp
    api_bp.register_blueprint(wave_bp, url_prefix='/waves')

    from bms_app.operation import bp as operation_bp
    api_bp.register_blueprint(operation_bp, url_prefix='/operations')

    from bms_app.mapping import bp as mapping_bp
    api_bp.register_blueprint(mapping_bp, url_prefix='/mappings')

    from bms_app.metadata import bp as metadata_bp
    api_bp.register_blueprint(metadata_bp, url_prefix='/metadata')

    from bms_app.restore import bp as restore_bp
    api_bp.register_blueprint(restore_bp, url_prefix='/restore')

    from bms_app.scheduled_tasks import bp as scheduled_task_bp
    api_bp.register_blueprint(scheduled_task_bp, url_prefix='/scheduled-tasks')

    from bms_app.labels import bp as labels_bp
    api_bp.register_blueprint(labels_bp, url_prefix='/labels')

    from bms_app.webhook import bp as webhook_bp
    flask_app.register_blueprint(webhook_bp, url_prefix='/webhooks')
    
    from bms_app.dms_cloudsql import bp as dms_cloudsql_bp
    api_bp.register_blueprint(dms_cloudsql_bp, url_prefix='/dms-cloudsql')

    # to server FE artifacts
    from bms_app.fe import bp as fe_bp
    flask_app.register_blueprint(fe_bp, url_prefix='/')

    flask_app.register_blueprint(api_bp)
