from app import db
from datetime import datetime
from sqlalchemy import String, Integer, Date, DateTime, ForeignKey, Boolean, Float, Text, Index, CheckConstraint
from sqlalchemy.dialects.postgresql import ARRAY, JSONB
from app.models.utils import generate_uuid

# ======================
# CORE TABLES (7 tables)
# ======================

class Domain(db.Model):
    """Domains like Web Dev, AI, Cloud"""
    __tablename__ = 'domains'
    id = db.Column(Integer, primary_key=True)
    name = db.Column(String(64), unique=True, nullable=False)
    description = db.Column(Text)
    created_at = db.Column(DateTime, default=datetime.utcnow)
    technologies = db.relationship('Technology', back_populates='domain', cascade='all, delete-orphan')

class Technology(db.Model):
    """Technologies like React, Docker, TensorFlow"""
    __tablename__ = 'technologies'
    id = db.Column(Integer, primary_key=True)
    domain_id = db.Column(Integer, ForeignKey('domains.id'), nullable=False, index=True)
    name = db.Column(String(64), unique=True, nullable=False)
    current_version = db.Column(String(20))
    description = db.Column(Text)
    created_at = db.Column(DateTime, default=datetime.utcnow)
    domain = db.relationship('Domain', back_populates='technologies')

class UserProfile(db.Model):
    """Student profile with learning preferences"""
    __tablename__ = 'user_profiles'
    __table_args__ = (
        CheckConstraint("current_level IN ('beginner', 'intermediate', 'advanced')", name='check_user_level'),
        CheckConstraint("learning_pace IN ('slow', 'medium', 'fast')", name='check_learning_pace'),
        CheckConstraint("update_frequency IN ('daily', 'weekly', 'monthly')", name='check_update_frequency'),
        CheckConstraint("update_difficulty IN ('easy', 'moderate', 'hard')", name='check_update_difficulty'),
        Index('idx_userprofile_domain', 'domain_id'),
        Index('idx_userprofile_level', 'current_level'),
    )

    id = db.Column(String(36), primary_key=True, default=generate_uuid)
    user_id = db.Column(String(36), ForeignKey('users.id'), nullable=False, unique=True)
    domain_id = db.Column(Integer, ForeignKey('domains.id'), nullable=False, index=True)
    current_level = db.Column(String(16), nullable=False)  # beginner, intermediate, advanced
    familiar_techs = db.Column(ARRAY(Integer))  # Array of technology_ids
    daily_time = db.Column(Integer)  # Minutes per day
    learning_pace = db.Column(String(10), nullable=False)  # slow, medium, fast

    # Auto-update preferences
    auto_update_enabled = db.Column(Boolean, default=True)
    update_frequency = db.Column(String(10), default='weekly')
    update_difficulty = db.Column(String(10), default='moderate')

    created_at = db.Column(DateTime, default=datetime.utcnow)
    updated_at = db.Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = db.relationship('User', back_populates='profile')
    domain = db.relationship('Domain')
    progress = db.relationship('UserProgress', back_populates='profile', cascade='all, delete-orphan')


class LearningPath(db.Model):
    """Main learning path container"""
    __tablename__ = 'learning_paths'

    id = db.Column(Integer, primary_key=True)
    user_id = db.Column(String(36), ForeignKey('users.id'), nullable=False, index=True)
    domain_id = db.Column(Integer, ForeignKey('domains.id'), nullable=False, index=True)
    current_version = db.Column(Integer, default=1)
    created_at = db.Column(DateTime, default=datetime.utcnow)
    updated_at = db.Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = db.relationship('User', back_populates='learning_paths')
    domain = db.relationship('Domain')
    courses = db.relationship('Course', back_populates='learning_path', cascade='all, delete-orphan')
    versions = db.relationship('RoadmapVersion', back_populates='path', cascade='all, delete-orphan')

class Course(db.Model):
    """Courses within a learning path"""
    __tablename__ = 'courses'
    __table_args__ = (
        Index('idx_course_path', 'path_id', 'order'),
    )

    id = db.Column(Integer, primary_key=True) 
    path_id = db.Column(Integer, ForeignKey('learning_paths.id'), nullable=False, index=True)
    title = db.Column(String(128), nullable=False)
    description = db.Column(Text)
    order = db.Column(Integer, nullable=False)
    estimated_time = db.Column(Integer)  # Minutes for entire course
    created_at = db.Column(DateTime, default=datetime.utcnow)

    # Relationships
    learning_path = db.relationship('LearningPath', back_populates='courses')
    modules = db.relationship('PathModule', back_populates='course', cascade='all, delete-orphan')

