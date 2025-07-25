"""cambiar_topic_id_por_subject_id_en_conversaciones

Revision ID: 8cdae24154d1
Revises: 8054f453a9dd
Create Date: 2025-05-18 10:46:27.285463

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '8cdae24154d1'
down_revision: Union[str, None] = '8054f453a9dd'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('conversations', sa.Column('subject_id', sa.Integer(), nullable=True))
    
    # Transferir datos del campo topic_id al campo subject_id
    # Este paso obtiene el subject_id asociado con cada topic antes de eliminar la columna
    conn = op.get_bind()
    conn.execute(sa.text("""
        UPDATE conversations c 
        SET subject_id = (
            SELECT t.subject_id 
            FROM topics t 
            WHERE t.id = c.topic_id
        )
        WHERE c.topic_id IS NOT NULL
    """))
    
    op.drop_constraint('conversations_topic_id_fkey', 'conversations', type_='foreignkey')
    op.create_foreign_key(None, 'conversations', 'subjects', ['subject_id'], ['id'])
    op.drop_column('conversations', 'topic_id')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('conversations', sa.Column('topic_id', sa.INTEGER(), autoincrement=False, nullable=True))
    op.drop_constraint(None, 'conversations', type_='foreignkey')
    op.create_foreign_key('conversations_topic_id_fkey', 'conversations', 'topics', ['topic_id'], ['id'])
    op.drop_column('conversations', 'subject_id')
    # ### end Alembic commands ###