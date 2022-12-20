"""Adding new column for DMS Config

Revision ID: 747fa0c03216
Revises: 5969aa58046d
Create Date: 2022-12-20 11:37:34.594048

"""
from alembic import op
import sqlalchemy as sa



# revision identifiers, used by Alembic.
revision = '747fa0c03216'
down_revision = '5969aa58046d'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('configs', sa.Column('cloud_dms_values', sa.JSON(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('configs', 'cloud_dms_values')
    # ### end Alembic commands ###