class PathModule(db.Model):
    """Individual topics in a course"""
    __tablename__ = 'path_modules'
    __table_args__ = (
        Index('idx_pathmodule_course', 'course_id', 'order'),
    )

    id = db.Column(Integer, primary_key=True)  # Keep as Integer
    course_id = db.Column(Integer, ForeignKey('courses.id'), nullable=False, index=True)
    path_id = db.Column(Integer, ForeignKey('learning_paths.id'), nullable=False, index=True)  # Keep for backward compatibility
    tech_id = db.Column(Integer, ForeignKey('technologies.id'), index=True)
    title = db.Column(String(128), nullable=False)
    description = db.Column(Text)
    order = db.Column(Integer, nullable=False)
    estimated_time = db.Column(Integer)  # Minutes
    tech_version = db.Column(String(20))
    created_at = db.Column(DateTime, default=datetime.utcnow)

    # Relationships
    course = db.relationship('Course', back_populates='modules')
    path = db.relationship('LearningPath')  # Keep for backward compatibility
    tech = db.relationship('Technology')
    resources = db.relationship('ModuleResource', back_populates='module', cascade='all, delete-orphan')
    progress = db.relationship('UserProgress', back_populates='module', 
                              foreign_keys='UserProgress.module_id',  # SPECIFY FOREIGN KEY
                              cascade='all, delete-orphan')
    activities = db.relationship('LearningActivity', back_populates='module', cascade='all, delete-orphan')

class ModuleResource(db.Model):
    """Learning materials for each module"""
    __tablename__ = 'module_resources'

    id = db.Column(Integer, primary_key=True)
    module_id = db.Column(Integer, ForeignKey('path_modules.id'), nullable=False, index=True)
    title = db.Column(String(128), nullable=False)
    url = db.Column(String(512), nullable=False)
    type = db.Column(String(16), nullable=False)  # video, course, documentation, article
    difficulty = db.Column(String(16))  # beginner, intermediate, advanced
    created_at = db.Column(DateTime, default=datetime.utcnow)

    # Relationships
    module = db.relationship('PathModule', back_populates='resources')

class UserProgress(db.Model):
    """Track module completion status"""
    __tablename__ = 'user_progress'
    __table_args__ = (
        Index('idx_userprogress_user_module', 'user_id', 'module_id'),
        Index('idx_userprogress_status', 'status'),
    )

    id = db.Column(Integer, primary_key=True)
    user_id = db.Column(String(36), ForeignKey('users.id'), nullable=False, index=True)
    module_id = db.Column(Integer, ForeignKey('path_modules.id'), nullable=False, index=True)
    profile_id = db.Column(String(36), ForeignKey('user_profiles.id'), nullable=False, index=True)
    status = db.Column(String(16), default='not_started')
    completion_date = db.Column(DateTime)
    version_id = db.Column(Integer, ForeignKey('roadmap_versions.id'), index=True)
    migrated_to = db.Column(Integer, ForeignKey('path_modules.id'), index=True)
    created_at = db.Column(DateTime, default=datetime.utcnow)
    updated_at = db.Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = db.relationship('User', back_populates='progress')
    profile = db.relationship('UserProfile', back_populates='progress')
    module = db.relationship('PathModule', back_populates='progress', 
                            foreign_keys=[module_id])  # SPECIFY FOREIGN KEY
    migrated_module = db.relationship('PathModule', 
                                     foreign_keys=[migrated_to])  # SPECIFY FOREIGN KEY
    version = db.relationship('RoadmapVersion')

# ======================
# ACTIVITY TABLES (2 tables)
# ======================

class LearningActivity(db.Model):
    """Unified table for assessments and projects"""
    __tablename__ = 'learning_activities'
    __table_args__ = (
        CheckConstraint("type IN ('quiz', 'project', 'exercise')", name='check_activity_type'),
        Index('idx_activity_module', 'module_id'),
    )

    id = db.Column(Integer, primary_key=True)
    module_id = db.Column(Integer, ForeignKey('path_modules.id'), nullable=False, index=True)
    type = db.Column(String(16), nullable=False)  # quiz, project, exercise
    title = db.Column(String(128), nullable=False)
    description = db.Column(Text)
    points = db.Column(Integer, default=0)
    deadline = db.Column(DateTime)
    github_template = db.Column(String(512))  # Only for projects
    created_at = db.Column(DateTime, default=datetime.utcnow)

    # Relationships
    module = db.relationship('PathModule', back_populates='activities')
    submissions = db.relationship('ActivitySubmission', back_populates='activity', cascade='all, delete-orphan')

