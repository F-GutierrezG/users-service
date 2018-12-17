"""empty message

Revision ID: f1e28ad30166
Revises: 4528e047a0ed
Create Date: 2018-12-15 16:04:17.110655

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f1e28ad30166'
down_revision = '4528e047a0ed'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('permissions',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('code', sa.String(length=128), nullable=False),
    sa.Column('name', sa.String(length=128), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    schema='users'
    )
    op.create_table('group_permissions',
    sa.Column('group_id', sa.Integer(), nullable=False),
    sa.Column('permission_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['group_id'], ['users.groups.id'], ),
    sa.ForeignKeyConstraint(['permission_id'], ['users.permissions.id'], ),
    sa.PrimaryKeyConstraint('group_id', 'permission_id'),
    schema='users'
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('group_permissions', schema='users')
    op.drop_table('permissions', schema='users')
    # ### end Alembic commands ###