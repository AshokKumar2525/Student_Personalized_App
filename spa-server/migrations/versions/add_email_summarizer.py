"""Add email summarizer tables

Revision ID: add_email_summarizer
Revises: 4c68364da00e
Create Date: 2024-01-01 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'add_email_summarizer'
down_revision = '4c68364da00e'  # Update with your latest migration
branch_labels = None
depends_on = None


def upgrade():
    # Create email_accounts table
    op.create_table(
        'email_accounts',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.String(length=36), nullable=False),
        sa.Column('email_address', sa.String(length=255), nullable=False),
        sa.Column('access_token', sa.Text(), nullable=True),
        sa.Column('refresh_token', sa.Text(), nullable=True),
        sa.Column('token_expires_at', sa.DateTime(), nullable=True),
        sa.Column('last_sync_at', sa.DateTime(), nullable=True),
        sa.Column('sync_token', sa.String(length=255), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id')
    )
    
    # Create emails table
    op.create_table(
        'emails',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('account_id', sa.Integer(), nullable=False),
        sa.Column('message_id', sa.String(length=255), nullable=False),
        sa.Column('thread_id', sa.String(length=255), nullable=True),
        sa.Column('subject', sa.Text(), nullable=True),
        sa.Column('sender_email', sa.String(length=255), nullable=False),
        sa.Column('sender_name', sa.String(length=255), nullable=True),
        sa.Column('snippet', sa.Text(), nullable=True),
        sa.Column('category', sa.String(length=32), nullable=True),
        sa.Column('is_starred', sa.Boolean(), nullable=True),
        sa.Column('is_read', sa.Boolean(), nullable=True),
        sa.Column('has_attachments', sa.Boolean(), nullable=True),
        sa.Column('email_date', sa.DateTime(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['account_id'], ['email_accounts.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('message_id')
    )
    
    # Create indexes for emails table
    op.create_index('idx_email_account', 'emails', ['account_id'])
    op.create_index('idx_email_date', 'emails', ['email_date'])
    op.create_index('idx_email_category', 'emails', ['category'])
    op.create_index('idx_email_starred', 'emails', ['is_starred'])
    
    # Create email_summaries table
    op.create_table(
        'email_summaries',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('email_id', sa.Integer(), nullable=False),
        sa.Column('summary_text', sa.Text(), nullable=False),
        sa.Column('key_points', postgresql.ARRAY(sa.String()), nullable=True),
        sa.Column('action_items', postgresql.ARRAY(sa.String()), nullable=True),
        sa.Column('priority', sa.String(length=16), nullable=True),
        sa.Column('sentiment', sa.String(length=16), nullable=True),
        sa.Column('model_used', sa.String(length=32), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['email_id'], ['emails.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('email_id')
    )


def downgrade():
    # Drop tables in reverse order
    op.drop_table('email_summaries')
    
    # Drop indexes first
    op.drop_index('idx_email_starred', table_name='emails')
    op.drop_index('idx_email_category', table_name='emails')
    op.drop_index('idx_email_date', table_name='emails')
    op.drop_index('idx_email_account', table_name='emails')
    
    op.drop_table('emails')
    op.drop_table('email_accounts')