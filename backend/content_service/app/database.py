from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
import os

# Database URL - using SQLite for development
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./content.db")

# Convert PostgreSQL URL to async URL if needed
if DATABASE_URL.startswith("postgresql://") and not DATABASE_URL.startswith("postgresql+asyncpg://"):
    DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://", 1)

# Create async engine
engine = create_async_engine(
    DATABASE_URL,
    echo=True,  # Set to False in production
    poolclass=StaticPool,
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {}
)

# Create async session factory
AsyncSessionLocal = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)

async def get_db():
    """Dependency to get database session."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()

async def create_tables():
    """Create all tables."""
    from .models import Base
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

async def drop_tables():
    """Drop all tables."""
    from .models import Base
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all) 