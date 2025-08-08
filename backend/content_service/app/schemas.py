from pydantic import BaseModel, Field, field_validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

class ContentType(str, Enum):
    VIDEO = "video"
    AUDIO = "audio"
    DOCUMENT = "document"
    IMAGE = "image"
    PRESENTATION = "presentation"
    SPREADSHEET = "spreadsheet"
    PDF = "pdf"
    ARCHIVE = "archive"
    OTHER = "other"

class AccessType(str, Enum):
    VIEW = "view"
    DOWNLOAD = "download"
    EDIT = "edit"
    ADMIN = "admin"

class ActionType(str, Enum):
    VIEW = "view"
    DOWNLOAD = "download"
    LIKE = "like"
    SHARE = "share"
    COMMENT = "comment"
    RATE = "rate"

# Base schemas
class ContentBase(BaseModel):
    title: str = Field(..., description="Content title")
    description: Optional[str] = Field(None, description="Content description")
    content_type: ContentType = Field(..., description="Type of content")
    course_id: Optional[int] = Field(None, description="Associated course ID")
    module_id: Optional[int] = Field(None, description="Associated module ID")
    is_public: bool = Field(False, description="Whether content is public")
    is_active: bool = Field(True, description="Whether content is active")

class ContentCreate(ContentBase):
    uploaded_by: int = Field(..., description="User ID who uploaded the content")

class ContentUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    content_type: Optional[ContentType] = None
    course_id: Optional[int] = None
    module_id: Optional[int] = None
    is_public: Optional[bool] = None
    is_active: Optional[bool] = None
    content_metadata: Optional[Dict[str, Any]] = None

class Content(ContentBase):
    id: int
    file_path: str
    file_name: str
    file_size: int
    mime_type: str
    duration: Optional[float] = None
    thumbnail_path: Optional[str] = None
    uploaded_by: int
    download_count: int
    view_count: int
    rating: float
    content_metadata: Optional[Dict[str, Any]] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class ContentCategoryBase(BaseModel):
    name: str = Field(..., description="Category name")
    description: Optional[str] = Field(None, description="Category description")
    parent_id: Optional[int] = Field(None, description="Parent category ID")
    is_active: bool = Field(True, description="Whether category is active")

class ContentCategoryCreate(ContentCategoryBase):
    pass

class ContentCategoryUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    parent_id: Optional[int] = None
    is_active: Optional[bool] = None

