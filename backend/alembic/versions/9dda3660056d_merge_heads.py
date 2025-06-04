"""merge_heads

Revision ID: 9dda3660056d
Revises: add_summary_to_documents, eliminar_user_role_conversations
Create Date: 2025-06-03 18:08:57.955949

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '9dda3660056d'
down_revision: Union[str, None] = ('add_summary_to_documents', 'eliminar_user_role_conversations')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass