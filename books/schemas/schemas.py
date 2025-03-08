from datetime import datetime

from pydantic import BaseModel, Field


class CommentBase(BaseModel):
    publication_date: datetime = Field(default_factory=datetime.now)
    content: str

    class Config:
        from_attributes = True


class CommentCreate(CommentBase):
    pass


class CommentRead(CommentBase):
    id: int  # id of the comment
    post_id: int  # id of the post


class PostBase(BaseModel):
    title: str
    content: str
    publication_date: datetime = Field(default_factory=datetime.now)

    class Config:
        from_attributes = True


class PostPartialUpdate(BaseModel):
    title: str | None = None
    content: str | None = None


class PostCreate(PostBase):
    pass


# When the user creates a post
# Pydantic validates out an id (int) and comments (list of CommentRead)
class PostRead(PostBase):
    id: int
    comments: list[CommentRead]
