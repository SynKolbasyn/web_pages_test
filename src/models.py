"""A module for working with a database."""


from sqlalchemy import ForeignKey
from sqlalchemy.orm import (
    Mapped,
    declarative_base,
    mapped_column,
    relationship,
)

Base = declarative_base()


class User(Base):

    """A class for user table."""

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    first_name: Mapped[str] = mapped_column()
    last_name: Mapped[str] = mapped_column()

    posts: Mapped[list["Post"]] = relationship(back_populates="author")

    def __init__(self, first_name: str, last_name: str) -> None:
        """Create User object."""
        self.first_name = first_name
        self.last_name = last_name

    def as_dict(self) -> dict[str, str]:
        """Represent user table as dict."""
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}


class Post(Base):

    """A class for post table."""

    __tablename__ = "posts"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column()
    text: Mapped[str] = mapped_column()
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))

    author: Mapped["User"] = relationship(back_populates="posts")
    images: Mapped[list["Image"]] = relationship(back_populates="post")

    def as_dict(self) -> dict[str, str]:
        """Represent post table as dict."""
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}


class Image(Base):

    """A class for image table."""

    __tablename__ = "images"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    post_id: Mapped[int] = mapped_column(ForeignKey("posts.id"))
    image: Mapped[bytes] = mapped_column()

    post: Mapped["Post"] = relationship(back_populates="images")

    def as_dict(self) -> dict[str, str]:
        """Represent image table as dict."""
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}
