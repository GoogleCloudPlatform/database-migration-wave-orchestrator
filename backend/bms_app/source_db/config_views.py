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

from flask import request

from bms_app.models import Config, db
from bms_app.schema import ConfigSchema
from bms_app.source_db import bp
from bms_app.source_db.services import SaveSourceDBConfigService


@bp.route('/<int:db_id>/config', methods=['GET'])
def get_config(db_id):
    """Return config."""
    config = db.session.query(Config) \
        .filter(Config.db_id == db_id) \
        .first()
    return ConfigSchema(exclude=['id']).dump(config)


@bp.route('/<int:db_id>/config', methods=['DELETE'])
def config_delete(db_id):
    """Delete config."""
    config = db.session.query(Config) \
        .filter(Config.db_id == db_id) \
        .first()

    if config:
        db.session.delete(config)
        db.session.commit()

    return {}, 204


@bp.route('/<int:db_id>/config', methods=['POST'])
def new_config(db_id):
    """Create/Update db config.

    Params:
        is_configured' -  required
        install_config_values - optional
        db_params_values' - optional
        data_mounts_values - optional
        asm_config_values - optional
        misc_config_values - optional
        rac_config_values - optional
        dms_config_values - optional
    """
    print(request.json)
    config = SaveSourceDBConfigService.run(db_id, request.json)

    return ConfigSchema(exclude=['id']).dump(config), 201
