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

"""Renaming source_db_lables to source_db_labels

Revision ID: 3b825ba0b5a6
Revises: 4ca6a17d5114
Create Date: 2022-06-02 14:05:36.948609

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '3b825ba0b5a6'
down_revision = '4ca6a17d5114'
branch_labels = None
depends_on = None


def upgrade():
    op.rename_table('source_db_lables', 'source_db_labels')


def downgrade():
    op.rename_table('source_db_labels', 'source_db_lables')