class ContentCategory(ContentCategoryBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class ContentTagBase(BaseModel):
    name: str = Field(..., description="Tag name")
    description: Optional[str] = Field(None, description="Tag description")
    color: Optional[str] = Field(None, description="Hex color code")
    is_active: bool = Field(True, description="Whether tag is active")

class ContentTagCreate(ContentTagBase):
    pass

class ContentTagUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    color: Optional[str] = None
    is_active: Optional[bool] = None

class ContentTag(ContentTagBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class ContentVersionBase(BaseModel):
    content_id: int = Field(..., description="Content ID")
    version_number: int = Field(..., description="Version number")
    change_log: Optional[str] = Field(None, description="Change log for this version")
    uploaded_by: int = Field(..., description="User ID who uploaded this version")

class ContentVersionCreate(ContentVersionBase):
    pass

class ContentVersionUpdate(BaseModel):
    change_log: Optional[str] = None
    is_active: Optional[bool] = None

class ContentVersion(ContentVersionBase):
    id: int
    file_path: str
    file_name: str
    file_size: int
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True

class ContentAccessBase(BaseModel):
    content_id: int = Field(..., description="Content ID")
    user_id: int = Field(..., description="User ID")
    access_type: AccessType = Field(..., description="Type of access")
    granted_by: Optional[int] = Field(None, description="User who granted access")
    expires_at: Optional[datetime] = Field(None, description="Access expiration date")

class ContentAccessCreate(ContentAccessBase):
    pass

class ContentAccessUpdate(BaseModel):
    access_type: Optional[AccessType] = None
    expires_at: Optional[datetime] = None

class ContentAccess(ContentAccessBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class ContentAnalyticsBase(BaseModel):
    content_id: int = Field(..., description="Content ID")
    user_id: int = Field(..., description="User ID")
    action_type: ActionType = Field(..., description="Type of action")
    session_duration: Optional[float] = Field(None, description="Session duration in seconds")
    progress_percentage: Optional[float] = Field(None, description="Progress percentage")
    device_info: Optional[Dict[str, Any]] = Field(None, description="Device information")
    ip_address: Optional[str] = Field(None, description="IP address")
    user_agent: Optional[str] = Field(None, description="User agent string")

class ContentAnalyticsCreate(ContentAnalyticsBase):
    pass

class ContentAnalytics(ContentAnalyticsBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True

class ContentPlaylistBase(BaseModel):
    name: str = Field(..., description="Playlist name")
    description: Optional[str] = Field(None, description="Playlist description")
    created_by: int = Field(..., description="User ID who created the playlist")
    is_public: bool = Field(False, description="Whether playlist is public")
    is_active: bool = Field(True, description="Whether playlist is active")

class ContentPlaylistCreate(ContentPlaylistBase):
    pass

class ContentPlaylistUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    is_public: Optional[bool] = None
    is_active: Optional[bool] = None

class ContentPlaylist(ContentPlaylistBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class ContentPlaylistItemBase(BaseModel):
    playlist_id: int = Field(..., description="Playlist ID")
    content_id: int = Field(..., description="Content ID")
    position: int = Field(..., description="Position in playlist")
    added_by: int = Field(..., description="User ID who added the item")

class ContentPlaylistItemCreate(ContentPlaylistItemBase):
    pass

class ContentPlaylistItemUpdate(BaseModel):
    position: Optional[int] = None

class ContentPlaylistItem(ContentPlaylistItemBase):
    id: int
    added_at: datetime

    class Config:
        from_attributes = True

class ContentCommentBase(BaseModel):
    content_id: int = Field(..., description="Content ID")
    user_id: int = Field(..., description="User ID")
    parent_id: Optional[int] = Field(None, description="Parent comment ID for replies")
    comment: str = Field(..., description="Comment text")
    rating: Optional[int] = Field(None, ge=1, le=5, description="Rating from 1-5")
    is_approved: bool = Field(False, description="Whether comment is approved")
    is_active: bool = Field(True, description="Whether comment is active")

class ContentCommentCreate(ContentCommentBase):
    pass

class ContentCommentUpdate(BaseModel):
    comment: Optional[str] = None
    rating: Optional[int] = Field(None, ge=1, le=5)
    is_approved: Optional[bool] = None
    is_active: Optional[bool] = None

class ContentComment(ContentCommentBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class ContentTranscriptionBase(BaseModel):
    content_id: int = Field(..., description="Content ID")
    language: str = Field("en", description="Language code")
    transcription_text: str = Field(..., description="Transcription text")
    start_time: Optional[float] = Field(None, description="Start time in seconds")
    end_time: Optional[float] = Field(None, description="End time in seconds")
    confidence_score: Optional[float] = Field(None, description="Confidence score")
    is_auto_generated: bool = Field(True, description="Whether transcription is auto-generated")

class ContentTranscriptionCreate(ContentTranscriptionBase):
    pass

class ContentTranscriptionUpdate(BaseModel):
    transcription_text: Optional[str] = None
    start_time: Optional[float] = None
    end_time: Optional[float] = None
    confidence_score: Optional[float] = None
    is_auto_generated: Optional[bool] = None

class ContentTranscription(ContentTranscriptionBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class ContentSubtitleBase(BaseModel):
    content_id: int = Field(..., description="Content ID")
    language: str = Field(..., description="Language code")
    subtitle_text: str = Field(..., description="Subtitle text")
    start_time: float = Field(..., description="Start time in seconds")
    end_time: float = Field(..., description="End time in seconds")
    is_auto_generated: bool = Field(True, description="Whether subtitle is auto-generated")

class ContentSubtitleCreate(ContentSubtitleBase):
    pass

class ContentSubtitleUpdate(BaseModel):
    subtitle_text: Optional[str] = None
    start_time: Optional[float] = None
    end_time: Optional[float] = None
    is_auto_generated: Optional[bool] = None

class ContentSubtitle(ContentSubtitleBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# Content with relationships
class ContentWithTags(Content):
    tags: List[ContentTag] = []

class ContentWithComments(Content):
    comments: List[ContentComment] = []

class ContentWithAnalytics(Content):
    analytics: List[ContentAnalytics] = []

class ContentWithVersions(Content):
    versions: List[ContentVersion] = []

class ContentWithAccess(Content):
    access_controls: List[ContentAccess] = []

# Playlist with items
class ContentPlaylistWithItems(ContentPlaylist):
    items: List[ContentPlaylistItem] = []

# Response schemas
class ContentResponse(BaseModel):
    success: bool
    data: Any
    message: str

class ContentListResponse(BaseModel):
    success: bool
    data: List[Content]
    total: int
    page: int
    size: int
    message: str

class ContentUploadResponse(BaseModel):
    success: bool
    data: Content
    message: str

class ContentSearchResponse(BaseModel):
    success: bool
    data: List[Content]
    total: int
    filters: Dict[str, Any]
    message: str

class ContentStatsResponse(BaseModel):
    success: bool
    data: Dict[str, Any]
    message: str

class ContentTagResponse(BaseModel):
    success: bool
    data: ContentTag
    message: str

class ContentTagListResponse(BaseModel):
    success: bool
    data: List[ContentTag]
    message: str

# File upload schemas
class FileUploadRequest(BaseModel):
    title: str
    description: Optional[str] = None
    content_type: ContentType
    course_id: Optional[int] = None
    module_id: Optional[int] = None
    is_public: bool = False
    tags: List[str] = []
    content_metadata: Optional[Dict[str, Any]] = None

class FileUploadResponse(BaseModel):
    success: bool
    data: Content
    message: str

# Search and filter schemas
class ContentSearchRequest(BaseModel):
    query: Optional[str] = None
    content_type: Optional[ContentType] = None
    course_id: Optional[int] = None
    uploaded_by: Optional[int] = None
    tags: List[str] = []
    is_public: Optional[bool] = None
    is_active: Optional[bool] = None
    sort_by: str = "created_at"
    sort_order: str = "desc"
    page: int = 1
    size: int = 20

class ContentStats(BaseModel):
    total_content: int
    total_views: int
    total_downloads: int
    average_rating: float
    content_by_type: Dict[str, int]
    recent_uploads: List[Content]
    popular_content: List[Content] 