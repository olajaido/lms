from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_, desc, asc, text
from sqlalchemy.orm import selectinload, joinedload
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import os
import aiofiles
import magic
from pathlib import Path
import uuid

from .models import (
    Content, ContentCategory, ContentTag, ContentTagAssociation, 
    ContentVersion, ContentAccess, ContentAnalytics, ContentPlaylist,
    ContentPlaylistItem, ContentComment, ContentTranscription, ContentSubtitle
)
from .schemas import (
    ContentCreate, ContentUpdate, ContentCategoryCreate, ContentCategoryUpdate,
    ContentTagCreate, ContentTagUpdate, ContentVersionCreate, ContentVersionUpdate,
    ContentAccessCreate, ContentAccessUpdate, ContentAnalyticsCreate,
    ContentPlaylistCreate, ContentPlaylistUpdate, ContentPlaylistItemCreate,
    ContentCommentCreate, ContentCommentUpdate, ContentTranscriptionCreate,
    ContentSubtitleCreate, ContentSearchRequest
)

# Content CRUD
async def create_content(db: AsyncSession, content: ContentCreate, file_path: str, file_name: str, file_size: int, mime_type: str) -> Content:
    """Create content record."""
    db_content = Content(
        **content.dict(),
        file_path=file_path,
        file_name=file_name,
        file_size=file_size,
        mime_type=mime_type
    )
    db.add(db_content)
    await db.commit()
    await db.refresh(db_content)
    return db_content

async def get_content(db: AsyncSession, content_id: int) -> Optional[Content]:
    """Get content by ID."""
    result = await db.execute(
        select(Content).where(Content.id == content_id)
    )
    return result.scalar_one_or_none()

async def get_content_by_file_path(db: AsyncSession, file_path: str) -> Optional[Content]:
    """Get content by file path."""
    result = await db.execute(
        select(Content).where(Content.file_path == file_path)
    )
    return result.scalar_one_or_none()

async def update_content(db: AsyncSession, content_id: int, content: ContentUpdate) -> Optional[Content]:
    """Update content."""
    db_content = await get_content(db, content_id)
    if not db_content:
        return None
    
    update_data = content.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_content, field, value)
    
    db_content.updated_at = datetime.utcnow()
    await db.commit()
    await db.refresh(db_content)
    return db_content

async def delete_content(db: AsyncSession, content_id: int) -> bool:
    """Delete content."""
    db_content = await get_content(db, content_id)
    if not db_content:
        return False
    
    # Delete file from filesystem
    try:
        if os.path.exists(db_content.file_path):
            os.remove(db_content.file_path)
    except Exception:
        pass  # Continue even if file deletion fails
    
    await db.delete(db_content)
    await db.commit()
    return True

async def list_content(
    db: AsyncSession, 
    skip: int = 0, 
    limit: int = 100,
    content_type: Optional[str] = None,
    course_id: Optional[int] = None,
    uploaded_by: Optional[int] = None,
    is_public: Optional[bool] = None,
    is_active: Optional[bool] = None
) -> List[Content]:
    """List content with filters."""
    query = select(Content)
    
    if content_type:
        query = query.where(Content.content_type == content_type)
    if course_id:
        query = query.where(Content.course_id == course_id)
    if uploaded_by:
        query = query.where(Content.uploaded_by == uploaded_by)
    if is_public is not None:
        query = query.where(Content.is_public == is_public)
    if is_active is not None:
        query = query.where(Content.is_active == is_active)
    
    query = query.order_by(desc(Content.created_at)).offset(skip).limit(limit)
    result = await db.execute(query)
    return result.scalars().all()

