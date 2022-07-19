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

"""Renaming OperationHistory to OperationDetails

Revision ID: e5b3f667fbf1
Revises: 0bbefb6e9f64
Create Date: 2022-02-23 15:05:30.401514

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0bbefb6e9f64'
down_revision = '5d9807733f52'
branch_labels = None
depends_on = None


def upgrade():
    op.rename_table('operation_history', 'operation_details')
    op.execute('ALTER SEQUENCE operation_history_id_seq RENAME TO operation_details_id_seq')
    op.execute('ALTER INDEX operation_history_pkey RENAME TO operation_details_pkey')


def downgrade():
    op.rename_table('operation_details', 'operation_history')
    op.execute('ALTER SEQUENCE operation_details_id_seq RENAME TO operation_history_id_seq')
    op.execute('ALTER INDEX operation_details_pkey RENAME TO operation_history_pkey')
