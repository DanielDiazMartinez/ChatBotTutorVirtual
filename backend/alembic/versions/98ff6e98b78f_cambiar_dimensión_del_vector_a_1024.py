"""Cambiar dimensión del vector a 1024

Revision ID: 98ff6e98b78f
Revises: c25776a485ec
Create Date: 2025-03-21 10:55:22.530742

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '98ff6e98b78f'
down_revision: Union[str, None] = 'c25776a485ec'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Eliminar datos existentes en las tablas (opcional, pero probablemente necesario)
    op.execute("TRUNCATE TABLE document_chunks")
    op.execute("TRUNCATE TABLE messages")
    
    # Modificar la columna de document_chunks
    op.execute("ALTER TABLE document_chunks ALTER COLUMN embedding TYPE vector(1024)")
    
    # Modificar la columna de messages
    op.execute("ALTER TABLE messages ALTER COLUMN embedding TYPE vector(1024)")

def downgrade() -> None:
    # Si necesitas revertir los cambios:
    op.execute("TRUNCATE TABLE document_chunks")
    op.execute("TRUNCATE TABLE messages")
    op.execute("ALTER TABLE document_chunks ALTER COLUMN embedding TYPE vector(1536)")
    op.execute("ALTER TABLE messages ALTER COLUMN embedding TYPE vector(1536)")