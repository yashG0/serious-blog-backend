"""Add new field to posts

Revision ID: 0d605457d7bb
Revises: 
Create Date: 2024-12-24 10:02:06.330726
"""

from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '0d605457d7bb'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add the 'image' column to the 'posts' table
    op.add_column('posts', sa.Column('image', sa.String(), nullable=True))


def downgrade() -> None:
    # Remove the 'image' column from the 'posts' table
    op.drop_column('posts', 'image')
