"""fix all foreign key constraints

Revision ID: 002_fix_all_foreign_keys
Revises: fix_foreign_key_constraints
Create Date: 2025-11-04 16:45:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '002_fix_all_foreign_keys'
down_revision = 'fix_foreign_key_constraints'
branch_labels = None
depends_on = None


def upgrade():
    # Fix module_resources foreign key
    op.drop_constraint('module_resources_module_id_fkey', 'module_resources', type_='foreignkey')
    op.create_foreign_key('module_resources_module_id_fkey', 'module_resources', 'path_modules', ['module_id'], ['id'], ondelete='CASCADE')
    
    # Fix learning_activities foreign key
    op.drop_constraint('learning_activities_module_id_fkey', 'learning_activities', type_='foreignkey')
    op.create_foreign_key('learning_activities_module_id_fkey', 'learning_activities', 'path_modules', ['module_id'], ['id'], ondelete='CASCADE')
    
    # Allow NULL for roadmap_cache learning_path_id
    op.alter_column('roadmap_cache', 'learning_path_id',
               existing_type=sa.INTEGER(),
               nullable=True)


def downgrade():
    # Revert module_resources foreign key
    op.drop_constraint('module_resources_module_id_fkey', 'module_resources', type_='foreignkey')
    op.create_foreign_key('module_resources_module_id_fkey', 'module_resources', 'path_modules', ['module_id'], ['id'])
    
    # Revert learning_activities foreign key
    op.drop_constraint('learning_activities_module_id_fkey', 'learning_activities', type_='foreignkey')
    op.create_foreign_key('learning_activities_module_id_fkey', 'learning_activities', 'path_modules', ['module_id'], ['id'])
    
    # Revert roadmap_cache learning_path_id
    op.alter_column('roadmap_cache', 'learning_path_id',
               existing_type=sa.INTEGER(),
               nullable=False)