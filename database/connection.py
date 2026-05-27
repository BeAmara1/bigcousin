import os
import logging
from pathlib import Path

from sqlalchemy.ext.asyncio import (AsyncSession, async_sessionmaker,
                                    create_async_engine)

logger = logging.getLogger("bigcousin.db")

DB_DIR = Path("data")
DB_DIR.mkdir(exist_ok=True)

DB_PATH = os.getenv("DATABASE_URL", f"sqlite+aiosqlite:///{DB_DIR}/bigcousin.db")

engine = create_async_engine(DB_PATH, echo=False)

async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def init_db():
    from database.models import Base
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Banco de dados inicializado com sucesso")


async def get_session():
    async with async_session() as session:
        yield session
