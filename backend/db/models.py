from sqlalchemy.orm import DeclarativeBase
from typing import List
from typing import Optional
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship
from sqlalchemy import ForeignKey, String, Text

class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "user_account"
    spotify_user_id: Mapped[str] = mapped_column(primary_key=True, autoincrement=False)
    refresh_token: Mapped[str] = mapped_column(Text, nullable=False) 

# class TestUser(Base):
#     __tablename__ = "test_user_account"
#     id: Mapped[int] = mapped_column(primary_key=True)
#     name: Mapped[str] = mapped_column(String(30))
#     fullname: Mapped[Optional[str]]
#     addresses: Mapped[List["Address"]] = relationship(back_populates="user")
#     def __repr__(self) -> str:
#         return f"User(id={self.id!r}, name={self.name!r}, fullname={self.fullname!r})"

# class Address(Base):
#     __tablename__ = "test_address"
#     id: Mapped[int] = mapped_column(primary_key=True)
#     email_address: Mapped[str]
#     user_id = mapped_column(ForeignKey("test_user_account.id"))
#     user: Mapped[User] = relationship(back_populates="addresses")
#     def __repr__(self) -> str:
#         return f"Address(id={self.id!r}, email_address={self.email_address!r})"