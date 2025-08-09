import os
from pathlib import Path
from typing import List, Optional, Dict, Any

from fastapi import Depends, FastAPI, File, HTTPException, status, UploadFile, Query, Form, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession

from .database import get_db, create_tables
from . import crud, schemas
from .service_integration import get_content_integration, content_integration

# Import authentication dependencies
import sys
import os
shared_path = os.path.join(os.path.dirname(__file__), '..', '..', 'shared')
if os.path.exists(shared_path):
    sys.path.append(shared_path)

try:
    from auth_middleware import require_user_auth, require_admin_auth, require_service_auth
    AUTH_MODULES_AVAILABLE = True
except ImportError:
    print("⚠️  Auth modules not available - running in standalone mode")
    AUTH_MODULES_AVAILABLE = False
    
    # Create dummy auth functions for when shared modules are not available
    def require_user_auth(request: Request):
        return {"user_id": 1, "email": "test@example.com", "role": "user"}
    
    def require_admin_auth(request: Request):
        return {"user_id": 1, "email": "admin@example.com", "role": "admin"}
    
    def require_service_auth(request: Request):
        return {"service_name": "content", "service_id": "content-1"}

# Directory where uploaded content will be stored
UPLOAD_DIR = os.getenv("UPLOAD_DIR", "./uploads")
Path(UPLOAD_DIR).mkdir(parents=True, exist_ok=True)

