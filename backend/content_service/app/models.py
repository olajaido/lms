from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean, ForeignKey, JSON, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
from datetime import datetime

Base = declarative_base()

class Content(Base):
    """Content management model."""
    __tablename__ = "content"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    content_type = Column(String(50), nullable=False)  # video, document, image, audio, etc.
    file_path = Column(String(500), nullable=False)
    file_name = Column(String(255), nullable=False)
    file_size = Column(Integer, nullable=False)  # in bytes
    mime_type = Column(String(100), nullable=False)
    duration = Column(Float, nullable=True)  # for video/audio content in seconds
    thumbnail_path = Column(String(500), nullable=True)
    course_id = Column(Integer, nullable=True)  # associated course
    module_id = Column(Integer, nullable=True)  # associated module
    uploaded_by = Column(Integer, nullable=False)  # user ID
    is_public = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    download_count = Column(Integer, default=0)
    view_count = Column(Integer, default=0)
    rating = Column(Float, default=0.0)
    content_metadata = Column(JSON, nullable=True)  # additional content metadata
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

class ContentCategory(Base):
    """Content categories for organization."""
    __tablename__ = "content_categories"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    parent_id = Column(Integer, ForeignKey("content_categories.id"), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

class ContentTag(Base):
    """Content tags for better organization and search."""
    __tablename__ = "content_tags"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), nullable=False, unique=True)
    description = Column(Text, nullable=True)
    color = Column(String(7), nullable=True)  # hex color code
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

class ContentTagAssociation(Base):
    """Many-to-many relationship between content and tags."""
    __tablename__ = "content_tag_associations"
    
    id = Column(Integer, primary_key=True, index=True)
    content_id = Column(Integer, ForeignKey("content.id"), nullable=False)
    tag_id = Column(Integer, ForeignKey("content_tags.id"), nullable=False)
    created_at = Column(DateTime, default=func.now())

class ContentVersion(Base):
    """Content versioning for tracking changes."""
    __tablename__ = "content_versions"
    
    id = Column(Integer, primary_key=True, index=True)
    content_id = Column(Integer, ForeignKey("content.id"), nullable=False)
    version_number = Column(Integer, nullable=False)
    file_path = Column(String(500), nullable=False)
    file_name = Column(String(255), nullable=False)
    file_size = Column(Integer, nullable=False)
    change_log = Column(Text, nullable=True)
    uploaded_by = Column(Integer, nullable=False)
    is_active = Column(Boolean, default=False)  # only one version can be active
    created_at = Column(DateTime, default=func.now())

class ContentAccess(Base):
    """Content access tracking and permissions."""
    __tablename__ = "content_access"
    
    id = Column(Integer, primary_key=True, index=True)
    content_id = Column(Integer, ForeignKey("content.id"), nullable=False)
    user_id = Column(Integer, nullable=False)
    access_type = Column(String(20), nullable=False)  # view, download, edit, admin
    granted_by = Column(Integer, nullable=True)  # user who granted access
    expires_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

class ContentAnalytics(Base):
    """Content usage analytics and statistics."""
    __tablename__ = "content_analytics"
    
    id = Column(Integer, primary_key=True, index=True)
    content_id = Column(Integer, ForeignKey("content.id"), nullable=False)
    user_id = Column(Integer, nullable=False)
    action_type = Column(String(20), nullable=False)  # view, download, like, share, etc.
    session_duration = Column(Float, nullable=True)  # for video/audio content
    progress_percentage = Column(Float, nullable=True)  # for video/audio content
    device_info = Column(JSON, nullable=True)
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(String(500), nullable=True)
    created_at = Column(DateTime, default=func.now())

class ContentPlaylist(Base):
    """Content playlists for organizing related content."""
    __tablename__ = "content_playlists"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    created_by = Column(Integer, nullable=False)
    is_public = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

class ContentPlaylistItem(Base):
    """Items in content playlists."""
    __tablename__ = "content_playlist_items"
    
    id = Column(Integer, primary_key=True, index=True)
    playlist_id = Column(Integer, ForeignKey("content_playlists.id"), nullable=False)
    content_id = Column(Integer, ForeignKey("content.id"), nullable=False)
    position = Column(Integer, nullable=False)  # order in playlist
    added_by = Column(Integer, nullable=False)
    added_at = Column(DateTime, default=func.now())

class ContentComment(Base):
    """Comments and reviews on content."""
    __tablename__ = "content_comments"
    
    id = Column(Integer, primary_key=True, index=True)
    content_id = Column(Integer, ForeignKey("content.id"), nullable=False)
    user_id = Column(Integer, nullable=False)
    parent_id = Column(Integer, ForeignKey("content_comments.id"), nullable=True)  # for replies
    comment = Column(Text, nullable=False)
    rating = Column(Integer, nullable=True)  # 1-5 rating
    is_approved = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

class ContentTranscription(Base):
    """Transcriptions for video/audio content."""
    __tablename__ = "content_transcriptions"
    
    id = Column(Integer, primary_key=True, index=True)
    content_id = Column(Integer, ForeignKey("content.id"), nullable=False)
    language = Column(String(10), nullable=False, default="en")
    transcription_text = Column(Text, nullable=False)
    start_time = Column(Float, nullable=True)  # for timed transcriptions
    end_time = Column(Float, nullable=True)
    confidence_score = Column(Float, nullable=True)
    is_auto_generated = Column(Boolean, default=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

class ContentSubtitle(Base):
    """Subtitles for video content."""
    __tablename__ = "content_subtitles"
    
    id = Column(Integer, primary_key=True, index=True)
    content_id = Column(Integer, ForeignKey("content.id"), nullable=False)
    language = Column(String(10), nullable=False)
    subtitle_text = Column(Text, nullable=False)
    start_time = Column(Float, nullable=False)
    end_time = Column(Float, nullable=False)
    is_auto_generated = Column(Boolean, default=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now()) 