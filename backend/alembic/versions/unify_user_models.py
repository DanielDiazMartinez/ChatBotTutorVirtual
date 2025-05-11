"""unify_user_models

Revision ID: unify_user_models
Revises: 33bfa4823779
Create Date: 2025-05-10 10:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = 'unify_user_models'
down_revision: Union[str, None] = '33bfa4823779'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    # Crear la nueva tabla users
    op.create_table('users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('email', sa.String(), nullable=False),
        sa.Column('full_name', sa.String(), nullable=True),
        sa.Column('hashed_password', sa.String(), nullable=False),
        sa.Column('role', sa.String(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)
    op.create_index(op.f('ix_users_id'), 'users', ['id'], unique=False)

    # Migrar datos de admin, teacher y student a users
    op.execute("""
        INSERT INTO users (email, full_name, hashed_password, role, created_at)
        SELECT email, full_name, hashed_password, 'admin', created_at
        FROM admins
    """)
    
    op.execute("""
        INSERT INTO users (email, full_name, hashed_password, role, created_at)
        SELECT email, full_name, hashed_password, 'teacher', created_at
        FROM teachers
    """)
    
    op.execute("""
        INSERT INTO users (email, full_name, hashed_password, role, created_at)
        SELECT email, full_name, hashed_password, 'student', created_at
        FROM students
    """)

    # Actualizar las foreign keys en las tablas relacionadas
    op.drop_constraint('documents_teacher_id_fkey', 'documents', type_='foreignkey')
    op.create_foreign_key(None, 'documents', 'users', ['teacher_id'], ['id'], ondelete='CASCADE')

    op.drop_constraint('conversations_student_id_fkey', 'conversations', type_='foreignkey')
    op.drop_constraint('conversations_teacher_id_fkey', 'conversations', type_='foreignkey')
    op.create_foreign_key(None, 'conversations', 'users', ['student_id'], ['id'], ondelete='CASCADE')
    op.create_foreign_key(None, 'conversations', 'users', ['teacher_id'], ['id'], ondelete='CASCADE')

    # Actualizar las tablas intermedias
    op.drop_constraint('teacher_subject_teacher_id_fkey', 'teacher_subject', type_='foreignkey')
    op.create_foreign_key(None, 'teacher_subject', 'users', ['teacher_id'], ['id'], ondelete='CASCADE')

    op.drop_constraint('student_subject_student_id_fkey', 'student_subject', type_='foreignkey')
    op.create_foreign_key(None, 'student_subject', 'users', ['student_id'], ['id'], ondelete='CASCADE')

    # Eliminar las tablas antiguas
    op.drop_table('admins')
    op.drop_table('teachers')
    op.drop_table('students')

def downgrade() -> None:
    # Recrear las tablas originales
    op.create_table('admins',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('email', sa.String(), nullable=False),
        sa.Column('full_name', sa.String(), nullable=True),
        sa.Column('hashed_password', sa.String(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_admins_email'), 'admins', ['email'], unique=True)
    op.create_index(op.f('ix_admins_id'), 'admins', ['id'], unique=False)

    op.create_table('teachers',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('email', sa.String(), nullable=False),
        sa.Column('full_name', sa.String(), nullable=True),
        sa.Column('hashed_password', sa.String(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_teachers_email'), 'teachers', ['email'], unique=True)
    op.create_index(op.f('ix_teachers_id'), 'teachers', ['id'], unique=False)

    op.create_table('students',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('email', sa.String(), nullable=False),
        sa.Column('full_name', sa.String(), nullable=True),
        sa.Column('hashed_password', sa.String(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_students_email'), 'students', ['email'], unique=True)
    op.create_index(op.f('ix_students_id'), 'students', ['id'], unique=False)

    # Migrar datos de users a las tablas originales
    op.execute("""
        INSERT INTO admins (email, full_name, hashed_password, created_at)
        SELECT email, full_name, hashed_password,created_at
        FROM users WHERE role = 'admin'
    """)
    
    op.execute("""
        INSERT INTO teachers (email, full_name, hashed_password, created_at)
        SELECT email, full_name, hashed_password, created_at
        FROM users WHERE role = 'teacher'
    """)
    
    op.execute("""
        INSERT INTO students (email, full_name, hashed_password, created_at)
        SELECT email, full_name, hashed_password, created_at
        FROM users WHERE role = 'student'
    """)

    # Restaurar las foreign keys originales
    op.drop_constraint(None, 'documents', type_='foreignkey')
    op.create_foreign_key('documents_teacher_id_fkey', 'documents', 'teachers', ['teacher_id'], ['id'], ondelete='CASCADE')

    op.drop_constraint(None, 'conversations', type_='foreignkey')
    op.drop_constraint(None, 'conversations', type_='foreignkey')
    op.create_foreign_key('conversations_student_id_fkey', 'conversations', 'students', ['student_id'], ['id'], ondelete='CASCADE')
    op.create_foreign_key('conversations_teacher_id_fkey', 'conversations', 'teachers', ['teacher_id'], ['id'], ondelete='CASCADE')

    op.drop_constraint(None, 'teacher_subject', type_='foreignkey')
    op.create_foreign_key('teacher_subject_teacher_id_fkey', 'teacher_subject', 'teachers', ['teacher_id'], ['id'], ondelete='CASCADE')

    op.drop_constraint(None, 'student_subject', type_='foreignkey')
    op.create_foreign_key('student_subject_student_id_fkey', 'student_subject', 'students', ['student_id'], ['id'], ondelete='CASCADE')

    # Eliminar la tabla users
    op.drop_table('users')
