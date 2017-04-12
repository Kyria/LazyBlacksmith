"""add corporation flag

Revision ID: d03236a0cda4
Revises: 47e567919169
Create Date: 2017-04-12 13:21:03.482000

"""

# revision identifiers, used by Alembic.

import sqlalchemy as sa

from alembic import op
from lazyblacksmith.models import Blueprint
from lazyblacksmith.models import db

revision = 'd03236a0cda4'
down_revision = '47e567919169'

def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('blueprint',
                  sa.Column('corporation', sa.Boolean(), nullable=False))
    Blueprint.query.update({'corporation': False})
    db.session.commit()
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('blueprint', 'corporation')
    # ### end Alembic commands ###
