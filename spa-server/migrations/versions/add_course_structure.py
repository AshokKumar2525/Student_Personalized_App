"""add course structure simple

Revision ID: add_course_structure
Revises: 535a44a19fdc
Create Date: 2025-01-18 23:50:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'add_course_structure'
down_revision = '535a44a19fdc'
branch_labels = None
depends_on = None

def upgrade():
    # Create courses table with INTEGER IDs to match existing structure
    op.create_table('courses',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('path_id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(128), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('order', sa.Integer(), nullable=False),
        sa.Column('estimated_time', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['path_id'], ['learning_paths.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_course_path', 'courses', ['path_id', 'order'])
    
    # Add course_id to path_modules
    op.add_column('path_modules', sa.Column('course_id', sa.Integer(), nullable=True))
    op.create_foreign_key('path_modules_course_id_fkey', 'path_modules', 'courses', ['course_id'], ['id'])
    op.create_index('idx_pathmodule_course', 'path_modules', ['course_id', 'order'])

def downgrade():
    # Remove foreign keys and indexes
    op.drop_constraint('path_modules_course_id_fkey', 'path_modules', type_='foreignkey')
    op.drop_index('idx_pathmodule_course', 'path_modules')
    op.drop_index('idx_course_path', 'courses')
    
    # Remove course_id column
    op.drop_column('path_modules', 'course_id')
    
    # Drop courses table
    op.drop_table('courses')