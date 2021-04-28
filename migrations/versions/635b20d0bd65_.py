"""empty message

Revision ID: 635b20d0bd65
Revises: 2155c6dcf735
Create Date: 2021-04-24 14:16:37.602008

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '635b20d0bd65'
down_revision = '2155c6dcf735'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('images', sa.Column('height', sa.Integer(), nullable=True))
    op.add_column('images', sa.Column('width', sa.Integer(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('images', 'width')
    op.drop_column('images', 'height')
    # ### end Alembic commands ###