app = FastAPI(title="Content Management Service", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    """Create database tables and setup service integration on startup."""
    await create_tables()
    
    # Setup service integration
    content_integration.setup_event_handlers()
    print("✅ Content service startup complete - Service integration ready")

@app.get("/api/v1/health")
async def health_check() -> dict[str, str]:
    return {"status": "ok"}

@app.get("/api/v1/integration/test")
async def test_integration() -> dict[str, Any]:
    """Test service integration functionality."""
    try:
        integration = await get_content_integration()
        
        # Test service registry
        from .service_integration import service_registry
        user_url = service_registry.get_service_url("user")
        course_url = service_registry.get_service_url("course")
        
        return {
            "status": "ok",
            "service_integration": "working",
            "user_service_url": user_url,
            "course_service_url": course_url,
            "event_handler_available": integration.event_handler is not None,
            "service_client_available": integration.service_client is not None,
            "message": "Service integration test successful"
        }
    except Exception as e:
        return {
            "status": "error",
            "service_integration": "failed",
            "error": str(e),
            "message": "Service integration test failed"
        }

@app.get("/api/v1/auth/test")
async def test_auth(auth_info: Dict[str, Any] = Depends(require_user_auth)) -> dict[str, Any]:
    """Test authentication functionality."""
    return {
        "status": "ok",
        "authentication": "working",
        "user_id": auth_info.get("user_id"),
        "email": auth_info.get("email"),
        "role": auth_info.get("role"),
        "message": "Authentication test successful"
    }

@app.get("/api/v1/auth/admin-test")
async def test_admin_auth(auth_info: Dict[str, Any] = Depends(require_admin_auth)) -> dict[str, Any]:
    """Test admin authentication functionality."""
    return {
        "status": "ok",
        "admin_authentication": "working",
        "user_id": auth_info.get("user_id"),
        "email": auth_info.get("email"),
        "role": auth_info.get("role"),
        "message": "Admin authentication test successful"
    }

# ============================================================================
# SPECIFIC ROUTES (must come before parameterized routes)
# ============================================================================

# Content Upload Endpoint
@app.post("/api/v1/content/upload", response_model=schemas.ContentUploadResponse, status_code=status.HTTP_201_CREATED)
async def upload_content(
    file: UploadFile = File(...),
    title: str = Form(...),
    description: Optional[str] = Form(None),
    content_type: schemas.ContentType = Form(...),
    course_id: Optional[int] = Form(None),
    module_id: Optional[int] = Form(None),
    is_public: bool = Form(False),
    tags: str = Form(""),  # Comma-separated tags
    metadata: Optional[str] = Form(None),  # JSON string
    uploaded_by: int = Form(...),
    auth_info: Dict[str, Any] = Depends(require_user_auth),
    db: AsyncSession = Depends(get_db)
) -> schemas.ContentUploadResponse:
    """Upload content with metadata."""
    try:
        # Read file content
        file_content = await file.read()
        
        # Save file
        file_path = await crud.save_uploaded_file(file_content, file.filename, UPLOAD_DIR)
        
        # Get file info
        file_size = len(file_content)
        mime_type = crud.get_mime_type(file_path)
        
        # Parse tags
        tag_list = [tag.strip() for tag in tags.split(",") if tag.strip()] if tags else []
        
        # Parse metadata
        metadata_dict = None
        if metadata:
            import json
            try:
                metadata_dict = json.loads(metadata)
            except json.JSONDecodeError:
                pass
        
        # Create content record
        content_data = schemas.ContentCreate(
            title=title,
            description=description,
            content_type=content_type,
            course_id=course_id,
            module_id=module_id,
            is_public=is_public,
            uploaded_by=uploaded_by
        )
        
        db_content = await crud.create_content(
            db, content_data, file_path, file.filename, file_size, mime_type
        )
        
        # Add tags
        if tag_list:
            await crud.add_content_tags(db, db_content.id, tag_list)
        
        # Update metadata if provided
        if metadata_dict:
            await crud.update_content(db, db_content.id, schemas.ContentUpdate(content_metadata=metadata_dict))
            await db.refresh(db_content)
        
        # Publish content uploaded event
        integration = await get_content_integration()
        await integration.publish_content_uploaded_event({
            "id": db_content.id,
            "course_id": db_content.course_id,
            "title": db_content.title,
            "content_type": db_content.content_type,
            "uploaded_by": db_content.uploaded_by
        })
        
        return schemas.ContentUploadResponse(
            success=True,
            data=db_content,
            message="Content uploaded successfully"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to upload content: {str(e)}"
        )

# Content List and Search Endpoints
@app.get("/api/v1/content", response_model=schemas.ContentListResponse)
async def list_content(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    content_type: Optional[schemas.ContentType] = Query(None),
    course_id: Optional[int] = Query(None),
    uploaded_by: Optional[int] = Query(None),
    is_public: Optional[bool] = Query(None),
    is_active: Optional[bool] = Query(None),
    db: AsyncSession = Depends(get_db)
) -> schemas.ContentListResponse:
    """List content with filters."""
    contents = await crud.list_content(
        db, skip=skip, limit=limit, content_type=content_type,
        course_id=course_id, uploaded_by=uploaded_by,
        is_public=is_public, is_active=is_active
    )
    return schemas.ContentListResponse(
        success=True,
        data=contents,
        total=len(contents),
        page=skip // limit + 1,
        size=limit,
        message="Content list retrieved successfully"
    )

@app.post("/api/v1/content/search", response_model=schemas.ContentSearchResponse)
async def search_content(
    search_request: schemas.ContentSearchRequest,
    db: AsyncSession = Depends(get_db)
) -> schemas.ContentSearchResponse:
    """Search content with advanced filters."""
    results = await crud.search_content(db, search_request)
    return schemas.ContentSearchResponse(
        success=True,
        data=results,
        total=len(results),
        filters=search_request.dict(),
        message="Content search completed successfully"
    )

# Content Tags Endpoints
@app.post("/api/v1/content/tags", response_model=schemas.ContentTagResponse, status_code=status.HTTP_201_CREATED)
async def create_content_tag(
    tag: schemas.ContentTagCreate,
    auth_info: Dict[str, Any] = Depends(require_admin_auth),
    db: AsyncSession = Depends(get_db)
) -> schemas.ContentTagResponse:
    """Create content tag."""
    try:
        db_tag = await crud.create_content_tag(db, tag)
        return schemas.ContentTagResponse(
            success=True,
            data=db_tag,
            message="Content tag created successfully"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to create content tag: {str(e)}"
        )

@app.get("/api/v1/content/tags", response_model=schemas.ContentTagListResponse)
async def list_content_tags(
    is_active: Optional[bool] = Query(None),
    db: AsyncSession = Depends(get_db)
) -> schemas.ContentTagListResponse:
    """List content tags."""
    tags = await crud.list_content_tags(db, is_active)
    return schemas.ContentTagListResponse(
        success=True,
        data=tags,
        message="Content tags retrieved successfully"
    )

# Content Categories Endpoints
@app.post("/api/v1/content/categories", response_model=schemas.ContentResponse, status_code=status.HTTP_201_CREATED)
async def create_content_category(
    category: schemas.ContentCategoryCreate,
    auth_info: Dict[str, Any] = Depends(require_admin_auth),
    db: AsyncSession = Depends(get_db)
) -> schemas.ContentResponse:
    """Create content category."""
    try:
        db_category = await crud.create_content_category(db, category)
        return schemas.ContentResponse(
            success=True,
            data=db_category,
            message="Content category created successfully"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to create content category: {str(e)}"
        )

@app.get("/api/v1/content/categories", response_model=schemas.ContentResponse)
async def list_content_categories(
    is_active: Optional[bool] = Query(None),
    db: AsyncSession = Depends(get_db)
) -> schemas.ContentResponse:
    """List content categories."""
    categories = await crud.list_content_categories(db, is_active)
    return schemas.ContentResponse(
        success=True,
        data=categories,
        message="Content categories retrieved successfully"
    )

# Content Playlists Endpoints
@app.post("/api/v1/content/playlists", response_model=schemas.ContentResponse, status_code=status.HTTP_201_CREATED)
async def create_content_playlist(
    playlist: schemas.ContentPlaylistCreate,
    db: AsyncSession = Depends(get_db)
) -> schemas.ContentResponse:
    """Create content playlist."""
    try:
        db_playlist = await crud.create_content_playlist(db, playlist)
        return schemas.ContentResponse(
            success=True,
            data=db_playlist,
            message="Content playlist created successfully"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to create content playlist: {str(e)}"
        )

@app.get("/api/v1/content/playlists/{playlist_id}", response_model=schemas.ContentResponse)
async def get_content_playlist(
    playlist_id: int,
    db: AsyncSession = Depends(get_db)
) -> schemas.ContentResponse:
    """Get content playlist."""
    db_playlist = await crud.get_content_playlist(db, playlist_id)
    if not db_playlist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Playlist not found"
        )
    
    return schemas.ContentResponse(
        success=True,
        data=db_playlist,
        message="Content playlist retrieved successfully"
    )