class ActivitySubmission(db.Model):
    """Unified table for assessment and project submissions"""
    __tablename__ = 'activity_submissions'
    __table_args__ = (
        CheckConstraint("status IN ('not_started', 'in_progress', 'submitted', 'completed', 'graded')", name='check_submission_status'),
        Index('idx_submission_user_activity', 'user_id', 'activity_id'),
    )

    id = db.Column(Integer, primary_key=True)
    user_id = db.Column(String(36), ForeignKey('users.id'), nullable=False, index=True)
    activity_id = db.Column(Integer, ForeignKey('learning_activities.id'), nullable=False, index=True)
    submission_url = db.Column(String(512))  # For projects (external URL)
    answer_data = db.Column(JSONB)  # For quizzes
    status = db.Column(String(16), default='not_started')
    score = db.Column(Integer)
    feedback = db.Column(Text)
    submitted_at = db.Column(DateTime, default=datetime.utcnow)
    reviewed_at = db.Column(DateTime)
    created_at = db.Column(DateTime, default=datetime.utcnow)
    updated_at = db.Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = db.relationship('User', back_populates='activity_submissions')
    activity = db.relationship('LearningActivity', back_populates='submissions')

# ======================
# GAMIFICATION TABLES (3 tables)
# ======================

class Badge(db.Model):
    """Badge types"""
    __tablename__ = 'badges'
    id = db.Column(Integer, primary_key=True)
    name = db.Column(String(32), unique=True, nullable=False)
    description = db.Column(String(256))
    icon_url = db.Column(String(512))

class UserBadge(db.Model):
    """Badges earned by users"""
    __tablename__ = 'user_badges'
    __table_args__ = (
        Index('idx_userbadge_user', 'user_id'),
        Index('idx_userbadge_badge', 'badge_id'),
    )

    id = db.Column(Integer, primary_key=True)
    user_id = db.Column(String(36), ForeignKey('users.id'), nullable=False, index=True)
    badge_id = db.Column(Integer, ForeignKey('badges.id'), nullable=False, index=True)
    earned_at = db.Column(DateTime, default=datetime.utcnow)
    badge_data = db.Column(JSONB)  # Additional badge data

    # Relationships
    user = db.relationship('User', back_populates='badges')
    badge = db.relationship('Badge')

class UserPoints(db.Model):
    """Points accumulated by users"""
    __tablename__ = 'user_points'
    __table_args__ = (
        CheckConstraint('points >= 0', name='check_points_positive'),
    )

    id = db.Column(Integer, primary_key=True)
    user_id = db.Column(String(36), ForeignKey('users.id'), nullable=False, unique=True)
    points = db.Column(Integer, default=0, nullable=False)
    last_updated = db.Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = db.relationship('User', back_populates='points')

# ======================
# COMMUNITY TABLES (2 tables)
# ======================

class ForumPost(db.Model):
    """Discussion threads"""
    __tablename__ = 'forum_posts'
    __table_args__ = (
        Index('idx_forumpost_user', 'user_id'),
        Index('idx_forumpost_module', 'module_id'),
    )

    id = db.Column(Integer, primary_key=True)
    user_id = db.Column(String(36), ForeignKey('users.id'), nullable=False, index=True)
    title = db.Column(String(128), nullable=False)
    content = db.Column(Text)
    module_id = db.Column(Integer, ForeignKey('path_modules.id'), index=True)
    created_at = db.Column(DateTime, default=datetime.utcnow)
    updated_at = db.Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = db.relationship('User', back_populates='forum_posts')
    module = db.relationship('PathModule')
    replies = db.relationship('ForumReply', back_populates='post', cascade='all, delete-orphan')

class ForumReply(db.Model):
    """Replies to forum posts"""
    __tablename__ = 'forum_replies'
    __table_args__ = (
        Index('idx_forumreply_post', 'post_id'),
        Index('idx_forumreply_user', 'user_id'),
    )

    id = db.Column(Integer, primary_key=True)
    post_id = db.Column(Integer, ForeignKey('forum_posts.id'), nullable=False, index=True)
    user_id = db.Column(String(36), ForeignKey('users.id'), nullable=False, index=True)
    content = db.Column(Text)
    created_at = db.Column(DateTime, default=datetime.utcnow)
    updated_at = db.Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    post = db.relationship('ForumPost', back_populates='replies')
    user = db.relationship('User', back_populates='forum_replies')

