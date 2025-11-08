"""separate module AI content cache

Revision ID: 004_separate_module_ai_cache
Revises: 003_fix_roadmap_cache_nullable
Create Date: 2025-11-05 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '004_separate_module_ai_cache'
down_revision = '003_fix_roadmap_cache_nullable'
branch_labels = None
depends_on = None


def upgrade():
    # Create dedicated table for module AI content caching
    op.create_table(
        'module_ai_content_cache',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('module_id', sa.Integer(), nullable=False),
        sa.Column('content_hash', sa.String(length=64), nullable=False),
        sa.Column('ai_content', sa.Text(), nullable=False),  # JSON string
        sa.Column('model_used', sa.String(length=32), nullable=True),
        sa.Column('is_valid', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('usage_count', sa.Integer(), nullable=False, server_default='1'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('NOW()')),
        sa.Column('last_accessed_at', sa.DateTime(), nullable=False, server_default=sa.text('NOW()')),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['module_id'], ['path_modules.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('module_id')  # One cache per module
    )
    
    # Create indexes for performance
    op.create_index('idx_module_ai_cache_module', 'module_ai_content_cache', ['module_id'])
    op.create_index('idx_module_ai_cache_hash', 'module_ai_content_cache', ['content_hash'])
    op.create_index('idx_module_ai_cache_valid', 'module_ai_content_cache', ['is_valid', 'last_accessed_at'])
    
    # Clean up roadmap_cache: Remove entries where learning_path_id is NULL
    # These were module AI content entries that should be in the new table
    op.execute("DELETE FROM roadmap_cache WHERE learning_path_id IS NULL")
    
    # Make learning_path_id NOT NULL again (it should always have a value for roadmap cache)
    op.alter_column('roadmap_cache', 'learning_path_id',
                   existing_type=sa.INTEGER(),
                   nullable=False)


def downgrade():
    # Revert learning_path_id to nullable
    op.alter_column('roadmap_cache', 'learning_path_id',
                   existing_type=sa.INTEGER(),
                   nullable=True)
    
    # Drop indexes
    op.drop_index('idx_module_ai_cache_valid', table_name='module_ai_content_cache')
    op.drop_index('idx_module_ai_cache_hash', table_name='module_ai_content_cache')
    op.drop_index('idx_module_ai_cache_module', table_name='module_ai_content_cache')
    
    # Drop table
    op.drop_table('module_ai_content_cache')