async def search_content(db: AsyncSession, search_request: ContentSearchRequest) -> Dict[str, Any]:
    """Search content with advanced filters."""
    query = select(Content)
    
    # Text search
    if search_request.query:
        search_term = f"%{search_request.query}%"
        query = query.where(
            or_(
                Content.title.ilike(search_term),
                Content.description.ilike(search_term)
            )
        )
    
    # Filters
    if search_request.content_type:
        query = query.where(Content.content_type == search_request.content_type)
    if search_request.course_id:
        query = query.where(Content.course_id == search_request.course_id)
    if search_request.uploaded_by:
        query = query.where(Content.uploaded_by == search_request.uploaded_by)
    if search_request.is_public is not None:
        query = query.where(Content.is_public == search_request.is_public)
    if search_request.is_active is not None:
        query = query.where(Content.is_active == search_request.is_active)
    
    # Tag filtering
    if search_request.tags:
        # This would need a more complex join for tag filtering
        pass
    
    # Sorting
    if search_request.sort_by == "title":
        query = query.order_by(asc(Content.title) if search_request.sort_order == "asc" else desc(Content.title))
    elif search_request.sort_by == "created_at":
        query = query.order_by(asc(Content.created_at) if search_request.sort_order == "asc" else desc(Content.created_at))
    elif search_request.sort_by == "view_count":
        query = query.order_by(asc(Content.view_count) if search_request.sort_order == "asc" else desc(Content.view_count))
    elif search_request.sort_by == "rating":
        query = query.order_by(asc(Content.rating) if search_request.sort_order == "asc" else desc(Content.rating))
    else:
        query = query.order_by(desc(Content.created_at))
    
    # Pagination
    total_query = select(func.count(Content.id))
    if search_request.query:
        search_term = f"%{search_request.query}%"
        total_query = total_query.where(
            or_(
                Content.title.ilike(search_term),
                Content.description.ilike(search_term)
            )
        )
    
    total_result = await db.execute(total_query)
    total = total_result.scalar()
    
    query = query.offset((search_request.page - 1) * search_request.size).limit(search_request.size)
    result = await db.execute(query)
    content_list = result.scalars().all()
    
    return {
        "content": content_list,
        "total": total,
        "page": search_request.page,
        "size": search_request.size,
        "pages": (total + search_request.size - 1) // search_request.size
    }

# Content Category CRUD
async def create_content_category(db: AsyncSession, category: ContentCategoryCreate) -> ContentCategory:
    """Create content category."""
    db_category = ContentCategory(**category.dict())
    db.add(db_category)
    await db.commit()
    await db.refresh(db_category)
    return db_category

async def get_content_category(db: AsyncSession, category_id: int) -> Optional[ContentCategory]:
    """Get content category by ID."""
    result = await db.execute(
        select(ContentCategory).where(ContentCategory.id == category_id)
    )
    return result.scalar_one_or_none()

async def list_content_categories(db: AsyncSession, is_active: Optional[bool] = None) -> List[ContentCategory]:
    """List content categories."""
    query = select(ContentCategory)
    if is_active is not None:
        query = query.where(ContentCategory.is_active == is_active)
    result = await db.execute(query.order_by(ContentCategory.name))
    return result.scalars().all()

# Content Tag CRUD
async def create_content_tag(db: AsyncSession, tag: ContentTagCreate) -> ContentTag:
    """Create content tag."""
    db_tag = ContentTag(**tag.dict())
    db.add(db_tag)
    await db.commit()
    await db.refresh(db_tag)
    return db_tag

async def get_content_tag(db: AsyncSession, tag_id: int) -> Optional[ContentTag]:
    """Get content tag by ID."""
    result = await db.execute(
        select(ContentTag).where(ContentTag.id == tag_id)
    )
    return result.scalar_one_or_none()

async def get_content_tag_by_name(db: AsyncSession, name: str) -> Optional[ContentTag]:
    """Get content tag by name."""
    result = await db.execute(
        select(ContentTag).where(ContentTag.name == name)
    )
    return result.scalar_one_or_none()

async def list_content_tags(db: AsyncSession, is_active: Optional[bool] = None) -> List[ContentTag]:
    """List content tags."""
    query = select(ContentTag)
    if is_active is not None:
        query = query.where(ContentTag.is_active == is_active)
    result = await db.execute(query.order_by(ContentTag.name))
    return result.scalars().all()

async def add_content_tags(db: AsyncSession, content_id: int, tag_names: List[str]) -> List[ContentTag]:
    """Add tags to content."""
    tags = []
    for tag_name in tag_names:
        # Get or create tag
        tag = await get_content_tag_by_name(db, tag_name)
        if not tag:
            tag = await create_content_tag(db, ContentTagCreate(name=tag_name))
        
        # Check if association already exists
        existing_assoc = await db.execute(
            select(ContentTagAssociation).where(
                and_(
                    ContentTagAssociation.content_id == content_id,
                    ContentTagAssociation.tag_id == tag.id
                )
            )
        )
        if not existing_assoc.scalar_one_or_none():
            assoc = ContentTagAssociation(content_id=content_id, tag_id=tag.id)
            db.add(assoc)
        
        tags.append(tag)
    
    await db.commit()
    return tags

async def get_content_tags(db: AsyncSession, content_id: int) -> List[ContentTag]:
    """Get tags for a content item."""
    result = await db.execute(
        select(ContentTag)
        .join(ContentTagAssociation, ContentTag.id == ContentTagAssociation.tag_id)
        .where(ContentTagAssociation.content_id == content_id)
    )
    return result.scalars().all()