@app.post("/api/v1/content/playlists/{playlist_id}/items", response_model=schemas.ContentResponse, status_code=status.HTTP_201_CREATED)
async def add_playlist_item(
    playlist_id: int,
    item: schemas.ContentPlaylistItemCreate,
    db: AsyncSession = Depends(get_db)
) -> schemas.ContentResponse:
    """Add item to playlist."""
    item.playlist_id = playlist_id
    try:
        db_item = await crud.add_playlist_item(db, item)
        return schemas.ContentResponse(
            success=True,
            data=db_item,
            message="Playlist item added successfully"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to add playlist item: {str(e)}"
        )

@app.get("/api/v1/content/playlists/{playlist_id}/items", response_model=schemas.ContentResponse)
async def get_playlist_items(
    playlist_id: int,
    db: AsyncSession = Depends(get_db)
) -> schemas.ContentResponse:
    """Get playlist items."""
    items = await crud.get_playlist_items(db, playlist_id)
    return schemas.ContentResponse(
        success=True,
        data=items,
        message="Playlist items retrieved successfully"
    )

# Content Analytics Endpoints
@app.get("/api/v1/content/analytics/stats", response_model=schemas.ContentStatsResponse)
async def get_content_stats(
    db: AsyncSession = Depends(get_db)
) -> schemas.ContentStatsResponse:
    """Get content statistics."""
    stats = await crud.get_content_stats(db)
    return schemas.ContentStatsResponse(
        success=True,
        data=stats,
        message="Content statistics retrieved successfully"
    )

