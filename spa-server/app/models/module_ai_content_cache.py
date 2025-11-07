"""
Module AI Content Cache Model
Dedicated caching for Gemini-generated educational content
"""

from app import db
from datetime import datetime
from sqlalchemy import String, Integer, DateTime, Text, Boolean, Index
import hashlib

class ModuleAIContentCache(db.Model):
    """
    Cache AI-generated content for individual modules
    Separate from roadmap cache to avoid conflicts
    """
    __tablename__ = 'module_ai_content_cache'
    __table_args__ = (
        Index('idx_module_ai_cache_module', 'module_id'),
        Index('idx_module_ai_cache_hash', 'content_hash'),
        Index('idx_module_ai_cache_valid', 'is_valid', 'last_accessed_at'),
    )

    id = db.Column(Integer, primary_key=True)
    module_id = db.Column(Integer, db.ForeignKey('path_modules.id', ondelete='CASCADE'), nullable=False, unique=True, index=True)
    
    # Content identification
    content_hash = db.Column(String(64), nullable=False, index=True)  # Hash of title+description
    
    # Cached data
    ai_content = db.Column(Text, nullable=False)  # JSON string of AI-generated content
    model_used = db.Column(String(32))  # e.g., 'gemini-2.0-flash'
    
    # Cache metadata
    is_valid = db.Column(Boolean, default=True, nullable=False)
    usage_count = db.Column(Integer, default=1, nullable=False)
    
    # Timestamps
    created_at = db.Column(DateTime, default=datetime.utcnow, nullable=False)
    last_accessed_at = db.Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    module = db.relationship('PathModule', backref=db.backref('ai_content_cache', uselist=False, cascade='all, delete-orphan'))

    def __repr__(self):
        return f'<ModuleAIContentCache module={self.module_id} valid={self.is_valid}>'

    @staticmethod
    def generate_content_hash(title: str, description: str) -> str:
        """Generate hash for content identification"""
        content = f"{title}:{description}"
        return hashlib.md5(content.encode()).hexdigest()

    def to_dict(self):
        import json
        return {
            'id': self.id,
            'module_id': self.module_id,
            'content_hash': self.content_hash,
            'ai_content': json.loads(self.ai_content) if self.ai_content else None,
            'model_used': self.model_used,
            'is_valid': self.is_valid,
            'usage_count': self.usage_count,
            'last_accessed_at': self.last_accessed_at.isoformat() if self.last_accessed_at else None,
        }
    
    def increment_usage(self):
        """Update usage statistics"""
        self.usage_count += 1
        self.last_accessed_at = datetime.utcnow()
    
    def invalidate(self):
        """Mark cache as invalid"""
        self.is_valid = False
        self.updated_at = datetime.utcnow()