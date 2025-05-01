"""Set embedding dimension to 1024

Revision ID: f2df68976544
Revises: 4b39e331971b
Create Date: 2025-05-01 13:05:35.590151

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f2df68976544'
down_revision: Union[str, None] = '4b39e331971b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    
    op.execute("TRUNCATE TABLE document_chunks")
    op.execute("TRUNCATE TABLE messages")
    # ------------------------------


    op.execute("ALTER TABLE document_chunks ALTER COLUMN embedding TYPE vector(1024)")


    op.execute("ALTER TABLE messages ALTER COLUMN embedding TYPE vector(1024)")


def downgrade() -> None:
  
    op.execute("TRUNCATE TABLE document_chunks")
    op.execute("TRUNCATE TABLE messages")
    # ------------------------------

 
    op.execute("ALTER TABLE document_chunks ALTER COLUMN embedding TYPE vector(768)")
    op.execute("ALTER TABLE messages ALTER COLUMN embedding TYPE vector(768)")