# Content Version CRUD
async def create_content_version(db: AsyncSession, version: ContentVersionCreate, file_path: str, file_name: str, file_size: int) -> ContentVersion:
    """Create content version."""
    db_version = ContentVersion(
        **version.dict(),
        file_path=file_path,
        file_name=file_name,
        file_size=file_size
    )
    db.add(db_version)
    await db.commit()
    await db.refresh(db_version)
    return db_version

async def get_content_versions(db: AsyncSession, content_id: int) -> List[ContentVersion]:
    """Get versions for a content item."""
    result = await db.execute(
        select(ContentVersion)
        .where(ContentVersion.content_id == content_id)
        .order_by(desc(ContentVersion.version_number))
    )
    return result.scalars().all()

async def get_active_content_version(db: AsyncSession, content_id: int) -> Optional[ContentVersion]:
    """Get active version for a content item."""
    result = await db.execute(
        select(ContentVersion)
        .where(
            and_(
                ContentVersion.content_id == content_id,
                ContentVersion.is_active == True
            )
        )
    )
    return result.scalar_one_or_none()

# Content Access CRUD
async def create_content_access(db: AsyncSession, access: ContentAccessCreate) -> ContentAccess:
    """Create content access record."""
    db_access = ContentAccess(**access.dict())
    db.add(db_access)
    await db.commit()
    await db.refresh(db_access)
    return db_access

async def get_content_access(db: AsyncSession, content_id: int, user_id: int) -> Optional[ContentAccess]:
    """Get content access for a user."""
    result = await db.execute(
        select(ContentAccess).where(
            and_(
                ContentAccess.content_id == content_id,
                ContentAccess.user_id == user_id
            )
        )
    )
    return result.scalar_one_or_none()

async def check_content_access(db: AsyncSession, content_id: int, user_id: int, access_type: str) -> bool:
    """Check if user has access to content."""
    # Check if content is public
    content = await get_content(db, content_id)
    if content and content.is_public:
        return True
    
    # Check specific access
    access = await get_content_access(db, content_id, user_id)
    if access and access.access_type == access_type:
        if access.expires_at and access.expires_at < datetime.utcnow():
            return False
        return True
    
    return False

# Content Analytics CRUD
async def create_content_analytics(db: AsyncSession, analytics: ContentAnalyticsCreate) -> ContentAnalytics:
    """Create content analytics record."""
    db_analytics = ContentAnalytics(**analytics.dict())
    db.add(db_analytics)
    await db.commit()
    await db.refresh(db_analytics)
    return db_analytics

async def update_content_stats(db: AsyncSession, content_id: int, action_type: str):
    """Update content statistics."""
    content = await get_content(db, content_id)
    if not content:
        return
    
    if action_type == "view":
        content.view_count += 1
    elif action_type == "download":
        content.download_count += 1
    
    await db.commit()

# Content Playlist CRUD
async def create_content_playlist(db: AsyncSession, playlist: ContentPlaylistCreate) -> ContentPlaylist:
    """Create content playlist."""
    db_playlist = ContentPlaylist(**playlist.dict())
    db.add(db_playlist)
    await db.commit()
    await db.refresh(db_playlist)
    return db_playlist

async def get_content_playlist(db: AsyncSession, playlist_id: int) -> Optional[ContentPlaylist]:
    """Get content playlist by ID."""
    result = await db.execute(
        select(ContentPlaylist).where(ContentPlaylist.id == playlist_id)
    )
    return result.scalar_one_or_none()

async def add_playlist_item(db: AsyncSession, item: ContentPlaylistItemCreate) -> ContentPlaylistItem:
    """Add item to playlist."""
    # Get next position
    result = await db.execute(
        select(func.max(ContentPlaylistItem.position))
        .where(ContentPlaylistItem.playlist_id == item.playlist_id)
    )
    max_position = result.scalar() or 0
    item.position = max_position + 1
    
    db_item = ContentPlaylistItem(**item.dict())
    db.add(db_item)
    await db.commit()
    await db.refresh(db_item)
    return db_item

async def get_playlist_items(db: AsyncSession, playlist_id: int) -> List[ContentPlaylistItem]:
    """Get items in a playlist."""
    result = await db.execute(
        select(ContentPlaylistItem)
        .where(ContentPlaylistItem.playlist_id == playlist_id)
        .order_by(ContentPlaylistItem.position)
    )
    return result.scalars().all()

