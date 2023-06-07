"""add postgres columns

Revision ID: 91ab03eea364
Revises: 3b825ba0b5a6
Create Date: 2023-05-28 18:31:35.939243

"""
from alembic import op
import sqlalchemy as sa
import sqlalchemy_utils
from bms_app.models import SourceDBEngine



# revision identifiers, used by Alembic.
revision = '91ab03eea364'
down_revision = '3b825ba0b5a6'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('configs', sa.Column('dms_config_values', sa.JSON(), nullable=True))
    op.alter_column('operation_details', 'mapping_id',
               existing_type=sa.INTEGER(),
               nullable=True)
    op.add_column('source_dbs', sa.Column('db_engine', sqlalchemy_utils.types.choice.ChoiceType(SourceDBEngine, impl=sa.String(20)), nullable=True))
    op.alter_column('source_dbs', 'oracle_version',
               existing_type=sa.VARCHAR(),
               nullable=True)
    op.alter_column('source_dbs', 'arch',
               existing_type=sa.VARCHAR(),
               nullable=True)
    op.alter_column('source_dbs', 'cores',
               existing_type=sa.INTEGER(),
               nullable=True)
    op.alter_column('source_dbs', 'ram',
               existing_type=sa.INTEGER(),
               nullable=True)
    op.alter_column('source_dbs', 'allocated_memory',
               existing_type=sa.INTEGER(),
               nullable=True)
    op.alter_column('source_dbs', 'db_size',
               existing_type=sa.NUMERIC(),
               nullable=True)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('source_dbs', 'db_size',
               existing_type=sa.NUMERIC(),
               nullable=False)
    op.alter_column('source_dbs', 'allocated_memory',
               existing_type=sa.INTEGER(),
               nullable=False)
    op.alter_column('source_dbs', 'ram',
               existing_type=sa.INTEGER(),
               nullable=False)
    op.alter_column('source_dbs', 'cores',
               existing_type=sa.INTEGER(),
               nullable=False)
    op.alter_column('source_dbs', 'arch',
               existing_type=sa.VARCHAR(),
               nullable=False)
    op.alter_column('source_dbs', 'oracle_version',
               existing_type=sa.VARCHAR(),
               nullable=False)
    op.drop_column('source_dbs', 'db_engine')
    op.alter_column('operation_details', 'mapping_id',
               existing_type=sa.INTEGER(),
               nullable=False)
    op.drop_column('configs', 'dms_config_values')
    # ### end Alembic commands ###
