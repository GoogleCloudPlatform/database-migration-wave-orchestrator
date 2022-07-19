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

from sqlalchemy.orm.attributes import flag_modified

from bms_app.models import Mapping, OperationDetails, db


def clear_bms_target_params(config):
    """Clear config parameters related to bms target."""
    if config:
        config.is_configured = False

        config.data_mounts_values = None
        config.asm_config_values = None
        config.rac_config_values = None
        config.misc_config_values['swap_blk_device'] = None
        config.misc_config_values['oracle_root'] = None
        flag_modified(config, "misc_config_values")

        db.session.add(config)


def does_db_have_operation(db_id):
    """Return is source_db has any operation."""
    operation_exists = db.session.query(Mapping, OperationDetails) \
        .filter(Mapping.db_id == db_id) \
        .filter(OperationDetails.mapping_id == Mapping.id) \
        .count()
    return bool(operation_exists)
