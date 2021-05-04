"""empty message

Revision ID: 12a7502b0990
Revises: a403585c54e6
Create Date: 2021-05-02 12:09:44.261019

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '12a7502b0990'
down_revision = 'a403585c54e6'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('palettes',
    sa.Column('created_on', sa.DateTime(), nullable=True),
    sa.Column('updated_on', sa.DateTime(), nullable=True),
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.Column('image_id', sa.Integer(), nullable=True),
    sa.Column('hex_values', postgresql.ARRAY(sa.String(length=128)), nullable=True),
    sa.Column('name', sa.String(length=128), nullable=True),
    sa.ForeignKeyConstraint(['image_id'], ['images.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('palettes')
    # ### end Alembic commands ###
