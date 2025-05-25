"""eliminar_user_role_de_conversations

Revision ID: eliminar_user_role_conversations
Revises: 9abdb3412878
Create Date: 2025-05-25

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'eliminar_user_role_conversations'
down_revision = '9abdb3412878'  # Ajusta esto al último ID de migración en tu carpeta versions
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Eliminar el campo user_role de la tabla conversations
    op.drop_column('conversations', 'user_role')
    # También eliminar el validador del modelo


def downgrade() -> None:
    # En caso de querer revertir, recrear la columna user_role
    op.add_column('conversations', sa.Column('user_role', sa.String(), nullable=True))
