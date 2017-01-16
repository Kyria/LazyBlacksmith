"""Change eveuser table name

Revision ID: 3948980c7a13
Revises: 1e2c15118d41
Create Date: 2017-01-16 11:50:01.207507

"""

# revision identifiers, used by Alembic.
revision = '3948980c7a13'
down_revision = '1e2c15118d41'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql


def upgrade():
    op.rename_table('eve_user', 'user')


def downgrade():
    op.rename_table('user', 'eve_user')