# Content Comment CRUD
async def create_content_comment(db: AsyncSession, comment: ContentCommentCreate) -> ContentComment:
    """Create content comment."""
    db_comment = ContentComment(**comment.dict())
    db.add(db_comment)
    await db.commit()
    await db.refresh(db_comment)
    return db_comment

async def get_content_comments(db: AsyncSession, content_id: int, is_approved: Optional[bool] = None) -> List[ContentComment]:
    """Get comments for content."""
    query = select(ContentComment).where(ContentComment.content_id == content_id)
    if is_approved is not None:
        query = query.where(ContentComment.is_approved == is_approved)
    result = await db.execute(query.order_by(desc(ContentComment.created_at)))
    return result.scalars().all()

# Content Transcription CRUD
async def create_content_transcription(db: AsyncSession, transcription: ContentTranscriptionCreate) -> ContentTranscription:
    """Create content transcription."""
    db_transcription = ContentTranscription(**transcription.dict())
    db.add(db_transcription)
    await db.commit()
    await db.refresh(db_transcription)
    return db_transcription

async def get_content_transcriptions(db: AsyncSession, content_id: int, language: Optional[str] = None) -> List[ContentTranscription]:
    """Get transcriptions for content."""
    query = select(ContentTranscription).where(ContentTranscription.content_id == content_id)
    if language:
        query = query.where(ContentTranscription.language == language)
    result = await db.execute(query.order_by(ContentTranscription.start_time))
    return result.scalars().all()

# Content Subtitle CRUD
async def create_content_subtitle(db: AsyncSession, subtitle: ContentSubtitleCreate) -> ContentSubtitle:
    """Create content subtitle."""
    db_subtitle = ContentSubtitle(**subtitle.dict())
    db.add(db_subtitle)
    await db.commit()
    await db.refresh(db_subtitle)
    return db_subtitle

async def get_content_subtitles(db: AsyncSession, content_id: int, language: Optional[str] = None) -> List[ContentSubtitle]:
    """Get subtitles for content."""
    query = select(ContentSubtitle).where(ContentSubtitle.content_id == content_id)
    if language:
        query = query.where(ContentSubtitle.language == language)
    result = await db.execute(query.order_by(ContentSubtitle.start_time))
    return result.scalars().all()

# File handling utilities
async def save_uploaded_file(file_content: bytes, filename: str, upload_dir: str) -> str:
    """Save uploaded file and return file path."""
    # Create unique filename
    file_ext = Path(filename).suffix
    unique_filename = f"{uuid.uuid4()}{file_ext}"
    file_path = Path(upload_dir) / unique_filename
    
    # Ensure upload directory exists
    Path(upload_dir).mkdir(parents=True, exist_ok=True)
    
    # Save file
    async with aiofiles.open(file_path, 'wb') as f:
        await f.write(file_content)
    
    return str(file_path)

def get_mime_type(file_path: str) -> str:
    """Get MIME type of file."""
    return magic.from_file(file_path, mime=True)

def get_file_size(file_path: str) -> int:
    """Get file size in bytes."""
    return os.path.getsize(file_path)

# Content statistics
async def get_content_stats(db: AsyncSession) -> Dict[str, Any]:
    """Get content statistics."""
    # Total content
    total_result = await db.execute(select(func.count(Content.id)))
    total_content = total_result.scalar() or 0
    
    # Total views and downloads
    views_result = await db.execute(select(func.sum(Content.view_count)))
    total_views = views_result.scalar() or 0
    
    downloads_result = await db.execute(select(func.sum(Content.download_count)))
    total_downloads = downloads_result.scalar() or 0
    
    # Average rating
    rating_result = await db.execute(select(func.avg(Content.rating)))
    average_rating = rating_result.scalar() or 0.0
    
    # Content by type
    type_result = await db.execute(
        select(Content.content_type, func.count(Content.id))
        .group_by(Content.content_type)
    )
    content_by_type = {row[0]: row[1] for row in type_result.fetchall()}
    
    # Recent uploads
    recent_result = await db.execute(
        select(Content)
        .order_by(desc(Content.created_at))
        .limit(10)
    )
    recent_uploads = recent_result.scalars().all()
    
    # Popular content
    popular_result = await db.execute(
        select(Content)
        .order_by(desc(Content.view_count))
        .limit(10)
    )
    popular_content = popular_result.scalars().all()
    
    return {
        "total_content": total_content,
        "total_views": total_views,
        "total_downloads": total_downloads,
        "average_rating": average_rating,
        "content_by_type": content_by_type,
        "recent_uploads": recent_uploads,
        "popular_content": popular_content
    } 