# ============================================================================
# INTEGRATED ENDPOINTS (with service communication)
# ============================================================================

@app.get("/api/v1/content/{content_id}/with-user-info", response_model=schemas.ContentResponse)
async def get_content_with_user_info(
    content_id: int,
    db: AsyncSession = Depends(get_db)
) -> schemas.ContentResponse:
    """Get content with user information from user service."""
    db_content = await crud.get_content(db, content_id)
    if not db_content:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Content not found"
        )
    
    # Get user information from user service
    integration = await get_content_integration()
    user_info = await integration.get_user_info(db_content.uploaded_by)
    
    # Add user info to response
    content_data = db_content.__dict__.copy()
    content_data["uploader_info"] = user_info
    
    return schemas.ContentResponse(
        success=True,
        data=content_data,
        message="Content with user info retrieved successfully"
    )

@app.get("/api/v1/content/{content_id}/with-course-info", response_model=schemas.ContentResponse)
async def get_content_with_course_info(
    content_id: int,
    db: AsyncSession = Depends(get_db)
) -> schemas.ContentResponse:
    """Get content with course information from course service."""
    db_content = await crud.get_content(db, content_id)
    if not db_content:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Content not found"
        )
    
    # Get course information from course service
    integration = await get_content_integration()
    course_info = await integration.get_course_info(db_content.course_id) if db_content.course_id else None
    
    # Add course info to response
    content_data = db_content.__dict__.copy()
    content_data["course_info"] = course_info
    
    return schemas.ContentResponse(
        success=True,
        data=content_data,
        message="Content with course info retrieved successfully"
    )

@app.post("/api/v1/content/{content_id}/view", response_model=schemas.ContentResponse)
async def record_content_view(
    content_id: int,
    user_id: int,
    auth_info: Dict[str, Any] = Depends(require_user_auth),
    db: AsyncSession = Depends(get_db)
) -> schemas.ContentResponse:
    """Record content view and update progress."""
    db_content = await crud.get_content(db, content_id)
    if not db_content:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Content not found"
        )
    
    integration = await get_content_integration()
    
    # Check if user is enrolled in course (if content is course-related)
    if db_content.course_id:
        is_enrolled = await integration.check_user_enrollment(user_id, db_content.course_id)
        if not is_enrolled:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User not enrolled in course"
            )
    
    # Record analytics
    await crud.create_content_analytics(db, schemas.ContentAnalyticsCreate(
        content_id=content_id,
        user_id=user_id,
        action_type="view",
        session_duration=0,
        metadata={"timestamp": "2025-08-04T18:30:00"}
    ))
    
    # Update user progress
    await integration.update_user_progress(user_id, db_content.course_id, {
        "content_id": content_id,
        "action": "view",
        "timestamp": "2025-08-04T18:30:00"
    })
    
    # Publish event
    await integration.publish_content_viewed_event(content_id, user_id)
    
    return schemas.ContentResponse(
        success=True,
        data={"content_id": content_id, "user_id": user_id, "action": "view"},
        message="Content view recorded successfully"
    )

