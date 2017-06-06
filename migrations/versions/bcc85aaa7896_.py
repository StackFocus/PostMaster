"""Creates the virtual_domains, virtual_aliases, and virtual_users tables

Revision ID: bcc85aaa7896
Revises: None
Create Date: 2016-07-13 18:48:36.702746

"""

# revision identifiers, used by Alembic.
revision = 'bcc85aaa7896'
down_revision = None

from alembic import op  # noqa: E402
import sqlalchemy as sa  # noqa: E402


def upgrade():
    op.create_table(
        'virtual_domains',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=50), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        mysql_charset='utf8',
        mysql_engine='InnoDB'
    )
    op.create_table(
        'virtual_aliases',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('domain_id', sa.Integer(), nullable=False),
        sa.Column('source', sa.String(length=100), nullable=False),
        sa.Column('destination', sa.String(length=100), nullable=False),
        sa.ForeignKeyConstraint(['domain_id'], ['virtual_domains.id'],
                                ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('source'),
        mysql_charset='utf8',
        mysql_engine='InnoDB'
    )
    op.create_table(
        'virtual_users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('domain_id', sa.Integer(), nullable=False),
        sa.Column('password', sa.String(length=106), nullable=False),
        sa.Column('email', sa.String(length=120), nullable=False),
        sa.ForeignKeyConstraint(['domain_id'], ['virtual_domains.id'],
                                ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('email'),
        mysql_charset='utf8',
        mysql_engine='InnoDB'
    )


def downgrade():
    op.drop_table('virtual_users')
    op.drop_table('virtual_aliases')
    op.drop_table('virtual_domains')
