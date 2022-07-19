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

from bms_app.models import SourceDB
from bms_app.source_db import bp
from bms_app.source_db.services import SourceDBOperationsHistoryService


@bp.route('/<int:db_id>/operations_history', methods=['GET'])
def get_operations_details(db_id):
    """Return operations history related to the db."""
    source_db = SourceDB.query.get_or_404(db_id)

    data = SourceDBOperationsHistoryService.run(source_db)

    return data, 200