@app.post("/api/v1/content/{content_id}/download", response_model=schemas.ContentResponse)
async def record_content_download(
    content_id: int,
    user_id: int,
    auth_info: Dict[str, Any] = Depends(require_user_auth),
    db: AsyncSession = Depends(get_db)
) -> schemas.ContentResponse:
    """Record content download and update progress."""
    db_content = await crud.get_content(db, content_id)
    if not db_content:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Content not found"
        )
    
    integration = await get_content_integration()
    
    # Check if user is enrolled in course (if content is course-related)
    if db_content.course_id:
        is_enrolled = await integration.check_user_enrollment(user_id, db_content.course_id)
        if not is_enrolled:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User not enrolled in course"
            )
    
    # Record analytics
    await crud.create_content_analytics(db, schemas.ContentAnalyticsCreate(
        content_id=content_id,
        user_id=user_id,
        action_type="download",
        session_duration=0,
        metadata={"timestamp": "2025-08-04T18:30:00"}
    ))
    
    # Update user progress
    await integration.update_user_progress(user_id, db_content.course_id, {
        "content_id": content_id,
        "action": "download",
        "timestamp": "2025-08-04T18:30:00"
    })
    
    # Publish event
    await integration.publish_content_downloaded_event(content_id, user_id)
    
    return schemas.ContentResponse(
        success=True,
        data={"content_id": content_id, "user_id": user_id, "action": "download"},
        message="Content download recorded successfully"
    )

# ============================================================================
# PARAMETERIZED ROUTES (must come after specific routes)
# ============================================================================

@app.get("/api/v1/content/{content_id}", response_model=schemas.ContentResponse)
async def get_content(
    content_id: int,
    db: AsyncSession = Depends(get_db)
) -> schemas.ContentResponse:
    """Get content by ID."""
    db_content = await crud.get_content(db, content_id)
    if not db_content:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Content not found"
        )
    
    return schemas.ContentResponse(
        success=True,
        data=db_content,
        message="Content retrieved successfully"
    )

@app.put("/api/v1/content/{content_id}", response_model=schemas.ContentResponse)
async def update_content(
    content_id: int,
    content: schemas.ContentUpdate,
    auth_info: Dict[str, Any] = Depends(require_user_auth),
    db: AsyncSession = Depends(get_db)
) -> schemas.ContentResponse:
    """Update content."""
    db_content = await crud.update_content(db, content_id, content)
    if not db_content:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Content not found"
        )
    
    return schemas.ContentResponse(
        success=True,
        data=db_content,
        message="Content updated successfully"
    )

@app.delete("/api/v1/content/{content_id}")
async def delete_content(
    content_id: int,
    auth_info: Dict[str, Any] = Depends(require_admin_auth),
    db: AsyncSession = Depends(get_db)
):
    """Delete content."""
    success = await crud.delete_content(db, content_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Content not found"
        )
    
    return {
        "success": True,
        "message": "Content deleted successfully"
    }

# File serving endpoints
@app.get("/api/v1/content/{content_id}/file")
async def get_content_file(
    content_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get content file."""
    db_content = await crud.get_content(db, content_id)
    if not db_content:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Content not found"
        )
    
    if not os.path.exists(db_content.file_path):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not found"
        )
    
    return FileResponse(
        db_content.file_path,
        filename=db_content.file_name,
        media_type=db_content.mime_type
    )

@app.get("/api/v1/content/{content_id}/thumbnail")
async def get_content_thumbnail(
    content_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get content thumbnail."""
    db_content = await crud.get_content(db, content_id)
    if not db_content or not db_content.thumbnail_path:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Thumbnail not found"
        )
    
    if not os.path.exists(db_content.thumbnail_path):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Thumbnail file not found"
        )
    
    return FileResponse(db_content.thumbnail_path)

# Content-specific endpoints
@app.get("/api/v1/content/{content_id}/tags", response_model=schemas.ContentResponse)
async def get_content_tags(
    content_id: int,
    db: AsyncSession = Depends(get_db)
) -> schemas.ContentResponse:
    """Get tags for content."""
    tags = await crud.get_content_tags(db, content_id)
    return schemas.ContentResponse(
        success=True,
        data=tags,
        message="Content tags retrieved successfully"
    )

