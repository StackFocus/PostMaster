"""Adds the failed_attempts, last_failed_date, and unlock_date columns to the
postmaster_admins table

Revision ID: c3803ac9b7dd
Revises: e8f52e92abd0
Create Date: 2016-07-20 01:30:13.068954

"""

# revision identifiers, used by Alembic.
revision = 'c3803ac9b7dd'
down_revision = 'e8f52e92abd0'

from alembic import op  # noqa: E402
import sqlalchemy as sa  # noqa: E402


def upgrade():
    op.add_column(
        'postmaster_admins',
        sa.Column('failed_attempts', sa.Integer(), nullable=True))
    op.add_column(
        'postmaster_admins',
        sa.Column('last_failed_date', sa.DateTime(), nullable=True))
    op.add_column(
        'postmaster_admins',
        sa.Column('unlock_date', sa.DateTime(), nullable=True))


def downgrade():
    op.drop_column('postmaster_admins', 'unlock_date')
    op.drop_column('postmaster_admins', 'last_failed_date')
    op.drop_column('postmaster_admins', 'failed_attempts')
