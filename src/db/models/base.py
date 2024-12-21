from datetime import datetime

import pytz
from sqlalchemy import delete as sqlalchemy_delete, update as sqlalchemy_update, select
from sqlalchemy import func, BigInteger
from sqlalchemy.ext.asyncio import AsyncAttrs, create_async_engine, AsyncSession
from sqlalchemy.orm import DeclarativeBase, declared_attr, sessionmaker
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.types import TypeDecorator, DateTime

from root import conf


class Base(AsyncAttrs, DeclarativeBase):

    @declared_attr
    def __tablename__(self) -> str:
        __name = self.__name__[:1]
        for i in self.__name__[1:]:
            if i.isupper():
                __name += '_'
            __name += i
        __name = __name.lower()

        if __name.endswith('y'):
            __name = __name[:-1] + 'ie'
        return __name + 's'


class AsyncDatabaseSession:
    def __init__(self):
        self._session = None
        self._engine = None

    def __getattr__(self, name):
        return getattr(self._session, name)

    def init(self):
        self._engine = create_async_engine(
            conf.db.db_url
        )
        self._session = sessionmaker(self._engine, expire_on_commit=False, class_=AsyncSession)()  # noqa

    async def create_all(self):
        async with self._engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    async def drop_all(self):
        async with self._engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)


db = AsyncDatabaseSession()
db.init()


class AbstractClass:
    @staticmethod
    async def commit():
        try:
            await db.commit()
        except Exception:
            await db.rollback()
            raise

    @classmethod
    async def create(cls, **kwargs):
        object_ = cls(**kwargs)  # noqa
        db.add(object_)
        await cls.commit()
        return object_

    @classmethod
    async def update(cls, id_=None, telegram_id=None, **kwargs):
        if id_:
            query = (
                sqlalchemy_update(cls)
                .where(cls.id == id_)  # noqa
                .values(**kwargs)
                .execution_options(synchronize_session="fetch")
            )
        else:
            query = (
                sqlalchemy_update(cls)
                .where(cls.telegram_id == telegram_id)  # noqa
                .values(**kwargs)
                .execution_options(synchronize_session="fetch")
            )
        await db.execute(query)
        await cls.commit()

    @classmethod
    async def get(cls, id_: int):
        query = select(cls).where(cls.id == id_)  # noqa
        return (await db.execute(query)).scalar()

    @classmethod
    async def get_user_by_type(cls, type: str):
        query = select(cls).where(cls.type == type)  # noqa
        return (await db.execute(query)).scalars()

    @classmethod
    async def delete(cls, id_=None, user_telegram_id=None):
        if id_:
            query = sqlalchemy_delete(cls).where(cls.id == id_)  # noqa
        else:
            query = sqlalchemy_delete(cls).where(cls.user_telegram_id == user_telegram_id)  # noqa
        await db.execute(query)
        await cls.commit()

    @classmethod
    async def delete_by_channel_id(cls, chat_id=None, user_telegram_id=None):
        if chat_id:
            query = sqlalchemy_delete(cls).where(cls.chat_id == chat_id)  # noqa
        else:
            query = sqlalchemy_delete(cls).where(cls.user_telegram_id == user_telegram_id)  # noqa
        await db.execute(query)
        await cls.commit()

    @classmethod
    async def get_all(cls) -> None:
        return (await db.execute(select(cls))).scalars()

    @classmethod
    async def get_with_telegram_id(cls, telegram_id: int) -> None:
        query = select(cls).where(cls.telegram_id == telegram_id)  # noqa
        return (await db.execute(query)).scalar()


class BaseModel(Base, AbstractClass):
    __abstract__ = True
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)

    def __str__(self):
        return f"{self.id}"


class TimeStamp(TypeDecorator):
    impl = DateTime(timezone=True)
    cache_ok = True
    TASHKENT_TIMEZONE = pytz.timezone("Asia/Tashkent")

    def process_bind_param(self, value: datetime, dialect):
        if value is None:
            return None
        if value.tzinfo is None:
            value = self.TASHKENT_TIMEZONE.localize(value)
        return value.astimezone(self.TASHKENT_TIMEZONE)

    def process_result_value(self, value, dialect):
        if value is not None:
            return value.astimezone(self.TASHKENT_TIMEZONE)
        return value


class TimeBaseModel(BaseModel):
    __abstract__ = True
    created_at: Mapped[TimeStamp] = mapped_column(TimeStamp, server_default=func.now())
    updated_at: Mapped[TimeStamp] = mapped_column(TimeStamp, server_default=func.now(), server_onupdate=func.now())
