"""Change embedding vector dimension to 768

Revision ID: 76891bdb42e6
Revises: f2df68976544
Create Date: 2025-05-05 15:42:02.328324

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '76891bdb42e6'
down_revision: Union[str, None] = 'f2df68976544'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("TRUNCATE TABLE document_chunks")
    op.execute("TRUNCATE TABLE messages")
    # ------------------------------


    op.execute("ALTER TABLE document_chunks ALTER COLUMN embedding TYPE vector(768)")


    op.execute("ALTER TABLE messages ALTER COLUMN embedding TYPE vector(768)")



def downgrade() -> None:
    op.execute("TRUNCATE TABLE document_chunks")
    op.execute("TRUNCATE TABLE messages")
    # ------------------------------

 
    op.execute("ALTER TABLE document_chunks ALTER COLUMN embedding TYPE vector(1024)")
    op.execute("ALTER TABLE messages ALTER COLUMN embedding TYPE vector(1024)")