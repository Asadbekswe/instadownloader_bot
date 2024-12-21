# from datetime import datetime
#
# import pytz
# from sqlalchemy import func, BigInteger
# from sqlalchemy.orm import Mapped, mapped_column
# from sqlalchemy.types import TypeDecorator, DateTime
#
# from src.db.models import Base, AbstractClass
#
#
# class BaseModel(Base, AbstractClass):
#     __abstract__ = True
#     id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
#
#     def __str__(self):
#         return f"{self.id}"
#
#
# class TimeStamp(TypeDecorator):
#     impl = DateTime(timezone=True)
#     cache_ok = True
#     TASHKENT_TIMEZONE = pytz.timezone("Asia/Tashkent")
#
#     def process_bind_param(self, value: datetime, dialect):
#         if value is None:
#             return None
#         if value.tzinfo is None:
#             value = self.TASHKENT_TIMEZONE.localize(value)
#         return value.astimezone(self.TASHKENT_TIMEZONE)
#
#     def process_result_value(self, value, dialect):
#         if value is not None:
#             return value.astimezone(self.TASHKENT_TIMEZONE)
#         return value
#
#
# class TimeBaseModel(BaseModel):
#     __abstract__ = True
#     created_at: Mapped[TimeStamp] = mapped_column(TimeStamp, server_default=func.now())
#     updated_at: Mapped[TimeStamp] = mapped_column(TimeStamp, server_default=func.now(), server_onupdate=func.now())
