"""Add Like model

Revision ID: e4623affcf8b
Revises: bac82e5e453c
Create Date: 2025-08-13 16:55:22.369105
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = 'e4623affcf8b'
down_revision: Union[str, Sequence[str], None] = 'bac82e5e453c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Добавляем колонку file_path к постам
    op.add_column('posts', sa.Column('file_path', sa.String(), nullable=True))

    op.alter_column('users', 'username', existing_type=sa.VARCHAR(), nullable=False)
    op.alter_column('users', 'email', existing_type=sa.VARCHAR(), nullable=False)
    op.alter_column('users', 'hashed_password', existing_type=sa.VARCHAR(), nullable=False)

    gender_enum = sa.Enum('male', 'female', name='genderenum')
    gender_enum.create(op.get_bind(), checkfirst=True)

    op.execute("""
        ALTER TABLE users
        ALTER COLUMN gender
        TYPE genderenum
        USING
            CASE
                WHEN gender = 'male' THEN 'male'::genderenum
                ELSE 'female'::genderenum
            END
    """)
    op.alter_column('users', 'gender', server_default=sa.text("'female'"))
    op.drop_column('users', 'relationship_goal')


def downgrade() -> None:
    """Downgrade schema."""
    op.add_column('users', sa.Column('relationship_goal', sa.VARCHAR(), nullable=True))

    op.execute('ALTER TABLE users ALTER COLUMN gender TYPE VARCHAR USING gender::text')

    gender_enum = sa.Enum('male', 'female', name='genderenum')
    gender_enum.drop(op.get_bind(), checkfirst=True)

    op.alter_column('users', 'hashed_password', existing_type=sa.VARCHAR(), nullable=True)
    op.alter_column('users', 'email', existing_type=sa.VARCHAR(), nullable=True)
    op.alter_column('users', 'username', existing_type=sa.VARCHAR(), nullable=True)

    op.drop_column('posts', 'file_path')
