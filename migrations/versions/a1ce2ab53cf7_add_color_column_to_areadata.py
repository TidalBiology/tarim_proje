"""Add color column to AreaData

Revision ID: a1ce2ab53cf7
Revises: 
Create Date: 2025-03-16 20:38:12.450808

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a1ce2ab53cf7'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('area_data', schema=None) as batch_op:
        batch_op.add_column(sa.Column('color', sa.String(length=20), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('area_data', schema=None) as batch_op:
        batch_op.drop_column('color')

    # ### end Alembic commands ###
