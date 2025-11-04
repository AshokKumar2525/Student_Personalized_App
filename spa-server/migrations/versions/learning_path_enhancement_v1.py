"""Phase 1: Enhanced Learning Path Database Schema

Revision ID: learning_path_enhancement_v1
Revises: add_email_summarizer
Create Date: 2025-01-27 00:00:00.000000

This migration adds:
1. Roadmap template caching for reuse
2. Enhanced progress tracking with time/session data
3. Module and course feedback systems
4. Learning session tracking
5. User streak gamification
6. Roadmap caching for performance
7. Additional indexes for optimization
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = 'learning_path_enhancement_v1'
down_revision = 'add_email_summarizer'
branch_labels = None
depends_on = None


def upgrade():
    # =====================
    # 1. ROADMAP TEMPLATES
    # =====================
    op.create_table(
        'roadmap_templates',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('template_hash', sa.String(length=64), nullable=False),
        sa.Column('domain_id', sa.Integer(), nullable=False),
        sa.Column('knowledge_level', sa.String(length=16), nullable=False),
        sa.Column('learning_pace', sa.String(length=10), nullable=False),
        sa.Column('weekly_hours_range', sa.String(length=10), nullable=True),
        sa.Column('roadmap_data', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column('usage_count', sa.Integer(), nullable=False, server_default='1'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('NOW()')),
        sa.Column('last_used_at', sa.DateTime(), nullable=False, server_default=sa.text('NOW()')),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['domain_id'], ['domains.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('template_hash')
    )
    
    op.create_index('idx_template_hash', 'roadmap_templates', ['template_hash'])
    op.create_index('idx_template_domain_level_pace', 'roadmap_templates', ['domain_id', 'knowledge_level', 'learning_pace'])
    op.create_index('idx_template_usage', 'roadmap_templates', ['usage_count', 'last_used_at'])

    # =====================
    # 2. MODULE FEEDBACK
    # =====================
    op.create_table(
        'module_feedback',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.String(length=36), nullable=False),
        sa.Column('module_id', sa.Integer(), nullable=False),
        sa.Column('rating', sa.Integer(), nullable=False),
        sa.Column('comments', sa.Text(), nullable=True),
        sa.Column('difficulty_rating', sa.Integer(), nullable=True),
        sa.Column('content_quality', sa.Integer(), nullable=True),
        sa.Column('time_accuracy', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('NOW()')),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.CheckConstraint('rating >= 1 AND rating <= 5', name='check_module_rating'),
        sa.CheckConstraint('difficulty_rating >= 1 AND difficulty_rating <= 5', name='check_difficulty_rating'),
        sa.CheckConstraint('content_quality >= 1 AND content_quality <= 5', name='check_content_quality'),
        sa.CheckConstraint('time_accuracy >= 1 AND time_accuracy <= 5', name='check_time_accuracy'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['module_id'], ['path_modules.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    
    op.create_index('idx_feedback_module', 'module_feedback', ['module_id'])
    op.create_index('idx_feedback_user', 'module_feedback', ['user_id'])
    op.create_index('idx_feedback_rating', 'module_feedback', ['rating'])

    # =====================
    # 3. COURSE FEEDBACK
    # =====================
    op.create_table(
        'course_feedback',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.String(length=36), nullable=False),
        sa.Column('course_id', sa.Integer(), nullable=False),
        sa.Column('rating', sa.Integer(), nullable=False),
        sa.Column('comments', sa.Text(), nullable=True),
        sa.Column('would_recommend', sa.Boolean(), nullable=True, server_default='true'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('NOW()')),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.CheckConstraint('rating >= 1 AND rating <= 5', name='check_course_rating'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['course_id'], ['courses.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    
    op.create_index('idx_course_feedback_course', 'course_feedback', ['course_id'])
    op.create_index('idx_course_feedback_user', 'course_feedback', ['user_id'])

    # =====================
    # 4. LEARNING SESSIONS
    # =====================
    op.create_table(
        'learning_sessions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.String(length=36), nullable=False),
        sa.Column('module_id', sa.Integer(), nullable=True),
        sa.Column('course_id', sa.Integer(), nullable=True),
        sa.Column('session_date', sa.Date(), nullable=False, server_default=sa.text('CURRENT_DATE')),
        sa.Column('duration_minutes', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('resources_viewed', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('notes_taken', sa.Boolean(), nullable=True, server_default='false'),
        sa.Column('completed_in_session', sa.Boolean(), nullable=True, server_default='false'),
        sa.Column('started_at', sa.DateTime(), nullable=False, server_default=sa.text('NOW()')),
        sa.Column('ended_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['module_id'], ['path_modules.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['course_id'], ['courses.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    
    op.create_index('idx_session_user_date', 'learning_sessions', ['user_id', 'session_date'])
    op.create_index('idx_session_module', 'learning_sessions', ['module_id'])

    # =====================
    # 5. USER STREAKS
    # =====================
    op.create_table(
        'user_streaks',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.String(length=36), nullable=False),
        sa.Column('current_streak', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('longest_streak', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('total_learning_days', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('last_activity_date', sa.Date(), nullable=False, server_default=sa.text('CURRENT_DATE')),
        sa.Column('streak_start_date', sa.Date(), nullable=True, server_default=sa.text('CURRENT_DATE')),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('NOW()')),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id')
    )
    
    op.create_index('idx_streak_user', 'user_streaks', ['user_id'])

    # =====================
    # 6. ROADMAP CACHE
    # =====================
    op.create_table(
        'roadmap_cache',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.String(length=36), nullable=False),
        sa.Column('learning_path_id', sa.Integer(), nullable=False),
        sa.Column('roadmap_data', sa.Text(), nullable=False),
        sa.Column('version', sa.Integer(), nullable=True, server_default='1'),
        sa.Column('is_valid', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('NOW()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('NOW()')),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['learning_path_id'], ['learning_paths.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('learning_path_id')
    )
    
    op.create_index('idx_cache_path', 'roadmap_cache', ['learning_path_id'])
    op.create_index('idx_cache_user', 'roadmap_cache', ['user_id'])
    op.create_index('idx_cache_updated', 'roadmap_cache', ['updated_at'])

    # =====================
    # 7. ENHANCE USER_PROGRESS
    # =====================
    with op.batch_alter_table('user_progress', schema=None) as batch_op:
        batch_op.add_column(sa.Column('started_at', sa.DateTime(), nullable=True))
        batch_op.add_column(sa.Column('time_spent_minutes', sa.Integer(), nullable=True, server_default='0'))
        batch_op.add_column(sa.Column('last_accessed_at', sa.DateTime(), nullable=True))
        batch_op.add_column(sa.Column('attempts_count', sa.Integer(), nullable=True, server_default='0'))
        batch_op.add_column(sa.Column('completion_percentage', sa.Float(), nullable=True, server_default='0.0'))

    op.create_index('idx_user_progress_last_accessed', 'user_progress', ['user_id', 'last_accessed_at'])
    op.create_index('idx_user_progress_time_spent', 'user_progress', ['user_id', 'time_spent_minutes'])

    # =====================
    # 8. ENHANCE USER_POINTS
    # =====================
    with op.batch_alter_table('user_points', schema=None) as batch_op:
        batch_op.add_column(sa.Column('streak_bonus', sa.Integer(), nullable=True, server_default='0'))
        batch_op.add_column(sa.Column('total_modules_completed', sa.Integer(), nullable=True, server_default='0'))
        batch_op.add_column(sa.Column('total_courses_completed', sa.Integer(), nullable=True, server_default='0'))

    # =====================
    # 9. ADDITIONAL INDEXES FOR PERFORMANCE
    # =====================
    
    # Optimize learning path queries
    op.create_index('idx_learning_paths_user_domain', 'learning_paths', ['user_id', 'domain_id'])
    
    # Optimize module queries
    op.create_index('idx_path_modules_course_order', 'path_modules', ['course_id', 'order'])
    
    # Optimize progress queries
    op.create_index('idx_user_progress_composite', 'user_progress', ['user_id', 'module_id', 'status'])
    
    # Optimize user profile queries
    op.create_index('idx_user_profiles_preferences', 'user_profiles', ['domain_id', 'current_level', 'learning_pace'])


def downgrade():
    # Drop new indexes
    op.drop_index('idx_user_profiles_preferences', table_name='user_profiles')
    op.drop_index('idx_user_progress_composite', table_name='user_progress')
    op.drop_index('idx_path_modules_course_order', table_name='path_modules')
    op.drop_index('idx_learning_paths_user_domain', table_name='learning_paths')
    
    # Drop enhanced user_points columns
    with op.batch_alter_table('user_points', schema=None) as batch_op:
        batch_op.drop_column('total_courses_completed')
        batch_op.drop_column('total_modules_completed')
        batch_op.drop_column('streak_bonus')
    
    # Drop enhanced user_progress columns and indexes
    op.drop_index('idx_user_progress_time_spent', table_name='user_progress')
    op.drop_index('idx_user_progress_last_accessed', table_name='user_progress')
    
    with op.batch_alter_table('user_progress', schema=None) as batch_op:
        batch_op.drop_column('completion_percentage')
        batch_op.drop_column('attempts_count')
        batch_op.drop_column('last_accessed_at')
        batch_op.drop_column('time_spent_minutes')
        batch_op.drop_column('started_at')
    
    # Drop new tables
    op.drop_index('idx_cache_updated', table_name='roadmap_cache')
    op.drop_index('idx_cache_user', table_name='roadmap_cache')
    op.drop_index('idx_cache_path', table_name='roadmap_cache')
    op.drop_table('roadmap_cache')
    
    op.drop_index('idx_streak_user', table_name='user_streaks')
    op.drop_table('user_streaks')
    
    op.drop_index('idx_session_module', table_name='learning_sessions')
    op.drop_index('idx_session_user_date', table_name='learning_sessions')
    op.drop_table('learning_sessions')
    
    op.drop_index('idx_course_feedback_user', table_name='course_feedback')
    op.drop_index('idx_course_feedback_course', table_name='course_feedback')
    op.drop_table('course_feedback')
    
    op.drop_index('idx_feedback_rating', table_name='module_feedback')
    op.drop_index('idx_feedback_user', table_name='module_feedback')
    op.drop_index('idx_feedback_module', table_name='module_feedback')
    op.drop_table('module_feedback')
    
    op.drop_index('idx_template_usage', table_name='roadmap_templates')
    op.drop_index('idx_template_domain_level_pace', table_name='roadmap_templates')
    op.drop_index('idx_template_hash', table_name='roadmap_templates')
    op.drop_table('roadmap_templates')