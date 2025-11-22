import os
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base

# Database URL - use environment variable or default to local postgres
# Supported databases:
# - PostgreSQL: postgresql+asyncpg://user:pass@host:port/db
# - MySQL: mysql+aiomysql://user:pass@host:port/db
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+asyncpg://domingossoares@localhost:5432/items_db"
)

# Create async engine with appropriate settings
# MySQL requires different pool settings
engine_args = {"echo": True}
if "mysql" in DATABASE_URL:
    engine_args["pool_pre_ping"] = True
    engine_args["pool_recycle"] = 3600

engine = create_async_engine(DATABASE_URL, **engine_args)

# Create async session factory
async_session_maker = async_sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)

# Base class for models
Base = declarative_base()


async def get_db():
    """Dependency to get database session"""
    async with async_session_maker() as session:
        yield session


async def init_db():
    """Initialize database tables"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
