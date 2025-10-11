"""Enable RLS on all tables

Revision ID: 002
Revises: 143bfdd9343d
Create Date: 2024-01-20 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '002'
down_revision = '143bfdd9343d'
branch_labels = None
depends_on = None


def upgrade():
    # Enable RLS on all tables
    op.execute('ALTER TABLE alembic_version ENABLE ROW LEVEL SECURITY')
    op.execute('ALTER TABLE users ENABLE ROW LEVEL SECURITY')
    op.execute('ALTER TABLE user_learning_profiles ENABLE ROW LEVEL SECURITY')
    op.execute('ALTER TABLE learning_paths ENABLE ROW LEVEL SECURITY')
    op.execute('ALTER TABLE learning_resources ENABLE ROW LEVEL SECURITY')
    
    # Create RLS policies
    
    # alembic_version policies (read/write for all)
    op.execute('''
        CREATE POLICY "Allow all operations on alembic_version" ON alembic_version
        FOR ALL USING (true)
    ''')
    
    # users table policies
    op.execute('''
        CREATE POLICY "Users can view all users" ON users
        FOR SELECT USING (true)
    ''')
    op.execute('''
        CREATE POLICY "Users can insert own user data" ON users
        FOR INSERT WITH CHECK (true)
    ''')
    op.execute('''
        CREATE POLICY "Users can update own user data" ON users
        FOR UPDATE USING (true)
    ''')
    
    # user_learning_profiles policies
    op.execute('''
        CREATE POLICY "Users can view all learning profiles" ON user_learning_profiles
        FOR SELECT USING (true)
    ''')
    op.execute('''
        CREATE POLICY "Users can insert own learning profile" ON user_learning_profiles
        FOR INSERT WITH CHECK (true)
    ''')
    op.execute('''
        CREATE POLICY "Users can update own learning profile" ON user_learning_profiles
        FOR UPDATE USING (true)
    ''')
    
    # learning_paths policies
    op.execute('''
        CREATE POLICY "Users can view all learning paths" ON learning_paths
        FOR SELECT USING (true)
    ''')
    op.execute('''
        CREATE POLICY "Users can insert own learning path" ON learning_paths
        FOR INSERT WITH CHECK (true)
    ''')
    op.execute('''
        CREATE POLICY "Users can update own learning path" ON learning_paths
        FOR UPDATE USING (true)
    ''')
    
    # learning_resources policies
    op.execute('''
        CREATE POLICY "Users can view all learning resources" ON learning_resources
        FOR SELECT USING (true)
    ''')
    op.execute('''
        CREATE POLICY "Users can insert learning resources" ON learning_resources
        FOR INSERT WITH CHECK (true)
    ''')
    op.execute('''
        CREATE POLICY "Users can update learning resources" ON learning_resources
        FOR UPDATE USING (true)
    ''')


def downgrade():
    # Drop all policies
    op.execute('DROP POLICY IF EXISTS "Allow all operations on alembic_version" ON alembic_version')
    op.execute('DROP POLICY IF EXISTS "Users can view all users" ON users')
    op.execute('DROP POLICY IF EXISTS "Users can insert own user data" ON users')
    op.execute('DROP POLICY IF EXISTS "Users can update own user data" ON users')
    op.execute('DROP POLICY IF EXISTS "Users can view all learning profiles" ON user_learning_profiles')
    op.execute('DROP POLICY IF EXISTS "Users can insert own learning profile" ON user_learning_profiles')
    op.execute('DROP POLICY IF EXISTS "Users can update own learning profile" ON user_learning_profiles')
    op.execute('DROP POLICY IF EXISTS "Users can view all learning paths" ON learning_paths')
    op.execute('DROP POLICY IF EXISTS "Users can insert own learning path" ON learning_paths')
    op.execute('DROP POLICY IF EXISTS "Users can update own learning path" ON learning_paths')
    op.execute('DROP POLICY IF EXISTS "Users can view all learning resources" ON learning_resources')
    op.execute('DROP POLICY IF EXISTS "Users can insert learning resources" ON learning_resources')
    op.execute('DROP POLICY IF EXISTS "Users can update learning resources" ON learning_resources')
    
    # Disable RLS on all tables
    op.execute('ALTER TABLE alembic_version DISABLE ROW LEVEL SECURITY')
    op.execute('ALTER TABLE users DISABLE ROW LEVEL SECURITY')
    op.execute('ALTER TABLE user_learning_profiles DISABLE ROW LEVEL SECURITY')
    op.execute('ALTER TABLE learning_paths DISABLE ROW LEVEL SECURITY')
    op.execute('ALTER TABLE learning_resources DISABLE ROW LEVEL SECURITY')