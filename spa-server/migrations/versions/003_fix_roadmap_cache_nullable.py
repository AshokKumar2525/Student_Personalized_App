"""fix roadmap_cache learning_path_id nullable

Revision ID: 003_fix_roadmap_cache_nullable
Revises: 002_fix_all_foreign_keys
Create Date: 2025-11-04 22:20:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '003_fix_roadmap_cache_nullable'
down_revision = '002_fix_all_foreign_keys'
branch_labels = None
depends_on = None


def upgrade():
    # Allow NULL for roadmap_cache learning_path_id
    op.alter_column('roadmap_cache', 'learning_path_id',
               existing_type=sa.INTEGER(),
               nullable=True)


def downgrade():
    # Revert roadmap_cache learning_path_id
    op.alter_column('roadmap_cache', 'learning_path_id',
               existing_type=sa.INTEGER(),
               nullable=False)