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

"""add BMSServer.location snd rm BMSServer.create_time

Revision ID: 67c3aa849e05
Revises: 8ac5d50205bb
Create Date: 2022-02-03 21:49:59.450289

"""
from alembic import op
import sqlalchemy as sa

from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '67c3aa849e05'
down_revision = '8ac5d50205bb'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('bms_servers', sa.Column('location', sa.String(), nullable=True))
    op.drop_column('bms_servers', 'create_time')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('bms_servers', sa.Column('create_time', postgresql.TIMESTAMP(), autoincrement=False, nullable=True))
    op.drop_column('bms_servers', 'location')
    # ### end Alembic commands ###
