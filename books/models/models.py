from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class Comment(Base):
    __tablename__ = "comments"  # table comments

    # comment id
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    # post id
    post_id: Mapped[int] = mapped_column(
        ForeignKey("posts.id"), nullable=False
    )  # foreign key in table posts column id

    # publication date
    publication_date: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=datetime.now
    )

    # content of the comment
    content: Mapped[str] = mapped_column(Text, nullable=False)

    # forward reference type hint, Mapped["Post"], Post between quotes because it's defined after the class Comment
    # relationship with the Post class, back_populates to table "comments"
    # one comment belongs to one post
    post: Mapped["Post"] = relationship("Post", back_populates="comments")


class Post(Base):
    __tablename__ = "posts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    publication_date: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=datetime.now
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)

    # one post has a list of comments
    # no need for the quotes in the type hint, no forward reference, Python knows class Comment
    # cascade, if a post is deleted, orphan comments? In this case, no, delete all
    comments: Mapped[list[Comment]] = relationship("Comment", cascade="all, delete")
