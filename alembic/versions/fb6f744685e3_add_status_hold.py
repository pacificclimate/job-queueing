"""Add status HOLD

Revision ID: fb6f744685e3
Revises: ef8e554efc91
Create Date: 2017-09-01 11:13:31.850056

"""
from warnings import warn

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'fb6f744685e3'
down_revision = 'ef8e554efc91'
branch_labels = None
depends_on = None


connection = op.get_bind()
dialect = connection.dialect.name


# Migrate the Enum type of the column ``status`` to add the value ``HOLD``.
#
# Migration of an Enum type is tricky and must be done differently depending
# on the database type. Fortunately we need only concern ourselves with
# SQLite in this project.
#
# For SQLite, we must use "batch mode" to
# do most table alterations, including the one that changes the Enum type
# for time_resolution. See http://alembic.zzzcomputing.com/en/latest/batch.html
#
# Most of this is copied from
# `a modelmeta migration <https://github.com/pacificclimate/modelmeta/blob/master/alembic/versions/614911daf883_add_seasonal_to_time_resolution_enum.py>`_


old_options = (
    'NEW', 'SUBMITTED', 'RUNNING', 'SUCCESS', 'ERROR'
)
new_options = (
    'NEW', 'HOLD', 'SUBMITTED', 'RUNNING', 'SUCCESS', 'ERROR'
)


def alter_column(curr_options, dest_options):
    """
    Alter columns, which in SQLite alters the check constraint. Yay.
    See http://alembic.zzzcomputing.com/en/latest/batch.html

    :param curr_options: tuple of options (members) in the current enum type
    :param dest_options: tuple of options (members) in the destination enum type
    :return: None
    """
    old_type = sa.Enum(*curr_options, name='statuses')
    new_type = sa.Enum(*dest_options, name='statuses')
    with op.batch_alter_table('generate_climos_queue') as batch_op:
        batch_op.alter_column(
            'status', type_=new_type, existing_type=old_type)


def upgrade():
    if dialect == 'sqlite':
        alter_column(old_options, new_options)
    else:
        warn('This migration is not known valid for dialect {}. Skipping.'
             .format(dialect))


def downgrade():
    if dialect == 'sqlite':
        alter_column(new_options, old_options)
    else:
        warn('This migration is not known valid for dialect {}. Skipping.'
             .format(dialect))
