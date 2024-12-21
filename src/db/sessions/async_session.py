# import contextlib
# from asyncio import current_task
# from contextlib import asynccontextmanager
# from typing import AsyncIterator
#
# from sqlalchemy.ext.asyncio import (
#     AsyncConnection,
#     AsyncEngine,
#     AsyncSession,
#     async_sessionmaker,
#     create_async_engine,
#     async_scoped_session,
# )
#
# from root import settings
#
#
# class AsyncDatabaseSessionManager:
#     def __init__(self):
#         self._engine: AsyncEngine | None = None
#         self._sessionmaker: async_sessionmaker | None = None
#
#     def init(self, url: str = None, echo: bool = False):
#         self._engine = create_async_engine(url=url, echo=echo)
#         self._sessionmaker = async_sessionmaker(
#             bind=self._engine,
#             autocommit=False,
#             expire_on_commit=False,
#             class_=AsyncSession,
#         )
#
#     async def close(self):
#         if self._engine is None:
#             raise Exception("DatabaseSessionManager is not initialized")
#         await self._engine.dispose()
#         self._engine = None
#         self._sessionmaker = None
#
#     @contextlib.asynccontextmanager
#     async def connect(self) -> AsyncIterator[AsyncConnection]:
#         if self._engine is None:
#             raise Exception("DatabaseSessionManager is not initialized")
#
#         async with self._engine.begin() as connection:
#             try:
#                 yield connection
#             except Exception:
#                 await connection.rollback()
#                 raise
#
#     def get_scoped_session(self):
#         return async_scoped_session(
#             session_factory=self._sessionmaker, scopefunc=current_task
#         )
#
#     @contextlib.asynccontextmanager
#     async def session_dependency(self) -> AsyncSession:
#         async with self.get_scoped_session()() as session:
#             yield session
#
#     @contextlib.asynccontextmanager
#     async def session(self) -> AsyncIterator[AsyncSession]:
#         if self._sessionmaker is None:
#             raise Exception("DatabaseSessionManager is not initialized")
#         async with self._sessionmaker() as session:
#             try:
#                 yield session
#             except Exception:
#                 await session.rollback()
#                 raise
#             finally:
#                 await session.close()
#
#     @staticmethod
#     async def create_all(connection: AsyncConnection):
#         await connection.run_sync(BaseModel.metadata.create_all)
#
#     @staticmethod
#     async def drop_all(connection: AsyncConnection):
#         await connection.run_sync(BaseModel.metadata.drop_all)
#
#
# session_manager = AsyncDatabaseSessionManager()
# session_manager.init(url=settings.db.url, echo=settings.db.echo)
#
#
# @asynccontextmanager
# async def get_db():
#     async with session_manager.session() as session:
#         yield session
