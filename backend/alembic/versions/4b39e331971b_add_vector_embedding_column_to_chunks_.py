"""Add vector embedding column to chunks table

Revision ID: 4b39e331971b
Revises: 2bf91dd235ce
Create Date: 2025-04-24 17:36:00.653114

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '4b39e331971b'
down_revision: Union[str, None] = '2bf91dd235ce'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("TRUNCATE TABLE document_chunks")
    op.execute("TRUNCATE TABLE messages")

     # Modificar la columna de document_chunks
    op.execute("ALTER TABLE document_chunks ALTER COLUMN embedding TYPE vector(768)")
    
    # Modificar la columna de messages
    op.execute("ALTER TABLE messages ALTER COLUMN embedding TYPE vector(768)")


def downgrade() -> None:
    op.execute("TRUNCATE TABLE document_chunks")
    op.execute("TRUNCATE TABLE messages")
    op.execute("ALTER TABLE document_chunks ALTER COLUMN embedding TYPE vector(1024)")
    op.execute("ALTER TABLE messages ALTER COLUMN embedding TYPE vector(1024)")
