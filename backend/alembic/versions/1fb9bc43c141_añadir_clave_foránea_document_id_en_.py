"""Añadir clave foránea document_id en Conversation

Revision ID: 1fb9bc43c141
Revises: 4659765734f4
Create Date: 2025-02-10 17:53:05.981235

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '1fb9bc43c141'
down_revision: Union[str, None] = '4659765734f4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    pass
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    pass
    # ### end Alembic commands ###