@app.post("/api/v1/content/{content_id}/comments", response_model=schemas.ContentResponse, status_code=status.HTTP_201_CREATED)
async def create_content_comment(
    content_id: int,
    comment: schemas.ContentCommentCreate,
    db: AsyncSession = Depends(get_db)
) -> schemas.ContentResponse:
    """Create content comment."""
    comment.content_id = content_id
    try:
        db_comment = await crud.create_content_comment(db, comment)
        return schemas.ContentResponse(
            success=True,
            data=db_comment,
            message="Content comment created successfully"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to create content comment: {str(e)}"
        )

@app.get("/api/v1/content/{content_id}/comments", response_model=schemas.ContentResponse)
async def get_content_comments(
    content_id: int,
    is_approved: Optional[bool] = Query(None),
    db: AsyncSession = Depends(get_db)
) -> schemas.ContentResponse:
    """Get content comments."""
    comments = await crud.get_content_comments(db, content_id, is_approved)
    return schemas.ContentResponse(
        success=True,
        data=comments,
        message="Content comments retrieved successfully"
    )

@app.post("/api/v1/content/{content_id}/analytics", response_model=schemas.ContentResponse, status_code=status.HTTP_201_CREATED)
async def create_content_analytics(
    content_id: int,
    analytics: schemas.ContentAnalyticsCreate,
    db: AsyncSession = Depends(get_db)
) -> schemas.ContentResponse:
    """Create content analytics."""
    analytics.content_id = content_id
    try:
        db_analytics = await crud.create_content_analytics(db, analytics)
        
        # Update content stats
        await crud.update_content_stats(db, content_id, analytics.action_type)
        
        return schemas.ContentResponse(
            success=True,
            data=db_analytics,
            message="Content analytics created successfully"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to create content analytics: {str(e)}"
        )

@app.post("/api/v1/content/{content_id}/transcriptions", response_model=schemas.ContentResponse, status_code=status.HTTP_201_CREATED)
async def create_content_transcription(
    content_id: int,
    transcription: schemas.ContentTranscriptionCreate,
    db: AsyncSession = Depends(get_db)
) -> schemas.ContentResponse:
    """Create content transcription."""
    transcription.content_id = content_id
    try:
        db_transcription = await crud.create_content_transcription(db, transcription)
        return schemas.ContentResponse(
            success=True,
            data=db_transcription,
            message="Content transcription created successfully"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to create content transcription: {str(e)}"
        )

@app.get("/api/v1/content/{content_id}/transcriptions", response_model=schemas.ContentResponse)
async def get_content_transcriptions(
    content_id: int,
    language: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db)
) -> schemas.ContentResponse:
    """Get content transcriptions."""
    transcriptions = await crud.get_content_transcriptions(db, content_id, language)
    return schemas.ContentResponse(
        success=True,
        data=transcriptions,
        message="Content transcriptions retrieved successfully"
    )

@app.post("/api/v1/content/{content_id}/subtitles", response_model=schemas.ContentResponse, status_code=status.HTTP_201_CREATED)
async def create_content_subtitle(
    content_id: int,
    subtitle: schemas.ContentSubtitleCreate,
    db: AsyncSession = Depends(get_db)
) -> schemas.ContentResponse:
    """Create content subtitle."""
    subtitle.content_id = content_id
    try:
        db_subtitle = await crud.create_content_subtitle(db, subtitle)
        return schemas.ContentResponse(
            success=True,
            data=db_subtitle,
            message="Content subtitle created successfully"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to create content subtitle: {str(e)}"
        )

@app.get("/api/v1/content/{content_id}/subtitles", response_model=schemas.ContentResponse)
async def get_content_subtitles(
    content_id: int,
    language: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db)
) -> schemas.ContentResponse:
    """Get content subtitles."""
    subtitles = await crud.get_content_subtitles(db, content_id, language)
    return schemas.ContentResponse(
        success=True,
        data=subtitles,
        message="Content subtitles retrieved successfully"
    )