# ======================
# AUTO-UPDATE TABLES (4 tables)
# ======================

class TechUpdate(db.Model):
    """Track new technology releases"""
    __tablename__ = 'tech_updates'
    __table_args__ = (
        Index('idx_techupdate_tech', 'tech_id'),
        Index('idx_techupdate_version', 'new_version'),
        CheckConstraint('confidence_score >= 0 AND confidence_score <= 1', name='check_confidence_score'),
        CheckConstraint('impact_score >= 1 AND impact_score <= 10', name='check_impact_score'),
        CheckConstraint("stability IN ('experimental', 'beta', 'stable', 'deprecated')", name='check_stability'),
        CheckConstraint("required_action IN ('learn', 'migrate', 'optional')", name='check_required_action'),
    )

    id = db.Column(Integer, primary_key=True)
    tech_id = db.Column(Integer, ForeignKey('technologies.id'), nullable=False, index=True)
    old_version = db.Column(String(20), nullable=False)
    new_version = db.Column(String(20))
    release_date = db.Column(Date)
    changelog = db.Column(Text)
    source_url = db.Column(String(512))
    is_major = db.Column(Boolean, default=False)
    confidence_score = db.Column(Float)
    impact_score = db.Column(Integer)  # 1-10
    affected_domains = db.Column(ARRAY(Integer))  # Array of domain_ids
    replacement_for_id = db.Column(Integer, ForeignKey('technologies.id'), index=True)
    adoption_rate = db.Column(Float)
    stability = db.Column(String(16))  # experimental, beta, stable, deprecated
    required_action = db.Column(String(16))  # learn, migrate, optional
    created_at = db.Column(DateTime, default=datetime.utcnow)

    # Relationships
    tech = db.relationship('Technology', foreign_keys=[tech_id])
    replacement_for = db.relationship('Technology', foreign_keys=[replacement_for_id])

class RoadmapVersion(db.Model):
    """Store historical versions of roadmaps"""
    __tablename__ = 'roadmap_versions'
    __table_args__ = (
        Index('idx_roadmapversion_path', 'path_id'),
    )

    id = db.Column(Integer, primary_key=True)
    path_id = db.Column(Integer, ForeignKey('learning_paths.id'), nullable=False, index=True)
    update_id = db.Column(Integer, ForeignKey('tech_updates.id'), index=True)
    version_number = db.Column(Integer, nullable=False)
    notes = db.Column(Text)
    created_at = db.Column(DateTime, default=datetime.utcnow)

    # Relationships
    path = db.relationship('LearningPath', back_populates='versions')
    update = db.relationship('TechUpdate')
    modules = db.relationship('VersionedModule', back_populates='version', cascade='all, delete-orphan')

class VersionedModule(db.Model):
    """Snapshots of modules across versions"""
    __tablename__ = 'versioned_modules'
    __table_args__ = (
        Index('idx_versionedmodule_version', 'version_id'),
        CheckConstraint("status IN ('current', 'deprecated', 'new')", name='check_versioned_module_status'),
    )

    id = db.Column(Integer, primary_key=True)
    version_id = db.Column(Integer, ForeignKey('roadmap_versions.id'), nullable=False, index=True)
    original_module_id = db.Column(Integer, ForeignKey('path_modules.id'), index=True)
    title = db.Column(String(128), nullable=False)
    description = db.Column(Text)
    content = db.Column(JSONB)  # Module data
    status = db.Column(String(16))  # current, deprecated, new
    created_at = db.Column(DateTime, default=datetime.utcnow)

    # Relationships
    version = db.relationship('RoadmapVersion', back_populates='modules')
    original_module = db.relationship('PathModule')

class UpdateFeedback(db.Model):
    """Student ratings on updates"""
    __tablename__ = 'update_feedback'
    __table_args__ = (
        Index('idx_feedback_user_update', 'user_id', 'update_id'),
        CheckConstraint('rating >= 1 AND rating <= 5', name='check_rating_range'),
    )

    id = db.Column(Integer, primary_key=True)
    user_id = db.Column(String(36), ForeignKey('users.id'), nullable=False, index=True)
    update_id = db.Column(Integer, ForeignKey('tech_updates.id'), nullable=False, index=True)
    rating = db.Column(Integer)  # 1-5 stars
    comments = db.Column(Text)
    created_at = db.Column(DateTime, default=datetime.utcnow)

    # Relationships
    user = db.relationship('User', back_populates='update_feedback')
    update = db.relationship('TechUpdate')