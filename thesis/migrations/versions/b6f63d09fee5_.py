"""empty message

Revision ID: b6f63d09fee5
Revises: 9511433bf073
Create Date: 2019-12-06 16:28:04.360181

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'b6f63d09fee5'
down_revision = '9511433bf073'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('studentinfo', sa.Column('check_time', sa.DateTime(), nullable=True))
    op.add_column('studentinfo', sa.Column('input_time', sa.DateTime(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('studentinfo', 'input_time')
    op.drop_column('studentinfo', 'check_time')
    # ### end Alembic commands ###
